from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PortfolioDeliveryTests(unittest.TestCase):
    def test_only_small_portfolio_material_is_present(self):
        allowed_top_level = {
            ".git",
            ".github",
            ".gitignore",
            "LICENSE",
            "README.md",
            "characterlab",
            "docs",
            "tests",
        }
        self.assertEqual({path.name for path in ROOT.iterdir()}, allowed_top_level)
        self.assertFalse((ROOT / "artifacts").exists())
        self.assertFalse((ROOT / "contracts").exists())

    def test_readme_states_local_scope_and_run_command(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("python -m characterlab.webapp", readme)
        self.assertIn("python -m characterlab.capture", readme)
        self.assertIn("current archive verifies as `완료 (3/3)`", readme)
        for filename in (
            "blocked_first_attempt.png",
            "uncertain_next_step.png",
            "planned_retry.png",
        ):
            self.assertIn(f"docs/phase1_ui/{filename}", readme)
        self.assertIn("not evidence of actual emotion", readme)
        self.assertNotIn("ai-emotion-lab", readme.lower())

    def test_license_is_standard_mit_and_readme_bounds_its_scope(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("MIT License", license_text)
        self.assertIn("Copyright (c) 2026 junwoo1206112", license_text)
        self.assertIn("Permission is hereby granted", license_text)
        self.assertIn("THE SOFTWARE IS PROVIDED \"AS IS\"", license_text)
        self.assertIn("[MIT License](LICENSE)", readme)
        self.assertIn("third-party material", readme)
        self.assertIn("does not establish or warrant actual emotion", readme)

    def test_ci_workflow_checks_both_supported_runners_without_publish_steps(self):
        workflow = (ROOT / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")

        self.assertIn("push:", workflow)
        self.assertIn("pull_request:", workflow)
        self.assertIn("ubuntu-latest", workflow)
        self.assertIn("windows-latest", workflow)
        self.assertIn('python-version: ["3.12"]', workflow)
        self.assertIn("actions/checkout@v6", workflow)
        self.assertIn("actions/setup-python@v5", workflow)
        self.assertIn("python -m unittest discover -s tests -v", workflow)
        self.assertIn("python -m characterlab.smoke", workflow)
        self.assertIn("git diff --check HEAD^ HEAD", workflow)
        self.assertNotIn("upload-artifact", workflow)
        self.assertNotIn("publish", workflow.lower())
