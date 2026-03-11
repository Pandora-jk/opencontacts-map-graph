import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

COMMON_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra_audit_common.py")
COMMON_SPEC = importlib.util.spec_from_file_location("infra_audit_common", COMMON_PATH)
infra_audit_common = importlib.util.module_from_spec(COMMON_SPEC)
assert COMMON_SPEC.loader is not None
COMMON_SPEC.loader.exec_module(infra_audit_common)

STATUS_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra-status.py")
STATUS_SPEC = importlib.util.spec_from_file_location("infra_status", STATUS_PATH)
infra_status = importlib.util.module_from_spec(STATUS_SPEC)
assert STATUS_SPEC.loader is not None
STATUS_SPEC.loader.exec_module(infra_status)

AUTOPILOT_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra-autopilot.py")
AUTOPILOT_SPEC = importlib.util.spec_from_file_location("infra_autopilot", AUTOPILOT_PATH)
infra_autopilot = importlib.util.module_from_spec(AUTOPILOT_SPEC)
assert AUTOPILOT_SPEC.loader is not None
AUTOPILOT_SPEC.loader.exec_module(infra_autopilot)


class InfraAuditCommonTests(unittest.TestCase):
    def test_auth_log_tail_commands_use_shared_limit(self) -> None:
        self.assertEqual(400, infra_audit_common.AUTH_LOG_SAMPLE_LIMIT)
        self.assertEqual(12000, infra_audit_common.AUTH_LOG_SAMPLE_MAX_CHARS)
        self.assertEqual(
            ['bash', '-lc', 'tail -n 400 /var/log/auth.log 2>/dev/null'],
            infra_audit_common.auth_log_tail_command(),
        )
        self.assertEqual(
            ['bash', '-lc', "journalctl -u ssh --since '24 hours ago' --no-pager 2>/dev/null | tail -n 400"],
            infra_audit_common.journalctl_ssh_tail_command(),
        )

    def test_status_and_autopilot_share_auth_log_sampling_limit(self) -> None:
        self.assertEqual(infra_audit_common.AUTH_LOG_SAMPLE_LIMIT, infra_status.AUTH_LOG_SAMPLE_LIMIT)
        self.assertEqual(infra_audit_common.AUTH_LOG_SAMPLE_MAX_CHARS, infra_status.AUTH_LOG_SAMPLE_MAX_CHARS)
        self.assertEqual(infra_audit_common.AUTH_LOG_SAMPLE_LIMIT, infra_autopilot.AUTH_LOG_SAMPLE_LIMIT)
        self.assertEqual(infra_audit_common.AUTH_LOG_SAMPLE_MAX_CHARS, infra_autopilot.AUTH_LOG_SAMPLE_MAX_CHARS)
        self.assertEqual(infra_status.auth_log_tail_command(), infra_autopilot.auth_log_tail_command())
        self.assertEqual(infra_status.journalctl_ssh_tail_command(), infra_autopilot.journalctl_ssh_tail_command())

    def test_inspect_unexpected_listeners_reports_scope_owner_and_hardening(self) -> None:
        observed: list[list[str]] = []

        def fake_run_cmd(cmd: list[str], max_chars: int = 800) -> str:
            observed.append(cmd)
            if "sport = :58627" in cmd[-1]:
                return 'udp UNCONN 0 0 *:58627 *:* users:(("openclaw-gateway",pid=4242,fd=9))'
            return 'n/a'

        result = infra_audit_common.inspect_unexpected_listeners(
            fake_run_cmd,
            "tcp [::ffff:127.0.0.1]:17564\nudp *:58627\ntcp 0.0.0.0:22",
        )

        self.assertIn("ALERT: Detailed inspection for unexpected listeners (1): udp/58627", result)
        self.assertIn("udp/58627 scope: *:58627", result)
        self.assertIn("udp/58627 owner(s): openclaw-gateway", result)
        self.assertIn("udp/58627 pid(s): 4242", result)
        self.assertIn("HARDENING: inspect the owning process with `ps -fp 4242`", result)
        self.assertEqual([['bash', '-lc', "ss -H -ulpn 'sport = :58627' 2>/dev/null | sed -n '1,10p'"]], observed)

    def test_check_firewall_status_reports_ufw_privilege_block(self) -> None:
        def fake_run_cmd(cmd: list[str], max_chars: int = 800) -> str:
            shell_cmd = cmd[-1]
            if 'command -v ufw' in shell_cmd:
                return '/usr/sbin/ufw'
            if 'sudo ufw status verbose' in shell_cmd:
                return 'sudo: The "no new privileges" flag is set, which prevents sudo from running as root.'
            return 'n/a'

        result = infra_audit_common.check_firewall_status(
            fake_run_cmd,
            which=lambda _: None,
        )

        self.assertIn('WARN: ufw installed but status visibility is blocked by current privileges', result)
        self.assertIn('HARDENING: verify `sudo ufw status verbose` from an unrestricted host shell', result)

    def test_summarize_auth_event_sources_ranks_ips_and_usernames(self) -> None:
        log_text = "\n".join(
            [
                "Mar 11 02:05:44 host sshd[1]: Invalid user sol from 64.225.75.83 port 42040",
                "Mar 11 02:05:45 host sshd[1]: Connection closed by invalid user sol 64.225.75.83 port 42040 [preauth]",
                "Mar 11 02:06:44 host sshd[1]: Invalid user solana from 64.225.75.83 port 42041",
                "Mar 11 02:06:45 host sshd[1]: Connection closed by invalid user solana 64.225.75.83 port 42041 [preauth]",
                "Mar 11 02:07:44 host sshd[1]: Invalid user admin from 164.92.146.128 port 33130",
            ]
        )

        result = infra_audit_common.summarize_auth_event_sources(log_text)

        self.assertIn(
            "ALERT: Auth event sources in sampled logs (5 events / 2 source(s)): 64.225.75.83 x4 (users: sol, solana); 164.92.146.128 x1 (users: admin)",
            result,
        )
        self.assertIn(
            "HARDENING: review recurring auth-event sources for host/cloud firewall blocking or access-list restrictions",
            result,
        )

    def test_summarize_auth_event_sources_handles_disconnect_lines_without_omitting_sources(self) -> None:
        log_text = "\n".join(
            [
                "Mar 11 02:05:44 host sshd[1]: Invalid user  from 115.190.119.177 port 42040",
                "Mar 11 02:05:45 host sshd[1]: Connection closed by invalid user  115.190.119.177 port 42040 [preauth]",
                "Mar 11 02:06:44 host sshd[1]: Invalid user admin from 192.109.200.220 port 30272",
                "Mar 11 02:06:45 host sshd[1]: Disconnected from invalid user admin 192.109.200.220 port 30272 [preauth]",
                "Mar 11 02:07:44 host sshd[1]: Invalid user support from 192.109.200.220 port 20450",
            ]
        )

        result = infra_audit_common.summarize_auth_event_sources(log_text)

        self.assertIn("115.190.119.177 x2", result)
        self.assertIn("192.109.200.220 x3 (users: admin, support)", result)
        self.assertNotIn("lacked a parseable source", result)


if __name__ == "__main__":
    unittest.main()
