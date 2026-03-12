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

    def test_validate_install_target_blocks_live_path_without_explicit_override(self) -> None:
        with self.assertRaisesRegex(ValueError, "matches the live sshd path"):
            infra_sshd_hardening.validate_install_target(
                infra_sshd_hardening.LIVE_SSHD_CONFIG,
                allow_live_install=False,
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
