import unittest
from pathlib import Path
from unittest import mock

import sys

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

import infra_disk


class InfraDiskTests(unittest.TestCase):
    def test_collect_reclaim_candidates_sorts_largest_first(self) -> None:
        sizes = {
            Path("/tmp"): 220 * 1024 * 1024,
            Path("/var/cache/apt"): 628 * 1024 * 1024,
            Path("/var/log/journal"): 143 * 1024 * 1024,
            Path("/home/ubuntu/.cache"): 366 * 1024 * 1024,
        }

        with mock.patch.object(infra_disk, "path_usage_bytes", side_effect=lambda path: sizes.get(path)):
            candidates = infra_disk.collect_reclaim_candidates()

        self.assertEqual(
            [str(path) for _, path, _ in candidates],
            ["/var/cache/apt", "/home/ubuntu/.cache", "/tmp", "/var/log/journal"],
        )

    def test_summarize_reclaim_guidance_adds_hotspots_and_hints(self) -> None:
        candidates = [
            (628 * 1024 * 1024, Path("/var/cache/apt"), "APT package cache"),
            (366 * 1024 * 1024, Path("/home/ubuntu/.cache"), "user cache"),
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
        self.assertIn("Stale /tmp entries older than 24h:", lines)
        self.assertIn("Cleanup helper available", lines)
        self.assertIn("Largest paths under /var/log/journal:", lines)
        self.assertIn("Journal review hint: journalctl --disk-usage", lines)
        self.assertIn("Journal vacuum hint: sudo journalctl --vacuum-time=7d", lines)

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
            infra_disk, "summarize_deleted_open_files", return_value=["No deleted-but-open files detected"]
        ):
            lines = infra_disk.build_disk_usage_report()

        self.assertIn("CRITICAL: Root filesystem usage is 100% (>90%)", lines)
        self.assertNotIn("Reclaim candidates (review before cleanup):", lines)
        self.assertIn("No deleted-but-open files detected", lines)


if __name__ == "__main__":
    unittest.main()
