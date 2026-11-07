import copy
import unittest

from characterlab.model import build_comparison, is_allowlisted_read_only_comparison, scenario_ids
from characterlab.webapp import has_visible_canonical_boundaries


class BoundaryRejectionTests(unittest.TestCase):
    def test_forbidden_claim_cases_fail_closed_for_all_scenario_profile_combinations(self):
        for scenario_id in scenario_ids():
            for profile_index in range(2):
                for claim in (
                    "This proves actual emotion.",
                    "This has a real personality.",
                    "This learns from these scenarios.",
                    "This is clinically safe.",
                ):
                    report = copy.deepcopy(build_comparison(scenario_id))
                    report["display_profiles"][profile_index]["static_wording"] += f" {claim}"
                    self.assertFalse(is_allowlisted_read_only_comparison(report))

    def test_conflicting_or_hidden_boundary_replacements_are_rejected(self):
        report = build_comparison()
        report["comparison_summary"] += " This proves actual emotion."
        self.assertFalse(is_allowlisted_read_only_comparison(report))
        hidden_replacement = "".join(
            f'<span style="visibility:hidden">{boundary}</span>'
            for boundary in build_comparison()["canonical_boundary_non_claims"]
        )
        self.assertFalse(has_visible_canonical_boundaries(hidden_replacement))
