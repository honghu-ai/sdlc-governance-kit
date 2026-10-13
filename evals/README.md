# Evals

各 Skill 的评估用例位于 `skills/<name>/evals/evals.json`。本目录保存运行结果（`results/`，已忽略提交）。

```bash
# 列出并校验全部用例（离线，CI 中运行）
python scripts/run_evals.py list

# 用任意命令运行用例，prompt 通过 stdin 传入
python scripts/run_evals.py run --runner "claude -p" --skill compose-spec

# 打分：grader 读取 JSON 负载并输出 {"results": [...]}；不提供 grader 时生成人工核对清单
python scripts/run_evals.py grade --grader "python my_grader.py" --min-pass-rate 0.8
```
