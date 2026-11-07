"""Deterministic, read-only display-profile comparison for the portfolio demo."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


ALLOWLISTED_COPING_SUGGESTIONS = (
    "pause_and_check",
    "ask_for_support",
    "retry_with_plan",
)


@dataclass(frozen=True)
class SyntheticExperience:
    """A fixed local event; it is not human data or a claim about feeling."""

    situation: str = "A planned task is blocked after a failed first attempt."
    observed_action: str = "ask_for_support"
    outcome: str = "A clarification enabled a planned retry."


@dataclass(frozen=True)
class DisplayProfile:
    """A pre-authored display variant, not a measured personal characteristic."""

    profile_id: str
    display_name: str
    static_wording: str
    suggestions: tuple[str, ...]
    difference_explanation: str


DISPLAY_PROFILES = (
    DisplayProfile(
        profile_id="check_first",
        display_name="확인 우선 표시",
        static_wording="먼저 멈춰 현재 상황을 확인한 뒤, 필요한 지원을 요청합니다.",
        suggestions=("pause_and_check", "ask_for_support", "retry_with_plan"),
        difference_explanation="같은 허용 목록을 확인과 지원 요청이 먼저 보이도록 사전작성한 표시 순서입니다.",
    ),
    DisplayProfile(
        profile_id="plan_next",
        display_name="계획 다음 표시",
        static_wording="확인 후 재시도 계획을 세우고, 필요하면 지원을 요청합니다.",
        suggestions=("pause_and_check", "retry_with_plan", "ask_for_support"),
        difference_explanation="같은 허용 목록을 계획적 재시도가 먼저 보이도록 사전작성한 표시 순서입니다.",
    ),
)


def no_change_fields() -> dict[str, dict[str, bool]]:
    """Return explicit capability boundaries at every report scope."""

    return {
        "state_fields": {"state_changed": False, "memory_saved": False},
        "authority_fields": {"authority_changed": False, "approval_granted": False},
        "action_execution_fields": {"actions_executed": False, "external_service_called": False},
    }


def build_comparison(experience: SyntheticExperience | None = None) -> dict[str, Any]:
    """Build a fixed side-by-side comparison without mutating any state."""

    experience = experience or SyntheticExperience()
    profile_cards = [
        {
            "profile_id": profile.profile_id,
            "display_name": profile.display_name,
            "static_wording": profile.static_wording,
            "suggestions": list(profile.suggestions),
            "difference_explanation": profile.difference_explanation,
            "profile_scope": "Pre-authored display variant; not a trait, diagnosis, learning result, or personalization.",
            **no_change_fields(),
        }
        for profile in DISPLAY_PROFILES
    ]
    return {
        "title": "Synthetic display-profile comparison",
        "comparison_label": "LOCAL · SYNTHETIC · STATIC · READ-ONLY",
        "synthetic_experience": asdict(experience),
        "coping_allowlist": list(ALLOWLISTED_COPING_SUGGESTIONS),
        "shared_context": "Both profiles receive the identical synthetic situation and identical allowlist.",
        "display_profiles": profile_cards,
        **no_change_fields(),
        "limitations": [
            "This is a deterministic local display comparison, not evidence of actual emotion, personality, learning, consciousness, or human development.",
            "Profiles are pre-authored display variants; no character, memory, authority, appearance, or action changes automatically.",
            "Allowlisted suggestions are labels only. They are not executed and do not establish clinical or real-world safety.",
        ],
    }


def is_allowlisted_read_only_comparison(report: dict[str, Any]) -> bool:
    """Validate the deterministic, non-mutating portfolio contract."""

    expected_membership = set(ALLOWLISTED_COPING_SUGGESTIONS)
    profiles = report.get("display_profiles", [])
    if len(profiles) != 2 or not report.get("synthetic_experience"):
        return False
    for scope in [report, *profiles]:
        for field_name in ("state_fields", "authority_fields", "action_execution_fields"):
            flags = scope.get(field_name)
            if not isinstance(flags, dict) or not flags or any(value is not False for value in flags.values()):
                return False
    return all(
        len(profile.get("suggestions", [])) == len(ALLOWLISTED_COPING_SUGGESTIONS)
        and set(profile["suggestions"]) == expected_membership
        and len(set(profile["suggestions"])) == len(ALLOWLISTED_COPING_SUGGESTIONS)
        for profile in profiles
    )


# Compatibility aliases for callers of the first portfolio release.
SAFE_ACTIONS = ALLOWLISTED_COPING_SUGGESTIONS
is_safe_comparison = is_allowlisted_read_only_comparison
