import unittest
import datetime as dt
from pathlib import Path
from unittest import mock

import sys

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

import infra_disk
import infra_home_cache_cleanup
import infra_workspace_cache_cleanup
import infra_workspace_log_cleanup


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
        }

        with mock.patch.object(infra_disk, "path_usage_bytes", side_effect=lambda path: sizes.get(path)), mock.patch.object(
            infra_disk, "scan_home_cache_cleanup_candidates", return_value=[]
        ), mock.patch.object(
            infra_disk, "scan_workspace_cache_cleanup_candidates", return_value=[]
        ), mock.patch.object(
            infra_disk, "scan_workspace_log_cleanup_candidates", return_value=[]
        ):
            candidates = infra_disk.collect_reclaim_candidates()

        self.assertEqual(
            [str(path) for _, path, _ in candidates],
            ["/var/cache/apt", "/tmp", "/var/log/journal"],
        )

    def test_summarize_reclaim_guidance_adds_hotspots_and_hints(self) -> None:
        candidates = [
            (628 * 1024 * 1024, Path("/var/cache/apt"), "APT package cache"),
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
            (
                1700 * 1024,
                Path("/home/ubuntu/.openclaw/workspace/.gradle"),
                "workspace Gradle cache",
            ),
            (
                6 * 1024 * 1024,
                Path("/home/ubuntu/.openclaw/workspace/logs/night-infra.log"),
                "generated workspace log",
            ),
        ]

        def fake_hotspots(path: Path) -> list[str]:
            return [f"Largest paths under {path}:", "sample output"]

        with mock.patch.object(infra_disk, "summarize_hotspots", side_effect=fake_hotspots), mock.patch.object(
            infra_disk, "summarize_stale_tmp_entries", return_value=["Stale /tmp entries older than 24h:", "- 913M /tmp/gradle-home"]
        ), mock.patch.object(
            infra_disk, "summarize_tmp_cleanup_helper", return_value=["Cleanup helper available"]
        ), mock.patch.object(
            infra_disk,
            "scan_home_cache_cleanup_candidates",
            return_value=[
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
            ],
        ), mock.patch.object(
            infra_disk,
            "scan_workspace_cache_cleanup_candidates",
            return_value=[
                infra_workspace_cache_cleanup.CleanupCandidate(
                    path=Path("/home/ubuntu/.openclaw/workspace/.gradle"),
                    size_bytes=1700 * 1024,
                    mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                    owner="ubuntu",
                    note="workspace Gradle cache",
                ),
            ],
        ), mock.patch.object(
            infra_disk,
            "scan_workspace_log_cleanup_candidates",
            return_value=[
                infra_workspace_log_cleanup.CleanupCandidate(
                    path=Path("/home/ubuntu/.openclaw/workspace/logs/night-infra.log"),
                    size_bytes=6 * 1024 * 1024,
                    mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                    owner="ubuntu",
                    note="generated workspace log",
                ),
            ],
        ):
            lines = infra_disk.summarize_reclaim_guidance(candidates)

        self.assertIn("Largest paths under /var/cache/apt:", lines)
        self.assertIn("APT cleanup hint: sudo apt-get clean", lines)
        self.assertIn("Largest paths under /home/ubuntu/.gradle/caches:", lines)
        self.assertIn("Largest paths under /home/ubuntu/.gradle/wrapper/dists:", lines)
        self.assertIn("Home cache cleanup helper available for allowlisted user-owned caches:", lines)
        self.assertIn(
            "- Review: python3 tools/infra_home_cache_cleanup.py --path /home/ubuntu/.gradle/caches --path /home/ubuntu/.gradle/wrapper/dists",
            lines,
        )
        self.assertIn("Stale /tmp entries older than 24h:", lines)
        self.assertIn("Cleanup helper available", lines)
        self.assertIn("Workspace cache cleanup helper available for repo-local caches:", lines)
        self.assertIn(
            "- Review: python3 tools/infra_workspace_cache_cleanup.py --path /home/ubuntu/.openclaw/workspace/.gradle",
            lines,
        )
        self.assertIn(
            "- Apply: python3 tools/infra_workspace_cache_cleanup.py --apply --path /home/ubuntu/.openclaw/workspace/.gradle",
            lines,
        )
        self.assertIn("Workspace log cleanup helper available for repo-local generated logs:", lines)
        self.assertIn(
            "- Review: python3 tools/infra_workspace_log_cleanup.py --path /home/ubuntu/.openclaw/workspace/logs/night-infra.log",
            lines,
        )
        self.assertIn(
            "- Apply: python3 tools/infra_workspace_log_cleanup.py --apply --path /home/ubuntu/.openclaw/workspace/logs/night-infra.log",
            lines,
        )
        self.assertIn("Largest paths under /var/log/journal:", lines)
        self.assertIn("Journal review hint: journalctl --disk-usage", lines)
        self.assertIn("Journal vacuum hint: sudo journalctl --vacuum-time=7d", lines)

    def test_summarize_home_cache_cleanup_helper_hides_apply_when_session_cannot_write(self) -> None:
        blocked_candidates = [
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.gradle/caches"),
                size_bytes=1900 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 9, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="Gradle dependency cache",
                apply_blocked_reason="current session cannot write inside /home/ubuntu/.gradle/caches (Permission denied)",
            ),
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.gradle/wrapper/dists"),
                size_bytes=410 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 9, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="Gradle wrapper distributions",
                apply_blocked_reason="current session cannot write inside /home/ubuntu/.gradle/wrapper/dists (Permission denied)",
            ),
        ]

        with mock.patch.object(infra_disk, "scan_home_cache_cleanup_candidates", return_value=blocked_candidates):
            lines = infra_disk.summarize_home_cache_cleanup_helper(
                [Path("/home/ubuntu/.gradle/caches"), Path("/home/ubuntu/.gradle/wrapper/dists")]
            )

        self.assertIn("Home cache cleanup helper available for allowlisted user-owned caches:", lines)
        self.assertIn(
            "- Review: python3 tools/infra_home_cache_cleanup.py --path /home/ubuntu/.gradle/caches --path /home/ubuntu/.gradle/wrapper/dists",
            lines,
        )
        self.assertNotIn(
            "- Apply: python3 tools/infra_home_cache_cleanup.py --apply --path /home/ubuntu/.gradle/caches --path /home/ubuntu/.gradle/wrapper/dists",
            lines,
        )
        self.assertIn("Home cache apply blocked from current session:", lines)
        self.assertTrue(any("/home/ubuntu/.gradle/caches" in line for line in lines))

    def test_collect_reclaim_candidates_includes_allowlisted_home_caches(self) -> None:
        sizes = {
            Path("/var/cache/apt"): 628 * 1024 * 1024,
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
        ), mock.patch.object(
            infra_disk, "scan_workspace_cache_cleanup_candidates", return_value=[]
        ), mock.patch.object(
            infra_disk, "scan_workspace_log_cleanup_candidates", return_value=[]
        ):
            candidates = infra_disk.collect_reclaim_candidates()

        self.assertEqual(
            [str(path) for _, path, _ in candidates[:2]],
            ["/home/ubuntu/.gradle/caches", "/var/cache/apt"],
        )

    def test_collect_reclaim_candidates_includes_workspace_caches(self) -> None:
        sizes = {
            Path("/var/cache/apt"): 628 * 1024 * 1024,
        }
        workspace_candidates = [
            infra_workspace_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.openclaw/workspace/.gradle"),
                size_bytes=1700 * 1024,
                mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="workspace Gradle cache",
            )
        ]

        with mock.patch.object(infra_disk, "path_usage_bytes", side_effect=lambda path: sizes.get(path)), mock.patch.object(
            infra_disk, "scan_home_cache_cleanup_candidates", return_value=[]
        ), mock.patch.object(
            infra_disk, "scan_workspace_cache_cleanup_candidates", return_value=workspace_candidates
        ), mock.patch.object(
            infra_disk, "scan_workspace_log_cleanup_candidates", return_value=[]
        ):
            candidates = infra_disk.collect_reclaim_candidates()

        self.assertEqual(
            [str(path) for _, path, _ in candidates[:2]],
            ["/var/cache/apt", "/home/ubuntu/.openclaw/workspace/.gradle"],
        )

    def test_collect_reclaim_candidates_includes_workspace_logs(self) -> None:
        sizes = {
            Path("/var/cache/apt"): 628 * 1024 * 1024,
        }
        workspace_log_candidates = [
            infra_workspace_log_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.openclaw/workspace/logs/night-infra.log"),
                size_bytes=6 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="generated workspace log",
            )
        ]

        with mock.patch.object(infra_disk, "path_usage_bytes", side_effect=lambda path: sizes.get(path)), mock.patch.object(
            infra_disk, "scan_home_cache_cleanup_candidates", return_value=[]
        ), mock.patch.object(
            infra_disk, "scan_workspace_cache_cleanup_candidates", return_value=[]
        ), mock.patch.object(
            infra_disk, "scan_workspace_log_cleanup_candidates", return_value=workspace_log_candidates
        ):
            candidates = infra_disk.collect_reclaim_candidates()

        self.assertEqual(
            [str(path) for _, path, _ in candidates[:2]],
            ["/var/cache/apt", "/home/ubuntu/.openclaw/workspace/logs/night-infra.log"],
        )

    def test_summarize_review_only_cache_roots_reports_hotspots_without_cleanup_command(self) -> None:
        def fake_path_usage(path: Path) -> int | None:
            if path == Path("/home/ubuntu/.cache"):
                return 366 * 1024 * 1024
            return None

        with mock.patch.object(infra_disk, "path_usage_bytes", side_effect=fake_path_usage), mock.patch.object(
            infra_disk,
            "summarize_hotspots",
            return_value=["Largest paths under /home/ubuntu/.cache:", "sample output"],
        ):
            lines = infra_disk.summarize_review_only_cache_roots()

        self.assertIn("Review-only cache roots (not safe broad cleanup targets):", lines)
        self.assertIn(
            "- 366M /home/ubuntu/.cache (shared cache root; review allowlisted build/package caches before deleting app state)",
            lines,
        )
        self.assertIn("Largest paths under /home/ubuntu/.cache:", lines)
        self.assertIn("Cache review hint: focus on package/build caches before deleting app state", lines)

    def test_build_disk_usage_report_skips_empty_reclaim_heading(self) -> None:
        with mock.patch.object(
            infra_disk,
            "run_cmd",
            side_effect=[
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
            infra_disk, "summarize_current_session_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_log_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_home_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_review_only_cache_roots", return_value=[]
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
            infra_disk, "summarize_current_session_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_log_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_home_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_review_only_cache_roots", return_value=[]
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

    def test_build_disk_usage_report_uses_single_root_snapshot_for_summary_and_plans(self) -> None:
        root_snapshot = (20401094656, 20246827008, 154267648, 99, "/")

        with mock.patch.object(
            infra_disk,
            "run_cmd",
            side_effect=[
                "15% /",
                "18G /\n9.3G /usr\n7.1G /home",
            ],
        ), mock.patch.object(
            infra_disk, "collect_reclaim_candidates", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_home_hotspots", return_value=[]
        ), mock.patch.object(
            infra_disk, "current_root_usage_bytes", return_value=root_snapshot
        ), mock.patch.object(
            infra_disk, "summarize_current_session_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_log_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_home_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_host_level_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_review_only_cache_roots", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_protected_home_paths", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_deleted_open_files", return_value=["No deleted-but-open files detected"]
        ):
            lines = infra_disk.build_disk_usage_report()

        self.assertIn("Root usage: /: 99% used (19G/19G, avail 147M)", lines)
        self.assertIn("CRITICAL: Root filesystem usage is 99% (>90%)", lines)

    def test_summarize_current_session_recovery_plan_reports_shortfall_when_tmp_cleanup_insufficient(self) -> None:
        tmp_candidates = [
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path("/tmp/jiti"),
                size_bytes=14 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 5, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="tmp dir",
            ),
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path("/tmp/oc-patch-test"),
                size_bytes=8 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 5, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="tmp dir",
            ),
        ]

        with mock.patch.object(infra_disk, "scan_cleanup_candidates", return_value=tmp_candidates):
            lines = infra_disk.summarize_current_session_recovery_plan(
                total_bytes=19 * 1024**3,
                used_bytes=19 * 1024**3,
                used_pct=100,
            )

        self.assertIn("Current-session writable recovery plan (stale /tmp only):", lines)
        self.assertIn("- Need about 1.9G reclaimed to reach <=90% on /", lines)
        self.assertIn("  All writable stale /tmp paths total 22M across 2 path(s); short by 1.9G", lines)
        self.assertIn("  Review top stale /tmp paths: python3 tools/infra_tmp_cleanup.py --limit 2", lines)
        self.assertIn("  Host-level reclaim is still required after current-session cleanup", lines)

    def test_summarize_current_session_recovery_plan_mentions_omitted_tmp_paths_when_scan_is_long(self) -> None:
        tmp_candidates = [
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path(f"/tmp/candidate-{index}"),
                size_bytes=(10 - index) * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 5, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="tmp dir",
            )
            for index in range(7)
        ]

        with mock.patch.object(infra_disk, "scan_cleanup_candidates", return_value=tmp_candidates):
            lines = infra_disk.summarize_current_session_recovery_plan(
                total_bytes=19 * 1024**3,
                used_bytes=19 * 1024**3,
                used_pct=100,
            )

        self.assertIn("  Review top stale /tmp paths: python3 tools/infra_tmp_cleanup.py --limit 5", lines)
        self.assertIn(
            "  Current scan found 7 writable stale /tmp path(s); rerun the helper with a higher --limit or targeted --path values before cleanup",
            lines,
        )

    def test_summarize_current_session_recovery_plan_builds_apply_bundle_when_tmp_cleanup_can_help(self) -> None:
        tmp_candidates = [
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path("/tmp/jiti"),
                size_bytes=120 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 5, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="tmp dir",
            ),
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path("/tmp/oc-patch-test"),
                size_bytes=40 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 5, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="tmp dir",
            ),
        ]

        with mock.patch.object(infra_disk, "scan_cleanup_candidates", return_value=tmp_candidates):
            lines = infra_disk.summarize_current_session_recovery_plan(
                total_bytes=1024 * 1024 * 1024,
                used_bytes=950 * 1024 * 1024,
                used_pct=93,
            )

        self.assertIn("- Need about 28M reclaimed to reach <=90% on /", lines)
        self.assertIn("  Writable stale /tmp paths can cover this with 120M across 1 path(s)", lines)
        self.assertIn(
            "  Apply bundle: python3 tools/infra_tmp_cleanup.py --apply --path /tmp/jiti",
            lines,
        )

    def test_summarize_workspace_cache_recovery_plan_reports_shortfall(self) -> None:
        candidates = [
            infra_workspace_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.openclaw/workspace/.gradle"),
                size_bytes=1700 * 1024,
                mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="workspace Gradle cache",
            ),
            infra_workspace_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.openclaw/workspace/tools/__pycache__"),
                size_bytes=316 * 1024,
                mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="Python bytecode cache",
            ),
        ]

        with mock.patch.object(infra_disk, "scan_workspace_cache_cleanup_candidates", return_value=candidates):
            lines = infra_disk.summarize_workspace_cache_recovery_plan(
                total_bytes=19 * 1024**3,
                used_bytes=19 * 1024**3,
                used_pct=100,
            )

        self.assertIn("Current-session writable workspace-cache plan:", lines)
        self.assertIn("- Need about 1.9G reclaimed to reach <=90% on /", lines)
        self.assertIn("  All workspace caches total 2.0M across 2 path(s); short by 1.9G", lines)
        self.assertIn(
            "  Review remaining workspace caches: python3 tools/infra_workspace_cache_cleanup.py --path /home/ubuntu/.openclaw/workspace/.gradle --path /home/ubuntu/.openclaw/workspace/tools/__pycache__",
            lines,
        )
        self.assertIn("  Host-level reclaim is still required after workspace-cache cleanup", lines)

    def test_summarize_workspace_cache_recovery_plan_builds_apply_bundle(self) -> None:
        candidates = [
            infra_workspace_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.openclaw/workspace/.gradle"),
                size_bytes=40 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="workspace Gradle cache",
            ),
            infra_workspace_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.openclaw/workspace/tools/__pycache__"),
                size_bytes=5 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="Python bytecode cache",
            ),
        ]

        with mock.patch.object(infra_disk, "scan_workspace_cache_cleanup_candidates", return_value=candidates):
            lines = infra_disk.summarize_workspace_cache_recovery_plan(
                total_bytes=1024 * 1024 * 1024,
                used_bytes=950 * 1024 * 1024,
                used_pct=93,
            )

        self.assertIn("- Need about 28M reclaimed to reach <=90% on /", lines)
        self.assertIn("  Workspace caches can cover this with 40M across 1 path(s)", lines)
        self.assertIn(
            "  Apply bundle: python3 tools/infra_workspace_cache_cleanup.py --apply --path /home/ubuntu/.openclaw/workspace/.gradle",
            lines,
        )

    def test_summarize_workspace_log_recovery_plan_reports_shortfall(self) -> None:
        candidates = [
            infra_workspace_log_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.openclaw/workspace/logs/night-infra.log"),
                size_bytes=6 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="generated workspace log",
            ),
            infra_workspace_log_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.openclaw/workspace/logs/night-coding.log"),
                size_bytes=2 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="generated workspace log",
            ),
        ]

        with mock.patch.object(infra_disk, "scan_workspace_log_cleanup_candidates", return_value=candidates):
            lines = infra_disk.summarize_workspace_log_recovery_plan(
                total_bytes=19 * 1024**3,
                used_bytes=19 * 1024**3,
                used_pct=100,
            )

        self.assertIn("Current-session writable workspace-log plan:", lines)
        self.assertIn("- Need about 1.9G reclaimed to reach <=90% on /", lines)
        self.assertIn("  All workspace logs total 8.0M across 2 path(s); short by 1.9G", lines)
        self.assertIn(
            "  Review remaining workspace logs: python3 tools/infra_workspace_log_cleanup.py --path /home/ubuntu/.openclaw/workspace/logs/night-infra.log --path /home/ubuntu/.openclaw/workspace/logs/night-coding.log",
            lines,
        )
        self.assertIn("  Host-level reclaim is still required after workspace-log cleanup", lines)

    def test_summarize_workspace_log_recovery_plan_builds_apply_bundle(self) -> None:
        candidates = [
            infra_workspace_log_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.openclaw/workspace/logs/night-infra.log"),
                size_bytes=40 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="generated workspace log",
            ),
            infra_workspace_log_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.openclaw/workspace/logs/night-coding.log"),
                size_bytes=5 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 10, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="generated workspace log",
            ),
        ]

        with mock.patch.object(infra_disk, "scan_workspace_log_cleanup_candidates", return_value=candidates):
            lines = infra_disk.summarize_workspace_log_recovery_plan(
                total_bytes=1024 * 1024 * 1024,
                used_bytes=950 * 1024 * 1024,
                used_pct=93,
            )

        self.assertIn("- Need about 28M reclaimed to reach <=90% on /", lines)
        self.assertIn("  Workspace logs can cover this with 40M across 1 path(s)", lines)
        self.assertIn(
            "  Apply bundle: python3 tools/infra_workspace_log_cleanup.py --apply --path /home/ubuntu/.openclaw/workspace/logs/night-infra.log",
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
            infra_disk, "summarize_current_session_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_log_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_home_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_review_only_cache_roots", return_value=[]
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

    def test_build_disk_usage_report_includes_review_only_cache_roots_when_pressure_is_high(self) -> None:
        with mock.patch.object(
            infra_disk,
            "run_cmd",
            side_effect=[
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
            infra_disk, "summarize_current_session_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_log_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_home_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk,
            "summarize_review_only_cache_roots",
            return_value=[
                "Review-only cache roots (not safe broad cleanup targets):",
                "- 366M /home/ubuntu/.cache (shared cache root; review allowlisted build/package caches before deleting app state)",
            ],
        ), mock.patch.object(
            infra_disk, "summarize_protected_home_paths", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_deleted_open_files", return_value=["No deleted-but-open files detected"]
        ):
            lines = infra_disk.build_disk_usage_report()

        self.assertIn("Review-only cache roots (not safe broad cleanup targets):", lines)
        self.assertIn(
            "- 366M /home/ubuntu/.cache (shared cache root; review allowlisted build/package caches before deleting app state)",
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

    def test_summarize_home_cache_recovery_plan_reports_apply_block_when_bundle_is_not_writable(self) -> None:
        candidates = [
            infra_home_cache_cleanup.CleanupCandidate(
                path=Path("/home/ubuntu/.gradle/caches"),
                size_bytes=2200 * 1024 * 1024,
                mtime=dt.datetime(2026, 3, 9, tzinfo=dt.timezone.utc),
                owner="ubuntu",
                note="Gradle dependency cache",
                apply_blocked_reason="current session cannot write inside /home/ubuntu/.gradle/caches (Permission denied)",
            ),
        ]

        with mock.patch.object(infra_disk, "scan_home_cache_cleanup_candidates", return_value=candidates):
            lines = infra_disk.summarize_home_cache_recovery_plan(
                total_bytes=19 * 1024**3,
                used_bytes=19 * 1024**3,
                used_pct=100,
            )

        self.assertIn("Allowlisted home-cache recovery plan:", lines)
        self.assertTrue(any("Review bundle: python3 tools/infra_home_cache_cleanup.py --path /home/ubuntu/.gradle/caches" in line for line in lines))
        self.assertTrue(any("Apply blocked from current session" in line for line in lines))
        self.assertFalse(any("Apply bundle:" in line for line in lines))

    def test_summarize_host_level_recovery_plan_quantifies_shortfall_and_commands(self) -> None:
        candidates = [
            (617 * 1024 * 1024, Path("/var/cache/apt"), "APT package cache"),
            (159 * 1024 * 1024, Path("/var/log/journal"), "systemd journals"),
            (1900 * 1024 * 1024, Path("/home/ubuntu/.gradle/caches"), "Gradle dependency cache"),
        ]

        lines = infra_disk.summarize_host_level_recovery_plan(
            total_bytes=19 * 1024**3,
            used_bytes=19 * 1024**3,
            used_pct=100,
            candidates=candidates,
        )

        self.assertIn("Host-level recovery plan (sudo required for host-owned caches/logs):", lines)
        self.assertIn("- Need about 1.9G reclaimed to reach <=90% on /", lines)
        self.assertTrue(any("All host-level caches/logs total 776M across 2 path(s); short by 1.1G" in line for line in lines))
        self.assertIn("  - /var/cache/apt: sudo apt-get clean", lines)
        self.assertIn("  - /var/log/journal: sudo journalctl --vacuum-time=7d", lines)
        self.assertIn("  Additional reclaim is still required after host-level cleanup", lines)

    def test_build_disk_usage_report_includes_host_level_recovery_plan_when_pressure_is_high(self) -> None:
        candidates = [
            (617 * 1024 * 1024, Path("/var/cache/apt"), "APT package cache"),
            (159 * 1024 * 1024, Path("/var/log/journal"), "systemd journals"),
        ]

        with mock.patch.object(
            infra_disk,
            "run_cmd",
            side_effect=[
                "15% /",
                "18G /\n9.3G /usr\n7.1G /home",
            ],
        ), mock.patch.object(
            infra_disk, "collect_reclaim_candidates", return_value=candidates
        ), mock.patch.object(
            infra_disk, "summarize_reclaim_guidance", return_value=[]
        ), mock.patch.object(
            infra_disk, "current_root_usage_bytes", return_value=(19 * 1024**3, 19 * 1024**3, 153 * 1024**2, 100, "/")
        ), mock.patch.object(
            infra_disk, "summarize_current_session_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_log_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_workspace_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_home_cache_recovery_plan", return_value=[]
        ), mock.patch.object(
            infra_disk,
            "summarize_host_level_recovery_plan",
            return_value=[
                "Host-level recovery plan (sudo required for host-owned caches/logs):",
                "- Need about 1.9G reclaimed to reach <=90% on /",
                "  - /var/cache/apt: sudo apt-get clean",
            ],
        ), mock.patch.object(
            infra_disk, "summarize_review_only_cache_roots", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_home_hotspots", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_protected_home_paths", return_value=[]
        ), mock.patch.object(
            infra_disk, "summarize_deleted_open_files", return_value=["No deleted-but-open files detected"]
        ):
            lines = infra_disk.build_disk_usage_report()

        self.assertIn("Host-level recovery plan (sudo required for host-owned caches/logs):", lines)
        self.assertIn("  - /var/cache/apt: sudo apt-get clean", lines)


if __name__ == "__main__":
    unittest.main()
