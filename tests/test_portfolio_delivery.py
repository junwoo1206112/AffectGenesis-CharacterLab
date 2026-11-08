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
        self.assertIn("python -m characterlab.release_receipt --require-complete", readme)
        self.assertIn("사이트에 연결할 수 없음", readme)
        self.assertIn("http://127.0.0.1:8766/healthz", readme)
        for filename in (
            "blocked_first_attempt.png",
            "uncertain_next_step.png",
            "planned_retry.png",
        ):
            self.assertIn(f"docs/phase1_ui/{filename}", readme)
        self.assertIn("실제 감정, 학습, 성격, 의식, 인간 발달", readme)
        self.assertIn("python -m characterlab.learning_experiment", readme)
        self.assertIn("정적 전시와 분리된", readme)
        self.assertIn("LLM·RAG·에이전트", readme)
        self.assertIn("/api/experiment-report", readme)
        self.assertIn("학습을 실행하거나 캐릭터 상태를 저장·변경하지 않습니다", readme)
        self.assertNotIn("ai-emotion-lab", readme.lower())

    def test_release_receipt_preserves_the_tag_boundary(self):
        receipt = (ROOT / "docs" / "v0_1_0_release_receipt.md").read_text(encoding="utf-8")

        self.assertIn("lightweight tag", receipt)
        self.assertIn("seed_a94b82a398a0", receipt)
        self.assertIn("미충족", receipt)
        self.assertIn("삭제·이동·수정·재게시하지 않는다", receipt)
        self.assertIn("438182316", receipt)
        self.assertIn("0e5b3168e5dbd151841b184a7856f52af384d206", receipt)

    def test_license_is_standard_mit_and_readme_bounds_its_scope(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("MIT License", license_text)
        self.assertIn("Copyright (c) 2026 junwoo1206112", license_text)
        self.assertIn("Permission is hereby granted", license_text)
        self.assertIn("THE SOFTWARE IS PROVIDED \"AS IS\"", license_text)
        self.assertIn("[MIT License](LICENSE)", readme)
        self.assertIn("제3자 자료·데이터·상표", readme)
        self.assertIn("실제 감정, 학습, 성격, 의식", readme)

    def test_ci_workflow_checks_both_supported_runners_without_publish_steps(self):
        workflow = (ROOT / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")

        self.assertIn("push:", workflow)
        self.assertIn("pull_request:", workflow)
        self.assertIn("ubuntu-latest", workflow)
        self.assertIn("windows-latest", workflow)
        self.assertIn('python-version: ["3.12"]', workflow)
        self.assertIn("actions/checkout@v6", workflow)
        self.assertIn("fetch-tags: true", workflow)
        self.assertIn("actions/setup-python@v5", workflow)
        self.assertIn("python -m unittest discover -s tests -v", workflow)
        self.assertIn("python -m characterlab.smoke", workflow)
        self.assertIn("git diff --check HEAD^ HEAD", workflow)
        self.assertNotIn("upload-artifact", workflow)
        self.assertNotIn("publish", workflow.lower())
