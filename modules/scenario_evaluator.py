"""Scenario-level evidence review for FlameGuard.

This module connects the existing scenario retrieval and ranking
functionality. It does not calculate physical fire probability,
flame severity, or certified spacecraft risk.
"""

from collections.abc import Mapping, Sequence

from modules.ranking_engine import (
    evaluate_scenario_priority,
    rank_scenarios,
)


SCENARIO_FIELDS = (
    "scenario_type",
    "fuel_or_material",
    "description",
    "oxygen_percent",
    "air_velocity_m_s",
    "temperature_k",
    "pressure_pa",
)


NUMERIC_SCENARIO_FIELDS = (
    "oxygen_percent",
    "air_velocity_m_s",
    "temperature_k",
    "pressure_pa",
)


def _validate_scenario(scenario):
    """Validate supported scenario fields and numerical inputs."""

    if not isinstance(scenario, Mapping):
        raise TypeError(
            "scenario must be a dictionary or mapping."
        )

    for field in NUMERIC_SCENARIO_FIELDS:

        value = scenario.get(field)

        if value is None or value == "":
            continue

        try:
            number = float(value)

        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field} must be numeric when provided."
            ) from exc

        if number < 0:
            raise ValueError(
                f"{field} cannot be negative."
            )

        if field == "oxygen_percent" and number > 100:
            raise ValueError(
                "oxygen_percent must be between 0 and 100."
            )


def evaluate_scenario(scenario, top_k=5):
    """
    Retrieve and prioritize research evidence for one scenario.

    The returned scores are evidence-review heuristics, not physical
    fire-risk scores.
    """

    _validate_scenario(scenario)

    if (
        isinstance(top_k, bool)
        or not isinstance(top_k, int)
        or top_k < 1
    ):
        raise ValueError(
            "top_k must be a positive integer."
        )

    result = evaluate_scenario_priority(
        dict(scenario),
        top_k=top_k
    )

    evidence = result.get("evidence", [])

    limitations = list(
        result.get("limitations", [])
    )

    gap_reasons = list(
        result.get("evidence_gap_reasons", [])
    )

    evidence_count = len(evidence)

    result["evaluation_type"] = "evidence_review"

    result["score_interpretation"] = (
        "Heuristic evidence-review indicators only. "
        "These scores are not physical fire-risk scores, "
        "fire probabilities, severity ratings, or safety certification."
    )

    result["evidence_count"] = evidence_count

    result["evidence_review_summary"] = {
        "evidence_found": evidence_count > 0,

        "evidence_support_score": result.get(
            "evidence_support_score",
            0.0
        ),

        "evidence_gap_priority": result.get(
            "evidence_gap_priority",
            100.0
        ),

        "limitations": limitations,

        "evidence_gap_reasons": gap_reasons,
    }

    if evidence_count == 0:

        result["interpretation"] = (
            "No relevant evidence was retrieved. "
            "This represents an evidence gap, "
            "not evidence that the scenario is safe."
        )

    else:

        result["interpretation"] = (
            "Retrieved research records provide context "
            "for scientific review only. Their applicability "
            "must be checked against the scenario's specific "
            "material and environmental conditions."
        )

    return result


def evaluate_scenarios(scenarios, top_k=5):
    """
    Evaluate and prioritize multiple scenarios.

    Scenarios are ordered by evidence-gap priority, according
    to the existing ranking_engine implementation.
    """

    if (
        not isinstance(scenarios, Sequence)
        or isinstance(scenarios, (str, bytes))
    ):
        raise TypeError(
            "scenarios must be a list or tuple of scenario mappings."
        )

    if (
        isinstance(top_k, bool)
        or not isinstance(top_k, int)
        or top_k < 1
    ):
        raise ValueError(
            "top_k must be a positive integer."
        )

    for scenario in scenarios:
        _validate_scenario(scenario)

    ranked = rank_scenarios(
        list(scenarios),
        top_k=top_k
    )

    for item in ranked:

        item["evaluation_type"] = "evidence_review"

        item["score_interpretation"] = (
            "Evidence-gap priority is a heuristic research-review "
            "indicator, not physical fire risk or danger."
        )

    return ranked


# Alternative function names for readability.

evaluate_fire_scenario = evaluate_scenario

evaluate_multiple_scenarios = evaluate_scenarios