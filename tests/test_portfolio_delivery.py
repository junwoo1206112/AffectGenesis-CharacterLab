from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PortfolioDeliveryTests(unittest.TestCase):
    def test_only_small_portfolio_material_is_present(self):
        allowed_top_level = {".git", ".gitignore", "README.md", "characterlab", "docs", "tests"}
        self.assertEqual({path.name for path in ROOT.iterdir()}, allowed_top_level)
        self.assertFalse((ROOT / "artifacts").exists())
        self.assertFalse((ROOT / "contracts").exists())

    def test_readme_states_local_scope_and_run_command(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("python -m characterlab.webapp", readme)
        self.assertIn("not evidence of actual emotion", readme)
        self.assertNotIn("ai-emotion-lab", readme.lower())
