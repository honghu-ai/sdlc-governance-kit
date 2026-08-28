# SDLC Governance Kit

一套面向 AI 原生软件开发生命周期的治理工具集。项目通过 Skills、模板、检查脚本和确定性关卡，让规划、设计、构建、测试、部署与维护共享同一条可追溯的产物链。

本项目受 Anthropic 发布的 [The AI-Native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook) 启发，并在文章原则之上提供一套具体的目录和产物约定。它不是 Anthropic 官方项目。

## 当前状态

仓库已经完成初始骨架，Skills 暂未实现。后续将逐个定义 Skill 的触发条件、输入、输出、职责边界、脚本和评估用例。

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

## 计划中的 Skills

| Skill | 类型 | 职责 |
| --- | --- | --- |
| `sdlc-scaffold` | 治理基础设施 | 初始化并审计代码库级治理结构 |
| `capture-intent` | 产物生成 | 将想法、工单或事故发现整理成 `intent.md` |
| `compose-spec` | 产物生成与校验 | 根据获批的 `intent.md` 生成或检查 `spec.md` |
| `brand-guidelines` | 领域政策 | 提供品牌约束和验收条件 |
| `compliance-policy` | 领域政策 | 提供合规义务、证据要求和人工裁决点 |
| `ux-standards` | 领域标准 | 提供用户流程、界面状态和可访问性要求 |
| `security-policy` | 领域政策 | 提供通用安全约束和安全验收条件 |
| `api-design-conventions` | 领域标准 | 约束 API 契约并检查实现兼容性 |
| `secure-api-review` | 专项验证 | 检查外部 API 的认证、校验、审计和 PII 风险 |

## 仓库结构

```text
sdlc-governance-kit/
├── .claude-plugin/
│   └── plugin.json
├── docs/
│   ├── 00_Index.md
│   ├── 01_Architecture.md
│   └── 02_SkillCatalog.md
├── skills/
├── templates/
├── scripts/
└── evals/
```

Claude Code 插件要求 `plugin.json` 位于 `.claude-plugin/`，Skills 位于插件根目录下的 `skills/`。其余目录将在相关能力开始开发时补充实际内容。

## 开发顺序

1. 实现 `sdlc-scaffold`，固定代码库级目录、模板和结构检查。
2. 实现 `capture-intent` 与 `compose-spec`，打通前两个阶段的产物交接。
3. 逐项实现品牌、合规、UX、安全和 API 领域能力。
4. 为每个 Skill 增加评估用例，并在治理配置变化时持续运行。
5. 根据强制性要求补充 Hooks、CI 检查和人工批准关卡。

详细设计从 [文档索引](docs/00_Index.md) 进入。
