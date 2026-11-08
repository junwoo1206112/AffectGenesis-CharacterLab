import subprocess
import tempfile
from pathlib import Path
import unittest

from characterlab.release_receipt import RELEASE_TARGET_SHA, release_receipt


class ReleaseReceiptTests(unittest.TestCase):
    def _run(self, root: Path, *arguments: str) -> None:
        subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True, text=True)

    def _repository_with_tag(self, tag_command: list[str]) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self._run(root, "init", "-q")
        self._run(root, "config", "user.email", "test@example.invalid")
        self._run(root, "config", "user.name", "Test")
        (root / "file.txt").write_text("receipt\n", encoding="utf-8")
        self._run(root, "add", "file.txt")
        self._run(root, "commit", "-qm", "fixture")
        self._run(root, *tag_command)
        return root

    def test_lightweight_tag_is_explicit_and_can_bind_the_expected_target(self):
        root = self._repository_with_tag(["tag", "v0.1.0"])
        receipt = release_receipt(root)

        # The fixture has a different commit, so it correctly fails target matching.
        self.assertEqual(receipt["tag_kind"], "lightweight")
        self.assertFalse(receipt["complete"])
        self.assertEqual(receipt["expected_target_sha"], RELEASE_TARGET_SHA)

    def test_annotated_tag_is_reported_without_being_conflated_with_lightweight(self):
        root = self._repository_with_tag(["tag", "-a", "v0.1.0", "-m", "fixture"])
        receipt = release_receipt(root)

        self.assertEqual(receipt["tag_kind"], "annotated")
        self.assertFalse(receipt["complete"])

    def test_missing_tag_is_not_complete(self):
        root = self._repository_with_tag(["tag", "other"])
        receipt = release_receipt(root)

        self.assertFalse(receipt["complete"])
        self.assertEqual(receipt["reason"], "tag_unavailable")

    def test_actual_repository_baseline_is_a_verified_lightweight_tag(self):
        root = Path(__file__).resolve().parents[1]
        receipt = release_receipt(root)

        self.assertTrue(receipt["complete"])
        self.assertEqual(receipt["status"], "verified_release_baseline")
        self.assertEqual(receipt["tag_kind"], "lightweight")
        self.assertTrue(receipt["target_matches"])
        self.assertEqual(receipt["prior_seed_status"], "unmet_annotated_tag_requirement")
