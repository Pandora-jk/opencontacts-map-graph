import datetime as dt
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

MODULE_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra_update_health.py")
SPEC = importlib.util.spec_from_file_location("infra_update_health", MODULE_PATH)
infra_update_health = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(infra_update_health)


class InfraUpdateHealthTests(unittest.TestCase):
    def test_load_systemd_unit_enablement_reports_enabled_disabled_masked_and_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            systemd_etc = root / "etc" / "systemd" / "system"
            unit_dir = root / "lib" / "systemd" / "system"
            wants_dir = systemd_etc / "timers.target.wants"
            wants_dir.mkdir(parents=True)
            unit_dir.mkdir(parents=True)

            enabled_unit = unit_dir / "apt-daily.timer"
            enabled_unit.write_text("[Timer]\n", encoding="utf-8")
            (wants_dir / "apt-daily.timer").symlink_to(enabled_unit)

            disabled_unit = unit_dir / "apt-daily-upgrade.timer"
            disabled_unit.write_text("[Timer]\n", encoding="utf-8")

            (systemd_etc / "apt-custom.timer").symlink_to("/dev/null")

            enabled = infra_update_health.load_systemd_unit_enablement(
                "apt-daily.timer",
                systemd_etc_dir=systemd_etc,
                unit_dirs=(unit_dir,),
            )
            disabled = infra_update_health.load_systemd_unit_enablement(
                "apt-daily-upgrade.timer",
                systemd_etc_dir=systemd_etc,
                unit_dirs=(unit_dir,),
            )
            masked = infra_update_health.load_systemd_unit_enablement(
                "apt-custom.timer",
                systemd_etc_dir=systemd_etc,
                unit_dirs=(unit_dir,),
            )
            missing = infra_update_health.load_systemd_unit_enablement(
                "apt-missing.timer",
                systemd_etc_dir=systemd_etc,
                unit_dirs=(unit_dir,),
            )

        self.assertEqual("enabled", enabled["status"])
        self.assertEqual(enabled_unit, enabled["unit_path"])
        self.assertEqual("disabled", disabled["status"])
        self.assertEqual(disabled_unit, disabled["unit_path"])
        self.assertEqual("masked", masked["status"])
        self.assertEqual(systemd_etc / "apt-custom.timer", masked["unit_path"])
        self.assertEqual("missing", missing["status"])
        self.assertIsNone(missing["unit_path"])

    def test_load_periodic_stamp_times_reads_known_stamp_mtimes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            periodic_dir = Path(tmpdir)
            update_stamp = periodic_dir / "update-stamp"
            upgrade_stamp = periodic_dir / "upgrade-stamp"
            update_stamp.touch()
            upgrade_stamp.touch()
            os.utime(update_stamp, (1710411900, 1710411900))
            os.utime(upgrade_stamp, (1710412200, 1710412200))

            stamps = infra_update_health.load_periodic_stamp_times(periodic_dir)

        self.assertEqual(dt.datetime.fromtimestamp(1710411900, tz=dt.UTC), stamps["update"])
        self.assertEqual(dt.datetime.fromtimestamp(1710412200, tz=dt.UTC), stamps["upgrade"])
        self.assertIsNone(stamps["unattended_upgrades"])

    def test_parse_apt_history_transactions_extracts_timestamps_and_commandline(self) -> None:
        transactions = infra_update_health.parse_apt_history_transactions(
            "\n".join(
                [
                    "Start-Date: 2026-03-14  13:06:05",
                    "Commandline: /usr/bin/unattended-upgrade",
                    "End-Date: 2026-03-14  13:10:15",
                    "",
                    "Start-Date: 2026-03-14  14:00:00",
                    "Commandline: apt-get upgrade -y",
                    "End-Date: 2026-03-14  14:00:10",
                ]
            )
        )

        self.assertEqual(2, len(transactions))
        self.assertEqual("/usr/bin/unattended-upgrade", transactions[0]["commandline"])
        self.assertEqual(dt.datetime(2026, 3, 14, 13, 6, 5, tzinfo=dt.UTC), transactions[0]["started_at"])
        self.assertEqual(dt.datetime(2026, 3, 14, 13, 10, 15, tzinfo=dt.UTC), transactions[0]["completed_at"])

    def test_parse_package_manager_processes_ignores_shutdown_helper_but_keeps_worker(self) -> None:
        processes = infra_update_health.parse_package_manager_processes(
            "\n".join(
                [
                    "740 369488 unattended-upgr /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal",
                    "812 1242 python3 /usr/bin/python3 /usr/bin/unattended-upgrade",
                    "920 301 dpkg /usr/bin/dpkg --configure -a",
                ]
            )
        )

        self.assertEqual(3, len(processes))
        self.assertFalse(processes[0]["active"])
        self.assertEqual("unattended-upgrade-shutdown", processes[0]["role"])
        self.assertTrue(processes[1]["active"])
        self.assertEqual("unattended-upgrade", processes[1]["role"])
        self.assertTrue(processes[2]["active"])
        self.assertEqual("dpkg", processes[2]["role"])

    def test_parse_upgradable_packages_extracts_unique_package_names(self) -> None:
        packages = infra_update_health.parse_upgradable_packages(
            [
                "linux-aws/noble-updates,noble-security 6.17.0-1009.9~24.04.2 amd64 [upgradable from: 6.17.0-1007.7~24.04.1]",
                "linux-image-aws/noble-updates,noble-security 6.17.0-1009.9~24.04.2 amd64 [upgradable from: 6.17.0-1007.7~24.04.1]",
                "linux-aws/noble-updates,noble-security 6.17.0-1009.9~24.04.2 amd64 [upgradable from: 6.17.0-1007.7~24.04.1]",
            ]
        )

        self.assertEqual(["linux-aws", "linux-image-aws"], packages)

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
            timer_statuses={
                "apt-daily.timer": {"unit": "apt-daily.timer", "status": "enabled"},
                "apt-daily-upgrade.timer": {"unit": "apt-daily-upgrade.timer", "status": "enabled"},
            },
            periodic_stamps={
                "update": None,
                "update_success": None,
                "download_upgradeable": None,
                "unattended_upgrades": None,
                "upgrade": None,
            },
            package_manager_processes=[],
        )

        self.assertIn("4 pending updates", result)
        self.assertIn("INFO: auto-updates enabled", result)
        self.assertIn("INFO: auto-update timers enabled at boot", result)
        self.assertIn("WARN: unattended-upgrades last started at 2026-03-12 14:35 UTC", result)
        self.assertIn(
            "RISK: unattended-upgrades appears stalled; last start was 2026-03-12 14:35 UTC",
            result,
        )
        self.assertNotIn("RISK: pending updates remain after an incomplete unattended-upgrades run", result)
        self.assertNotIn("WARN: pending updates detected but unattended-upgrades completion history is unavailable", result)

    def test_render_auto_update_health_uses_apt_history_to_suppress_false_stalled_risk(self) -> None:
        now = dt.datetime(2026, 3, 14, 16, 30, tzinfo=dt.UTC)
        config = {
            "enabled": True,
            "settings": {
                "APT::Periodic::Update-Package-Lists": "1",
                "APT::Periodic::Unattended-Upgrade": "1",
            },
        }
        latest_run = {
            "status": "incomplete",
            "started_at": dt.datetime(2026, 3, 14, 13, 6, 5, tzinfo=dt.UTC),
            "completed_at": None,
            "completion_line": "",
        }
        latest_history = {
            "commandline": "/usr/bin/unattended-upgrade",
            "started_at": dt.datetime(2026, 3, 14, 13, 6, 5, tzinfo=dt.UTC),
            "completed_at": dt.datetime(2026, 3, 14, 13, 10, 15, tzinfo=dt.UTC),
        }

        result = infra_update_health.render_auto_update_health(
            2,
            now=now,
            config=config,
            latest_run=latest_run,
            latest_history=latest_history,
            timer_statuses={
                "apt-daily.timer": {"unit": "apt-daily.timer", "status": "enabled"},
                "apt-daily-upgrade.timer": {"unit": "apt-daily-upgrade.timer", "status": "enabled"},
            },
            package_manager_processes=[],
        )

        self.assertIn("INFO: unattended-upgrades last completed at 2026-03-14 13:10 UTC", result)
        self.assertIn("apt history recorded a completed unattended-upgrade transaction", result)
        self.assertIn("INFO: pending updates should clear on the next successful unattended-upgrades run", result)
        self.assertNotIn("RISK: unattended-upgrades appears stalled;", result)
        self.assertNotIn("RISK: pending updates remain after an incomplete unattended-upgrades run", result)

    def test_render_auto_update_health_uses_periodic_completion_stamp_to_suppress_false_stalled_risk(self) -> None:
        now = dt.datetime(2026, 3, 14, 16, 30, tzinfo=dt.UTC)
        config = {
            "enabled": True,
            "settings": {
                "APT::Periodic::Update-Package-Lists": "1",
                "APT::Periodic::Unattended-Upgrade": "1",
            },
        }
        latest_run = {
            "status": "incomplete",
            "started_at": dt.datetime(2026, 3, 14, 13, 6, 5, tzinfo=dt.UTC),
            "completed_at": None,
            "completion_line": "",
        }

        result = infra_update_health.render_auto_update_health(
            2,
            now=now,
            config=config,
            latest_run=latest_run,
            latest_history={
                "commandline": "",
                "started_at": None,
                "completed_at": None,
            },
            timer_statuses={
                "apt-daily.timer": {"unit": "apt-daily.timer", "status": "enabled"},
                "apt-daily-upgrade.timer": {"unit": "apt-daily-upgrade.timer", "status": "enabled"},
            },
            periodic_stamps={
                "update": dt.datetime(2026, 3, 14, 13, 6, tzinfo=dt.UTC),
                "update_success": dt.datetime(2026, 3, 14, 13, 5, tzinfo=dt.UTC),
                "download_upgradeable": dt.datetime(2026, 3, 14, 13, 6, tzinfo=dt.UTC),
                "unattended_upgrades": dt.datetime(2026, 3, 14, 13, 10, tzinfo=dt.UTC),
                "upgrade": dt.datetime(2026, 3, 14, 13, 10, tzinfo=dt.UTC),
            },
            package_manager_processes=[],
        )

        self.assertIn("INFO: unattended-upgrades last completed at 2026-03-14 13:10 UTC", result)
        self.assertIn("apt periodic stamps recorded a newer unattended-upgrades/upgrade completion", result)
        self.assertIn("INFO: pending updates should clear on the next successful unattended-upgrades run", result)
        self.assertNotIn("RISK: unattended-upgrades appears stalled;", result)
        self.assertNotIn("WARN: apt periodic stamps recorded fresh update discovery", result)

    def test_render_auto_update_health_keeps_incomplete_run_non_stalled_when_worker_is_active(self) -> None:
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
            "started_at": dt.datetime(2026, 3, 13, 2, 5, tzinfo=dt.UTC),
            "completed_at": None,
            "completion_line": "",
        }

        result = infra_update_health.render_auto_update_health(
            4,
            now=now,
            config=config,
            latest_run=latest_run,
            timer_statuses={
                "apt-daily.timer": {"unit": "apt-daily.timer", "status": "enabled"},
                "apt-daily-upgrade.timer": {"unit": "apt-daily-upgrade.timer", "status": "enabled"},
            },
            periodic_stamps={
                "update": None,
                "update_success": None,
                "download_upgradeable": None,
                "unattended_upgrades": None,
                "upgrade": None,
            },
            package_manager_processes=[
                {
                    "pid": 812,
                    "elapsed_seconds": 1200,
                    "comm": "python3",
                    "args": "/usr/bin/python3 /usr/bin/unattended-upgrade",
                    "role": "unattended-upgrade",
                    "active": True,
                }
            ],
        )

        self.assertIn("INFO: package-manager activity: unattended-upgrade(pid=812, runtime=20m)", result)
        self.assertIn("RISK: pending updates remain after an incomplete unattended-upgrades run", result)
        self.assertNotIn("RISK: unattended-upgrades appears stalled;", result)

    def test_render_auto_update_health_flags_disabled_apt_timers_when_config_is_enabled(self) -> None:
        now = dt.datetime(2026, 3, 14, 16, 30, tzinfo=dt.UTC)
        config = {
            "enabled": True,
            "settings": {
                "APT::Periodic::Update-Package-Lists": "1",
                "APT::Periodic::Unattended-Upgrade": "1",
            },
        }
        latest_run = {
            "status": "completed",
            "started_at": dt.datetime(2026, 3, 14, 13, 6, 5, tzinfo=dt.UTC),
            "completed_at": dt.datetime(2026, 3, 14, 13, 10, 15, tzinfo=dt.UTC),
            "completion_line": "All upgrades installed",
        }

        result = infra_update_health.render_auto_update_health(
            0,
            now=now,
            config=config,
            latest_run=latest_run,
            timer_statuses={
                "apt-daily.timer": {
                    "unit": "apt-daily.timer",
                    "status": "disabled",
                    "unit_path": Path("/lib/systemd/system/apt-daily.timer"),
                },
                "apt-daily-upgrade.timer": {
                    "unit": "apt-daily-upgrade.timer",
                    "status": "masked",
                    "unit_path": Path("/etc/systemd/system/apt-daily-upgrade.timer"),
                },
            },
        )

        self.assertIn(
            "RISK: auto-update timers not enabled at boot: apt-daily.timer=disabled (/lib/systemd/system/apt-daily.timer); apt-daily-upgrade.timer=masked (/etc/systemd/system/apt-daily-upgrade.timer)",
            result,
        )

    def test_render_auto_update_health_reports_periodic_stamp_gap_for_incomplete_run(self) -> None:
        now = dt.datetime(2026, 3, 14, 17, 30, tzinfo=dt.UTC)
        config = {
            "enabled": True,
            "settings": {
                "APT::Periodic::Update-Package-Lists": "1",
                "APT::Periodic::Unattended-Upgrade": "1",
            },
        }
        latest_run = {
            "status": "incomplete",
            "started_at": dt.datetime(2026, 3, 14, 13, 6, 5, tzinfo=dt.UTC),
            "completed_at": None,
            "completion_line": "",
        }

        result = infra_update_health.render_auto_update_health(
            5,
            now=now,
            config=config,
            latest_run=latest_run,
            latest_history={
                "commandline": "",
                "started_at": None,
                "completed_at": None,
            },
            timer_statuses={
                "apt-daily.timer": {"unit": "apt-daily.timer", "status": "enabled"},
                "apt-daily-upgrade.timer": {"unit": "apt-daily-upgrade.timer", "status": "enabled"},
            },
            periodic_stamps={
                "update": dt.datetime(2026, 3, 14, 13, 6, tzinfo=dt.UTC),
                "update_success": dt.datetime(2026, 3, 14, 13, 5, tzinfo=dt.UTC),
                "download_upgradeable": dt.datetime(2026, 3, 14, 13, 6, tzinfo=dt.UTC),
                "unattended_upgrades": dt.datetime(2026, 3, 14, 6, 26, tzinfo=dt.UTC),
                "upgrade": dt.datetime(2026, 3, 14, 6, 26, tzinfo=dt.UTC),
            },
            package_manager_processes=[],
        )

        self.assertIn(
            "WARN: apt periodic stamps recorded fresh update discovery at 2026-03-14 13:06 UTC but no newer unattended-upgrades/upgrade completion stamp was written",
            result,
        )
        self.assertIn("latest completion stamp: 2026-03-14 06:26 UTC", result)
        self.assertIn("RISK: unattended-upgrades appears stalled; last start was 2026-03-14 13:06 UTC", result)

    def test_render_auto_update_health_flags_security_sensitive_kernel_updates(self) -> None:
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
            timer_statuses={
                "apt-daily.timer": {"unit": "apt-daily.timer", "status": "enabled"},
                "apt-daily-upgrade.timer": {"unit": "apt-daily-upgrade.timer", "status": "enabled"},
            },
            package_lines=[
                "linux-image-aws/noble-updates,noble-security 6.17.0-1009.9~24.04.2 amd64 [upgradable from: 6.17.0-1007.7~24.04.1]",
                "linux-libc-dev/noble-updates,noble-security 6.8.0-106.106 amd64 [upgradable from: 6.8.0-101.101]",
            ],
        )

        self.assertIn(
            "RISK: security-sensitive updates pending: kernel=linux-image-aws, linux-libc-dev",
            result,
        )
        self.assertIn("HARDENING: schedule a maintenance reboot after these updates land", result)

    def test_render_auto_update_health_reports_reboot_required_without_pending_updates(self) -> None:
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
            "completion_line": "All upgrades installed",
        }

        result = infra_update_health.render_auto_update_health(
            0,
            now=now,
            config=config,
            latest_run=latest_run,
            timer_statuses={
                "apt-daily.timer": {"unit": "apt-daily.timer", "status": "enabled"},
                "apt-daily-upgrade.timer": {"unit": "apt-daily-upgrade.timer", "status": "enabled"},
            },
            reboot_required=True,
        )

        self.assertIn("No pending updates", result)
        self.assertIn("WARN: reboot required by previously installed updates", result)

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
            timer_statuses={
                "apt-daily.timer": {"unit": "apt-daily.timer", "status": "enabled"},
                "apt-daily-upgrade.timer": {"unit": "apt-daily-upgrade.timer", "status": "enabled"},
            },
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
            timer_statuses={
                "apt-daily.timer": {"unit": "apt-daily.timer", "status": "enabled"},
                "apt-daily-upgrade.timer": {"unit": "apt-daily-upgrade.timer", "status": "enabled"},
            },
            periodic_stamps={
                "update": None,
                "update_success": None,
                "download_upgradeable": None,
                "unattended_upgrades": None,
                "upgrade": None,
            },
            package_manager_processes=[],
        )

        self.assertIn("No pending updates", result)
        self.assertIn("INFO: unattended-upgrades last started at 2026-03-12 14:35 UTC", result)
        self.assertIn("but no completion was logged; no pending updates remain", result)
        self.assertNotIn("WARN: unattended-upgrades last started", result)


if __name__ == "__main__":
    unittest.main()
