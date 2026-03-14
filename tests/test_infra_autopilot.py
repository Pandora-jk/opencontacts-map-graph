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
                infra_autopilot,
                "ssh_hardening_validation_status",
                return_value="ERROR: effective sshd policy drift detected\n- AllowStreamLocalForwarding=yes (expected no)",
            ), mock.patch.object(
                infra_autopilot,
                "ssh_ban_hardening_status",
                return_value="WARN: live config drift: /etc/fail2ban/jail.d/99-openclaw-sshd.local",
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
        self.assertIn("## SSH Hardening Validation", content)
        self.assertIn("AllowStreamLocalForwarding=yes (expected no)", content)
        self.assertIn("## Auth Source Summary", content)
        self.assertIn("## SSH Ban Hardening", content)
        self.assertIn("live config drift: /etc/fail2ban/jail.d/99-openclaw-sshd.local", content)

    def test_ssh_hardening_validation_status_reports_effective_drift(self) -> None:
        with mock.patch.object(
            infra_autopilot,
            "sshd_managed_config_status",
            return_value="managed config ready",
        ), mock.patch.object(
            infra_autopilot,
            "sshd_live_config_status",
            return_value="live config drift",
        ), mock.patch.object(
            infra_autopilot,
            "read_effective_sshd_settings",
            return_value=(
                {
                    "passwordauthentication": "no",
                    "permitrootlogin": "without-password",
                    "permitemptypasswords": "no",
                    "kbdinteractiveauthentication": "no",
                    "x11forwarding": "no",
                    "allowtcpforwarding": "no",
                    "allowagentforwarding": "no",
                    "allowstreamlocalforwarding": "yes",
                    "permittunnel": "no",
                    "maxauthtries": "3",
                    "logingracetime": "30",
                    "maxstartups": "10:30:60",
                },
                None,
            ),
        ):
            result = infra_autopilot.ssh_hardening_validation_status()

        self.assertIn("managed config ready", result)
        self.assertIn("live config drift", result)
        self.assertIn("ERROR: effective sshd policy drift detected", result)
        self.assertIn("AllowStreamLocalForwarding=yes (expected no)", result)

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

    def test_score_task_from_artifact_ignores_hardened_ufw_observability_gap_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "security.md"
            artifact.write_text(
                "\n".join(
                    [
                        "WARN: ufw installed but status visibility is blocked by current privileges",
                        "INFO: ufw boot config ENABLED=yes (/etc/ufw/ufw.conf)",
                        "INFO: ufw defaults input=DROP output=ACCEPT forward=DROP ipv6=yes manage_builtins=no (/etc/default/ufw)",
                        "INFO: ufw service enabled at boot (/etc/systemd/system/multi-user.target.wants/ufw.service -> /usr/lib/systemd/system/ufw.service)",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_artifact(
                "Run security audit: Check for open ports, SSH config, failed logins.",
                artifact,
            )

        self.assertEqual(0, score)
        self.assertEqual("latest artifact security.md has no active risk markers", reason)

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
                "RISK: AllowStreamLocalForwarding enabled\n"
                "RISK: PermitTunnel enabled\n"
                "WARN: MaxAuthTries is high (6)\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_status(
                "Run security audit: Check for open ports, SSH config, failed logins.",
                artifact,
            )

        self.assertEqual(140, score)
        self.assertIn("latest infra-status shows SSH tcp forwarding enabled", reason)
        self.assertIn("latest infra-status shows SSH agent forwarding enabled", reason)
        self.assertIn("latest infra-status shows SSH stream-local forwarding enabled", reason)
        self.assertIn("latest infra-status shows SSH tunneling enabled", reason)
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

    def test_score_task_from_status_ignores_hardened_ufw_observability_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "infra-status.md"
            artifact.write_text(
                "\n".join(
                    [
                        "WARN: ufw installed but status visibility is blocked by current privileges",
                        "INFO: ufw boot config ENABLED=yes (/etc/ufw/ufw.conf)",
                        "INFO: ufw defaults input=DROP output=ACCEPT forward=DROP ipv6=yes manage_builtins=no (/etc/default/ufw)",
                        "INFO: ufw service enabled at boot (/etc/systemd/system/multi-user.target.wants/ufw.service -> /usr/lib/systemd/system/ufw.service)",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_status(
                "Run security audit: Check for open ports, SSH config, failed logins.",
                artifact,
            )

        self.assertEqual(0, score)
        self.assertEqual("latest infra-status infra-status.md has no active markers for security", reason)

    def test_score_task_from_status_counts_live_fail2ban_drift_for_security(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "infra-status.md"
            artifact.write_text(
                "WARN: live config drift: /etc/fail2ban/jail.d/99-openclaw-sshd.local\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_status(
                "Run security audit: Check for open ports, SSH config, failed logins.",
                artifact,
            )

        self.assertEqual(45, score)
        self.assertIn("latest infra-status shows live fail2ban sshd jail drift", reason)

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

    def test_score_task_from_status_prioritizes_disabled_auto_update_timers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "infra-status.md"
            artifact.write_text(
                "0 pending updates\n"
                "INFO: auto-updates enabled (APT::Periodic::Update-Package-Lists=1, "
                "APT::Periodic::Unattended-Upgrade=1)\n"
                "RISK: auto-update timers not enabled at boot: apt-daily.timer=disabled (/lib/systemd/system/apt-daily.timer)\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_status(
                "Check for system updates daily and report count.",
                artifact,
            )

        self.assertEqual(75, score)
        self.assertIn("auto-update timers are not enabled at boot", reason)

    def test_score_task_from_status_prioritizes_stalled_unattended_updates_more_strongly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "infra-status.md"
            artifact.write_text(
                "4 pending updates\n"
                "INFO: auto-updates enabled (APT::Periodic::Update-Package-Lists=1, "
                "APT::Periodic::Unattended-Upgrade=1)\n"
                "WARN: unattended-upgrades last started at 2026-03-12 14:35 UTC (12h ago) but no completion was logged\n"
                "INFO: package-manager activity: no active apt/dpkg/unattended-upgrades process visible\n"
                "RISK: unattended-upgrades appears stalled; last start was 2026-03-12 14:35 UTC and no active package-manager process is visible\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_status(
                "Check for system updates daily and report count.",
                artifact,
            )

        self.assertEqual(95, score)
        self.assertIn("unattended-upgrades appears stalled", reason)

    def test_score_task_from_status_adds_security_sensitive_update_weight(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "infra-status.md"
            artifact.write_text(
                "2 pending updates\n"
                "INFO: auto-updates enabled (APT::Periodic::Update-Package-Lists=1, "
                "APT::Periodic::Unattended-Upgrade=1)\n"
                "INFO: unattended-upgrades last completed at 2026-03-13 01:05 UTC (1h ago): "
                "All upgrades installed\n"
                "RISK: security-sensitive updates pending: kernel=linux-image-aws, linux-libc-dev\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_status(
                "Check for system updates daily and report count.",
                artifact,
            )

        self.assertEqual(40, score)
        self.assertIn("security-sensitive updates pending", reason)

    def test_score_task_from_artifact_adds_reboot_required_weight(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = Path(tmpdir) / "updates.md"
            artifact.write_text(
                "No pending updates\n"
                "INFO: auto-updates enabled (APT::Periodic::Update-Package-Lists=1, "
                "APT::Periodic::Unattended-Upgrade=1)\n"
                "WARN: reboot required by previously installed updates (/var/run/reboot-required)\n",
                encoding="utf-8",
            )

            score, reason = infra_autopilot.score_task_from_artifact(
                "Check for system updates daily and report count.",
                artifact,
            )

        self.assertEqual(50, score)
        self.assertIn("reboot required by previously installed updates", reason)

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
