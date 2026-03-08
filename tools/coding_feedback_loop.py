#!/usr/bin/env python3
"""
Audit unmerged coding branches and classify the next owner.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path("/home/ubuntu/.openclaw/workspace")
CODING_DIR = ROOT / "departments" / "coding"
KANBAN_DIR = CODING_DIR / "kanban"
TRACKED_PREFIXES = ("feature/", "feat/")
SECTION_NAMES = ("Backlog", "Ready", "In Progress", "Review", "Done")


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git command failed")
    return result


def discover_repositories(root: Path = ROOT) -> list[Path]:
    repos: list[Path] = []
    for candidate in (root, root / "opencontacts-map-graph"):
        if (candidate / ".git").exists():
            repos.append(candidate)
    return repos


def default_branch(repo: Path) -> str:
    for branch in ("main", "master"):
        result = run_git(repo, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}", check=False)
        if result.returncode == 0:
            return branch
    current = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD", check=False)
    branch = current.stdout.strip()
    return branch or "main"


def list_unmerged_feature_branches(repo: Path, base_branch: str) -> list[str]:
    branches = run_git(repo, "branch", "--format=%(refname:short)").stdout.splitlines()
    unmerged: list[str] = []
    for branch in branches:
        branch = branch.strip()
        if branch == base_branch or not branch.startswith(TRACKED_PREFIXES):
            continue
        merged = run_git(repo, "merge-base", "--is-ancestor", branch, base_branch, check=False)
        if merged.returncode != 0:
            unmerged.append(branch)
    return sorted(unmerged)


def safe_relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def parse_kanban_index(kanban_dir: Path = KANBAN_DIR, root: Path = ROOT) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    if not kanban_dir.exists():
        return index

    for board in sorted(kanban_dir.glob("*.md")):
        if board.name == "README.md":
            continue
        section = ""
        current: dict[str, str] | None = None
        for raw in board.read_text(encoding="utf-8").splitlines() + ["## __END__"]:
            stripped = raw.strip()
            if stripped.startswith("## "):
                if current and current.get("branch"):
                    current["board"] = safe_relative(board, root)
                    index[current["branch"]] = current
                current = None
                heading = stripped[3:].strip()
                section = heading if heading in SECTION_NAMES else ""
                continue
            if not section:
                continue
            if stripped.startswith(("- [ ]", "- [x]", "- [~]")):
                if current and current.get("branch"):
                    current["board"] = safe_relative(board, root)
                    index[current["branch"]] = current
                title = re.sub(r"^- \[[ x~]\]\s*", "", stripped).strip()
                current = {"title": title, "lane": section}
                continue
            if not current:
                continue
            if stripped.startswith("- branch:"):
                current["branch"] = stripped.split(":", 1)[1].strip().strip("`")
            elif stripped.startswith("- tests:"):
                current["tests"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("- acceptance:"):
                current["acceptance"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("- test-results:"):
                current["test_results"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("- notes:"):
                current["notes"] = stripped.split(":", 1)[1].strip()
    return index


def branch_divergence(repo: Path, base_branch: str, branch: str) -> tuple[int, int]:
    counts = run_git(repo, "rev-list", "--left-right", "--count", f"{base_branch}...{branch}").stdout.strip().split()
    if len(counts) != 2:
        return 0, 0
    behind, ahead = counts
    return int(behind), int(ahead)


def branch_has_remote(repo: Path, branch: str) -> bool:
    result = run_git(repo, "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{branch}", check=False)
    return result.returncode == 0


def branch_merge_conflicts(repo: Path, base_branch: str, branch: str) -> bool:
    merge_base_result = run_git(repo, "merge-base", base_branch, branch, check=False)
    merge_base = merge_base_result.stdout.strip()
    if merge_base_result.returncode != 0 or not merge_base:
        return True
    result = run_git(repo, "merge-tree", merge_base, base_branch, branch, check=False)
    merged_text = (result.stdout or "") + (result.stderr or "")
    return any(marker in merged_text for marker in ("<<<<<<<", "changed in both", "added in both", "removed in both"))


def has_test_evidence(card: dict[str, str] | None) -> bool:
    if not card:
        return False
    text = card.get("test_results", "").strip()
    return bool(text)


def is_blocked(card: dict[str, str] | None) -> bool:
    if not card:
        return True
    haystack = " ".join(
        [
            card.get("title", ""),
            card.get("tests", ""),
            card.get("test_results", ""),
            card.get("notes", ""),
        ]
    ).lower()
    return "blocked" in haystack or "sandblocked" in haystack


def classify_branch(
    root: Path,
    repo: Path,
    base_branch: str,
    branch: str,
    card: dict[str, str] | None,
) -> dict[str, object]:
    behind, ahead = branch_divergence(repo, base_branch, branch)
    remote_exists = branch_has_remote(repo, branch)
    merge_conflicts = branch_merge_conflicts(repo, base_branch, branch)
    lane = card.get("lane", "Untracked") if card else "Untracked"
    blocked = is_blocked(card)
    test_evidence = has_test_evidence(card)
    merge_ready = (
        lane == "Review"
        and test_evidence
        and not blocked
        and remote_exists
        and ahead > 0
        and behind == 0
        and not merge_conflicts
    )
    if merge_ready:
        owner = "review_agent"
        status = "merge_ready"
        reason = "Review card has test evidence, remote branch exists, and the branch merges cleanly into main."
    elif lane == "Review" or lane == "Done":
        owner = "review_agent"
        status = "review_needed"
        reasons = []
        if not test_evidence:
            reasons.append("missing test evidence")
        if blocked:
            reasons.append("recorded blocker")
        if not remote_exists:
            reasons.append("branch not pushed to origin")
        if behind > 0:
            reasons.append("branch is behind main")
        if merge_conflicts:
            reasons.append("merge conflicts against main")
        if not reasons:
            reasons.append("review lane still needs explicit merge decision")
        reason = ", ".join(reasons)
    else:
        owner = "coding_agent"
        status = "coding_needed"
        reasons = []
        if card is None:
            reasons.append("branch is not linked to any coding card")
        elif lane in {"Backlog", "Ready", "In Progress"}:
            reasons.append(f"card is still in {lane}")
        if not remote_exists:
            reasons.append("branch not pushed to origin")
        if ahead <= 0:
            reasons.append("branch has no unique commits")
        if behind > 0:
            reasons.append("branch is behind main")
        reason = ", ".join(reasons) if reasons else "branch needs more coding work before review"

    return {
        "repo": safe_relative(repo, root),
        "repo_path": str(repo),
        "main_branch": base_branch,
        "branch": branch,
        "owner": owner,
        "status": status,
        "reason": reason,
        "lane": lane,
        "title": card.get("title", "") if card else "",
        "board": card.get("board", "") if card else "",
        "tests": card.get("tests", "") if card else "",
        "test_results": card.get("test_results", "") if card else "",
        "acceptance": card.get("acceptance", "") if card else "",
        "notes": card.get("notes", "") if card else "",
        "remote_exists": remote_exists,
        "merge_conflicts": merge_conflicts,
        "blocked": blocked,
        "has_test_evidence": test_evidence,
        "behind_main": behind,
        "ahead_of_main": ahead,
    }


def summarize_feedback(items: list[dict[str, object]]) -> dict[str, int]:
    summary = {
        "unmerged_total": len(items),
        "merge_ready": 0,
        "review_needed": 0,
        "coding_needed": 0,
    }
    for item in items:
        status = str(item.get("status", ""))
        if status in summary:
            summary[status] += 1
    return summary


def audit_feedback_loop(
    root: Path = ROOT,
    repos: list[Path] | None = None,
    kanban_dir: Path | None = None,
) -> tuple[list[dict[str, object]], dict[str, int]]:
    root = root.resolve()
    repos = repos or discover_repositories(root)
    kanban_dir = kanban_dir or (root / "departments" / "coding" / "kanban")
    index = parse_kanban_index(kanban_dir, root=root)
    items: list[dict[str, object]] = []
    for repo in repos:
        base_branch = default_branch(repo)
        for branch in list_unmerged_feature_branches(repo, base_branch):
            card = index.get(branch)
            items.append(classify_branch(root, repo, base_branch, branch, card))
    items.sort(key=feedback_priority)
    return items, summarize_feedback(items)


def feedback_priority(item: dict[str, object]) -> tuple[int, str, str]:
    status = str(item.get("status", "coding_needed"))
    order = {
        "merge_ready": 0,
        "review_needed": 1,
        "coding_needed": 2,
    }
    return (
        order.get(status, 99),
        str(item.get("repo", "")),
        str(item.get("branch", "")),
    )


def choose_feedback_item(items: list[dict[str, object]]) -> dict[str, object] | None:
    return items[0] if items else None


def build_snapshot(summary: dict[str, int]) -> str:
    return (
        "feedback_loop:"
        f" unmerged={summary['unmerged_total']}"
        f" merge_ready={summary['merge_ready']}"
        f" review_needed={summary['review_needed']}"
        f" coding_needed={summary['coding_needed']}"
    )


def build_report(items: list[dict[str, object]], summary: dict[str, int], emit_telegram: bool = False) -> str:
    if emit_telegram:
        lines = [
            "[CODING FEEDBACK]",
            f"Unmerged: {summary['unmerged_total']}",
            f"Merge ready: {summary['merge_ready']}",
            f"Review needed: {summary['review_needed']}",
            f"Coding needed: {summary['coding_needed']}",
        ]
    else:
        lines = [
            "# Coding Feedback Loop",
            "",
            f"- Unmerged branches: {summary['unmerged_total']}",
            f"- Merge ready: {summary['merge_ready']}",
            f"- Review needed: {summary['review_needed']}",
            f"- Coding needed: {summary['coding_needed']}",
            "",
        ]
    for item in items[:12]:
        title = str(item.get("title", "")).strip() or "untracked branch"
        line = (
            f"{item['owner']} | {item['status']} | {item['repo']} | {item['branch']} | "
            f"lane={item['lane']} | ahead={item['ahead_of_main']} | behind={item['behind_main']} | "
            f"remote={'yes' if item['remote_exists'] else 'no'} | {title}"
        )
        lines.append(line if emit_telegram else f"- {line}")
        if not emit_telegram:
            lines.append(f"  reason: {item['reason']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit unmerged coding branches")
    parser.add_argument("--emit-telegram", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    items, summary = audit_feedback_loop()
    if args.json:
        print(json.dumps({"summary": summary, "items": items}, indent=2))
        return 0
    print(build_report(items, summary, emit_telegram=args.emit_telegram), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
