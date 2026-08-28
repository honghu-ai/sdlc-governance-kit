# Skills

此目录用于存放 Claude Code Skills。每个 Skill 使用独立子目录，并以 `SKILL.md` 作为入口。

当前包含：

- `sdlc-scaffold`：初始化或审计代码库级治理骨架，保留已有团队内容。
- `capture-intent`：把原始材料整理为 `intent.md` 草稿。
- `compose-spec`：根据已接受的意图生成或校验 `spec.md` 草稿。
- `brand-guidelines`：提供或审核品牌约束、验收条件、违规与冲突。
- `compliance-policy`：提供或审核合规义务、证据、冲突与例外。
- `security-policy`：提供或审核通用安全约束、威胁关注点和验收条件。

Skill 专用的 `agents/`、`assets/`、`scripts/` 和 `evals/` 与入口放在同一子目录，避免与仓库级共享资源混淆。完整职责与状态见 [Skill 目录](../docs/02_SkillCatalog.md)。
