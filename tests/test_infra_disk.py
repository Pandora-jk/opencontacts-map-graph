import unittest
import datetime as dt
from pathlib import Path
from unittest import mock

import sys

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

import infra_disk
import infra_home_cache_cleanup


class InfraDiskTests(unittest.TestCase):
    def test_current_root_usage_bytes_parses_byte_output(self) -> None:
        with mock.patch.object(
            infra_disk,
            "run_cmd",
            return_value="20401094656 20246827008 154267648 100% /",
        ):
            snapshot = infra_disk.current_root_usage_bytes()

        self.assertEqual(snapshot, (20401094656, 20246827008, 154267648, 100, "/"))

    def test_collect_reclaim_candidates_sorts_largest_first(self) -> None:
        sizes = {
            Path("/tmp"): 220 * 1024 * 1024,
            Path("/var/cache/apt"): 628 * 1024 * 1024,
            Path("/var/log/journal"): 143 * 1024 * 1024,
            Path("/home/ubuntu/.cache"): 366 * 1024 * 1024,
        }

        with mock.patch.object(infra_disk, "path_usage_bytes", side_effect=lambda path: sizes.get(path)), mock.patch.object(
            infra_disk, "scan_home_cache_cleanup_candidates", return_value=[]
        ):
            candidates = infra_disk.collect_reclaim_candidates()

        self.assertEqual(
            [str(path) for _, path, _ in candidates],
            ["/var/cache/apt", "/home/ubuntu/.cache", "/tmp", "/var/log/journal"],
        )

    def test_summarize_reclaim_guidance_adds_hotspots_and_hints(self) -> None:
        candidates = [
            (628 * 1024 * 1024, Path("/var/cache/apt"), "APT package cache"),
            (366 * 1024 * 1024, Path("/home/ubuntu/.cache"), "user cache"),
            (
                1900 * 1024 * 1024,
                Path("/home/ubuntu/.gradle/caches"),
                "Gradle dependency cache",
            ),
            (
                410 * 1024 * 1024,
                Path("/home/ubuntu/.gradle/wrapper/dists"),
                "Gradle wrapper distributions",
            ),
            (220 * 1024 * 1024, Path("/tmp"), "temporary files under /tmp"),
            (143 * 1024 * 1024, Path("/var/log/journal"), "systemd journals"),
        ]

        def fake_hotspots(path: Path) -> list[str]:
            return [f"Largest paths under {path}:", "sample output"]

        with mock.patch.object(infra_disk, "summarize_hotspots", side_effect=fake_hotspots), mock.patch.object(
            infra_disk, "summarize_stale_tmp_entries", return_value=["Stale /tmp entries older than 24h:", "- 913M /tmp/gradle-home"]
        ), mock.patch.object(
            infra_disk, "summarize_tmp_cleanup_helper", return_value=["Cleanup helper available"]
        ):
            lines = infra_disk.summarize_reclaim_guidance(candidates)

        self.assertIn("Largest paths under /var/cache/apt:", lines)
        self.assertIn("APT cleanup hint: sudo apt-get clean", lines)
        self.assertIn("Largest paths under /home/ubuntu/.cache:", lines)
        self.assertIn("Cache review hint: focus on package/build caches before deleting app state", lines)
        self.assertIn("Largest paths under /home/ubuntu/.gradle/caches:", lines)
        self.assertIn("Largest paths under /home/ubuntu/.gradle/wrapper/dists:", lines)
        self.assertIn("Home cache cleanup helper available for allowlisted user-owned caches:", lines)
        self.assertIn(
            "- Review: python3 tools/infra_home_cache_cleanup.py --path /home/ubuntu/.gradle/caches --path /home/ubuntu/.gradle/wrapper/dists",
            lines,
        )
        self.assertIn("Stale /tmp entries older than 24h:", lines)
        self.assertIn("Cleanup helper available", lines)
        self.assertIn("Largest paths under /var/log/journal:", lines)
        self.assertIn("Journal review hint: journalctl --disk-usage", lines)
        self.assertIn("Journal vacuum hint: sudo journalctl --vacuum-time=7d", lines)

    def test_collect_reclaim_candidates_includes_allowlisted_home_caches(self) -> None:
        sizes = {
            Path("/var/cache/apt"): 628 * 1024 * 1024,
            Path("/home/ubuntu/.cache"): 366 * 1024 * 1024,
        }
        home_candidates = [
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.gradle/caches"),
                size_bytes=1900 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 9, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="Gradle dependency cache",
            )
        ]

        with mock.patch.object(infra_disk, "path_usage_bytes", side_effect=lambda path: sizes.get(path)), mock.patch.object(
            infra_disk, "scan_home_cache_cleanup_candidates", return_value=home_candidates
        ):
            candidates = infra_disk.collect_reclaim_candidates()

        self.assertEqual(
            [str(path) for _, path, _ in candidates[:3]],
            ["/home/ubuntu/.gradle/caches", "/var/cache/apt", "/home/ubuntu/.cache"],
        )

    def test_build_disk_usage_report_skips_empty_reclaim_heading(self) -> None:
        with mock.patch.object(
            infra_disk,
            "run_cmd",
            side_effect=[
                "19G 19G 153M 100% /",
                "15% /",
                "18G /\n9.3G /usr\n7.1G /home",
            ],
        ), mock.patch.object(
            infra_disk, "collect_reclaim_candidates", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_home_hotspots", return_value=[]
        ), mock.patch.object(
            infra_disk, "current_root_usage_bytes", return_value=(19 * 1024**3, 19 * 1024**3, 153 * 1024**2, 100, "/")
        ), mock.patch.object(
            infra_disk, "summarize_home_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_protected_home_paths", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_deleted_open_files", return_value=["No deleted-but-open files detected"]
        ):
            lines = infra_disk.build_disk_usage_report()

        self.assertIn("CRITICAL: Root filesystem usage is 100% (>90%)", lines)
        self.assertNotIn("Reclaim candidates (review before cleanup):", lines)
        self.assertIn("No deleted-but-open files detected", lines)

    def test_build_disk_usage_report_includes_home_hotspots_when_pressure_is_high(self) -> None:
        with mock.patch.object(
            infra_disk,
            "run_cmd",
            side_effect=[
                "19G 19G 153M 100% /",
                "15% /",
                "18G /\n9.3G /usr\n7.1G /home",
            ],
        ), mock.patch.object(
            infra_disk, "collect_reclaim_candidates", return_value=[]
        ), mock.patch.object(
            infra_disk,
            "summarize_home_hotspots",
            return_value=[
                "Largest paths under /home/ubuntu (review-only):",
                "7.1G /home/ubuntu\n2.3G /home/ubuntu/.gradle",
                "Home review hint: prioritize build/package caches before SDKs or active workspaces",
            ],
        ), mock.patch.object(
            infra_disk, "current_root_usage_bytes", return_value=(19 * 1024**3, 19 * 1024**3, 153 * 1024**2, 100, "/")
        ), mock.patch.object(
            infra_disk, "summarize_home_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_protected_home_paths", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_deleted_open_files", return_value=["No deleted-but-open files detected"]
        ):
            lines = infra_disk.build_disk_usage_report()

        self.assertIn("Largest paths under /home/ubuntu (review-only):", lines)
        self.assertIn("7.1G /home/ubuntu\n2.3G /home/ubuntu/.gradle", lines)
        self.assertIn(
            "Home review hint: prioritize build/package caches before SDKs or active workspaces",
            lines,
        )

    def test_collect_protected_home_paths_sorts_largest_first(self) -> None:
        sizes = {
            Path("/home/ubuntu/.npm-global"): 1800 * 1024 * 1024,
            Path("/home/ubuntu/.local/share/pipx/venvs"): 482 * 1024 * 1024,
            Path("/home/ubuntu/.android-sdk"): 965 * 1024 * 1024,
        }

        with mock.patch.object(infra_disk, "path_usage_bytes", side_effect=lambda path: sizes.get(path)):
            candidates = infra_disk.collect_protected_home_paths()

        self.assertEqual(
            [str(path) for _, path, _ in candidates],
            [
                "/home/ubuntu/.npm-global",
                "/home/ubuntu/.android-sdk",
                "/home/ubuntu/.local/share/pipx/venvs",
            ],
        )

    def test_build_disk_usage_report_includes_protected_home_paths_when_pressure_is_high(self) -> None:
        with mock.patch.object(
            infra_disk,
            "run_cmd",
            side_effect=[
                "19G 19G 153M 100% /",
                "15% /",
                "18G /\n9.3G /usr\n7.1G /home",
            ],
        ), mock.patch.object(
            infra_disk, "collect_reclaim_candidates", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_home_hotspots", return_value=[]
        ), mock.patch.object(
            infra_disk, "current_root_usage_bytes", return_value=(19 * 1024**3, 19 * 1024**3, 153 * 1024**2, 100, "/")
        ), mock.patch.object(
            infra_disk, "summarize_home_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk,
            "summarize_protected_home_paths",
            return_value=[
                "Protected install roots under /home/ubuntu (manual review, not safe cache cleanup):",
                "- 1.8G /home/ubuntu/.npm-global (global npm packages; removing may break installed CLIs)",
            ],
        ), mock.patch.object(
            infra_disk, "summarize_deleted_open_files", return_value=["No deleted-but-open files detected"]
        ):
            lines = infra_disk.build_disk_usage_report()

        self.assertIn(
            "Protected install roots under /home/ubuntu (manual review, not safe cache cleanup):",
            lines,
        )
        self.assertIn(
            "- 1.8G /home/ubuntu/.npm-global (global npm packages; removing may break installed CLIs)",
            lines,
        )

    def test_summarize_home_cache_recovery_plan_distinguishes_relief_vs_alert_clear(self) -> None:
        candidates = [
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.gradle/caches"),
                size_bytes=1900 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 9, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="Gradle dependency cache",
            ),
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.gradle/wrapper/dists"),
                size_bytes=410 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 9, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="Gradle wrapper distributions",
            ),
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.cache/pip"),
                size_bytes=198 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 9, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="pip download cache",
            ),
        ]

        with mock.patch.object(infra_disk, "scan_home_cache_cleanup_candidates", return_value=candidates):
            lines = infra_disk.summarize_home_cache_recovery_plan(
                total_bytes=19 * 1024**3,
                used_bytes=19 * 1024**3,
                used_pct=100,
            )

        self.assertIn("Allowlisted home-cache recovery plan:", lines)
        self.assertIn("- Need about 1.9G reclaimed to reach <=90% on /", lines)
        self.assertTrue(any("Review bundle: python3 tools/infra_home_cache_cleanup.py --path /home/ubuntu/.gradle/caches" in line for line in lines))
        self.assertIn("- Need about 3.8G reclaimed to reach <=80% on /", lines)
        self.assertTrue(any("short by" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
