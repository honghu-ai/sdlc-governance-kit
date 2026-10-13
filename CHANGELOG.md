# 更新日志

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本遵循语义化版本。

## [未发布] - 0.3.0

### 新增

- `ux-standards`、`api-design-conventions`、`secure-api-review` 三个 Skills；`secure-api-review` 附 OpenAPI 安全预检脚本。
- `scripts/check_skills.py`：校验 Skill frontmatter、界面元数据、评估用例和插件清单。
- `scripts/run_evals.py`：列出、运行并打分评估用例，runner/grader 可接入任意命令。
- GitHub Actions CI：JSON/YAML 校验、Skill 结构检查、ruff、pytest。
- Claude Code Hook：编辑治理文件后自动运行 `sdlc-scaffold audit`。
- PR 模板、`examples/intent-to-spec` 示例、MIT 许可证。

### 变更

- `sdlc-scaffold` 的内容审计规则移至 `assets/audit_rules.json`，支持 `--rules` 覆盖。
- 研究笔记与译文移至 `docs/notes/`。

### 修复

- `plugin.json` 的 repository 地址改为 `honghu-ai/sdlc-governance-kit`。

## [0.2.0] - 2026-08-28

### 新增

- `sdlc-scaffold`、`capture-intent`、`compose-spec`、`brand-guidelines`、`compliance-policy`、`security-policy` 六个 Skills。
