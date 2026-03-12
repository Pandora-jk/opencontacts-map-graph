import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
