#!/usr/bin/env python3
"""Behavioral regression tests for memory, migration, evidence and scoped review."""

import base64
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import render_visual as visual
import taste_library as library

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=')
SCRIPT = Path(library.__file__).resolve()


def board_data():
    return {
        'title': 'Reference', 'source_url': 'https://example.com/page',
        'captured_at': '2026-10-05', 'summary': 'Measured visual relationships.',
        'learning_focus': ['layout', 'typography'], 'scope': 'Desktop and mobile',
        'screenshots': [{'id': 'desktop', 'label': 'Desktop', 'path': 'desktop.png', 'viewport': '1440 x 900'},
                        {'id': 'mobile', 'label': 'Mobile', 'path': 'desktop.png', 'viewport': '390 x 844'}],
        'palette': [{'name': 'Ink', 'value': '#161616', 'role': 'Text'}],
        'type_scale': [{'role': 'Display', 'sample': 'Heading', 'size_px': 72, 'line_height_px': 64, 'weight': 700, 'font_family': 'Reference Serif'},
                       {'role': 'Caption', 'sample': 'Caption', 'size_px': 12, 'line_height_px': 16, 'weight': 400}],
        'geometry': [{'name': 'Gutter', 'value': '72 px', 'role': 'Alignment'}, {'name': 'Gap', 'value': '24 px', 'role': 'Grouping'}],
        'layout_skeletons': [{'label': 'Desktop', 'columns': 12, 'blocks': [{'label': 'Copy', 'span': 5}, {'label': 'Media', 'span': 7}]}],
        'comparisons': [{'title': 'Hero reflow', 'desktop': 'desktop', 'mobile': 'mobile', 'summary': 'Columns stack.'}],
        'sections': [{'title': 'Composition', 'summary': 'Hierarchy', 'evidence': [
            {'id': 'width', 'type': 'measured', 'label': 'Width', 'value': '1296 px', 'confidence': 'high', 'screenshot_ref': 'desktop'}]}],
        'principles': [
            {'id': 'hierarchy', 'title': 'Stage hierarchy', 'evidence': 'Width supports hierarchy', 'evidence_refs': ['width'],
             'use_when': 'Narrative portfolio pages', 'avoid_when': 'Dense dashboards', 'implementation_cue': 'Alternate scenes and content bands.', 'confidence': 'high'},
            {'id': 'spacing', 'title': 'Loose spacing', 'evidence': 'Composition observation', 'evidence_refs': ['width'],
             'use_when': 'Editorial pages', 'avoid_when': 'Tables', 'implementation_cue': 'Reserve room around headings.', 'confidence': 'medium'}],
        'do_not_copy': ['Brand identity'], 'gaps': ['Reduced motion not captured'],
    }


def option_data():
    return {'title': 'Navigation', 'context': 'Same content', 'decision_question': 'Choose a direction', 'options': [
        {'id': 'A', 'name': 'Compact', 'preview_html': '<style>body{background:red}nav{color:red}</style><nav>Compact</nav>',
         'difference': 'Dense', 'tradeoff': 'Less room', 'states': 'default', 'viewport': {'width': 390, 'height': 320}},
        {'id': 'B', 'name': 'Editorial', 'preview_html': '<nav>Editorial</nav>',
         'difference': 'Spacious', 'tradeoff': 'More height', 'states': 'default', 'viewport': {'width': 390, 'height': 320}}]}


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.iframes = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'iframe':
            self.iframes.append(attrs)


class RenderVisualTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'desktop.png').write_bytes(PNG)

    def tearDown(self):
        self.temp.cleanup()

    def test_self_contained_board_with_visual_scale_and_evidence_links(self):
        data = board_data()
        output = visual.render_taste_board(data, self.root / 'input.json')
        self.assertIn('data:image/png;base64,', output)
        self.assertNotIn(str(self.root), output)
        parser = DocumentParser()
        parser.feed(output)
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertIn('font-size:72px', output)
        self.assertIn('font-size:12px', output)
        self.assertIn('system substitute', output)
        self.assertIn('href="#width"', output)
        self.assertIn('grid-column:span 5', output)
        self.assertIn('width:33.333', output)
        (self.root / 'report.html').write_text(output)
        parsed = library.read_board({'visual_report': str(self.root / 'report.html'), 'source_url': data['source_url']})
        self.assertEqual(parsed['principles'][0]['evidence_refs'], ['width'])

    def test_legacy_typography_spec_renders_actual_size(self):
        output = visual.render_type_scale([{'role': 'Display', 'sample': 'Hero', 'spec': '72/64, 700'}])
        self.assertIn('font-size:72.0px', output)
        self.assertIn('line-height:64.0px', output)

    def test_reviewable_board_requires_real_evidence(self):
        for field in ('screenshots', 'sections', 'principles'):
            data = board_data()
            data[field] = []
            with self.subTest(field=field), self.assertRaises(SystemExit):
                visual.render_taste_board(data, self.root / 'input.json')

    def test_incomplete_board_needs_gaps_and_is_not_approvable(self):
        data = board_data()
        data.update(status='incomplete', screenshots=[], sections=[], principles=[], comparisons=[])
        output = visual.render_taste_board(data, self.root / 'input.json')
        report = self.root / 'incomplete.html'
        report.write_text(output)
        with self.assertRaises(ValueError):
            library.read_board({'visual_report': str(report), 'source_url': data['source_url']})
        data['gaps'] = []
        with self.assertRaises(SystemExit):
            visual.render_taste_board(data, self.root / 'input.json')

    def test_principle_refs_cannot_point_to_unknown_or_interpreted_evidence(self):
        for invalid in ('not-found', 'width'):
            data = board_data()
            data['principles'][0]['evidence_refs'] = [invalid]
            if invalid == 'width':
                data['sections'][0]['evidence'][0]['type'] = 'interpreted'
            with self.subTest(ref=invalid), self.assertRaises(SystemExit):
                visual.validate_board(data)

    def test_duplicate_ids_and_wrong_comparison_are_rejected(self):
        data = board_data()
        data['principles'][0]['id'] = 'width'
        with self.assertRaises(SystemExit):
            visual.validate_board(data)
        data = board_data()
        data['comparisons'][0]['mobile'] = 'missing'
        with self.assertRaises(SystemExit):
            visual.render_taste_board(data, self.root / 'input.json')

    def test_options_have_isolated_equal_sandboxed_viewports(self):
        output = visual.render_component_choice(option_data(), self.root / 'choice.json')
        parser = DocumentParser()
        parser.feed(output)
        self.assertEqual(len(parser.iframes), 2)
        self.assertTrue(all(frame['sandbox'] == '' for frame in parser.iframes))
        self.assertIn('body{background:red}', parser.iframes[0]['srcdoc'])
        self.assertNotIn('background:red', parser.iframes[1]['srcdoc'])
        self.assertEqual(parser.iframes[0]['style'], parser.iframes[1]['style'])
        self.assertIn('does not save approval', output)
        data = option_data()
        data['options'][1]['viewport']['width'] = 800
        with self.assertRaises(SystemExit):
            visual.render_component_choice(data, self.root / 'choice.json')

    def test_metadata_escapes_script_end_and_roundtrips(self):
        data = board_data()
        data['summary'] = '</script><script>alert(1)</script>'
        output = visual.render_taste_board(data, self.root / 'input.json')
        self.assertNotIn('<script>alert(1)</script>', output)
        (self.root / 'report.html').write_text(output)
        result = library.read_board({'visual_report': str(self.root / 'report.html'), 'source_url': data['source_url']})
        self.assertEqual(result['summary'], data['summary'])

    def test_remote_screenshot_and_invalid_font_size_rejected(self):
        with self.assertRaises(SystemExit):
            visual.local_image_data('https://example.com/image.png', self.root)
        with self.assertRaises(SystemExit):
            visual.render_type_scale([{'role': 'Display', 'sample': 'Hero', 'size_px': -20}])

    def test_state_and_motion_captures_keep_labels_and_timestamps(self):
        data = board_data()
        data['state_groups'] = [{'title': 'Menu states', 'frames': [{'label': 'Open', 'screenshot_ref': 'desktop'}]}]
        data['motion_sequences'] = [{'title': 'Entrance', 'frames': [
            {'label': 'Before', 'screenshot_ref': 'desktop', 'at_ms': 0},
            {'label': 'After', 'screenshot_ref': 'mobile', 'at_ms': 200}]}]
        output = visual.render_taste_board(data, self.root / 'input.json')
        self.assertIn('After · 200 ms', output)
        data['motion_sequences'][0]['frames'][0]['at_ms'] = -1
        with self.assertRaises(SystemExit):
            visual.render_taste_board(data, self.root / 'input.json')


class LibraryWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.old_root = library.LIBRARY_ROOT
        self.quiet = contextlib.redirect_stdout(io.StringIO())
        self.quiet.__enter__()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        library.configure_library(self.root / 'library')
        library.initialize_library()

    def tearDown(self):
        library.configure_library(self.old_root)
        self.temp.cleanup()
        self.quiet.__exit__(None, None, None)

    def new_source(self, slug='reference'):
        args = SimpleNamespace(title='Example', url='https://example.com/page', learning_focus='layout and interaction',
                               learning_scope='desktop and mobile', slug=slug, date='2026-10-05', page_type='portfolio')
        library.new_record(args)
        return library.SITES / (slug + '.md')

    def reviewed_source(self, slug='reference'):
        path = self.new_source(slug)
        (library.REPORTS / 'desktop.png').write_bytes(PNG)
        data = board_data()
        report = library.REPORTS / (slug + '.html')
        report.write_text(visual.render_taste_board(data, library.REPORTS / 'input.json'))
        text = path.read_text().replace('review_status: "pending"', "review_status: 'confirmed'")
        text = text.replace('visual_report: "pending"', 'visual_report: "reports/' + slug + '.html"')
        text = re.sub(r'TODO:[^\n]+', 'Completed observation or explicitly out of scope.', text)
        text += '\n[Desktop screenshot](../reports/desktop.png)\n'
        path.write_text(text)
        return path

    def review(self, decision='approved', scope='global', principle='hierarchy', source='reference'):
        library.record_decision(SimpleNamespace(source=source, principle_id=principle, decision=decision,
                                               scope=scope, user_words='Explicit user choice: ' + decision))

    def results(self, query='', scope='global'):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            library.search(SimpleNamespace(query=query, scope=scope, limit=4))
        return json.loads(output.getvalue())

    def test_pending_scaffold_and_application_validate(self):
        self.new_source()
        library.new_application(SimpleNamespace(title='古诗展示页', target='/workspace/poems', slug=None, date='2026-10-05'))
        library.build_index()
        library.validate()
        self.assertIn('pending', library.INDEX.read_text())

    def test_normal_markdown_links_and_single_quotes_validate(self):
        self.reviewed_source()
        library.validate()
        self.assertEqual(library.parse_frontmatter(library.SITES / 'reference.md')[0]['review_status'], 'confirmed')
        self.assertFalse(library.has_placeholder('[Fit for a narrative page]'))
        self.assertFalse(library.has_placeholder('[Transferable rule.](reference.md)'))

    def test_empty_url_and_invalid_date_rejected(self):
        path = self.reviewed_source()
        original = path.read_text()
        for before, after in [('source_url: "https://example.com/page"', 'source_url: ""'),
                              ('captured_at: "2026-10-05"', 'captured_at: "not-a-date"'),
                              ('tags: []', 'tags: string')]:
            path.write_text(original.replace(before, after))
            with self.subTest(after=after), self.assertRaises(SystemExit):
                library.validate()

    def test_report_capture_date_must_match_source_record(self):
        path = self.reviewed_source()
        path.write_text(path.read_text().replace('captured_at: "2026-10-05"', 'captured_at: "2026-10-04"'))
        with self.assertRaises(SystemExit):
            library.validate()

    def test_parser_handles_quoted_lists_escapes_and_rejects_duplicate_keys(self):
        path = self.root / 'metadata.md'
        title = 'Quotes " and newline\n and slash \\'
        path.write_text('---\ntitle: ' + library.quote_yaml(title) + "\ntags: ['one, two', 'it''s', bare]\n---\nBody")
        meta, body = library.parse_frontmatter(path)
        self.assertEqual(meta['title'], title)
        self.assertEqual(meta['tags'], ['one, two', "it's", 'bare'])
        self.assertEqual(body, 'Body')
        path.write_text('---\ntitle: A\ntitle: B\n---\n')
        with self.assertRaises(ValueError):
            library.parse_frontmatter(path)

    def test_reviewed_record_needs_valid_report_and_complete_text(self):
        path = self.new_source()
        path.write_text(path.read_text().replace('review_status: "pending"', 'review_status: "confirmed"'))
        with self.assertRaises(SystemExit):
            library.validate()

    def test_new_record_cannot_use_legacy_report_bypass(self):
        path = self.reviewed_source()
        text = re.sub(r'^visual_report:.*$', 'visual_report: "not-created-legacy"', path.read_text(), flags=re.M)
        path.write_text(text)
        with self.assertRaises(SystemExit):
            library.validate()

    def test_implemented_application_rejects_todo_but_accepts_links(self):
        library.new_application(SimpleNamespace(title='Application', target='/workspace/app', slug='app', date='2026-10-05'))
        path = library.APPLICATIONS / 'app.md'
        text = path.read_text().replace('status: "pending"', 'status: "implemented"')
        path.write_text(text)
        with self.assertRaises(SystemExit):
            library.validate()
        text = re.sub(r'TODO:[^\n]+', 'Verified or not applicable.', text)
        text = text.replace('[Source record]', '[Source](../sites/reference.md)').replace('[Fit]', 'Appropriate').replace('[Transferable relationships]', 'Hierarchy').replace('[Excluded traits]', 'Brand').replace('[Conflict or none]', 'None')
        path.write_text(text)
        library.validate()

    def test_chinese_names_and_query_variants_do_not_collide(self):
        self.assertNotEqual(library.slugify('古诗展示页'), library.slugify('个人档案'))
        self.assertNotEqual(library.default_slug('https://example.com/?page=1'), library.default_slug('https://example.com/?page=2'))
        self.assertEqual(library.default_slug('https://example.com/#one'), library.default_slug('https://example.com/#two'))
        for title in ('古诗展示页', '个人档案', '古诗展示页'):
            library.new_application(SimpleNamespace(title=title, target='/workspace/app', slug=None, date='2026-10-05'))
        self.assertEqual(len(library.application_paths()), 3)

    def test_partial_approval_search_rejection_and_revocation(self):
        self.reviewed_source()
        self.assertEqual(self.results()['matches'], [])
        self.review()
        self.review(decision='rejected', principle='spacing')
        results = self.results('portfolio')
        self.assertEqual(len(results['matches']), 1)
        self.assertEqual([p['id'] for p in results['matches'][0]['principles']], ['hierarchy'])
        self.assertEqual([p['id'] for p in results['matches'][0]['exclusions']], ['spacing'])
        self.assertIn('Stage hierarchy', library.PROFILE.read_text())
        self.review(decision='revoked')
        self.assertEqual(self.results()['matches'], [])
        self.assertEqual(len(self.results()['exclusions']), 1)
        self.assertNotIn('### Stage hierarchy', library.PROFILE.read_text())
        self.assertEqual(len(library.load_decisions()), 3)
        library.validate()

    def test_project_choice_does_not_become_global_preference(self):
        self.reviewed_source()
        self.review(scope='project:poems')
        self.assertEqual(self.results()['matches'], [])
        self.assertEqual(len(self.results(scope='project:poems')['matches']), 1)
        self.assertEqual(self.results(scope='project:dashboard')['matches'], [])

    def test_project_rejection_overrides_global_approval(self):
        self.reviewed_source()
        self.review()
        self.review(decision='rejected', scope='project:dashboard')
        self.assertEqual(len(self.results()['matches']), 1)
        self.assertEqual(self.results(scope='project:dashboard')['matches'], [])

    def test_pending_rejected_or_unapproved_sources_are_not_positive_memory(self):
        path = self.reviewed_source()
        self.review()
        original = path.read_text()
        for status in ('pending', 'rejected'):
            path.write_text(original.replace("review_status: 'confirmed'", 'review_status: "' + status + '"'))
            self.assertEqual(self.results()['matches'], [])
        with self.assertRaises(SystemExit):
            self.review()

    def test_rejected_source_can_record_an_explicit_exclusion(self):
        path = self.reviewed_source()
        path.write_text(path.read_text().replace("review_status: 'confirmed'", 'review_status: "rejected"'))
        self.review(decision='rejected')
        self.assertEqual(self.results()['matches'], [])
        self.assertEqual(len(self.results()['exclusions']), 1)

    def test_approval_cannot_reference_missing_principle_or_incomplete_report(self):
        self.reviewed_source()
        with self.assertRaises(SystemExit):
            self.review(principle='missing')
        data = board_data()
        data.update(status='incomplete')
        (library.REPORTS / 'reference.html').write_text(visual.render_taste_board(data, library.REPORTS / 'input.json'))
        with self.assertRaises(SystemExit):
            self.review()
        self.assertEqual(library.load_decisions(), [])

    def test_log_corruption_is_reported_instead_of_silently_ignored(self):
        library.DECISIONS.write_text('{bad json}\n')
        with self.assertRaises(SystemExit):
            library.validate()

    def test_incomplete_decision_snapshot_is_rejected(self):
        self.reviewed_source()
        self.review()
        event = library.load_decisions()[0]
        event['principle']['evidence_refs'] = 'width'
        library.DECISIONS.write_text(json.dumps(event) + '\n')
        with self.assertRaises(SystemExit):
            library.validate()

    def test_init_does_not_overwrite_memory_and_skill_root_is_not_writable_library(self):
        library.PROFILE.write_text('Preserved user memory')
        library.initialize_library()
        self.assertEqual(library.PROFILE.read_text(), 'Preserved user memory')
        library.configure_library(library.SKILL_ROOT / 'references')
        with self.assertRaises(SystemExit):
            library.initialize_library()
        with self.assertRaises(SystemExit):
            library.build_index()
        with self.assertRaises(SystemExit):
            library.rebuild_profile()

    def test_cli_works_from_another_project_and_explicit_data_root(self):
        templates_before = {path: path.read_bytes() for path in library.TEMPLATES.glob('*.md')}
        destination = self.root / 'cli-library'
        result = subprocess.run([sys.executable, str(SCRIPT), '--library-root', str(destination), 'new',
                                 '--title', 'Reference', '--url', 'https://example.com', '--learning-focus', 'layout',
                                 '--learning-scope', 'desktop'], cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((destination / 'sites').glob('*.md'))), 1)
        self.assertFalse((self.root / 'references').exists())
        self.assertEqual(templates_before, {path: path.read_bytes() for path in library.TEMPLATES.glob('*.md')})

    def test_default_data_root_honors_environment_without_creating_it(self):
        root = self.root / 'environment-library'
        with patch.dict(os.environ, {'WEB_TASTE_LIBRARY_ROOT': str(root)}):
            self.assertEqual(library.default_library_root(), root)
            result = subprocess.run([sys.executable, str(SCRIPT), 'root'], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(result.stdout.strip()), root.resolve())
        self.assertFalse(root.exists())

    def test_host_native_installs_share_scoped_memory_without_codex_metadata(self):
        self.reviewed_source()
        self.review()
        installations = {}
        for host, folder in [('codex', '.agents'), ('claude-code', '.claude'),
                             ('cursor', '.cursor'), ('github-copilot', '.github')]:
            target = self.root / host / folder / 'skills' / 'web-taste'
            shutil.copytree(library.SKILL_ROOT, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            # UI metadata must not become a dependency of any helper.
            (target / 'agents' / 'openai.yaml').unlink()
            script = target / 'scripts' / 'taste_library.py'
            installations[host] = script
            result = subprocess.run([sys.executable, str(script), '--library-root', str(library.LIBRARY_ROOT),
                                     'search', '--query', 'portfolio'], cwd=self.root / host,
                                    text=True, capture_output=True)
            with self.subTest(host=host):
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)['matches'][0]['principles'][0]['id'], 'hierarchy')
                validation = subprocess.run([sys.executable, str(script), '--library-root', str(library.LIBRARY_ROOT),
                                             'validate'], cwd=self.root / host, text=True, capture_output=True)
                self.assertEqual(validation.returncode, 0, validation.stderr)
        # A decision from another installed copy must immediately affect shared memory.
        revoke = subprocess.run([sys.executable, str(installations['claude-code']), '--library-root', str(library.LIBRARY_ROOT),
                                 'review', '--source', 'reference', '--principle-id', 'hierarchy', '--decision', 'revoked',
                                 '--scope', 'global', '--user-words', 'Withdraw this fixture preference.'],
                                cwd=self.root / 'claude-code', text=True, capture_output=True)
        self.assertEqual(revoke.returncode, 0, revoke.stderr)
        self.assertEqual(self.results()['matches'], [])
        self.assertEqual(len(library.load_decisions()), 2)

    def test_migration_backs_up_preserves_links_and_is_idempotent(self):
        legacy = self.root / 'legacy'
        (legacy / 'sites').mkdir(parents=True)
        (legacy / 'reports').mkdir()
        report = legacy / 'reports' / 'old.html'
        report.write_text('<!doctype html><title>Old evidence</title>')
        (legacy / 'taste-profile.md').write_text('# Taste Profile\nOld preference without decision history\n')
        source = legacy / 'sites' / 'old.md'
        source.write_text('---\nvisual_report: ' + library.quote_yaml(str(report)) + '\n---\nOld evidence\n')
        # An empty legacy metadata record still migrates intact; validation can report its gaps afterward.
        library.configure_library(self.root / 'migrated')
        library.migrate(SimpleNamespace(from_root=legacy))
        imported = library.SITES / 'old.md'
        self.assertEqual(library.parse_frontmatter(imported)[0]['visual_report'], 'reports/old.html')
        self.assertTrue(source.exists())
        self.assertTrue(any(library.LIBRARY_ROOT.glob('backups/*/sites/old.md')))
        self.assertIn('Old preference', (library.LIBRARY_ROOT / 'legacy-profile.md').read_text())
        self.assertNotIn('Old preference without', library.PROFILE.read_text())
        imported.write_text(imported.read_text() + '\nNew local correction\n')
        library.migrate(SimpleNamespace(from_root=legacy))
        self.assertIn('New local correction', imported.read_text())
        source.write_text(source.read_text() + '\nChanged legacy source\n')
        with self.assertRaises(SystemExit):
            library.migrate(SimpleNamespace(from_root=legacy))

    def test_migration_refuses_overwriting_existing_records(self):
        legacy = self.root / 'legacy'
        (legacy / 'sites').mkdir(parents=True)
        (legacy / 'sites' / 'reference.md').write_text('Old')
        self.new_source()
        before = (library.SITES / 'reference.md').read_text()
        with self.assertRaises(SystemExit):
            library.migrate(SimpleNamespace(from_root=legacy))
        self.assertEqual((library.SITES / 'reference.md').read_text(), before)

    def test_malformed_legacy_metadata_fails_before_importing_any_record(self):
        legacy = self.root / 'legacy'
        (legacy / 'sites').mkdir(parents=True)
        (legacy / 'sites' / 'bad.md').write_text('Missing frontmatter')
        with self.assertRaises(ValueError):
            library.migrate(SimpleNamespace(from_root=legacy))
        self.assertEqual(library.record_paths(), [])
        self.assertFalse((library.LIBRARY_ROOT / 'backups').exists())


if __name__ == '__main__':
    unittest.main()
