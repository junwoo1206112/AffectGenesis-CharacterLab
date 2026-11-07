"""Deterministic, read-only comparison model for the portfolio demo."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


SAFE_ACTIONS = ("pause_and_check", "ask_for_support", "retry_with_plan")


@dataclass(frozen=True)
class Character:
    """A display character with a stable, non-authoritative temperament label."""

    character_id: str = "mira-01"
    display_name: str = "Mira"
    temperament: str = "cautious"


@dataclass(frozen=True)
class SyntheticExperience:
    """A fixed local event; it is not human data or a claim about feeling."""

    situation: str = "A planned task is blocked after a failed first attempt."
    observed_action: str = "ask_for_support"
    outcome: str = "A safe clarification enabled a planned retry."


def build_comparison(
    character: Character | None = None,
    experience: SyntheticExperience | None = None,
) -> dict[str, Any]:
    """Return two explanations for identical inputs without changing either input.

    ``approved_learning`` only changes which pre-recorded synthetic memory may be
    cited.  It never writes a model checkpoint, character state, or authority.
    """

    character = character or Character()
    experience = experience or SyntheticExperience()
    shared_context = {
        "character": asdict(character),
        "synthetic_experience": asdict(experience),
        "safety_boundary": "Only predefined safe coping actions are shown; no action is executed.",
    }
    conditions = [
        {
            "condition": "unapproved_learning",
            "learning_approved": False,
            "memory_used": False,
            "suggestions": ["pause_and_check", "ask_for_support"],
            "explanation": "The character uses a fixed safety-first response and does not cite the recorded experience.",
        },
        {
            "condition": "approved_learning",
            "learning_approved": True,
            "memory_used": True,
            "suggestions": ["pause_and_check", "ask_for_support", "retry_with_plan"],
            "explanation": "The same fixed synthetic experience is cited to add a planned retry after safety checking and support.",
        },
    ]
    return {
        "title": "Synthetic coping comparison",
        **shared_context,
        "comparison_conditions": conditions,
        "limitations": [
            "This is a deterministic local demonstration, not evidence of actual emotion, consciousness, or human development.",
            "Approved learning is a read-only comparison flag, not an automatic character update.",
        ],
    }


def is_safe_comparison(report: dict[str, Any]) -> bool:
    """Check the small invariant used by tests and the web endpoint."""

    return all(
        action in SAFE_ACTIONS
        for condition in report["comparison_conditions"]
        for action in condition["suggestions"]
    )
