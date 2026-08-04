# Web Taste

让你的 AI 逐步形成自己的网页审美：从真实网页中学习前端视觉语言，把经过确认的设计规律沉淀为 taste memory，再复用到新的网页、组件和产品中。

Web Taste 不是一个“照抄参考站”的工具。它关注可迁移的关系，例如信息层级、排版节奏、空间比例、色彩职责、组件语法、交互状态、响应式重组和动效逻辑，同时明确排除品牌标识、专有素材、原站代码与其他不可复用内容。

## 功能

- **学习网页前端**：用真实浏览器观察参考网页的桌面端、移动端和关键交互状态。
- **建立视觉证据**：将截图、排版、色板、间距、组件状态和动效整理成 Visual Taste Board。
- **培养 AI taste**：只有经过用户确认的规律才会进入长期 taste profile；偶然特征、冲突偏好和明确拒绝的方向会分开记录。
- **复用设计规律**：根据新项目的用户、内容、功能和情绪目标，检索最相关的历史案例并形成 Memory Fusion Note。
- **先选方向再实现**：当组件存在多个合理方向时，先渲染 2-3 个可比较方案，确认后再扩展到完整界面。
- **验证最终结果**：检查桌面端、移动端、交互状态、键盘可访问性、溢出和 reduced motion，而不只检查源代码。

## 工作方式

### 学习模式

1. 快速扫描参考网址。
2. 和用户确认 Learn Brief，明确要学什么、检查哪些页面和状态、是否写入长期知识库。
3. 深入检查布局、排版、颜色、图像、间距、组件、响应式和动效。
4. 输出可视化的 Visual Taste Board，区分观察、测量、解释和未知项。
5. 用户确认或修正后，才把可复用规律写入 taste library。

### 复用模式

1. 了解目标项目、用户、功能、内容和限制，确认 Application Brief。
2. 从历史记录中选择 2-4 个最相关案例，说明采用什么、排除什么、如何解决冲突。
3. 对关键组件给出可比较的方向，等待用户选择。
4. 实现并验证桌面端、移动端、交互与可访问性。

## 安装

### 让 Codex 安装

在 Codex 中发送：

```text
请从 https://github.com/lllkn/web-taste 安装 web-taste skill。
```

### 手动安装

```bash
git clone --depth 1 https://github.com/lllkn/web-taste.git web-taste-repo
mkdir -p ~/.codex/skills
cp -R web-taste-repo/web-taste ~/.codex/skills/
```

重新启动 Codex 或开启一个新任务，让 skill 被重新发现。

## 使用

学习一个网页并建立 taste memory：

```text
使用 $web-taste 学习 https://example.com 的排版、组件、响应式和动效。先给我 Learn Brief，确认后再深入分析，并把我认可的规律保存下来。
```

将已经学习的 taste 用到项目中：

```text
使用 $web-taste 重新设计这个前端。先结合我的 taste library 给出 Application Brief 和 Memory Fusion Note，关键组件让我选择方向后再实现。
```

学习并立即复用：

```text
使用 $web-taste 学习这个参考站，然后把确认后的视觉规律应用到当前项目。不要复制品牌、素材或源码。
```

## 仓库结构

```text
web-taste/
├── SKILL.md                         # AI 工作流与行为约束
├── agents/openai.yaml               # Codex 中显示的 skill 信息
├── scripts/
│   ├── render_visual.py             # 生成自包含的 Taste Board / 组件方案页
│   ├── taste_library.py             # 新建、索引和校验 taste 记录
│   └── test_workflow.py             # 脚本回归测试
└── references/
    ├── workflow-artifacts.md        # Brief、报告和决策记录格式
    ├── visual-analysis-rubric.md    # 网页视觉分析维度
    ├── site-record-template.md      # 单个参考站记录规范
    ├── taste-profile.md             # 用户确认后的长期偏好摘要
    ├── site-index.md                # 已学习网页的索引
    ├── sites/                       # 本地网页学习记录，不随仓库上传
    ├── reports/                     # 本地视觉报告，不随仓库上传
    └── applications/                # 本地应用决策，不随仓库上传
```

`render_visual.py` 和 `taste_library.py` 只依赖 Python 3 标准库。网页检查本身需要 AI 环境具备可操作的真实浏览器。

## 隐私与版权边界

这个公开仓库只包含 skill 工作流、通用模板和脚本，不包含作者自己的 taste profile、已学习网站记录、截图报告或项目应用记录。

使用过程中生成的 `sites/`、`reports/` 和 `applications/` 内容默认被 Git 忽略。请不要把第三方网页截图、品牌素材、专有字体、源代码或包含个人信息的记录公开提交。Web Taste 学习的是设计关系与约束，不是网站身份。

## License

[MIT](LICENSE)
