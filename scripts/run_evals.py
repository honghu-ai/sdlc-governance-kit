#!/usr/bin/env python3
"""Skill 评估运行器。

子命令：
- list      列出全部（或指定 Skill 的）评估用例，并校验结构。
- run       把每个用例的 prompt 通过 stdin 交给 --runner 命令，保存输出。
- grade     把输出与 expectations 交给 --grader 命令打分（grader 输出 JSON：
            {"results": [{"expectation": str, "passed": bool, "evidence": str}]}）；
            不提供 grader 时生成供人工勾选的 Markdown 清单。

runner 与 grader 都是任意 shell 命令，例如 `claude -p`，便于在不同环境接入模型。
环境变量 SKILL_NAME、EVAL_ID 会传给子进程。
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "evals" / "results"


def load_cases(skills_dir: Path, only: list[str] | None) -> list[tuple[str, dict]]:
    cases: list[tuple[str, dict]] = []
    for path in sorted(skills_dir.glob("*/evals/evals.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        name = data["skill_name"]
        if only and name not in only:
            continue
        for case in data["evals"]:
            missing = [k for k in ("id", "prompt", "expectations") if not case.get(k)]
            if missing:
                raise ValueError(f"{path}: 用例 {case.get('id')} 缺少 {missing}")
            cases.append((name, case))
    return cases


def build_prompt(skill: str, case: dict) -> str:
    files = "\n".join(f"- {f}" for f in case.get("files", []))
    extra = f"\n\n相关文件：\n{files}" if files else ""
    return f"使用 ${skill} 处理以下请求。\n\n{case['prompt']}{extra}\n"


def run_command(command: str, stdin: str, skill: str, case_id: int, timeout: int) -> str:
    env = {**os.environ, "SKILL_NAME": skill, "EVAL_ID": str(case_id)}
    result = subprocess.run(
        shlex.split(command), input=stdin, capture_output=True, text=True, env=env, timeout=timeout, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"命令失败（{result.returncode}）：{result.stderr.strip()[:500]}")
    return result.stdout


def output_path(out_dir: Path, skill: str, case_id: int) -> Path:
    return out_dir / skill / f"{case_id}.md"


def cmd_list(cases: list[tuple[str, dict]], _args: argparse.Namespace) -> int:
    for skill, case in cases:
        print(f"{skill}#{case['id']}：{len(case['expectations'])} 条期望")
    skills = {s for s, _ in cases}
    print(f"共 {len(skills)} 个 Skills、{len(cases)} 个用例。")
    return 0


def cmd_run(cases: list[tuple[str, dict]], args: argparse.Namespace) -> int:
    failures = 0
    for skill, case in cases:
        target = output_path(args.out, skill, case["id"])
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            output = run_command(args.runner, build_prompt(skill, case), skill, case["id"], args.timeout)
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            failures += 1
            print(f"FAIL {skill}#{case['id']}：{exc}")
            continue
        target.write_text(output, encoding="utf-8")
        print(f"OK   {skill}#{case['id']} → {target}")
    return 1 if failures else 0


def grade_payload(skill: str, case: dict, output: str) -> str:
    return json.dumps(
        {
            "skill": skill,
            "id": case["id"],
            "prompt": case["prompt"],
            "expectations": case["expectations"],
            "output": output,
        },
        ensure_ascii=False,
    )


def cmd_grade(cases: list[tuple[str, dict]], args: argparse.Namespace) -> int:
    report: list[dict] = []
    checklist: list[str] = ["# Skill 评估人工核对清单", ""]
    for skill, case in cases:
        source = output_path(args.out, skill, case["id"])
        if not source.is_file():
            report.append({"skill": skill, "id": case["id"], "status": "missing-output"})
            continue
        output = source.read_text(encoding="utf-8")
        if args.grader:
            raw = run_command(args.grader, grade_payload(skill, case, output), skill, case["id"], args.timeout)
            results = json.loads(raw)["results"]
            passed = sum(bool(r.get("passed")) for r in results)
            report.append(
                {"skill": skill, "id": case["id"], "passed": passed, "total": len(results), "results": results}
            )
        else:
            checklist += [f"## {skill}#{case['id']}", "", f"输出：`{source}`", ""]
            checklist += [f"- [ ] {e}" for e in case["expectations"]] + [""]

    args.out.mkdir(parents=True, exist_ok=True)
    if not args.grader:
        path = args.out / "checklist.md"
        path.write_text("\n".join(checklist), encoding="utf-8")
        print(f"未提供 --grader，已生成人工核对清单：{path}")
    (args.out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    graded = [r for r in report if "total" in r]
    total = sum(r["total"] for r in graded)
    passed = sum(r["passed"] for r in graded)
    missing = [r for r in report if r.get("status") == "missing-output"]
    if graded:
        print(f"期望通过率：{passed}/{total}")
    if missing:
        print(f"缺少输出的用例：{len(missing)} 个（先运行 run 子命令）")
    if args.min_pass_rate is not None and total:
        return 0 if passed / total >= args.min_pass_rate else 1
    return 1 if missing else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("list", "run", "grade"))
    parser.add_argument("--skill", action="append", help="只评估指定 Skill，可重复")
    parser.add_argument("--skills-dir", type=Path, default=REPO_ROOT / "skills")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="输出目录，默认 evals/results")
    parser.add_argument("--runner", help="run 使用的命令，prompt 通过 stdin 传入")
    parser.add_argument("--grader", help="grade 使用的命令，JSON 负载通过 stdin 传入")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--min-pass-rate", type=float, help="grade 的最低通过率（0-1）")
    args = parser.parse_args(argv)

    cases = load_cases(args.skills_dir, args.skill)
    if not cases:
        print("没有找到评估用例。", file=sys.stderr)
        return 2
    if args.command == "run" and not args.runner:
        parser.error("run 需要 --runner")
    return {"list": cmd_list, "run": cmd_run, "grade": cmd_grade}[args.command](cases, args)


if __name__ == "__main__":
    raise SystemExit(main())
