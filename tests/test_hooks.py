"""hooks/audit_on_edit.py 的行为测试。"""

import json
import subprocess
import sys

from conftest import REPO_ROOT

HOOK = REPO_ROOT / "hooks" / "audit_on_edit.py"
SCAFFOLD = REPO_ROOT / "skills" / "sdlc-scaffold" / "scripts" / "sdlc_scaffold.py"


def run_hook(cwd, file_path, strict=False):
    env = {"SDLC_AUDIT_STRICT": "1"} if strict else {}
    payload = json.dumps({"cwd": str(cwd), "tool_input": {"file_path": str(file_path)}})
    return subprocess.run(
        [sys.executable, str(HOOK)], input=payload, capture_output=True, text=True, env=env, check=False
    )


def test_skips_repo_without_scaffold(tmp_path):
    result = run_hook(tmp_path, tmp_path / "CLAUDE.md", strict=True)
    assert result.returncode == 0 and result.stdout == ""


def test_skips_non_governance_file(tmp_path):
    subprocess.run([sys.executable, str(SCAFFOLD), "init", "--target", str(tmp_path)], capture_output=True)
    result = run_hook(tmp_path, tmp_path / "src" / "main.py", strict=True)
    assert result.returncode == 0 and result.stdout == ""


def test_strict_mode_blocks_on_error(tmp_path):
    subprocess.run([sys.executable, str(SCAFFOLD), "init", "--target", str(tmp_path)], capture_output=True)
    (tmp_path / "docs/sdlc/changes/c1").mkdir()
    result = run_hook(tmp_path, tmp_path / "docs/sdlc/00_Index.md", strict=True)
    assert result.returncode == 2
    assert "单项变更目录缺少 00_Index.md" in result.stderr


def test_default_mode_only_reports(tmp_path):
    subprocess.run([sys.executable, str(SCAFFOLD), "init", "--target", str(tmp_path)], capture_output=True)
    (tmp_path / "docs/sdlc/changes/c1").mkdir()
    result = run_hook(tmp_path, tmp_path / "REVIEW.md")
    assert result.returncode == 0
    assert "ERROR" in result.stdout
