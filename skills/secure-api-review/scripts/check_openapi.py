#!/usr/bin/env python3
"""对 OpenAPI 3 契约做确定性安全预检。结果只作为人工复核线索，不代表接口安全。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

METHODS = ("get", "put", "post", "delete", "patch", "head", "options")
PII_PATTERN = re.compile(
    r"(e-?mail|phone|mobile|id_?card|id_?number|ssn|passport|address|birth|real_?name|bank|card_?number)",
    re.IGNORECASE,
)


def load_document(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("读取 YAML 需要 pyyaml：pip install pyyaml") from exc
    return yaml.safe_load(text)


def resolve(doc: dict, node: dict) -> dict:
    ref = node.get("$ref") if isinstance(node, dict) else None
    if not ref or not ref.startswith("#/"):
        return node
    target = doc
    for part in ref[2:].split("/"):
        target = target.get(part, {})
    return target


def walk_schema(doc: dict, schema: dict, location: str, findings: list, seen: set) -> None:
    schema = resolve(doc, schema or {})
    key = id(schema)
    if key in seen:
        return
    seen.add(key)
    kind = schema.get("type")
    if kind == "array" and "maxItems" not in schema:
        findings.append(("重要", location, "数组未声明 maxItems"))
    if kind == "string" and not any(k in schema for k in ("maxLength", "enum", "format", "pattern")):
        findings.append(("建议", location, "字符串未声明 maxLength/enum/format/pattern"))
    for name, prop in (schema.get("properties") or {}).items():
        sub = f"{location}.{name}"
        if PII_PATTERN.search(name):
            findings.append(("重要", sub, "疑似 PII 字段，确认是否必要、脱敏或按权限返回"))
        walk_schema(doc, prop, sub, findings, seen)
    if "items" in schema:
        walk_schema(doc, schema["items"], f"{location}[]", findings, seen)
    for combo in ("allOf", "oneOf", "anyOf"):
        for index, part in enumerate(schema.get(combo) or []):
            walk_schema(doc, part, f"{location}.{combo}[{index}]", findings, seen)


def check(doc: dict) -> list[tuple[str, str, str]]:
    findings: list[tuple[str, str, str]] = []
    global_security = doc.get("security")
    for path, item in (doc.get("paths") or {}).items():
        for method in METHODS:
            op = item.get(method)
            if not op:
                continue
            where = f"{method.upper()} {path}"
            security = op.get("security", global_security)
            responses = {str(code) for code in (op.get("responses") or {})}
            if not security or security == [{}]:
                findings.append(("严重", where, "未声明认证要求（security 为空），匿名访问需有明确理由"))
            else:
                if "401" not in responses:
                    findings.append(("重要", where, "未声明 401 响应"))
                if "403" not in responses and ("{" in path or method != "get"):
                    findings.append(("重要", where, "按 ID 访问或写操作未声明 403 响应，确认对象级授权"))
            if method == "get" and "{" not in path:
                names = {p.get("name") for p in (resolve(doc, p) for p in op.get("parameters") or [])}
                if not names & {"limit", "page_size", "pageSize", "per_page", "first"}:
                    findings.append(("建议", where, "集合接口未见分页上限参数"))
            seen: set = set()
            for param in op.get("parameters") or []:
                param = resolve(doc, param)
                walk_schema(doc, param.get("schema") or {}, f"{where} 参数 {param.get('name')}", findings, seen)
            body = resolve(doc, op.get("requestBody") or {})
            for media in (body.get("content") or {}).values():
                walk_schema(doc, media.get("schema") or {}, f"{where} 请求体", findings, seen)
            for code, response in (op.get("responses") or {}).items():
                for media in (resolve(doc, response).get("content") or {}).values():
                    walk_schema(doc, media.get("schema") or {}, f"{where} 响应 {code}", findings, seen)
    order = {"严重": 0, "重要": 1, "建议": 2}
    return sorted(findings, key=lambda f: (order[f[0]], f[1]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="OpenAPI 文件（.yaml/.yml/.json）")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = parser.parse_args(argv)
    if not args.spec.is_file():
        print(f"ERROR {args.spec}：文件不存在", file=sys.stderr)
        return 2
    findings = check(load_document(args.spec))
    if args.json:
        print(
            json.dumps(
                [dict(zip(("severity", "location", "message"), f, strict=True)) for f in findings], ensure_ascii=False
            )
        )
    else:
        for severity, location, message in findings:
            print(f"[{severity}] {location}：{message}")
        counts = {s: sum(f[0] == s for f in findings) for s in ("严重", "重要", "建议")}
        print(f"汇总：严重 {counts['严重']}，重要 {counts['重要']}，建议 {counts['建议']}。结果需人工复核。")
    return 1 if any(f[0] == "严重" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
