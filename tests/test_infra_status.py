import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

MODULE_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra-status.py")
SPEC = importlib.util.spec_from_file_location("infra_status", MODULE_PATH)
infra_status = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(infra_status)


class InfraStatusTests(unittest.TestCase):
    def test_check_open_ports_uses_supplied_raw_port_lines(self) -> None:
        result = infra_status.check_open_ports("udp 0.0.0.0:5353\nudp 127.0.0.1:323")

        self.assertIn("ALERT: Unexpected externally exposed listeners (1): udp/5353", result)

    def test_check_open_ports_treats_ipv4_mapped_loopback_as_local_only(self) -> None:
        result = infra_status.check_open_ports(
            "tcp [::ffff:127.0.0.1]:17564\nudp *:58627\ntcp 0.0.0.0:22"
        )

        self.assertIn("ALERT: Unexpected externally exposed listeners (1): udp/58627", result)
        self.assertNotIn("tcp/17564", result)

    def test_check_unexpected_listener_details_uses_supplied_raw_port_lines(self) -> None:
        def fake_run_cmd(cmd: list[str], max_chars: int = 800) -> str:
            if "sport = :58627" in cmd[-1]:
                return 'udp UNCONN 0 0 *:58627 *:* users:(("openclaw-gateway",pid=4242,fd=9))'
            return 'n/a'

        with mock.patch.object(infra_status, "run_cmd", side_effect=fake_run_cmd):
            result = infra_status.check_unexpected_listener_details(
                "tcp [::ffff:127.0.0.1]:17564\nudp *:58627\ntcp 0.0.0.0:22"
            )

        self.assertIn("udp/58627 owner(s): openclaw-gateway", result)
        self.assertNotIn("tcp/17564", result)

    def test_check_firewall_status_detects_ufw_outside_default_path(self) -> None:
        def fake_run_cmd(cmd: list[str], max_chars: int = 800) -> str:
            shell_cmd = cmd[-1]
            if 'command -v ufw' in shell_cmd:
                return '/usr/sbin/ufw'
            if 'sudo ufw status verbose' in shell_cmd:
                return 'Status: active'
            return 'n/a'

        with mock.patch.object(infra_status, "run_cmd", side_effect=fake_run_cmd), mock.patch.object(
            infra_status.shutil, "which", return_value=None
        ):
            result = infra_status.check_firewall_status()

        self.assertIn("ufw: active", result)
        self.assertNotIn("WARN: ufw unavailable on host", result)

    def test_check_failed_logins_uses_full_auth_sample_budget(self) -> None:
        observed: dict[str, int] = {}

        def fake_run_cmd(cmd: list[str], max_chars: int = 800) -> str:
            observed["max_chars"] = max_chars
            return "Invalid user admin"

        with mock.patch.object(infra_status.Path, "exists", return_value=True), mock.patch.object(
            infra_status, "run_cmd", side_effect=fake_run_cmd
        ):
            infra_status.check_failed_logins()

        self.assertEqual(infra_status.AUTH_LOG_SAMPLE_MAX_CHARS, observed["max_chars"])

    def test_generate_report_uses_raw_port_lines_for_mdns_detection(self) -> None:
        with mock.patch.object(infra_status, "current_port_lines", return_value="udp 0.0.0.0:5353"), mock.patch.object(
            infra_status, "check_system_updates", return_value="No pending updates"
        ), mock.patch.object(
            infra_status, "check_disk_usage", return_value="Disk usage nominal"
        ), mock.patch.object(
            infra_status, "check_unexpected_listener_details", return_value="No unexpected listener details to inspect"
        ), mock.patch.object(
            infra_status, "check_firewall_status", return_value="Firewall nominal"
        ), mock.patch.object(
            infra_status, "check_ssh_config", return_value="SSH nominal"
        ), mock.patch.object(
            infra_status, "check_failed_logins", return_value="No failed authentication attempts found in sampled logs"
        ), mock.patch.object(
            infra_status, "check_backup_integrity", return_value="Backup nominal"
        ), mock.patch.object(
            infra_status, "check_service_health", return_value="service-manager: unavailable"
        ), mock.patch.object(
            infra_status, "run_cmd", return_value="UNCONN 0 0 0.0.0.0:5353 0.0.0.0:*"
        ), mock.patch(
            "infra_network._service_state", return_value=None
        ):
            md_content, summary_lines = infra_status.generate_report()

        self.assertIn("## Multicast DNS Exposure", md_content)
        self.assertIn("## Unexpected Listener Details", md_content)
        self.assertIn("## Auth Source Summary", md_content)
        self.assertIn("ALERT: External mDNS listener detected on udp/5353", md_content)
        self.assertTrue(
            any("mDNS: ALERT: External mDNS listener detected on udp/5353" in line for line in summary_lines)
        )

    def test_check_auth_source_summary_reports_sources_and_source_name(self) -> None:
        log_text = "\n".join(
            [
                "Mar 11 02:05:44 host sshd[1]: Invalid user sol from 64.225.75.83 port 42040",
                "Mar 11 02:05:45 host sshd[1]: Connection closed by invalid user sol 64.225.75.83 port 42040 [preauth]",
                "Mar 11 02:06:44 host sshd[1]: Invalid user admin from 164.92.146.128 port 33130",
                "Mar 11 02:06:45 host sshd[1]: Connection closed by invalid user admin 164.92.146.128 port 33130 [preauth]",
                "Mar 11 02:07:44 host sshd[1]: Invalid user root from 64.225.75.83 port 42041",
            ]
        )

        with mock.patch.object(infra_status, "get_auth_sample", return_value=(log_text, "auth.log")):
            result = infra_status.check_auth_source_summary()

        self.assertIn("64.225.75.83 x3 (users: root, sol)", result)
        self.assertIn("164.92.146.128 x2 (users: admin)", result)
        self.assertIn("Source: auth.log", result)

    def test_check_auth_source_summary_counts_disconnect_lines_without_parseable_username(self) -> None:
        log_text = "\n".join(
            [
                "Mar 11 02:05:44 host sshd[1]: Invalid user  from 115.190.119.177 port 42040",
                "Mar 11 02:05:45 host sshd[1]: Connection closed by invalid user  115.190.119.177 port 42040 [preauth]",
                "Mar 11 02:06:44 host sshd[1]: Invalid user admin from 192.109.200.220 port 30272",
                "Mar 11 02:06:45 host sshd[1]: Disconnected from invalid user admin 192.109.200.220 port 30272 [preauth]",
                "Mar 11 02:07:44 host sshd[1]: Invalid user support from 192.109.200.220 port 20450",
            ]
        )

        with mock.patch.object(infra_status, "get_auth_sample", return_value=(log_text, "auth.log")):
            result = infra_status.check_auth_source_summary()

        self.assertIn("115.190.119.177 x2", result)
        self.assertIn("192.109.200.220 x3 (users: admin, support)", result)
        self.assertNotIn("lacked a parseable source", result)

    def test_read_sshd_config_follows_include_order_with_first_value_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            main = root / "sshd_config"
            dropins = root / "sshd_config.d"
            dropins.mkdir()
            (dropins / "60-cloudimg-settings.conf").write_text(
                "PasswordAuthentication no\nPermitRootLogin prohibit-password\nMaxAuthTries 3\n",
                encoding="utf-8",
            )
            main.write_text(
                "\n".join(
                    [
                        f"Include {dropins}/*.conf",
                        "PasswordAuthentication yes",
                        "X11Forwarding no",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            cfg = infra_status.read_sshd_config(main)

        self.assertEqual("no", cfg["passwordauthentication"])
        self.assertEqual("prohibit-password", cfg["permitrootlogin"])
        self.assertEqual("3", cfg["maxauthtries"])
        self.assertEqual("no", cfg["x11forwarding"])

    def test_score_ssh_risk_treats_key_only_root_login_as_non_risky(self) -> None:
        info, risks = infra_status.score_ssh_risk(
            {
                "permitrootlogin": "prohibit-password",
                "passwordauthentication": "no",
                "x11forwarding": "no",
                "permitemptypasswords": "no",
                "maxauthtries": "3",
                "logingracetime": "30",
            }
        )

        self.assertIn("INFO: root SSH login is limited to keys", info)
        self.assertNotIn("RISK: PermitRootLogin enabled", risks)

    def test_score_ssh_risk_adds_managed_dropin_guidance_when_settings_are_not_explicit(self) -> None:
        _, risks = infra_status.score_ssh_risk({"x11forwarding": "no"})

        combined = "\n".join(risks)
        self.assertIn("WARN: effective SSH hardening is only partially visible", combined)
        self.assertIn(
            "HARDENING: preview a managed sshd drop-in with `python3 tools/infra_sshd_hardening.py --stdout`",
            combined,
        )

    def test_get_effective_ssh_config_falls_back_to_files_when_sshd_t_has_no_parseable_keys(self) -> None:
        with mock.patch.object(infra_status, "find_sshd_binary", return_value="/usr/sbin/sshd"), mock.patch.object(
            infra_status, "run_cmd", return_value="sshd: no hostkeys available -- exiting."
        ), mock.patch.object(
            infra_status, "read_sshd_config", return_value={"passwordauthentication": "no"}
        ):
            cfg = infra_status.get_effective_ssh_config()

        self.assertEqual({"passwordauthentication": "no"}, cfg)

    def test_generate_report_risk_summary_includes_ssh_warn_first_line(self) -> None:
        with mock.patch.object(infra_status, "current_port_lines", return_value="tcp 0.0.0.0:22"), mock.patch.object(
            infra_status, "check_system_updates", return_value="No pending updates"
        ), mock.patch.object(
            infra_status, "check_disk_usage", return_value="Disk usage nominal"
        ), mock.patch.object(
            infra_status, "check_unexpected_listener_details", return_value="No unexpected listener details to inspect"
        ), mock.patch.object(
            infra_status, "check_firewall_status", return_value="Firewall nominal"
        ), mock.patch.object(
            infra_status, "check_ssh_config",
            return_value=(
                "WARN: effective SSH hardening is only partially visible; some key settings are not explicitly set\n"
                "HARDENING: preview a managed sshd drop-in with `python3 tools/infra_sshd_hardening.py --stdout`"
            ),
        ), mock.patch.object(
            infra_status, "check_failed_logins", return_value="No failed authentication attempts found in sampled logs"
        ), mock.patch.object(
            infra_status, "check_auth_source_summary", return_value="No suspicious auth-event source summary available (auth.log)"
        ), mock.patch.object(
            infra_status, "check_backup_integrity", return_value="Backup nominal"
        ), mock.patch.object(
            infra_status, "check_service_health", return_value="service-manager: unavailable"
        ):
            md_content, _ = infra_status.generate_report()

        self.assertIn(
            "- RISK: WARN: effective SSH hardening is only partially visible; some key settings are not explicitly set",
            md_content,
        )


if __name__ == "__main__":
    unittest.main()
