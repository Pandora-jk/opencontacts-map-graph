import datetime as dt
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import unittest

import sys

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

import infra_home_cache_cleanup


class InfraHomeCacheCleanupTests(unittest.TestCase):
    def test_validate_candidate_rejects_non_allowlisted_path(self) -> None:
        candidate, reason = infra_home_cache_cleanup.validate_candidate(
            Path("/home/ubuntu/projects"),
            min_bytes=infra_home_cache_cleanup.DEFAULT_MIN_BYTES,
        )

        self.assertIsNone(candidate)
        self.assertEqual(reason, "not an allowlisted home cache path")

    def test_validate_candidate_accepts_allowlisted_owned_cache(self) -> None:
        target = Path("/home/ubuntu/.gradle/caches")
        fake_stat = SimpleNamespace(
            st_uid=1000,
            st_mtime=dt.datetime(2026, 3, 8, tzinfo=dt.timezone.utc).timestamp(),
        )

        with mock.patch.object(Path, "exists", return_value=True), mock.patch.object(
            Path, "is_symlink", return_value=False
        ), mock.patch.object(
            Path, "lstat", return_value=fake_stat
        ), mock.patch.object(
            infra_home_cache_cleanup, "path_owner", return_value="ubuntu"
        ), mock.patch.object(
            infra_home_cache_cleanup, "has_open_files", return_value=False
        ), mock.patch.object(
            infra_home_cache_cleanup, "du_bytes", return_value=1900 * 1024 * 1024
        ), mock.patch.object(
            infra_home_cache_cleanup.os, "getuid", return_value=1000
        ), mock.patch.object(
            infra_home_cache_cleanup.pwd, "getpwuid", return_value=SimpleNamespace(pw_name="ubuntu")
        ):
            candidate, reason = infra_home_cache_cleanup.validate_candidate(
                target,
                min_bytes=infra_home_cache_cleanup.DEFAULT_MIN_BYTES,
            )

        self.assertIsNone(reason)
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.path, target)
        self.assertEqual(candidate.note, "Gradle dependency cache")

    def test_validate_candidate_accepts_gradle_wrapper_distributions(self) -> None:
        target = Path("/home/ubuntu/.gradle/wrapper/dists")
        fake_stat = SimpleNamespace(
            st_uid=1000,
            st_mtime=dt.datetime(2026, 3, 9, tzinfo=dt.timezone.utc).timestamp(),
        )

        with mock.patch.object(Path, "exists", return_value=True), mock.patch.object(
            Path, "is_symlink", return_value=False
        ), mock.patch.object(
            Path, "lstat", return_value=fake_stat
        ), mock.patch.object(
            infra_home_cache_cleanup, "path_owner", return_value="ubuntu"
        ), mock.patch.object(
            infra_home_cache_cleanup, "has_open_files", return_value=False
        ), mock.patch.object(
            infra_home_cache_cleanup, "du_bytes", return_value=410 * 1024 * 1024
        ), mock.patch.object(
            infra_home_cache_cleanup.os, "getuid", return_value=1000
        ), mock.patch.object(
            infra_home_cache_cleanup.pwd, "getpwuid", return_value=SimpleNamespace(pw_name="ubuntu")
        ):
            candidate, reason = infra_home_cache_cleanup.validate_candidate(
                target,
                min_bytes=infra_home_cache_cleanup.DEFAULT_MIN_BYTES,
            )

        self.assertIsNone(reason)
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.path, target)
        self.assertEqual(candidate.note, "Gradle wrapper distributions")

    def test_scan_cleanup_candidates_sorts_largest_first(self) -> None:
        sizes = {
            Path("/home/ubuntu/.gradle/caches"): 1900 * 1024 * 1024,
            Path("/home/ubuntu/.gradle/wrapper/dists"): 410 * 1024 * 1024,
            Path("/home/ubuntu/.cache/pip"): 198 * 1024 * 1024,
        }

        def fake_validate(path: Path, *, min_bytes: int):
            size = sizes.get(path)
            if size is None:
                return None, "missing"
            return (
                infra_home_cache_cleanup.CleanupCandidate(
                    path=path,
                    size_bytes=size,
                    mtime=dt.datetime(2026, 3, 9, tzinfo=dt.timezone.utc),
                    owner="ubuntu",
                    note=infra_home_cache_cleanup.ALLOWED_CACHE_TARGETS[path],
                ),
                None,
            )

        with mock.patch.object(infra_home_cache_cleanup, "validate_candidate", side_effect=fake_validate):
            candidates = infra_home_cache_cleanup.scan_cleanup_candidates(
                min_bytes=infra_home_cache_cleanup.DEFAULT_MIN_BYTES
            )

        self.assertEqual(
            [candidate.path for candidate in candidates[:3]],
            [
                Path("/home/ubuntu/.gradle/caches"),
                Path("/home/ubuntu/.gradle/wrapper/dists"),
                Path("/home/ubuntu/.cache/pip"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
