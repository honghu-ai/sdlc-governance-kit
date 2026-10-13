"""run_evals.py 的离线测试：用 shell 命令模拟 runner 与 grader。"""

import sys

import pytest
from conftest import load_module


@pytest.fixture(scope="module")
def evals():
    return load_module("run_evals", "scripts/run_evals.py")


def test_list_loads_all_skills(evals, capsys):
    assert evals.main(["list"]) == 0
    assert "共" in capsys.readouterr().out


def test_run_and_grade_with_fake_commands(evals, tmp_path, capsys):
    out = tmp_path / "results"
    assert evals.main(["run", "--skill", "capture-intent", "--out", str(out), "--runner", "cat"]) == 0
    assert any(out.glob("capture-intent/*.md"))
    grader = (
        f'{sys.executable} -c "import json,sys;d=json.load(sys.stdin);'
        "print(json.dumps({'results':[{'expectation':e,'passed':True,'evidence':''} for e in d['expectations']]}))\""
    )
    code = evals.main(
        ["grade", "--skill", "capture-intent", "--out", str(out), "--grader", grader, "--min-pass-rate", "1"]
    )
    assert code == 0
    assert "通过率" in capsys.readouterr().out
    assert (out / "report.json").is_file()


def test_grade_without_grader_writes_checklist(evals, tmp_path):
    out = tmp_path / "results"
    evals.main(["run", "--skill", "security-policy", "--out", str(out), "--runner", "cat"])
    assert evals.main(["grade", "--skill", "security-policy", "--out", str(out)]) == 0
    assert "- [ ]" in (out / "checklist.md").read_text(encoding="utf-8")


def test_failing_runner_reports_failure(evals, tmp_path):
    assert evals.main(["run", "--skill", "security-policy", "--out", str(tmp_path), "--runner", "false"]) == 1
