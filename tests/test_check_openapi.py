"""secure-api-review/scripts/check_openapi.py 测试。"""

from pathlib import Path

import pytest
from conftest import load_module

SAMPLE = Path(__file__).parent / "fixtures" / "openapi" / "sample.yaml"


@pytest.fixture(scope="module")
def checker():
    return load_module("check_openapi", "skills/secure-api-review/scripts/check_openapi.py")


def test_flags_anonymous_endpoint_and_pii(checker):
    findings = checker.check(checker.load_document(SAMPLE))
    assert ("严重", "GET /users", "未声明认证要求（security 为空），匿名访问需有明确理由") in findings
    assert any(sev == "重要" and "数组未声明 maxItems" in msg for sev, _, msg in findings)
    assert any("PII" in msg and loc.endswith(".email") for _, loc, msg in findings)


def test_secured_endpoint_with_401_403_has_no_auth_findings(checker):
    findings = checker.check(checker.load_document(SAMPLE))
    auth = [f for f in findings if f[1] == "GET /users/{id}" and ("401" in f[2] or "403" in f[2] or "认证" in f[2])]
    assert auth == []


def test_exit_code_reflects_severity(checker, tmp_path):
    assert checker.main([str(SAMPLE)]) == 1
    clean = tmp_path / "clean.json"
    clean.write_text('{"openapi": "3.0.3", "paths": {}}', encoding="utf-8")
    assert checker.main([str(clean)]) == 0
    assert checker.main([str(tmp_path / "missing.yaml")]) == 2
