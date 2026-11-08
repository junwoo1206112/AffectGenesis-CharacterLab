"""Small, reproducible synthetic outcome-prediction experiment.

This module is intentionally separate from the static CharacterLab web demo.
It trains only on explicit synthetic observations, never calls a network or
external model, and does not alter a character, UI profile, or user data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "characterlab-synthetic-holdout-1"
ALLOWED_ACTIONS = ("pause_and_check", "ask_for_support", "retry_with_plan")
OUTCOMES = ("clarified", "recovered", "blocked")
MINIMUM_IMPROVEMENT = 0.20


@dataclass(frozen=True)
class Observation:
    context: str
    action: str
    outcome: str


TRAIN_OBSERVATIONS = (
    Observation("blocked", "pause_and_check", "clarified"),
    Observation("blocked", "ask_for_support", "clarified"),
    Observation("blocked", "retry_with_plan", "recovered"),
    Observation("uncertain", "pause_and_check", "clarified"),
    Observation("uncertain", "ask_for_support", "clarified"),
    Observation("uncertain", "retry_with_plan", "blocked"),
)
HOLDOUT_OBSERVATIONS = (
    Observation("new_context", "pause_and_check", "clarified"),
    Observation("new_context", "ask_for_support", "clarified"),
    Observation("new_context", "retry_with_plan", "blocked"),
)


def _validate(observations: Iterable[Observation]) -> tuple[Observation, ...]:
    values = tuple(observations)
    for item in values:
        if item.action not in ALLOWED_ACTIONS:
            raise ValueError(f"unsafe action is not allowed: {item.action}")
        if item.outcome not in OUTCOMES:
            raise ValueError(f"unknown synthetic outcome: {item.outcome}")
    return values


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class ActionOutcomeModel:
    """Count-based classifier that learns outcomes from synthetic action labels."""

    def __init__(self, counts: dict[str, dict[str, int]], fallback: str) -> None:
        self.counts = counts
        self.fallback = fallback

    @classmethod
    def train(cls, observations: Iterable[Observation]) -> "ActionOutcomeModel":
        values = _validate(observations)
        grouped: dict[str, Counter[str]] = defaultdict(Counter)
        outcomes: Counter[str] = Counter()
        for item in values:
            grouped[item.action][item.outcome] += 1
            outcomes[item.outcome] += 1
        fallback = sorted(outcomes.items(), key=lambda pair: (-pair[1], pair[0]))[0][0]
        return cls(
            {action: dict(counter) for action, counter in sorted(grouped.items())},
            fallback,
        )

    def predict(self, observation: Observation) -> str:
        _validate((observation,))
        choices = self.counts.get(observation.action)
        if not choices:
            return self.fallback
        return sorted(choices.items(), key=lambda pair: (-pair[1], pair[0]))[0][0]

    def checkpoint(self) -> dict[str, Any]:
        body = {"schema": SCHEMA, "counts": self.counts, "fallback": self.fallback}
        return {**body, "sha256": hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()}

    @classmethod
    def restore(cls, checkpoint: dict[str, Any]) -> "ActionOutcomeModel":
        body = {key: checkpoint[key] for key in ("schema", "counts", "fallback")}
        if body["schema"] != SCHEMA or checkpoint.get("sha256") != hashlib.sha256(
            _canonical(body).encode("utf-8")
        ).hexdigest():
            raise ValueError("checkpoint integrity mismatch")
        counts = body["counts"]
        if not isinstance(counts, dict) or body["fallback"] not in OUTCOMES:
            raise ValueError("invalid checkpoint")
        return cls({str(action): {str(key): int(value) for key, value in outcomes.items()} for action, outcomes in counts.items()}, str(body["fallback"]))


def _accuracy(predictions: list[str], observations: tuple[Observation, ...]) -> float:
    return sum(prediction == item.outcome for prediction, item in zip(predictions, observations, strict=True)) / len(observations)


def evaluate() -> dict[str, Any]:
    """Evaluate a fixed split, including a save/restore reproduction check."""
    train = _validate(TRAIN_OBSERVATIONS)
    holdout = _validate(HOLDOUT_OBSERVATIONS)
    model = ActionOutcomeModel.train(train)
    baseline = model.fallback
    baseline_predictions = [baseline] * len(holdout)
    learned_predictions = [model.predict(item) for item in holdout]
    checkpoint = model.checkpoint()
    restored_predictions = [ActionOutcomeModel.restore(checkpoint).predict(item) for item in holdout]
    baseline_accuracy = _accuracy(baseline_predictions, holdout)
    learned_accuracy = _accuracy(learned_predictions, holdout)
    improvement = learned_accuracy - baseline_accuracy
    safety_violations = sum(item.action not in ALLOWED_ACTIONS for item in (*train, *holdout))
    return {
        "schema": SCHEMA,
        "scope": "fixed local synthetic outcome prediction only",
        "non_claim": (
            "This is not an LLM, RAG system, agent, emotion model, personality model, "
            "human-development model, real-world safety result, or user-data experiment."
        ),
        "split": {"train_count": len(train), "holdout_count": len(holdout), "holdout_contexts": [item.context for item in holdout]},
        "baseline": {"kind": "fixed_global_majority_outcome", "prediction": baseline, "holdout_accuracy": baseline_accuracy},
        "learned": {"kind": "action_outcome_count_model", "holdout_accuracy": learned_accuracy, "predictions": learned_predictions},
        "minimum_improvement": MINIMUM_IMPROVEMENT,
        "improvement": improvement,
        "effect_status": "observed_on_fixed_synthetic_holdout" if improvement >= MINIMUM_IMPROVEMENT else "not_observed",
        "safety": {"allowed_actions": list(ALLOWED_ACTIONS), "violation_count": safety_violations},
        "checkpoint": {"sha256": checkpoint["sha256"], "restored_predictions_match": restored_predictions == learned_predictions},
        "observations": {"train": [asdict(item) for item in train], "holdout": [asdict(item) for item in holdout]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local synthetic holdout experiment.")
    parser.add_argument("--checkpoint", type=Path, help="Optional path to write the verified local checkpoint.")
    args = parser.parse_args()
    report = evaluate()
    if args.checkpoint:
        model = ActionOutcomeModel.train(TRAIN_OBSERVATIONS)
        args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
        args.checkpoint.write_text(_canonical(model.checkpoint()) + "\n", encoding="utf-8")
        report["checkpoint"]["path"] = str(args.checkpoint)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["safety"]["violation_count"] == 0 and report["checkpoint"]["restored_predictions_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
