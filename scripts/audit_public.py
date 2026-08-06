#!/usr/bin/env python3

import re
from pathlib import Path
from urllib.parse import unquote, urlparse


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".drawio", ".json", ".md", ".py", ".txt", ".yaml", ".yml"}
GENERATED_NAMES = {".DS_Store", "__pycache__"}
GENERATED_SUFFIXES = {".dtmp", ".pyc", ".pyo"}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def content_patterns() -> dict[str, re.Pattern[str]]:
    user_home = "/" + "Users" + "/"
    linux_home = "/" + "home" + "/"
    private_key = "BEGIN " + "PRIVATE KEY"
    company_name = "pie" + "tra"
    workspace_name = "parsec" + "-project"
    token_prefixes = "(?:ghp|github_pat|sk|xox[baprs])-" + r"[A-Za-z0-9_-]{12,}"
    return {
        "absolute user path": re.compile(
            rf"(?:{re.escape(user_home)}|{re.escape(linux_home)})[^\s'\"<>]+"
        ),
        "email address": re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),
        "private key": re.compile(re.escape(private_key)),
        "access token": re.compile(token_prefixes),
        "cloud access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "project-specific term": re.compile(
            rf"(?:{company_name}|{workspace_name})", re.IGNORECASE
        ),
    }


def local_markdown_targets(content: str) -> list[str]:
    targets = []
    inside_fence = False
    for line in content.splitlines():
        if line.lstrip().startswith("```"):
            inside_fence = not inside_fence
            continue
        if inside_fence:
            continue
        targets.extend(match.group(1).strip() for match in MARKDOWN_LINK.finditer(line))
    return targets


def audit_repository(root: Path) -> list[str]:
    findings = []
    patterns = content_patterns()

    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue

        relative_path = path.relative_to(root)
        if path.name in GENERATED_NAMES or path.suffix in GENERATED_SUFFIXES:
            findings.append(f"generated file: {relative_path}")
            continue

        if path.is_symlink():
            resolved = path.resolve()
            if resolved != root and root not in resolved.parents:
                findings.append(f"external symlink: {relative_path} -> {resolved}")
            continue

        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue

        content = path.read_text(encoding="utf-8")
        for label, pattern in patterns.items():
            for match in pattern.finditer(content):
                line_number = content.count("\n", 0, match.start()) + 1
                findings.append(f"{label}: {relative_path}:{line_number}")

        if path.suffix == ".md":
            for target in local_markdown_targets(content):
                parsed = urlparse(target)
                if parsed.scheme or target.startswith(("#", "/")):
                    continue
                target_path = path.parent / unquote(target.split("#", 1)[0])
                if not target_path.exists():
                    findings.append(f"broken local link: {relative_path} -> {target}")

    return findings


def main() -> None:
    findings = audit_repository(REPOSITORY_ROOT)
    if findings:
        raise SystemExit("Public audit failed:\n" + "\n".join(findings))
    print("Public audit passed.")


if __name__ == "__main__":
    main()
