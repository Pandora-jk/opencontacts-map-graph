import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sys

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

import infra_workspace_cache_cleanup


class InfraWorkspaceCacheCleanupTests(unittest.TestCase):
    def test_validate_candidate_accepts_workspace_gradle_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            gradle_dir = root / ".gradle"
            gradle_dir.mkdir()
            (gradle_dir / "cache.bin").write_bytes(b"x" * 4096)

            with mock.patch.object(infra_workspace_cache_cleanup, "ROOT", root), mock.patch.dict(
                infra_workspace_cache_cleanup.ALLOWLISTED_EXACT_PATHS,
                {root / ".gradle": "workspace Gradle cache"},
                clear=True,
            ), mock.patch.object(
                infra_workspace_cache_cleanup, "has_open_files", return_value=False
            ):
                candidate, reason = infra_workspace_cache_cleanup.validate_candidate(gradle_dir, min_bytes=1024)

        self.assertIsNone(reason)
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.path, gradle_dir.resolve())
        self.assertEqual(candidate.note, "workspace Gradle cache")

    def test_validate_candidate_rejects_symlink_component_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            real_parent = root / "tools"
            pycache_dir = real_parent / "__pycache__"
            pycache_dir.mkdir(parents=True)
            (pycache_dir / "module.pyc").write_bytes(b"x" * 2048)
            alias_parent = root / "alias-tools"
            alias_parent.symlink_to(real_parent, target_is_directory=True)

            with mock.patch.object(infra_workspace_cache_cleanup, "ROOT", root), mock.patch.object(
                infra_workspace_cache_cleanup, "has_open_files", return_value=False
            ):
                candidate, reason = infra_workspace_cache_cleanup.validate_candidate(
                    alias_parent / "__pycache__",
                    min_bytes=1024,
                )

        self.assertIsNone(candidate)
        self.assertEqual(reason, "symlink skipped")

    def test_scan_cleanup_candidates_finds_workspace_caches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            pycache_dir = root / "tools" / "__pycache__"
            pycache_dir.mkdir(parents=True)
            (pycache_dir / "module.pyc").write_bytes(b"x" * 2048)
            gradle_dir = root / ".gradle"
            gradle_dir.mkdir()
            (gradle_dir / "cache.bin").write_bytes(b"x" * 4096)

            with mock.patch.object(infra_workspace_cache_cleanup, "ROOT", root), mock.patch.dict(
                infra_workspace_cache_cleanup.ALLOWLISTED_EXACT_PATHS,
                {root / ".gradle": "workspace Gradle cache"},
                clear=True,
            ), mock.patch.object(
                infra_workspace_cache_cleanup, "has_open_files", return_value=False
            ):
                candidates = infra_workspace_cache_cleanup.scan_cleanup_candidates(min_bytes=1024)

        self.assertEqual(
            [candidate.path for candidate in candidates],
            [gradle_dir.resolve(), pycache_dir.resolve()],
        )

    def test_apply_mode_removes_allowlisted_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pycache_dir = root / "tests" / "__pycache__"
            pycache_dir.mkdir(parents=True)
            (pycache_dir / "module.pyc").write_bytes(b"x" * 2048)

            with mock.patch.object(infra_workspace_cache_cleanup, "ROOT", root), mock.patch.dict(
                infra_workspace_cache_cleanup.ALLOWLISTED_EXACT_PATHS,
                {},
                clear=True,
            ), mock.patch.object(
                infra_workspace_cache_cleanup, "has_open_files", return_value=False
            ):
                status = infra_workspace_cache_cleanup.apply_mode([str(pycache_dir)], min_bytes=1024)

        self.assertEqual(status, 0)
        self.assertFalse(pycache_dir.exists())


if __name__ == "__main__":
    unittest.main()
