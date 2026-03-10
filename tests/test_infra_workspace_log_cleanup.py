import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sys

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

import infra_workspace_log_cleanup


class InfraWorkspaceLogCleanupTests(unittest.TestCase):
    def test_validate_candidate_accepts_workspace_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            log_path = root / "logs" / "night-infra.log"
            log_path.parent.mkdir()
            log_path.write_bytes(b"x" * 4096)

            with mock.patch.object(infra_workspace_log_cleanup, "ROOT", root), mock.patch.object(
                infra_workspace_log_cleanup, "LOG_ROOT", root / "logs"
            ), mock.patch.object(
                infra_workspace_log_cleanup, "has_open_files", return_value=None
            ):
                candidate, reason = infra_workspace_log_cleanup.validate_candidate(log_path, min_bytes=1024)

        self.assertIsNone(reason)
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.path, log_path.resolve())
        self.assertEqual(candidate.note, "generated workspace log")

    def test_validate_candidate_rejects_non_night_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            log_path = root / "logs" / "infra-activity.log"
            log_path.parent.mkdir()
            log_path.write_bytes(b"x" * 4096)

            with mock.patch.object(infra_workspace_log_cleanup, "ROOT", root), mock.patch.object(
                infra_workspace_log_cleanup, "LOG_ROOT", root / "logs"
            ), mock.patch.object(
                infra_workspace_log_cleanup, "has_open_files", return_value=None
            ):
                candidate, reason = infra_workspace_log_cleanup.validate_candidate(log_path, min_bytes=1024)

        self.assertIsNone(candidate)
        self.assertEqual(reason, "not an allowlisted workspace log path")

    def test_validate_candidate_rejects_open_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            log_path = root / "logs" / "night-infra.log"
            log_path.parent.mkdir()
            log_path.write_bytes(b"x" * 4096)

            with mock.patch.object(infra_workspace_log_cleanup, "ROOT", root), mock.patch.object(
                infra_workspace_log_cleanup, "LOG_ROOT", root / "logs"
            ), mock.patch.object(
                infra_workspace_log_cleanup, "has_open_files", return_value="open files detected"
            ):
                candidate, reason = infra_workspace_log_cleanup.validate_candidate(log_path, min_bytes=1024)

        self.assertIsNone(candidate)
        self.assertEqual(reason, "open files detected")

    def test_scan_cleanup_candidates_only_lists_night_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            logs_dir = root / "logs"
            logs_dir.mkdir()
            (logs_dir / "night-infra.log").write_bytes(b"x" * 4096)
            (logs_dir / "infra-activity.log").write_bytes(b"x" * 8192)

            with mock.patch.object(infra_workspace_log_cleanup, "ROOT", root), mock.patch.object(
                infra_workspace_log_cleanup, "LOG_ROOT", logs_dir
            ), mock.patch.object(
                infra_workspace_log_cleanup, "has_open_files", return_value=None
            ):
                candidates = infra_workspace_log_cleanup.scan_cleanup_candidates(min_bytes=1024)

        self.assertEqual([candidate.path.name for candidate in candidates], ["night-infra.log"])

    def test_apply_mode_removes_allowlisted_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            log_path = root / "logs" / "night-infra.log"
            log_path.parent.mkdir()
            log_path.write_bytes(b"x" * 2048)

            with mock.patch.object(infra_workspace_log_cleanup, "ROOT", root), mock.patch.object(
                infra_workspace_log_cleanup, "LOG_ROOT", root / "logs"
            ), mock.patch.object(
                infra_workspace_log_cleanup, "has_open_files", return_value=None
            ):
                status = infra_workspace_log_cleanup.apply_mode([str(log_path)], min_bytes=1024)

        self.assertEqual(status, 0)
        self.assertFalse(log_path.exists())


if __name__ == "__main__":
    unittest.main()
