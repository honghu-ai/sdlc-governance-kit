# 示例：从 intent.md 到 spec.md

这个目录是一个已经初始化治理骨架的最小示例仓库，演示一次变更从原始需求到规范草稿的产物链。所有内容均为虚构示例。

## 步骤

1. **初始化骨架**：`python3 skills/sdlc-scaffold/scripts/sdlc_scaffold.py init --target <repo>`，生成 `CLAUDE.md`、`REVIEW.md` 和 `docs/sdlc/`。
2. **捕获意图**：把工单交给 `$capture-intent`，得到 [intent.md](docs/sdlc/changes/2026-10-export-csv/intent.md) 草稿；产品负责人修订并接受。
3. **编写规范**：`$compose-spec` 读取已接受的 intent，按需调用 `$security-policy`、`$ux-standards` 等领域 Skill，生成 [spec.md](docs/sdlc/changes/2026-10-export-csv/spec.md)，状态保持“待评审”。
4. **审计结构**：

   ```bash
   python3 skills/sdlc-scaffold/scripts/sdlc_scaffold.py audit --target examples/intent-to-spec
   ```

   预期输出 `OK：治理骨架结构与本地引用检查通过。`
5. **下一步**：人工批准 spec 后，用 Claude Code 计划模式生成 `plan.md`，再进入实现与 PR（使用 [PR 模板](../../templates/pull_request_template.md)）。

注意示例中 intent 的未决问题（导出上限）在 spec 中被保留为未决问题，而不是被替人决定。
