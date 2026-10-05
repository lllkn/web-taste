# Web Taste 修复与验证记录

日期：2026-10-05。针对[原始优化分析](optimization-review.zh-CN.md)中的问题完成修订，并补充多 agent 适配。更新概要见 [CHANGELOG](../CHANGELOG.md)。

## 已完成

| 范围 | 修复 |
| --- | --- |
| 数据生命周期 | 个人库默认位于用户数据目录，支持环境变量和 `--library-root`；脚本拒绝向 skill 安装目录写个人数据。静态 profile/index 仅作初始化模板。 |
| 旧库迁移 | `migrate` 备份并复制旧库，保留源文件、修复内部绝对报告路径、拒绝覆盖冲突；同一来源重复迁移不会重写新记忆。旧摘要留在 `legacy-profile.md` 等待审阅。 |
| 审批语义 | 网站观察可信度与用户认可分开；来源审阅不等于全盘喜好。原则级认可、拒绝和撤回保存到 `decisions.jsonl`，包括用户原话、全局/项目范围、证据快照和报告哈希。 |
| 校验 | 正常 Markdown 链接可用；修复空值、日期、URL、状态、标签类型和损坏日志检查。支持规定的扁平元数据格式，拒绝重复键与不支持的嵌套 YAML。 |
| 记录 ID | 保留中文名称；默认网站 ID 含页面身份哈希，区分查询参数；重复项目记录自动使用不同 ID。 |
| 检索 | `search` 仅返回相关已认可原则，按项目范围覆盖同一原则的全局决定；待审/拒绝来源不进入正向记忆，排除条件独立返回。空库或单来源均可继续工作。 |
| 证据展示 | 实际字号、行高、字重和字体替代说明；布局骨架、相对间距、响应式对照、状态和带时间戳的动效截图；原则可定位对应证据和截图。 |
| 缺证处理 | `draft` / `incomplete` 报告必须解释缺口；不足以审阅的报告不能用于批准长期原则。新记录不能借 legacy 标记跳过证据关联。 |
| 组件比较 | HTML 方案使用独立 sandbox iframe，保持相同视口，避免 CSS 相互污染；选择按钮明确只改变显示，用户在对话中反馈后才记录。 |
| 执行流程 | 收窄触发范围，按需读取参考说明；清楚的请求直接推进，合并重要未决选择，长期偏好仍需明确认可。使用绝对脚本路径，支持从其他项目调用。 |
| 多 agent 适配 | 共用标准 SKILL、脚本与数据格式，补齐 Codex、Claude Code、Cursor、GitHub Copilot 安装及调用说明；按实际浏览器、文件、Python 能力降级，允许顺序共享同一个私人库。 |
| 配套文档 | 更新 SKILL、UI 元数据、报告/记录格式、中英文 README、Git ignore 和 CI。 |

## 验证结果

- Python 3.9 与 Python 3.12 下均通过 **34 个行为回归测试**，包括从四种原生安装目录运行脚本、移除 Codex 专用元数据后使用共享记忆，以及跨安装认可和撤回。
- Skills CLI 1.7.0 在隔离项目中识别四个目标并成功安装本地 skill；测试没有修改用户的实际 agent 安装。尚未在四种客户端中逐一完成完整的学习、人工审阅和复用流程。
- skill-creator `quick_validate.py` 通过；其 PyYAML 依赖使用临时 `uv` 环境，没有添加到运行脚本依赖。
- YAML 元数据、CI 配置和 skill 内部 Markdown 引用路径检查通过。
- 隔离个人库的 `init → index → validate → search` CLI 流程通过，空库给出正常冷启动结果。
- Chrome headless 下检查 **1440 px 桌面和 390 px 手机**视口：Board 无横向溢出、无失效图片/证据链接，字号按 72 px / 12 px 实际渲染。
- 组件方案均保持 390 px 内部视口；方案 A 的全局红色背景不影响方案 B 或报告；鼠标和键盘选择正常，无页面脚本错误。
- 已查看桌面与手机报告、组件页截图。浏览器检查使用独立测试界面，没有写入真实用户偏好。
- `git diff --check` 通过。

## 使用变化

运行脚本仍只依赖 Python 标准库。CLI 的数据根参数放在子命令之前：

```bash
python3 /absolute/web-taste/scripts/taste_library.py --library-root /absolute/private/library init
python3 /absolute/web-taste/scripts/taste_library.py --library-root /absolute/private/library migrate --from /absolute/old/skill/references
```

升级旧安装前先迁移个人数据；迁移会保留旧摘要和来源证据。新增原则认可需要新格式的可审阅报告，不能从旧摘要自动推断批准。

检索是轻量关键词候选检索，最终仍需按当前任务检查适用和排除条件。HTML 方案预览禁用脚本，JS 驱动状态用实际组件截图展示。结构校验不代替真实网页观察或人类认可。
