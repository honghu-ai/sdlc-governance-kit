#!/usr/bin/env python3
"""Initialize or audit repository-level SDLC governance scaffolding."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSET_ROOT = SKILL_ROOT / "assets"
CORE_DIRECTORIES = (
    Path("docs/sdlc/changes"),
    Path("docs/sdlc/incidents"),
)
CORE_FILES = {
    Path("CLAUDE.md"): ASSET_ROOT / "CLAUDE.md.tpl",
    Path("REVIEW.md"): ASSET_ROOT / "REVIEW.md.tpl",
    Path("docs/sdlc/00_Index.md"): ASSET_ROOT / "00_Index.md.tpl",
}
TRACKING_FILES = (
    Path("docs/sdlc/changes/.gitkeep"),
    Path("docs/sdlc/incidents/.gitkeep"),
)
LINK_PATTERN = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")


def add_finding(findings: list[tuple[str, Path, str]], level: str, path: Path, message: str) -> None:
    findings.append((level, path, message))


def has_pattern(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) is not None


def check_required_content(root: Path, findings: list[tuple[str, Path, str]]) -> None:
    checks = {
        Path("CLAUDE.md"): (
            (r"^#{1,6}\s+.*命令", "缺少命令章节"),
            (r"(构建|build)", "未记录构建命令"),
            (r"(测试|test)", "未记录测试命令"),
            (r"(lint|静态检查)", "未记录 lint 命令"),
            (r"(健康输出|成功输出)", "未记录健康输出示例"),
            (r"^#{1,6}\s+.*约定", "缺少关键约定章节"),
            (r"^#{1,6}\s+.*架构", "缺少架构边界章节"),
            (r"(容易出错|常见错误|重复错误)", "未记录智能体重复错误"),
        ),
        Path("REVIEW.md"): (
            (r"评审轮次", "缺少评审轮次"),
            (r"important", "缺少 Important 定义"),
            (r"\bnit\b", "缺少 Nit 定义"),
            (r"(不要报告|忽略项|排除)", "缺少忽略项"),
            (r"(人工批准|人工阈值|代码负责人)", "缺少人工批准边界"),
        ),
        Path("docs/sdlc/00_Index.md"): (
            (r"活动变更", "缺少活动变更索引"),
            (r"近期完成", "缺少近期完成索引"),
            (r"(近期事故|事故)", "缺少事故索引"),
        ),
    }

    for relative_path, rules in checks.items():
        file_path = root / relative_path
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8")
        for pattern, message in rules:
            if not has_pattern(text, pattern):
                add_finding(findings, "WARN", relative_path, message)
        if "待团队填写" in text or "[项目名称]" in text:
            add_finding(findings, "WARN", relative_path, "仍含待团队确认的占位内容")


def local_link_target(markdown_file: Path, raw_target: str) -> Path | None:
    candidate = raw_target.strip()
    if candidate.startswith("<") and ">" in candidate:
        target = candidate[1 : candidate.index(">")]
    else:
        target = candidate.split(maxsplit=1)[0]
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith("#"):
        return None
    path_text = unquote(parsed.path)
    if not path_text:
        return None
    target_path = Path(path_text)
    if target_path.is_absolute():
        return target_path
    return markdown_file.parent / target_path


def check_links(root: Path, findings: list[tuple[str, Path, str]]) -> None:
    sdlc_root = root / "docs/sdlc"
    if not sdlc_root.is_dir():
        return
    for markdown_file in sorted(sdlc_root.rglob("*.md")):
        text = markdown_file.read_text(encoding="utf-8")
        for raw_target in LINK_PATTERN.findall(text):
            target = local_link_target(markdown_file, raw_target)
            if target is not None and not target.exists():
                relative_file = markdown_file.relative_to(root)
                add_finding(findings, "ERROR", relative_file, f"本地引用不存在：{raw_target}")


def check_item_directories(root: Path, findings: list[tuple[str, Path, str]]) -> None:
    changes_root = root / "docs/sdlc/changes"
    if changes_root.is_dir():
        for item in sorted(changes_root.iterdir()):
            if item.is_dir() and not item.name.startswith(".") and not (item / "00_Index.md").is_file():
                add_finding(
                    findings,
                    "ERROR",
                    item.relative_to(root),
                    "单项变更目录缺少 00_Index.md",
                )

    incidents_root = root / "docs/sdlc/incidents"
    if incidents_root.is_dir():
        for item in sorted(incidents_root.iterdir()):
            if item.is_dir() and not item.name.startswith(".") and not (item / "incident.md").is_file():
                add_finding(
                    findings,
                    "ERROR",
                    item.relative_to(root),
                    "事故目录缺少 incident.md",
                )

    sdlc_root = root / "docs/sdlc"
    if not sdlc_root.is_dir():
        return
    for name in ("intent.md", "spec.md", "plan.md"):
        for artifact in sorted(sdlc_root.rglob(name)):
            relative = artifact.relative_to(sdlc_root)
            if len(relative.parts) != 3 or relative.parts[0] != "changes":
                add_finding(
                    findings,
                    "ERROR",
                    artifact.relative_to(root),
                    "阶段产物必须位于 docs/sdlc/changes/<change-id>/",
                )


def audit(root: Path) -> list[tuple[str, Path, str]]:
    findings: list[tuple[str, Path, str]] = []
    for relative_path in CORE_DIRECTORIES:
        directory = root / relative_path
        if not directory.is_dir():
            add_finding(findings, "ERROR", relative_path, "缺少核心目录")
        elif not any(directory.iterdir()) and not (directory / ".gitkeep").is_file():
            add_finding(findings, "WARN", relative_path, "空目录缺少 .gitkeep，无法进入版本控制")
    for relative_path in CORE_FILES:
        if not (root / relative_path).is_file():
            add_finding(findings, "ERROR", relative_path, "缺少核心文件")

    check_required_content(root, findings)
    check_links(root, findings)
    check_item_directories(root, findings)
    return findings


def print_findings(findings: list[tuple[str, Path, str]]) -> None:
    if not findings:
        print("OK：治理骨架结构与本地引用检查通过。")
        return
    for level, path, message in findings:
        print(f"{level} {path.as_posix()}：{message}")
    errors = sum(level == "ERROR" for level, _, _ in findings)
    warnings = sum(level == "WARN" for level, _, _ in findings)
    print(f"汇总：{errors} 个错误，{warnings} 个警告。")


def initialize(root: Path) -> None:
    added: list[Path] = []
    unchanged: list[Path] = []

    for relative_path in CORE_DIRECTORIES:
        target = root / relative_path
        if target.is_dir():
            unchanged.append(relative_path)
        elif target.exists():
            unchanged.append(relative_path)
        else:
            target.mkdir(parents=True, exist_ok=True)
            added.append(relative_path)

    for relative_path in TRACKING_FILES:
        target = root / relative_path
        if target.exists():
            unchanged.append(relative_path)
            continue
        if not target.parent.is_dir():
            continue
        target.touch()
        added.append(relative_path)

    for relative_path, template in CORE_FILES.items():
        target = root / relative_path
        if target.exists():
            unchanged.append(relative_path)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(template, target)
        added.append(relative_path)

    print("新增：")
    if added:
        for path in added:
            print(f"- {path.as_posix()}")
    else:
        print("- 无")
    print("未修改：")
    if unchanged:
        for path in unchanged:
            print(f"- {path.as_posix()}")
    else:
        print("- 无")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("init", "audit"), help="初始化或只读审计")
    parser.add_argument("--target", type=Path, default=Path.cwd(), help="目标代码库，默认为当前目录")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.target.expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR {root}：目标代码库不存在或不是目录。", file=sys.stderr)
        return 2

    if args.mode == "init":
        initialize(root)
        print("结构检查：")
    findings = audit(root)
    print_findings(findings)
    return 1 if any(level == "ERROR" for level, _, _ in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
