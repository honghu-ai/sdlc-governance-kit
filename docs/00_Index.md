# 项目文档索引

这里汇总 SDLC Governance Kit 的设计文档。项目已实现代码库治理脚手架、意图捕获、规范编写及品牌、合规、通用安全三个领域政策 Skills；其余能力按目录中的状态继续演进。

| 文档 | 内容 |
| --- | --- |
| [01_Architecture.md](01_Architecture.md) | 项目分层、产物循环和治理边界 |
| [02_SkillCatalog.md](02_SkillCatalog.md) | 已实现与计划中的 Skills、触发阶段和预期输出 |
| [AiNativeSdlc-skills-hub.md](AiNativeSdlc-skills-hub.md) | 六步流程中的 Skill 职责、产物关系和能力边界 |
| [AiNativeSdlc-笔记.md](AiNativeSdlc-笔记.md) | AI 原生 SDLC 的核心判断、优先实践、采用顺序和待验证问题 |
| [AiNativeSdlc-规范目录设计.md](AiNativeSdlc-规范目录设计.md) | 按变更聚合的产物目录、索引、命名和元数据约定 |
| [AiNativeSdlc-译文.md](AiNativeSdlc-译文.md) | 《The AI-Native SDLC playbook》中文译文 |

## 当前决定

- 项目名称为 `sdlc-governance-kit`。
- 项目按照 Claude Code 插件结构组织。
- `skills/` 当前包含六个可加载的 Skill 实现。
- 脚手架只处理代码库级结构，不创建单项变更或阶段产物。
- `capture-intent` 生成 `intent.md` 草稿，`compose-spec` 生成或校验 `spec.md` 草稿。
- `brand-guidelines`、`compliance-policy` 和 `security-policy` 只提供或审核各自领域内容，不拥有完整 `spec.md`。
- 产品、政策和技术负责人保留人工审核与批准职责，Skill 输出不等于批准。
- 每个 Skill 单独设计、评审、评估和演进。
