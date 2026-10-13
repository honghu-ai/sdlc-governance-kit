#!/usr/bin/env python3
"""Claude Code PostToolUse Hook：编辑治理文件后运行 sdlc-scaffold 只读审计。

- 只在被编辑文件属于 CLAUDE.md、REVIEW.md 或 docs/sdlc/ 时触发。
- 目标代码库尚未初始化治理骨架（没有 docs/sdlc/）时跳过。
- 默认只提示；设置 SDLC_AUDIT_STRICT=1 时，审计出现 ERROR 以退出码 2 把结果反馈给智能体。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = PLUGIN_ROOT / "skills" / "sdlc-scaffold" / "scripts" / "sdlc_scaffold.py"
WATCHED_NAMES = {"CLAUDE.md", "REVIEW.md"}


def is_governance_file(root: Path, file_path: Path) -> bool:
    try:
        relative = file_path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return relative.as_posix() in WATCHED_NAMES or relative.parts[:2] == ("docs", "sdlc")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    root = Path(payload.get("cwd") or os.getcwd())
    file_path = (payload.get("tool_input") or {}).get("file_path")
    if not file_path or not (root / "docs" / "sdlc").is_dir():
        return 0
    if not is_governance_file(root, Path(file_path)):
        return 0

    result = subprocess.run(
        [sys.executable, str(SCAFFOLD), "audit", "--target", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 1 and os.environ.get("SDLC_AUDIT_STRICT") == "1":
        print(result.stdout, file=sys.stderr)
        return 2
    if result.stdout.strip():
        print(result.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
