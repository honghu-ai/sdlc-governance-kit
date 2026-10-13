"""sdlc_scaffold.py 的 init / audit 行为测试。"""

import json
from pathlib import Path


def levels(findings):
    return {(level, path.as_posix(), message) for level, path, message in findings}


def test_init_creates_core_structure(scaffold, tmp_path):
    assert scaffold.main(["init", "--target", str(tmp_path)]) == 0
    for relative in ("CLAUDE.md", "REVIEW.md", "docs/sdlc/00_Index.md"):
        assert (tmp_path / relative).is_file()
    for relative in ("docs/sdlc/changes/.gitkeep", "docs/sdlc/incidents/.gitkeep"):
        assert (tmp_path / relative).is_file()


def test_init_is_idempotent_and_keeps_team_content(scaffold, tmp_path):
    scaffold.main(["init", "--target", str(tmp_path)])
    claude = tmp_path / "CLAUDE.md"
    claude.write_text("# 团队自定义\n", encoding="utf-8")
    scaffold.main(["init", "--target", str(tmp_path)])
    assert claude.read_text(encoding="utf-8") == "# 团队自定义\n"


def test_audit_empty_repo_reports_errors(scaffold, tmp_path, capsys):
    assert scaffold.main(["audit", "--target", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "缺少核心目录" in out
    assert "缺少核心文件" in out


def test_audit_missing_target_returns_2(scaffold, tmp_path):
    assert scaffold.main(["audit", "--target", str(tmp_path / "nope")]) == 2


def test_broken_local_link_is_error(scaffold, tmp_path):
    scaffold.main(["init", "--target", str(tmp_path)])
    index = tmp_path / "docs/sdlc/00_Index.md"
    index.write_text(index.read_text(encoding="utf-8") + "\n[坏链接](changes/missing.md)\n", encoding="utf-8")
    findings = scaffold.audit(tmp_path)
    assert any(level == "ERROR" and "本地引用不存在" in msg for level, _, msg in findings)


def test_external_and_anchor_links_ignored(scaffold, tmp_path):
    md = tmp_path / "x.md"
    assert scaffold.local_link_target(md, "https://example.com/a.md") is None
    assert scaffold.local_link_target(md, "#anchor") is None
    assert scaffold.local_link_target(md, "<a%20b.md>") == tmp_path / "a b.md"


def test_change_dir_requires_index(scaffold, tmp_path):
    scaffold.main(["init", "--target", str(tmp_path)])
    (tmp_path / "docs/sdlc/changes/2026-001").mkdir()
    findings = scaffold.audit(tmp_path)
    assert ("ERROR", "docs/sdlc/changes/2026-001", "单项变更目录缺少 00_Index.md") in levels(findings)


def test_incident_dir_requires_incident_md(scaffold, tmp_path):
    scaffold.main(["init", "--target", str(tmp_path)])
    (tmp_path / "docs/sdlc/incidents/inc-1").mkdir()
    findings = scaffold.audit(tmp_path)
    assert ("ERROR", "docs/sdlc/incidents/inc-1", "事故目录缺少 incident.md") in levels(findings)


def test_artifact_outside_change_dir_is_error(scaffold, tmp_path):
    scaffold.main(["init", "--target", str(tmp_path)])
    (tmp_path / "docs/sdlc/spec.md").write_text("# spec\n", encoding="utf-8")
    good = tmp_path / "docs/sdlc/changes/c1"
    good.mkdir()
    (good / "00_Index.md").write_text("# c1\n", encoding="utf-8")
    (good / "intent.md").write_text("# intent\n", encoding="utf-8")
    errors = [(p.as_posix(), m) for lvl, p, m in scaffold.audit(tmp_path) if lvl == "ERROR"]
    assert ("docs/sdlc/spec.md", "阶段产物必须位于 docs/sdlc/changes/<change-id>/") in errors
    assert all(not p.endswith("c1/intent.md") for p, _ in errors)


def test_default_rules_file_is_valid(scaffold):
    rules = scaffold.load_rules()
    assert set(rules["required_content"]) == {"CLAUDE.md", "REVIEW.md", "docs/sdlc/00_Index.md"}
    for file_rules in rules["required_content"].values():
        for rule in file_rules:
            assert rule["pattern"] and rule["message"]


def test_custom_rules_file_overrides_defaults(scaffold, tmp_path):
    scaffold.main(["init", "--target", str(tmp_path)])
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(
        json.dumps(
            {
                "required_content": {"CLAUDE.md": [{"pattern": "Commands", "message": "missing Commands"}]},
                "placeholders": [],
            }
        ),
        encoding="utf-8",
    )
    findings = scaffold.audit(tmp_path, scaffold.load_rules(rules_path))
    messages = [m for _, _, m in findings]
    assert "missing Commands" in messages
    assert "缺少命令章节" not in messages


def test_complete_repo_passes(scaffold, tmp_path):
    scaffold.main(["init", "--target", str(tmp_path)])
    fixture = Path(__file__).parent / "fixtures" / "complete"
    for src in fixture.rglob("*.md"):
        dst = tmp_path / src.relative_to(fixture)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    assert scaffold.audit(tmp_path) == []
