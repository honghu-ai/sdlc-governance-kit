# 项目文档索引

这里汇总 SDLC Governance Kit 的设计文档。Skills 尚未开始实现，当前文档用于固定项目范围和开发边界。

| 文档 | 内容 |
| --- | --- |
| [01_Architecture.md](01_Architecture.md) | 项目分层、产物循环和治理边界 |
| [02_SkillCatalog.md](02_SkillCatalog.md) | 计划中的 Skills、触发阶段和预期输出 |

## 当前决定

- 项目名称为 `sdlc-governance-kit`。
- 项目按照 Claude Code 插件结构组织。
- `skills/` 当前不包含任何 Skill 实现。
- 脚手架只处理代码库级结构，不创建单项变更或阶段产物。
- 每个 Skill 单独设计、评审和开发。
