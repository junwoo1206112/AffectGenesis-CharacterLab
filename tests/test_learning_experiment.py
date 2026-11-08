import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from characterlab.learning_experiment import (
    ALLOWED_ACTIONS,
    ActionOutcomeModel,
    Observation,
    TRAIN_OBSERVATIONS,
    evaluate,
    main,
)


class LearningExperimentTests(unittest.TestCase):
    def test_fixed_synthetic_holdout_beats_frozen_baseline_and_restores(self):
        report = evaluate()
        self.assertEqual(report["safety"]["violation_count"], 0)
        self.assertTrue(report["checkpoint"]["restored_predictions_match"])
        self.assertEqual(report["effect_status"], "observed_on_fixed_synthetic_holdout")
        self.assertGreaterEqual(report["improvement"], report["minimum_improvement"])

    def test_unsafe_action_is_rejected_before_training_or_prediction(self):
        with self.assertRaisesRegex(ValueError, "unsafe action"):
            ActionOutcomeModel.train((Observation("synthetic", "external_call", "clarified"),))

    def test_tampered_checkpoint_is_rejected(self):
        checkpoint = ActionOutcomeModel.train(TRAIN_OBSERVATIONS).checkpoint()
        checkpoint["fallback"] = "blocked"
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            ActionOutcomeModel.restore(checkpoint)

    def test_cli_checkpoint_is_parseable_and_uses_only_allowed_actions(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "checkpoint.json"
            with patch("sys.argv", ["characterlab.learning_experiment", "--checkpoint", str(output)]):
                self.assertEqual(main(), 0)
            checkpoint = json.loads(output.read_text(encoding="utf-8"))
        self.assertIn(checkpoint["fallback"], {"clarified", "recovered", "blocked"})
        self.assertEqual(set(ALLOWED_ACTIONS), {"pause_and_check", "ask_for_support", "retry_with_plan"})
