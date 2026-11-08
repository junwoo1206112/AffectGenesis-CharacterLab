import unittest

from characterlab.model import scenario_ids
from characterlab.smoke import run_smoke


class LiveHttpSmokeTests(unittest.TestCase):
    def test_loopback_smoke_checks_all_fixed_scenarios_without_mutation(self):
        receipt = run_smoke()

        self.assertEqual(receipt["schema"], "characterlab-live-http-smoke-1")
        self.assertEqual(receipt["checked_scenarios"], list(scenario_ids()))
        self.assertTrue(receipt["get_responses_stable"])
        self.assertEqual(receipt["rejected_mutation_methods"], ["POST", "PUT", "PATCH", "DELETE"])
        self.assertIn("does not prove emotion", receipt["non_claim"])
