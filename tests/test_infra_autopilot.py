import datetime as dt
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

MODULE_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra-autopilot.py")
SPEC = importlib.util.spec_from_file_location("infra_autopilot", MODULE_PATH)
infra_autopilot = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(infra_autopilot)


class InfraAutopilotTests(unittest.TestCase):
    def test_summarize_external_ports_treats_ipv4_mapped_loopback_as_local_only(self) -> None:
        result = infra_autopilot.summarize_external_ports(
            "tcp [::ffff:127.0.0.1]:17564\nudp *:58627\ntcp 0.0.0.0:22"
        )

        self.assertIn("ALERT: Unexpected externally exposed listeners (1): udp/58627", result)
        self.assertNotIn("tcp/17564", result)

    def test_check_firewall_status_detects_ufw_outside_default_path(self) -> None:
        def fake_run_cmd(cmd: list[str], max_chars: int = 800) -> str:
            shell_cmd = cmd[-1]
            if 'command -v ufw' in shell_cmd:
                return '/usr/sbin/ufw'
            if 'sudo ufw status verbose' in shell_cmd:
                return 'Status: active'
            return 'n/a'

        with mock.patch.object(infra_autopilot, "run_cmd", side_effect=fake_run_cmd), mock.patch.object(
            infra_autopilot.shutil, "which", return_value=None
        ):
            result = infra_autopilot.check_firewall_status()

        self.assertIn("ufw: active", result)
        self.assertNotIn("WARN: ufw unavailable on host", result)

    def test_execute_task_security_audit_includes_unexpected_listener_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            art_dir = Path(tmpdir)
            with mock.patch.object(infra_autopilot, "ART_DIR", art_dir), mock.patch.object(
                infra_autopilot, "run_cmd",
                side_effect=[
                    "tcp 0.0.0.0:22\nudp *:58627",
                    "SSH config unavailable",
                ],
            ), mock.patch.object(
                infra_autopilot, "inspect_unexpected_listener_details",
                return_value="ALERT: Detailed inspection for unexpected listeners (1): udp/58627\nudp/58627 owner(s): openclaw-gateway",
            ), mock.patch.object(
                infra_autopilot, "inspect_mdns_exposure", return_value="No external mDNS listener detected"
            ), mock.patch.object(
                infra_autopilot, "check_firewall_status", return_value="Firewall nominal"
            ), mock.patch.object(
                infra_autopilot, "get_auth_sample", return_value=("Invalid user root from 1.2.3.4", "auth.log")
            ):
                artifact, _ = infra_autopilot.execute_task(
                    "Run security audit: Check for open ports, SSH config, failed logins.",
                    145,
                )

            content = artifact.read_text(encoding="utf-8")

        self.assertIn("## Unexpected Listener Details", content)
        self.assertIn("udp/58627 owner(s): openclaw-gateway", content)
        self.assertIn("## Auth Source Summary", content)

    def test_score_task_from_status_ignores_stale_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "20260310T153953Z-infra-status.md"
            artifact.write_text("CRITICAL: Root filesystem usage is 100%", encoding="utf-8")
            stale_now = dt.datetime(2026, 3, 11, 11, 30, tzinfo=dt.timezone.utc)
            stale_mtime = (stale_now - dt.timedelta(hours=20)).timestamp()
            artifact.touch()
            Path(artifact).chmod(0o600)
            os.utime(artifact, (stale_mtime, stale_mtime))

            score, reason = infra_autopilot.score_task_from_status(
                "Monitor disk usage: Alert if >80%.",
                artifact,
            )

        self.assertEqual(score, 0)
        self.assertIn("is stale", reason)

    def test_score_task_from_artifact_ignores_listener_detail_alert_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "security.md"
            artifact.write_text(
                "ALERT: Unexpected externally exposed listeners (1): udp/58627\n"
                "ALERT: Detailed inspection for unexpected listeners (1): udp/58627\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_artifact(
                "Run security audit: Check for open ports, SSH config, failed logins.",
                artifact,
            )

        self.assertEqual(60, score)
        self.assertEqual("ALERT: Unexpected externally exposed listeners (1): udp/58627", reason)

    def test_score_task_from_status_counts_partial_ssh_hardening_visibility_for_security(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "infra-status.md"
            artifact.write_text(
                "WARN: effective SSH hardening is only partially visible; some key settings are not explicitly set\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_status(
                "Run security audit: Check for open ports, SSH config, failed logins.",
                artifact,
            )

        self.assertEqual(20, score)
        self.assertIn("latest infra-status shows incomplete SSH hardening visibility", reason)

    def test_score_task_from_status_counts_explicit_ssh_forwarding_risks_for_security(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "infra-status.md"
            artifact.write_text(
                "RISK: AllowTcpForwarding enabled\n"
                "RISK: AllowAgentForwarding enabled\n"
                "WARN: MaxAuthTries is high (6)\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_status(
                "Run security audit: Check for open ports, SSH config, failed logins.",
                artifact,
            )

        self.assertEqual(80, score)
        self.assertIn("latest infra-status shows SSH tcp forwarding enabled", reason)
        self.assertIn("latest infra-status shows SSH agent forwarding enabled", reason)
        self.assertIn("latest infra-status shows high SSH MaxAuthTries", reason)

    def test_score_task_from_status_counts_blocked_ufw_visibility_for_security(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "infra-status.md"
            artifact.write_text(
                "WARN: ufw installed but status visibility is blocked by current privileges\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_status(
                "Run security audit: Check for open ports, SSH config, failed logins.",
                artifact,
            )

        self.assertEqual(40, score)
        self.assertIn("latest infra-status shows blocked ufw visibility", reason)

    def test_score_task_from_status_keeps_healthy_pending_updates_low_priority(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "infra-status.md"
            artifact.write_text(
                "2 pending updates\n"
                "INFO: auto-updates enabled (APT::Periodic::Update-Package-Lists=1, "
                "APT::Periodic::Unattended-Upgrade=1)\n"
                "INFO: unattended-upgrades last completed at 2026-03-13 01:05 UTC (1h ago): "
                "No packages found that can be upgraded unattended and no pending auto-removals\n"
                "INFO: pending updates should clear on the next successful unattended-upgrades run\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_status(
                "Check for system updates daily and report count.",
                artifact,
            )

        self.assertEqual(5, score)
        self.assertIn("awaiting the next unattended-upgrades window", reason)

    def test_score_task_from_status_prioritizes_incomplete_unattended_updates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "infra-status.md"
            artifact.write_text(
                "4 pending updates\n"
                "INFO: auto-updates enabled (APT::Periodic::Update-Package-Lists=1, "
                "APT::Periodic::Unattended-Upgrade=1)\n"
                "WARN: unattended-upgrades last started at 2026-03-12 14:35 UTC (12h ago) but no completion was logged\n"
                "RISK: pending updates remain after an incomplete unattended-upgrades run\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_status(
                "Check for system updates daily and report count.",
                artifact,
            )

        self.assertEqual(70, score)
        self.assertIn("pending updates after an incomplete unattended-upgrades run", reason)

    def test_select_task_prefers_non_stale_security_risk_over_stale_disk_status(self) -> None:
        tasks = [
            "Run security audit: Check for open ports, SSH config, failed logins.",
            "Monitor disk usage: Alert if >80%.",
        ]
        state = {"cursor": 0}
        stale_status = Path("/tmp/stale-status.md")

        with mock.patch.object(
            infra_autopilot,
            "latest_status_artifact",
            return_value=stale_status,
        ), mock.patch.object(
            infra_autopilot,
            "latest_artifact_for_task",
            side_effect=lambda task: Path("/tmp/security.md") if "security audit" in task else Path("/tmp/disk.md"),
        ), mock.patch.object(
            infra_autopilot,
            "score_task_from_status",
            side_effect=lambda task, artifact: (0, "stale status") if artifact == stale_status else (0, "no status"),
        ), mock.patch.object(
            infra_autopilot,
            "score_task_from_artifact",
            side_effect=lambda task, artifact: (85, "unexpected udp/5353 listener still exposed")
            if "security audit" in task
            else (0, "latest artifact has no active risk markers"),
        ):
            task, reason = infra_autopilot.select_task(tasks, state)

        self.assertEqual(tasks[0], task)
        self.assertEqual("risk-based priority: unexpected udp/5353 listener still exposed", reason)


if __name__ == "__main__":
    unittest.main()
