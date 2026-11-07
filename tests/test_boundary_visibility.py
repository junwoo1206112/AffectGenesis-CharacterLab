import unittest

from characterlab.model import canonical_boundaries, build_comparison, scenario_ids
from characterlab.webapp import has_visible_canonical_boundaries, normalized_visible_text, page, synthetic_input_panel


class BoundaryVisibilityTests(unittest.TestCase):
    def test_every_scenario_shows_fixed_input_and_all_canonical_boundaries(self):
        for scenario_id in scenario_ids():
            report = build_comparison(scenario_id)
            rendered = page(scenario_id)
            panel = synthetic_input_panel(report)
            self.assertIn("고정 합성 입력", rendered)
            for value in report["synthetic_experience"].values():
                self.assertIn(value, rendered)
            self.assertTrue(has_visible_canonical_boundaries(rendered))
            self.assertTrue(has_visible_canonical_boundaries(panel))

    def test_normalization_allows_only_markup_entities_and_whitespace(self):
        statement = canonical_boundaries()[0]
        html = f"<p>  {statement.replace('read-only', 'read&#45;only')}  </p>"
        self.assertIn(statement, normalized_visible_text(html))
        self.assertFalse(has_visible_canonical_boundaries("<p>shortened text</p>"))

    def test_hidden_boundary_text_does_not_count_as_visible(self):
        content = "".join(f'<p hidden>{item}</p>' for item in canonical_boundaries())
        self.assertFalse(has_visible_canonical_boundaries(content))
        css_hidden = "".join(f'<p style="display: none">{item}</p>' for item in canonical_boundaries())
        self.assertFalse(has_visible_canonical_boundaries(css_hidden))
        aria_hidden = "".join(f'<p aria-hidden="true">{item}</p>' for item in canonical_boundaries())
        self.assertFalse(has_visible_canonical_boundaries(aria_hidden))
        for hidden_class in ("hidden", "visually-hidden", "sr-only"):
            class_hidden = "".join(
                f'<p class="{hidden_class}">{item}</p>' for item in canonical_boundaries()
            )
            self.assertFalse(has_visible_canonical_boundaries(class_hidden))
