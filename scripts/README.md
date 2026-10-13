# Scripts

仓库级脚本：

- `check_skills.py`：校验每个 Skill 的 `SKILL.md` frontmatter、`agents/openai.yaml`、`evals/evals.json` 及插件清单。
- `run_evals.py`：列出、运行并打分 Skill 评估用例，详见 [evals/README.md](../evals/README.md)。

Skill 专用脚本放在对应 `skills/<name>/scripts/` 下。
