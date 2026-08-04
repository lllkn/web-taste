#!/usr/bin/env python3
"""Regression tests for the Web Taste P0 workflow helpers."""

import base64
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import render_visual
import taste_library


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class RenderVisualTests(unittest.TestCase):
    def test_renders_self_contained_taste_board(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            screenshot = root / "desktop.png"
            screenshot.write_bytes(PNG_1X1)
            input_path = root / "board.json"
            data = {
                "title": "Reference",
                "source_url": "https://example.com/final",
                "captured_at": "2026-08-03",
                "summary": "Measured visual system.",
                "learning_focus": ["layout", "typography"],
                "scope": "Desktop and mobile",
                "screenshots": [
                    {"label": "Desktop", "path": "desktop.png", "viewport": "1440 x 900"}
                ],
                "palette": [{"name": "Ink", "value": "#161616", "role": "Primary text"}],
                "type_scale": [
                    {"role": "Display", "sample": "Reference", "spec": "72/64, 700"}
                ],
                "geometry": [
                    {"name": "Gutter", "value": "72 px", "role": "Desktop anchor"}
                ],
                "sections": [
                    {
                        "title": "Composition and hierarchy",
                        "summary": "One dominant message.",
                        "evidence": [
                            {
                                "type": "measured",
                                "label": "Width",
                                "value": "1296 px",
                                "confidence": "high",
                            }
                        ],
                    }
                ],
                "principles": [
                    {
                        "title": "Stage hierarchy",
                        "evidence": "Measured full-height scenes.",
                        "use_when": "Narrative pages",
                        "avoid_when": "Dense tools",
                        "implementation_cue": "Alternate viewport scenes and content bands.",
                        "confidence": "high",
                    }
                ],
                "do_not_copy": ["Brand identity"],
                "gaps": ["Reduced motion unavailable"],
            }
            input_path.write_text(json.dumps(data), encoding="utf-8")
            output = render_visual.render_taste_board(data, input_path)
            self.assertIn("data:image/png;base64,", output)
            self.assertIn("Transferable principles", output)
            self.assertNotIn(str(screenshot), output)

    def test_renders_two_component_options(self):
        data = {
            "title": "Navigation",
            "context": "Same content and viewport",
            "decision_question": "Which grammar should continue?",
            "options": [
                {
                    "id": "A",
                    "name": "Compact",
                    "preview_html": "<nav>Compact</nav>",
                    "difference": "Dense actions",
                    "tradeoff": "Less editorial presence",
                    "states": "default, focus, mobile",
                },
                {
                    "id": "B",
                    "name": "Editorial",
                    "preview_html": "<nav>Editorial</nav>",
                    "difference": "More breathing room",
                    "tradeoff": "Uses more height",
                    "states": "default, focus, mobile",
                },
            ],
        }
        output = render_visual.render_component_choice(data, Path("choice.json"))
        self.assertIn("data-choice=\"A\"", output)
        self.assertIn("data-choice=\"B\"", output)
        self.assertIn("Selected option", output)

    def test_rejects_remote_screenshot(self):
        with self.assertRaises(SystemExit):
            render_visual.local_image_data("https://example.com/image.png", Path.cwd())


class LibraryWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.references = self.root / "references"
        taste_library.REFERENCES = self.references
        taste_library.SITES = self.references / "sites"
        taste_library.APPLICATIONS = self.references / "applications"
        taste_library.REPORTS = self.references / "reports"
        taste_library.INDEX = self.references / "site-index.md"
        taste_library.PROFILE = self.references / "taste-profile.md"
        self.references.mkdir(parents=True)
        taste_library.PROFILE.write_text("# Taste Profile\n", encoding="utf-8")
        taste_library.INDEX.write_text("# Site Index\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_scaffolds_and_validates_pending_workflow(self):
        taste_library.new_record(
            SimpleNamespace(
                title="Example",
                url="https://example.com/page",
                learning_focus="layout and interaction",
                learning_scope="current page; desktop and mobile",
                slug=None,
                date="2026-08-03",
                page_type="landing-page",
            )
        )
        taste_library.new_application(
            SimpleNamespace(
                title="Example application",
                target="/workspace/example",
                slug=None,
                date="2026-08-03",
            )
        )
        taste_library.build_index()
        taste_library.validate()
        index = taste_library.INDEX.read_text(encoding="utf-8")
        self.assertIn("Learning focus", index)
        self.assertIn("pending", index)
        self.assertEqual(len(taste_library.record_paths()), 1)
        self.assertEqual(len(taste_library.application_paths()), 1)

    def test_reviewed_source_requires_visual_report(self):
        taste_library.new_record(
            SimpleNamespace(
                title="Reviewed",
                url="https://example.com/reviewed",
                learning_focus="components",
                learning_scope="current page; desktop",
                slug=None,
                date="2026-08-03",
                page_type="tool",
            )
        )
        path = taste_library.record_paths()[0]
        content = path.read_text(encoding="utf-8").replace(
            'review_status: "pending"', 'review_status: "confirmed"'
        )
        path.write_text(content, encoding="utf-8")
        with self.assertRaises(SystemExit):
            taste_library.validate()

    def test_implemented_application_rejects_unresolved_placeholders(self):
        taste_library.new_application(
            SimpleNamespace(
                title="Implemented",
                target="/workspace/implemented",
                slug=None,
                date="2026-08-03",
            )
        )
        path = taste_library.application_paths()[0]
        content = path.read_text(encoding="utf-8").replace(
            'status: "pending"', 'status: "implemented"'
        )
        path.write_text(content, encoding="utf-8")
        with self.assertRaises(SystemExit):
            taste_library.validate()


if __name__ == "__main__":
    unittest.main()
