import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

MODULE_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra_ssh_ban_hardening.py")
SPEC = importlib.util.spec_from_file_location("infra_ssh_ban_hardening", MODULE_PATH)
infra_ssh_ban_hardening = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(infra_ssh_ban_hardening)


class InfraSshBanHardeningTests(unittest.TestCase):
    def test_managed_config_matches_expected_content(self) -> None:
        content = Path(infra_ssh_ban_hardening.MANAGED_FAIL2BAN_CONFIG).read_text(encoding="utf-8")
        self.assertEqual(infra_ssh_ban_hardening.FAIL2BAN_SSH_JAIL, content)
        self.assertIn("maxretry = 3", content)
        self.assertIn("findtime = 10m", content)
        self.assertIn("bantime = 4h", content)

    def test_validate_install_target_blocks_live_path_without_explicit_override(self) -> None:
        with self.assertRaisesRegex(ValueError, "matches the live fail2ban path"):
            infra_ssh_ban_hardening.validate_install_target(
                infra_ssh_ban_hardening.LIVE_FAIL2BAN_CONFIG,
                allow_live_install=False,
            )

    def test_staged_validation_reports_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            stage_dir = Path(tmpdir)
            staged_path = infra_ssh_ban_hardening.staged_config_path(stage_dir)
            infra_ssh_ban_hardening.write_config(staged_path)

            self.assertEqual(
                f"staged config installed: {staged_path} (mode 0644)",
                infra_ssh_ban_hardening.staged_config_status(staged_path),
            )

    def test_fail2ban_policy_status_reports_hardened_thresholds(self) -> None:
        status = infra_ssh_ban_hardening.fail2ban_policy_status()

        self.assertIn("maxretry=3", status)
        self.assertIn("findtime=10m", status)
        self.assertIn("bantime=4h", status)

    def test_fail2ban_service_status_uses_socket_visibility_when_service_manager_is_unavailable(self) -> None:
        with mock.patch.object(
            infra_ssh_ban_hardening,
            "run_cmd",
            side_effect=["n/a", "n/a"],
        ), mock.patch.object(
            infra_ssh_ban_hardening,
            "fail2ban_socket_status",
            return_value="INFO: fail2ban socket present: /var/run/fail2ban/fail2ban.sock (mode 0600, owner root:root)",
        ):
            status = infra_ssh_ban_hardening.fail2ban_service_status()

        self.assertIn("service state not visible from current shell", status)
        self.assertIn("owner root:root", status)

    def test_fail2ban_sshd_status_reports_root_only_socket_access(self) -> None:
        with mock.patch.object(
            infra_ssh_ban_hardening,
            "run_cmd",
            return_value="2026-03-13 fail2ban ERROR Permission denied to socket: /var/run/fail2ban/fail2ban.sock",
        ), mock.patch.object(
            infra_ssh_ban_hardening,
            "fail2ban_socket_status",
            return_value="INFO: fail2ban socket present: /var/run/fail2ban/fail2ban.sock (mode 0600, owner root:root)",
        ):
            status = infra_ssh_ban_hardening.fail2ban_sshd_status()

        self.assertIn("status requires root", status)
        self.assertIn("owner root:root", status)


if __name__ == "__main__":
    unittest.main()
