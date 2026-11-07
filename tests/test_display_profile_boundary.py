import copy
import unittest

from characterlab.model import build_comparison, is_allowlisted_read_only_comparison


class DisplayProfileBoundaryTests(unittest.TestCase):
    def test_every_scope_has_strictly_false_capability_flags(self):
        report = build_comparison()
        for scope in [report, *report["display_profiles"]]:
            for field_name in ("state_fields", "authority_fields", "action_execution_fields"):
                self.assertTrue(scope[field_name])
                self.assertTrue(all(value is False for value in scope[field_name].values()))
        self.assertTrue(is_allowlisted_read_only_comparison(report))

    def test_any_missing_true_or_nonboolean_capability_flag_fails_closed(self):
        cases = []
        missing = copy.deepcopy(build_comparison())
        del missing["display_profiles"][0]["state_fields"]
        cases.append(missing)
        true_value = copy.deepcopy(build_comparison())
        true_value["authority_fields"]["authority_changed"] = True
        cases.append(true_value)
        nonboolean = copy.deepcopy(build_comparison())
        nonboolean["display_profiles"][1]["action_execution_fields"]["actions_executed"] = 0
        cases.append(nonboolean)
        unknown_action = copy.deepcopy(build_comparison())
        unknown_action["display_profiles"][0]["suggestions"][0] = "do_anything"
        cases.append(unknown_action)
        for invalid in cases:
            self.assertFalse(is_allowlisted_read_only_comparison(invalid))
