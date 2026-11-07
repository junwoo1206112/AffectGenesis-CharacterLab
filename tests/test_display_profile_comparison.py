import unittest

from characterlab.model import ALLOWLISTED_COPING_SUGGESTIONS, build_comparison, is_allowlisted_read_only_comparison
from characterlab.webapp import page


class DisplayProfileComparisonTests(unittest.TestCase):
    def test_profiles_share_one_situation_and_allowlist_but_differ_visibly(self):
        report = build_comparison()
        first, second = report["display_profiles"]
        self.assertEqual(report["coping_allowlist"], list(ALLOWLISTED_COPING_SUGGESTIONS))
        self.assertEqual(set(first["suggestions"]), set(second["suggestions"]))
        self.assertNotEqual(first["suggestions"], second["suggestions"])
        self.assertNotEqual(first["static_wording"], second["static_wording"])
        self.assertIn("사전작성", first["difference_explanation"])
        self.assertIn("사전작성", second["difference_explanation"])
        self.assertTrue(is_allowlisted_read_only_comparison(report))

    def test_output_is_deterministic_and_rendered_side_by_side(self):
        self.assertEqual(build_comparison(), build_comparison())
        rendered = page()
        self.assertIn("확인 우선 표시", rendered)
        self.assertIn("계획 다음 표시", rendered)
        self.assertIn("profiles", rendered)
