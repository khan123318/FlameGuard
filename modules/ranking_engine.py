
"""
FlameGuard Evidence Ranking and Scenario Prioritization Engine.

This module ranks research records using:
    1. Text retrieval relevance
    2. Evidence strength
    3. Documentation completeness

It also prioritizes scenarios according to their available
scientific evidence and evidence gaps.

IMPORTANT:
These scores are research-support indicators.
They are NOT fire-risk scores, hazard probabilities,
safety thresholds, or safety certifications.
"""

from modules.scenario_retrieval import retrieve_for_scenario


# =========================================================
# CONFIGURATION
# =========================================================

RELEVANCE_WEIGHT = 0.50
EVIDENCE_WEIGHT = 0.30
COMPLETENESS_WEIGHT = 0.20

# Fields used to assess documentation completeness.
EXPERIMENT_COMPLETENESS_FIELDS = [
    "fuel_material",
    "environment",
    "variables_studied",
    "findings",
    "safety_relevance",
    "limitations",
    "source_url",
]

RETRIEVAL_COMPLETENESS_FIELDS = [
    "fuel_material",
    "findings",
    "safety_relevance",
    "limitations",
    "matched_passage",
    "source_url",
]

# Default fields for retrieval records.
COMPLETENESS_FIELDS = RETRIEVAL_COMPLETENESS_FIELDS


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def _is_missing(value):
    """Check whether a value is missing or an unavailable placeholder."""

    if value is None:
        return True

    text = str(value).strip().lower()

    missing_values = {
        "",
        "not reported",
        "not stated",
        "not specified",
        "unavailable",
        "unknown",
        "nan",
        "none",
        "null",
    }

    if text in missing_values:
        return True

    missing_phrases = (
        "not reported",
        "not stated",
        "not specified",
    )

    return text.startswith(missing_phrases)


def _safe_float(value, default=0.0):
    """Convert a value into a valid float between 0 and 1."""

    try:
        number = float(value)

        if number != number:  # NaN check
            return default

        return max(0.0, min(1.0, number))

    except (TypeError, ValueError):
        return default


# =========================================================
# 1. EVIDENCE STRENGTH
# =========================================================

def calculate_evidence_strength(record):
    """
    Estimate evidence strength from the evidence_level label.

    Returns a score between 0 and 100.

    These are heuristic classifications, not scientific
    certainty measurements.
    """

    if not isinstance(record, dict):
        raise TypeError("Record must be a dictionary.")

    evidence_level = record.get("evidence_level", "")

    if _is_missing(evidence_level):
        return 0.0

    label = str(evidence_level).strip().lower()

    # Check secondary evidence before generic observation labels.
    if "secondary summary" in label:
        return 45.0

    if "literature review" in label:
        return 45.0

    if "planned" in label:
        return 10.0

    if "descriptive only" in label:
        return 20.0

    if "simulation" in label:
        return 65.0

    if  "preliminary theory" in label:
        return 90.0

    if "trend summary" in label:
        return 90.0

    if "hypothesis" in label:
        return 85.0
    
    if "theory" in label:
        return 50.0

    if "reported observation" in label:
        return 100.0

    # Unknown evidence labels are not automatically treated
    # as strong evidence.
    return 20.0


# =========================================================
# 2. DOCUMENTATION COMPLETENESS
# =========================================================

def calculate_completeness(record):
    """
    Calculate documentation completeness using the appropriate
    fields for the record type.

    Raw experiment records and retrieved research records have
    different schemas, so they must use different denominators.
    """

    if not isinstance(record, dict):
        raise TypeError("Record must be a dictionary.")

    if "relevance_score" in record:
        fields = RETRIEVAL_COMPLETENESS_FIELDS
    else:
        fields = EXPERIMENT_COMPLETENESS_FIELDS

    reported_fields = sum(
        not _is_missing(record.get(field))
        for field in fields
    )

    return (reported_fields / len(fields)) * 100

# =========================================================
# 3. EVIDENCE RANKING
# =========================================================

def rank_evidence(records):
    """
    Rank retrieved research records.

    Input:
        A list of dictionaries returned by retrieve_research().

    Output:
        A new list of dictionaries containing the original
        research information and additional ranking scores.
    """

    if not isinstance(records, list):
        raise TypeError("Records must be provided as a list.")

    ranked_records = []

    for record in records:

        if not isinstance(record, dict):
            raise TypeError("Every research record must be a dictionary.")

        # Existing TF-IDF relevance score is between 0 and 1.
        relevance = _safe_float(
            record.get("relevance_score", 0.0)
        ) * 100

        evidence_strength = calculate_evidence_strength(record)

        completeness = calculate_completeness(record)

        overall_score = (
            relevance * RELEVANCE_WEIGHT
            + evidence_strength * EVIDENCE_WEIGHT
            + completeness * COMPLETENESS_WEIGHT
        )

        ranked_record = record.copy()

        ranked_record["relevance_component_score"] = round(
            relevance, 2
        )

        ranked_record["evidence_strength_score"] = round(
            evidence_strength, 2
        )

        ranked_record["completeness_score"] = round(
            completeness, 2
        )

        ranked_record["overall_score"] = round(
            overall_score, 2
        )

        ranked_record["ranking_reasons"] = [
            f"Text relevance: {relevance:.2f}/100",
            f"Evidence strength: {evidence_strength:.2f}/100",
            f"Documentation completeness: {completeness:.2f}/100",
        ]

        ranked_records.append(ranked_record)

    # Python's sort is stable, so equal-scoring records
    # retain their original relative order.
    ranked_records.sort(
        key=lambda item: item["overall_score"],
        reverse=True
    )

    return ranked_records


# =========================================================
# 4. SINGLE SCENARIO EVIDENCE PRIORITIZATION
# =========================================================

def evaluate_scenario_priority(scenario, top_k=5):
    """
    Evaluate the scientific evidence available for one scenario.

    Returns:
        query
        evidence
        limitations
        evidence_support_score
        evidence_gap_priority
        evidence_gap_reasons

    These scores represent evidence availability, NOT fire risk.
    """

    if not isinstance(scenario, dict):
        raise TypeError("Scenario must be a dictionary.")

    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer.")

    result = retrieve_for_scenario(scenario, top_k=top_k)

    evidence = result.get("evidence", [])
    limitations = result.get("limitations", [])

    if not isinstance(evidence, list):
        raise ValueError("Scenario retrieval returned invalid evidence.")

    if not isinstance(limitations, list):
        raise ValueError("Scenario retrieval returned invalid limitations.")

    # No retrieved evidence means no evidence support in this dataset.
    if not evidence:
        support_score = 0.0

    else:
        evidence_scores = []
        relevance_scores = []

        for record in evidence:

            strength = calculate_evidence_strength(record)

            relevance = _safe_float(
                record.get("relevance_score", 0.0)
            ) * 100

            evidence_scores.append(strength)
            relevance_scores.append(relevance)

        average_strength = sum(evidence_scores) / len(evidence_scores)
        average_relevance = sum(relevance_scores) / len(relevance_scores)

        # A small number of retrieved records should not be
        # interpreted as extensive evidence coverage.
        evidence_count_factor = min(len(evidence) / 3, 1.0)

        support_score = (
            (average_strength * 0.60)
            + (average_relevance * 0.40)
        ) * evidence_count_factor

    # Identify specific evidence gaps from existing limitations.
    gap_reasons = []

    for limitation in limitations:

        text = str(limitation).lower()

        if (
            "no matching evidence" in text
            or "no evidence" in text
            or "no searchable fields" in text
        ):
            gap_reasons.append(str(limitation))

        elif "material" in text and (
            "not named" in text or "not explicitly" in text
        ):
            gap_reasons.append(str(limitation))

        elif "electrical" in text:
            gap_reasons.append(str(limitation))

    # Missing evidence increases investigation priority.
    # These penalties do not represent physical hazard severity.
    gap_priority = 100.0 - support_score

    for reason in gap_reasons:

        text = reason.lower()

        if "electrical" in text:
            gap_priority += 10

        elif "material" in text:
            gap_priority += 15

    gap_priority = min(100.0, max(0.0, gap_priority))

    return {
        "scenario": scenario.copy(),
        "query": result.get("query", ""),
        "evidence": evidence,
        "limitations": limitations,
        "evidence_support_score": round(support_score, 2),
        "evidence_gap_priority": round(gap_priority, 2),
        "evidence_gap_reasons": gap_reasons,
    }


# =========================================================
# 5. MULTIPLE SCENARIO PRIORITIZATION
# =========================================================

def rank_scenarios(scenarios, top_k=5):
    """
    Rank multiple scenarios by evidence-gap priority.

    Scenarios with less supporting evidence and more explicit
    evidence gaps receive higher investigation priority.

    This is NOT a physical fire-risk ranking.
    """

    if not isinstance(scenarios, list):
        raise TypeError("Scenarios must be provided as a list.")

    ranked_scenarios = []

    for index, scenario in enumerate(scenarios):

        if not isinstance(scenario, dict):
            raise TypeError("Every scenario must be a dictionary.")

        evaluation = evaluate_scenario_priority(
            scenario,
            top_k=top_k
        )

        evaluation["scenario_name"] = (
            scenario.get("scenario_name")
            or scenario.get("name")
            or f"Scenario {index + 1}"
        )

        evaluation["original_order"] = index

        ranked_scenarios.append(evaluation)

    ranked_scenarios.sort(
        key=lambda item: item["evidence_gap_priority"],
        reverse=True
    )

    return ranked_scenarios

def rank_experiments(records):
    """
    Rank distinct experiments using their retrieved research passages.

    Relevance is calculated using the average of the three highest
    passage relevance scores for each experiment.

    Evidence strength and completeness use the highest available
    component scores among that experiment's passages.

    Returns one result per experiment, retaining all supporting passages.
    """

    if not isinstance(records, list):
        raise TypeError("Records must be a list.")

    if not records:
        return []

    grouped_records = {}

    for record in records:
        if not isinstance(record, dict):
            raise TypeError("Every record must be a dictionary.")

        experiment_id = record.get("experiment_id")

        if _is_missing(experiment_id):
            raise ValueError("Every record must have an experiment_id.")

        required_scores = [
            "relevance_component_score",
            "evidence_strength_score",
            "completeness_score",
        ]

        for field in required_scores:
            if field not in record:
                raise ValueError(f"Record is missing {field}.")

        grouped_records.setdefault(experiment_id, []).append(record)

    ranked_experiments = []

    for experiment_id, passages in grouped_records.items():

        # Sort passages by relevance, highest first.
        passages = sorted(
            passages,
            key=lambda item: float(item["relevance_component_score"]),
            reverse=True
        )

        # Use the average of the three strongest relevance scores.
        top_relevance_scores = [
            float(record["relevance_component_score"])
            for record in passages[:3]
        ]

        relevance_score = sum(top_relevance_scores) / len(top_relevance_scores)

        # Retain the strongest available experiment-level component scores.
        evidence_strength = max(
            float(record["evidence_strength_score"])
            for record in passages
        )

        completeness = max(
            float(record["completeness_score"])
            for record in passages
        )

        overall_score = (
            0.50 * relevance_score
            + 0.30 * evidence_strength
            + 0.20 * completeness
        )

        first_record = passages[0]

        ranked_experiments.append({
            "experiment_id": experiment_id,
            "experiment_name": first_record.get("experiment_name", "Unknown"),
            "passage_count": len(passages),
            "relevance_component_score": round(relevance_score, 2),
            "evidence_strength_score": round(evidence_strength, 2),
            "completeness_score": round(completeness, 2),
            "overall_score": round(overall_score, 2),
            "ranking_reasons": [
                f"Average of top passage relevance scores: {relevance_score:.2f}/100",
                f"Evidence strength: {evidence_strength:.2f}/100",
                f"Documentation completeness: {completeness:.2f}/100",
                f"Supporting research passages: {len(passages)}",
            ],
            "supporting_passages": passages,
        })

    # Rank experiments by their overall scores.
    ranked_experiments.sort(
        key=lambda item: item["overall_score"],
        reverse=True
    )

    return ranked_experiments
