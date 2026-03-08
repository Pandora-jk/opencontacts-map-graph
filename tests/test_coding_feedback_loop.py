import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

from coding_feedback_loop import audit_feedback_loop


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


class CodingFeedbackLoopTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.kanban_dir = self.root / "departments" / "coding" / "kanban"
        self.kanban_dir.mkdir(parents=True)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.name", "Test User")
        git(self.repo, "config", "user.email", "test@example.com")
        (self.repo / "README.md").write_text("base\n", encoding="utf-8")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-m", "base")

        self.remote = self.root / "remote.git"
        git(self.root, "init", "--bare", str(self.remote))
        git(self.repo, "remote", "add", "origin", str(self.remote))
        git(self.repo, "push", "-u", "origin", "main")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_board(self, body: str) -> None:
        (self.kanban_dir / "workspace-core.md").write_text(body, encoding="utf-8")

    def create_branch(self, name: str, filename: str, content: str, push: bool = False) -> None:
        git(self.repo, "checkout", "-b", name)
        (self.repo / filename).write_text(content, encoding="utf-8")
        git(self.repo, "add", filename)
        git(self.repo, "commit", "-m", f"add {filename}")
        if push:
            git(self.repo, "push", "-u", "origin", name)
        git(self.repo, "checkout", "main")

    def test_review_branch_with_evidence_becomes_merge_ready(self) -> None:
        self.create_branch("feature/review-branch-2026-03-08", "feature.txt", "ready\n", push=True)
        self.write_board(
            "# Kanban - workspace-core\n\n"
            "## Review\n"
            "- [ ] **Review branch**\n"
            "  - branch: `feature/review-branch-2026-03-08`\n"
            "  - tests: unit tests\n"
            "  - acceptance: branch can merge cleanly\n"
            "  - test-results: `python3 -m unittest` => passed\n"
            "\n"
            "## Done\n"
        )

        items, summary = audit_feedback_loop(self.root, repos=[self.repo], kanban_dir=self.kanban_dir)

        self.assertEqual(summary["unmerged_total"], 1)
        self.assertEqual(summary["merge_ready"], 1)
        self.assertEqual(items[0]["status"], "merge_ready")
        self.assertEqual(items[0]["owner"], "review_agent")
        self.assertEqual(items[0]["lane"], "Review")

    def test_ready_branch_without_remote_stays_coding_work(self) -> None:
        self.create_branch("feature/coding-branch-2026-03-08", "coding.txt", "draft\n", push=False)
        (self.repo / "README.md").write_text("base\nmain change\n", encoding="utf-8")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-m", "advance main")
        git(self.repo, "push", "origin", "main")
        self.write_board(
            "# Kanban - workspace-core\n\n"
            "## Ready\n"
            "- [ ] **Coding branch**\n"
            "  - branch: `feature/coding-branch-2026-03-08`\n"
            "  - tests: add coverage\n"
            "  - acceptance: branch is ready for review after tests\n"
            "\n"
            "## Done\n"
        )

        items, summary = audit_feedback_loop(self.root, repos=[self.repo], kanban_dir=self.kanban_dir)

        self.assertEqual(summary["coding_needed"], 1)
        self.assertEqual(items[0]["status"], "coding_needed")
        self.assertEqual(items[0]["owner"], "coding_agent")
        self.assertIn("card is still in Ready", items[0]["reason"])
        self.assertFalse(items[0]["remote_exists"])
        self.assertGreater(items[0]["behind_main"], 0)


if __name__ == "__main__":
    unittest.main()
