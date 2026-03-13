import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/.openclaw/workspace/tools")

MODULE_PATH = Path("/home/ubuntu/.openclaw/workspace/tools/infra_sshd_hardening.py")
SPEC = importlib.util.spec_from_file_location("infra_sshd_hardening", MODULE_PATH)
infra_sshd_hardening = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(infra_sshd_hardening)


class InfraSshdHardeningTests(unittest.TestCase):
    def test_managed_config_matches_expected_content(self) -> None:
        content = Path(infra_sshd_hardening.MANAGED_SSHD_CONFIG).read_text(encoding="utf-8")
        self.assertEqual(infra_sshd_hardening.SSHD_HARDENING_CONFIG, content)

    def test_managed_config_disables_forwarding(self) -> None:
        self.assertIn("AllowTcpForwarding no\n", infra_sshd_hardening.SSHD_HARDENING_CONFIG)
        self.assertIn("AllowAgentForwarding no\n", infra_sshd_hardening.SSHD_HARDENING_CONFIG)
        self.assertIn("AllowStreamLocalForwarding no\n", infra_sshd_hardening.SSHD_HARDENING_CONFIG)
        self.assertIn("PermitTunnel no\n", infra_sshd_hardening.SSHD_HARDENING_CONFIG)

    def test_validate_install_target_blocks_live_path_without_explicit_override(self) -> None:
        with self.assertRaisesRegex(ValueError, "matches the live sshd path"):
            infra_sshd_hardening.validate_install_target(
                infra_sshd_hardening.LIVE_SSHD_CONFIG,
                allow_live_install=False,
            )

    def test_validation_main_config_targets_staged_artifacts(self) -> None:
        stage_dir = Path("/tmp/openclaw-sshd-stage-test")
        self.assertEqual(
            (
                f"HostKey {stage_dir / 'ssh_host_ed25519_key'}\n"
                f"PidFile {stage_dir / 'sshd.pid'}\n"
                f"Include {stage_dir}/*.conf\n"
            ),
            infra_sshd_hardening.validation_main_config(stage_dir),
        )

    def test_staged_validation_reports_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            stage_dir = Path(tmpdir)
            staged_path = infra_sshd_hardening.staged_config_path(stage_dir)
            infra_sshd_hardening.write_config(staged_path)

            self.assertEqual(
                f"staged config installed: {staged_path} (mode 0644)",
                infra_sshd_hardening.staged_config_status(staged_path),
            )


if __name__ == "__main__":
    unittest.main()
