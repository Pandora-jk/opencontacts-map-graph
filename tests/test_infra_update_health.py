import datetime as dt
import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

MODULE_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra_update_health.py")
SPEC = importlib.util.spec_from_file_location("infra_update_health", MODULE_PATH)
infra_update_health = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(infra_update_health)


class InfraUpdateHealthTests(unittest.TestCase):
    def test_parse_latest_unattended_run_marks_incomplete_last_run(self) -> None:
        log_text = "\n".join(
            [
                "2026-03-12 06:43:47,035 INFO Starting unattended upgrades script",
                "2026-03-12 06:43:57,106 INFO All upgrades installed",
                "2026-03-12 14:35:25,283 INFO Starting unattended upgrades script",
                "2026-03-12 14:35:25,283 INFO Allowed origins are: o=Ubuntu,a=noble-security",
            ]
        )

        latest = infra_update_health.parse_latest_unattended_run(log_text)

        self.assertEqual("incomplete", latest["status"])
        self.assertEqual(dt.datetime(2026, 3, 12, 14, 35, 25, tzinfo=dt.UTC), latest["started_at"])
        self.assertIsNone(latest["completed_at"])

    def test_render_auto_update_health_flags_incomplete_run_with_pending_updates(self) -> None:
        now = dt.datetime(2026, 3, 13, 2, 30, tzinfo=dt.UTC)
        config = {
            "enabled": True,
            "settings": {
                "APT::Periodic::Update-Package-Lists": "1",
                "APT::Periodic::Unattended-Upgrade": "1",
            },
        }
        latest_run = {
            "status": "incomplete",
            "started_at": dt.datetime(2026, 3, 12, 14, 35, 25, tzinfo=dt.UTC),
            "completed_at": None,
            "completion_line": "",
        }

        result = infra_update_health.render_auto_update_health(
            4,
            now=now,
            config=config,
            latest_run=latest_run,
        )

        self.assertIn("4 pending updates", result)
        self.assertIn("INFO: auto-updates enabled", result)
        self.assertIn("WARN: unattended-upgrades last started at 2026-03-12 14:35 UTC", result)
        self.assertIn("RISK: pending updates remain after an incomplete unattended-upgrades run", result)

    def test_render_auto_update_health_keeps_recent_pending_updates_informational(self) -> None:
        now = dt.datetime(2026, 3, 13, 2, 30, tzinfo=dt.UTC)
        config = {
            "enabled": True,
            "settings": {
                "APT::Periodic::Update-Package-Lists": "1",
                "APT::Periodic::Unattended-Upgrade": "1",
            },
        }
        latest_run = {
            "status": "completed",
            "started_at": dt.datetime(2026, 3, 13, 1, 0, tzinfo=dt.UTC),
            "completed_at": dt.datetime(2026, 3, 13, 1, 5, tzinfo=dt.UTC),
            "completion_line": "No packages found that can be upgraded unattended and no pending auto-removals",
        }

        result = infra_update_health.render_auto_update_health(
            2,
            now=now,
            config=config,
            latest_run=latest_run,
        )

        self.assertIn("2 pending updates", result)
        self.assertIn("INFO: unattended-upgrades last completed at 2026-03-13 01:05 UTC", result)
        self.assertIn("INFO: pending updates should clear on the next successful unattended-upgrades run", result)
        self.assertNotIn("RISK: pending updates remain", result)

    def test_render_auto_update_health_downgrades_incomplete_run_when_updates_are_clear(self) -> None:
        now = dt.datetime(2026, 3, 13, 2, 30, tzinfo=dt.UTC)
        config = {
            "enabled": True,
            "settings": {
                "APT::Periodic::Update-Package-Lists": "1",
                "APT::Periodic::Unattended-Upgrade": "1",
            },
        }
        latest_run = {
            "status": "incomplete",
            "started_at": dt.datetime(2026, 3, 12, 14, 35, 25, tzinfo=dt.UTC),
            "completed_at": None,
            "completion_line": "",
        }

        result = infra_update_health.render_auto_update_health(
            0,
            now=now,
            config=config,
            latest_run=latest_run,
        )

        self.assertIn("No pending updates", result)
        self.assertIn("INFO: unattended-upgrades last started at 2026-03-12 14:35 UTC", result)
        self.assertIn("but no completion was logged; no pending updates remain", result)
        self.assertNotIn("WARN: unattended-upgrades last started", result)


if __name__ == "__main__":
    unittest.main()
