"""Deterministic, read-only display-profile comparison for the portfolio demo."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


ALLOWLISTED_COPING_SUGGESTIONS = (
    "pause_and_check",
    "ask_for_support",
    "retry_with_plan",
)

# This is the single source of truth for what the static portfolio does and
# does not claim.  Reports, the API, and the HTML view all render this exact
# ordered list; a changed, missing, added, or reordered item fails validation.
CANONICAL_BOUNDARY_NON_CLAIMS = (
    "Static, read-only, pre-authored display material.",
    "Both profiles receive the identical synthetic input and allowlisted suggestions.",
    "No state or memory changes.",
    "No authority changes and no action execution.",
    "This does not represent actual emotion, personality, learning, personalization, or adaptation.",
)

_FORBIDDEN_CLAIM_CASES = (
    "proves actual emotion",
    "has a real personality",
    "learns from these scenarios",
    "is clinically safe",
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


@dataclass(frozen=True)
class SyntheticScenario:
    """One fixed exhibition case, never user-authored or persisted."""

    scenario_id: str
    display_name: str
    experience: SyntheticExperience
    comparison_summary: str


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


SYNTHETIC_SCENARIOS = (
    SyntheticScenario(
        scenario_id="blocked_first_attempt",
        display_name="첫 시도 뒤 막힘",
        experience=SyntheticExperience(),
        comparison_summary="두 표시는 같은 사전작성 상황과 제안 목록을 공유합니다. 확인 우선 표시는 지원 요청을, 계획 다음 표시는 재시도 계획을 먼저 보이게 할 뿐입니다.",
    ),
    SyntheticScenario(
        scenario_id="uncertain_next_step",
        display_name="다음 단계가 불확실함",
        experience=SyntheticExperience(
            situation="The next safe step is unclear after incomplete instructions.",
            observed_action="pause_and_check",
            outcome="A pause made the missing information visible before a planned retry.",
        ),
        comparison_summary="두 표시는 동일한 불확실성 입력을 받습니다. 문구와 제안의 표시 순서만 사전작성되어 다르며, 어느 쪽도 상황을 계산하거나 학습하지 않습니다.",
    ),
    SyntheticScenario(
        scenario_id="planned_retry",
        display_name="계획한 재시도",
        experience=SyntheticExperience(
            situation="A clarified plan allows one bounded retry after an earlier block.",
            observed_action="retry_with_plan",
            outcome="The fixed example records a planned retry label only; no action is performed.",
        ),
        comparison_summary="두 표시는 같은 재시도 예시를 전시합니다. 강조 순서가 다를 뿐, 제안은 같은 허용 목록이고 행동·권한·상태는 바뀌지 않습니다.",
    ),
)

_SCENARIOS_BY_ID = {scenario.scenario_id: scenario for scenario in SYNTHETIC_SCENARIOS}


def no_change_fields() -> dict[str, dict[str, bool]]:
    """Return explicit capability boundaries at every report scope."""

    return {
        "state_fields": {"state_changed": False, "memory_saved": False},
        "authority_fields": {"authority_changed": False, "approval_granted": False},
        "action_execution_fields": {"actions_executed": False, "external_service_called": False},
    }


def scenario_ids() -> tuple[str, ...]:
    """Return the canonical order of the fixed exhibition catalog."""

    return tuple(scenario.scenario_id for scenario in SYNTHETIC_SCENARIOS)


def profile_ids() -> tuple[str, ...]:
    """Return the canonical, pre-authored display-profile order."""

    return tuple(profile.profile_id for profile in DISPLAY_PROFILES)


def canonical_boundaries() -> tuple[str, ...]:
    """Return the ordered, immutable boundary/non-claim contract."""

    return CANONICAL_BOUNDARY_NON_CLAIMS


def build_comparison(scenario_id: str | None = None) -> dict[str, Any]:
    """Build one fixed side-by-side comparison without mutating any state."""

    selected_id = scenario_id or SYNTHETIC_SCENARIOS[0].scenario_id
    scenario = _SCENARIOS_BY_ID.get(selected_id)
    if scenario is None:
        raise ValueError(f"Unknown fixed scenario: {selected_id}")
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
        "scenario_id": scenario.scenario_id,
        "scenario_display_name": scenario.display_name,
        "synthetic_experience": asdict(scenario.experience),
        "comparison_summary": scenario.comparison_summary,
        "coping_allowlist": list(ALLOWLISTED_COPING_SUGGESTIONS),
        "shared_context": "Both profiles receive the identical synthetic situation and identical allowlist.",
        "canonical_boundary_non_claims": list(canonical_boundaries()),
        "shared_boundaries": list(canonical_boundaries()),
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
    if (
        len(profiles) != 2
        or report.get("scenario_id") not in scenario_ids()
        or tuple(profile.get("profile_id") for profile in profiles) != profile_ids()
        or not report.get("synthetic_experience")
        or not isinstance(report.get("comparison_summary"), str)
        or not report.get("comparison_summary")
        or report.get("canonical_boundary_non_claims") != list(canonical_boundaries())
        or report.get("shared_boundaries") != list(canonical_boundaries())
    ):
        return False
    for scope in [report, *profiles]:
        for field_name in ("state_fields", "authority_fields", "action_execution_fields"):
            flags = scope.get(field_name)
            if not isinstance(flags, dict) or not flags or any(value is not False for value in flags.values()):
                return False
    display_text = " ".join(
        [report.get("comparison_summary", "")]
        + [
            " ".join((profile.get("static_wording", ""), profile.get("difference_explanation", "")))
            for profile in profiles
        ]
    ).lower()
    if any(forbidden in display_text for forbidden in _FORBIDDEN_CLAIM_CASES):
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
