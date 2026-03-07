#!/usr/bin/env python3
"""
Scan tracked or staged git files for likely hardcoded secrets.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

RULES = [
    ("github_pat", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")),
    ("groq_api_key", re.compile(r"\bgsk_[A-Za-z0-9]{20,}\b")),
    ("nvidia_api_key", re.compile(r"\bnvapi-[A-Za-z0-9_-]{20,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")),
    ("cerebras_api_key", re.compile(r"\bcsk-[A-Za-z0-9]{20,}\b")),
    ("openrouter_api_key", re.compile(r"\bsk-or-v1-[A-Za-z0-9]{20,}\b")),
    ("chutes_api_key", re.compile(r"\bcpk_[A-Za-z0-9.]{20,}\b")),
    ("sendinblue_api_key", re.compile(r"\bxkeysib-[A-Za-z0-9_-]{20,}\b")),
    ("telegram_bot_token", re.compile(r"\b\d{7,12}:[A-Za-z0-9_-]{20,}\b")),
]


def run_git(repo: Path, args: list[str]) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", errors="replace").strip() or "git command failed")
    return proc.stdout


def git_file_list(repo: Path, staged: bool) -> list[Path]:
    args = ["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"] if staged else ["ls-files", "-z"]
    data = run_git(repo, args)
    raw = [item for item in data.decode("utf-8", errors="replace").split("\0") if item]
    return [repo / item for item in raw]


def git_revision_list(repo: Path, history_ref: str, max_commits: int) -> list[str]:
    data = run_git(repo, ["rev-list", f"--max-count={max(1, max_commits)}", history_ref])
    return [item for item in data.decode("utf-8", errors="replace").splitlines() if item]


def scan_history(repo: Path, history_ref: str, max_commits: int) -> list[tuple[str, str, int]]:
    revisions = git_revision_list(repo, history_ref, max_commits)
    if not revisions:
        return []

    aggregated: dict[tuple[str, str], dict[str, set[str] | set[int]]] = {}
    for label, pattern in RULES:
        proc = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "grep",
                "-nI",
                "-E",
                pattern.pattern,
                *revisions,
                "--",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode not in (0, 1):
            raise RuntimeError(proc.stderr.strip() or f"git grep failed for {label}")
        for raw in proc.stdout.splitlines():
            parts = raw.split(":", 3)
            if len(parts) < 3:
                continue
            commit = parts[0]
            rel = parts[1]
            try:
                lineno = int(parts[2])
            except ValueError:
                continue
            key = (label, rel)
            entry = aggregated.setdefault(key, {"commits": set(), "lines": set()})
            entry["commits"].add(commit[:12])
            entry["lines"].add(lineno)

    findings: list[tuple[str, str, int]] = []
    for (label, rel), meta in sorted(aggregated.items()):
        commits = sorted(meta["commits"])
        lines = sorted(meta["lines"])
        suffix = (
            f"{rel} [commits={len(commits)}, lines={len(lines)}, "
            f"first_line={lines[0]}, sample={commits[0]}]"
        )
        findings.append((label, suffix, lines[0]))
    return findings


def scan_text(path: Path) -> list[tuple[str, int]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError, PermissionError, UnicodeDecodeError):
        return []

    findings: list[tuple[str, int]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for label, pattern in RULES:
            if pattern.search(line):
                findings.append((label, lineno))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan git-tracked files for likely secrets")
    parser.add_argument("--repo", default=".", help="Git repo root")
    parser.add_argument("--staged", action="store_true", help="Scan staged files instead of all tracked files")
    parser.add_argument("--history-ref", help="Also scan commit history reachable from this ref")
    parser.add_argument("--max-commits", type=int, default=400, help="Max commits to scan for --history-ref")
    parser.add_argument("files", nargs="*", help="Optional explicit file list relative to repo")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if args.files:
        files = [repo / rel for rel in args.files]
    else:
        try:
            files = git_file_list(repo, staged=args.staged)
        except RuntimeError as exc:
            print(f"SECRET_SCAN_ERROR: {exc}")
            return 2

    findings: list[tuple[str, str, int]] = []
    for path in files:
        rel = path.relative_to(repo).as_posix()
        for label, lineno in scan_text(path):
            findings.append((label, rel, lineno))

    if args.history_ref:
        try:
            findings.extend(scan_history(repo, args.history_ref, args.max_commits))
        except RuntimeError as exc:
            print(f"SECRET_SCAN_ERROR: {exc}")
            return 2

    if findings:
        print("SECRET_SCAN_FAIL")
        for label, rel, _lineno in findings:
            print(f"- {label}: {rel}")
        return 1

    scope = "staged" if args.staged else "tracked"
    if args.history_ref:
      scope = f"{scope}+history({args.history_ref})"
    print(f"SECRET_SCAN_OK scope={scope} files={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
