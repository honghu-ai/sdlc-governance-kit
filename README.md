# SDLC Governance Kit

一套面向 AI 原生软件开发生命周期的治理工具集。项目通过 Skills、模板、检查脚本和确定性关卡，让规划、设计、构建、测试、部署与维护共享同一条可追溯的产物链。

本项目受 Anthropic 发布的 [The AI-Native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook) 启发，并在文章原则之上提供一套具体的目录和产物约定。它不是 Anthropic 官方项目。

## 当前状态

仓库已提供代码库治理脚手架，以及从原始意图到规范编写和领域政策应用的首批六个 Skills：`sdlc-scaffold`、`capture-intent`、`compose-spec`、`brand-guidelines`、`compliance-policy` 和 `security-policy`。每个 Skill 都包含独立入口、界面元数据和评估用例；脚手架与产物生成 Skills 另带所需模板。

## 治理目标

- 让每个阶段提交可供下一阶段读取的正式产物。
- 让 Git、CI、PR、部署与事故系统各自保存唯一事实来源。
- 让需要判断的决策保留明确的人工负责人和批准记录。
- 让建议性知识进入 Skills，让强制约束进入 Hooks、权限、分支保护和 CI。

## 产物循环

```text
intent.md
    ↓
spec.md
    ↓
plan.md
    ↓
代码差异与测试
    ↓
PR、评审发现与人工批准
    ↓
部署或事故记录
    ↓
新的 intent.md
```

## 项目边界

`sdlc-scaffold` 只初始化和检查代码库级治理结构。它不会创建单项变更目录，也不会创建 `intent.md`、`spec.md`、`plan.md` 或其他阶段产物。

阶段产物在流程真正发生时由对应能力创建。`capture-intent` 生成 `intent.md`，`compose-spec` 生成 `spec.md`，Claude Code 计划模式生成 `plan.md`。代码、测试、PR 和事故记录继续由各自的权威系统保存。

## Skills

| Skill | 状态 | 类型 | 职责 |
| --- | --- | --- | --- |
| `capture-intent` | 已实现 | 产物生成 | 将想法、工单或事故发现整理成 `intent.md` 草稿 |
| `compose-spec` | 已实现 | 产物生成与校验 | 根据已接受的 `intent.md` 生成或检查 `spec.md` 草稿 |
| `brand-guidelines` | 已实现 | 领域政策 | 提供或审核品牌约束、验收条件、违规与冲突 |
| `compliance-policy` | 已实现 | 领域政策 | 提供或审核合规义务、证据、冲突与例外 |
| `security-policy` | 已实现 | 领域政策 | 提供或审核通用安全约束、威胁关注点和验收条件 |
| `sdlc-scaffold` | 已实现 | 治理基础设施 | 初始化并审计代码库级治理结构 |
| `ux-standards` | 计划中 | 领域标准 | 提供用户流程、界面状态和可访问性要求 |
| `api-design-conventions` | 计划中 | 领域标准 | 约束 API 契约并检查实现兼容性 |
| `secure-api-review` | 计划中 | 专项验证 | 检查外部 API 的认证、校验、审计和 PII 风险 |

## 仓库结构

```text
sdlc-governance-kit/
├── .claude-plugin/
│   └── plugin.json
├── docs/
│   ├── 00_Index.md
│   ├── 01_Architecture.md
│   ├── 02_SkillCatalog.md
│   ├── AiNativeSdlc-skills-hub.md
│   ├── AiNativeSdlc-笔记.md
│   ├── AiNativeSdlc-规范目录设计.md
│   └── AiNativeSdlc-译文.md
├── skills/
│   ├── sdlc-scaffold/
│   ├── capture-intent/
│   ├── compose-spec/
│   ├── brand-guidelines/
│   ├── compliance-policy/
│   └── security-policy/
├── templates/
├── scripts/
└── evals/
```

Claude Code 插件要求 `plugin.json` 位于 `.claude-plugin/`，Skills 位于插件根目录下的 `skills/`。Skill 专用模板、脚本和评估用例与对应 Skill 放在一起；仓库级共享资源继续放在顶层目录。

## 后续开发

1. 用现有六个 Skills 验证代码库初始化、`intent.md` 到 `spec.md` 及品牌、合规、安全领域输出的产物交接。
2. 继续实现 UX、API 设计和 API 专项安全能力。
3. 在 Skill 和治理配置变化时持续运行对应评估用例。
4. 根据强制性要求补充 Hooks、CI 检查和人工批准关卡。

详细设计从 [文档索引](docs/00_Index.md) 进入。
