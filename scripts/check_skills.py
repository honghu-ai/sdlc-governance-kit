#!/usr/bin/env python3
"""校验 skills/*/ 的结构：SKILL.md frontmatter、agents/openai.yaml、evals/evals.json 与模板引用。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\]\((?!https?://|#)([^)\s]+)\)")
MAX_DESCRIPTION = 1024


def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    data = yaml.safe_load(text[4:end])
    return data if isinstance(data, dict) else None


def check_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    rel = skill_dir.relative_to(REPO_ROOT).as_posix()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{rel}：缺少 SKILL.md"]

    text = skill_md.read_text(encoding="utf-8")
    meta = parse_frontmatter(text)
    if meta is None:
        errors.append(f"{rel}/SKILL.md：缺少或无法解析 YAML frontmatter")
    else:
        name = meta.get("name")
        description = meta.get("description")
        if name != skill_dir.name:
            errors.append(f"{rel}/SKILL.md：name `{name}` 与目录名 `{skill_dir.name}` 不一致")
        if not isinstance(name, str) or not NAME_PATTERN.match(name or ""):
            errors.append(f"{rel}/SKILL.md：name 必须是小写短横线格式")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{rel}/SKILL.md：缺少 description")
        elif len(description) > MAX_DESCRIPTION:
            errors.append(f"{rel}/SKILL.md：description 超过 {MAX_DESCRIPTION} 字符")

    for target in LINK_PATTERN.findall(text):
        if not (skill_dir / target.split("#", 1)[0]).exists():
            errors.append(f"{rel}/SKILL.md：本地引用不存在：{target}")

    agent_yaml = skill_dir / "agents" / "openai.yaml"
    if not agent_yaml.is_file():
        errors.append(f"{rel}：缺少 agents/openai.yaml")
    else:
        data = yaml.safe_load(agent_yaml.read_text(encoding="utf-8")) or {}
        interface = data.get("interface", {})
        for key in ("display_name", "short_description", "default_prompt"):
            if not interface.get(key):
                errors.append(f"{rel}/agents/openai.yaml：interface.{key} 为空")
        prompt = interface.get("default_prompt", "")
        if prompt and f"${skill_dir.name}" not in prompt:
            errors.append(f"{rel}/agents/openai.yaml：default_prompt 未引用 ${skill_dir.name}")

    evals = skill_dir / "evals" / "evals.json"
    if not evals.is_file():
        errors.append(f"{rel}：缺少 evals/evals.json")
    else:
        try:
            data = json.loads(evals.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}/evals/evals.json：JSON 无效：{exc}")
        else:
            if data.get("skill_name") != skill_dir.name:
                errors.append(f"{rel}/evals/evals.json：skill_name 与目录名不一致")
            cases = data.get("evals") or []
            if not cases:
                errors.append(f"{rel}/evals/evals.json：没有评估用例")
            ids = [case.get("id") for case in cases]
            if len(ids) != len(set(ids)):
                errors.append(f"{rel}/evals/evals.json：用例 id 重复")
            for case in cases:
                for key in ("id", "prompt", "expected_output", "expectations"):
                    if not case.get(key):
                        errors.append(f"{rel}/evals/evals.json：用例 {case.get('id')} 缺少 {key}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, default=REPO_ROOT / "skills")
    args = parser.parse_args(argv)
    skill_dirs = sorted(p for p in args.skills_dir.iterdir() if p.is_dir())
    errors = [e for d in skill_dirs for e in check_skill(d)]

    plugin = json.loads((REPO_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    for key in ("name", "version", "description", "repository"):
        if not plugin.get(key):
            errors.append(f".claude-plugin/plugin.json：缺少 {key}")

    for error in errors:
        print(f"ERROR {error}")
    print(f"检查 {len(skill_dirs)} 个 Skills：{len(errors)} 个错误。")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
