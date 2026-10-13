# Skills

此目录用于存放 Claude Code Skills。每个 Skill 使用独立子目录，并以 `SKILL.md` 作为入口。

当前包含：

- `sdlc-scaffold`：初始化或审计代码库级治理骨架，保留已有团队内容。
- `capture-intent`：把原始材料整理为 `intent.md` 草稿。
- `compose-spec`：根据已接受的意图生成或校验 `spec.md` 草稿。
- `brand-guidelines`：提供或审核品牌约束、验收条件、违规与冲突。
- `compliance-policy`：提供或审核合规义务、证据、冲突与例外。
- `security-policy`：提供或审核通用安全约束、威胁关注点和验收条件。
- `ux-standards`：提供或审核用户流程、界面状态和可访问性验收条件。
- `api-design-conventions`：约束 API 契约并检查向后兼容性。
- `secure-api-review`：对外部 API 做认证、授权、校验、审计和 PII 专项检查，附 OpenAPI 预检脚本。

Skill 专用的 `agents/`、`assets/`、`scripts/` 和 `evals/` 与入口放在同一子目录，避免与仓库级共享资源混淆。完整职责与状态见 [Skill 目录](../docs/02_SkillCatalog.md)。
