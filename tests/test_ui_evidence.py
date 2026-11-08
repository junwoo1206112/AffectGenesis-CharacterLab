from pathlib import Path
import tempfile
import unittest

from characterlab.evidence import (
    EXPECTED_SCREENSHOTS,
    PNG_SIGNATURE,
    evidence_directory,
    public_ui_evidence_status,
    ui_evidence_status,
)


class UiEvidenceTests(unittest.TestCase):
    def test_missing_screenshots_are_reported_without_creating_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            status = ui_evidence_status(root)

            self.assertFalse(status["complete"])
            self.assertEqual(status["valid_files"], [])
            self.assertEqual(status["missing_or_invalid_files"], list(EXPECTED_SCREENSHOTS))
            self.assertFalse(evidence_directory(root).exists())

    def test_only_exact_png_named_capture_set_is_complete(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            directory = evidence_directory(root)
            directory.mkdir(parents=True)
            for filename in EXPECTED_SCREENSHOTS:
                (directory / filename).write_bytes(PNG_SIGNATURE + b"local-static-capture")

            status = ui_evidence_status(root)

            self.assertTrue(status["complete"])
            self.assertEqual(status["valid_files"], list(EXPECTED_SCREENSHOTS))
            self.assertEqual(status["missing_or_invalid_files"], [])

    def test_public_status_excludes_host_specific_evidence_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            status = public_ui_evidence_status(root)

            self.assertNotIn("evidence_directory", status)
            self.assertFalse(status["complete"])
            self.assertEqual(status["expected_files"], list(EXPECTED_SCREENSHOTS))
