import pandas as pd

from modules.data_loader import load_experiments


# Fields confirmed in the existing experiment dataset
ANALYTICS_CATEGORIES = [
    "research_program",
    "evidence_level",
    "material_class",
    "environment",
    "fuel_material",
]

# Fields used to assess dataset completeness
COVERAGE_FIELDS = [
    "research_program",
    "fuel_material",
    "environment",
    "variables_studied",
    "findings",
    "safety_relevance",
    "evidence_level",
    "limitations",
]


def get_experiment_data():
    """
    Load the curated combustion experiment dataset.
    Uses the existing project data loader.
    """
    return load_experiments()


# def _is_missing_value(value):
#     """Identify values that do not provide an actual reported field value."""

#     if pd.isna(value):
#         return True

#     text = str(value).strip().lower()

#     if not text:
#         return True

#     missing_markers = [
#         "not reported",
#         "not stated",
#         "not specified",
#         "unknown",
#         "unavailable",
#         "nan",
#         "none",
#         "null"
#     ]

#     return any(marker in text for marker in missing_markers)


def _is_missing_value(value):
    """Identify values that do not provide an actual reported field value."""

    if pd.isna(value):
        return True

    text = str(value).strip().lower()

    if not text:
        return True

    missing_markers = [
        "not reported",
        "not stated",
        "not specified",
        "unavailable",
        "nan",
        "none",
        "null",
    ]

    # Exact matches are missing values.
    if text in missing_markers or text == "unknown":
        return True

    # Phrases beginning with these markers indicate missing information.
    if text.startswith(("not reported", "not stated", "not specified")):
        return True

    return False


def _reported_values(series):
    """Return values containing reported information."""

    return series[~series.apply(_is_missing_value)]


def _classify_findings_status(row):
    """Classify the documented status without assuming missing results."""

    evidence = str(row.get("evidence_level", "")).lower()
    experiment_type = str(row.get("experiment_type", "")).lower()
    findings = str(row.get("findings", "")).lower()

    if "planned" in evidence or "planned" in experiment_type:
        return "Planned; no results reported"

    if "test point ran" in findings and "no measured results" in findings:
        return "Test reported; measured results unavailable"

    if "no results" in findings:
        return "Research described; results unavailable"

    if _is_missing_value(row.get("findings", "")):
        return "Findings unavailable"

    return "Findings reported in available record"


def _classify_evidence_type(row):
    """Classify the evidence type while preserving mixed evidence."""

    evidence = str(row.get("evidence_level", "")).lower()
    experiment_type = str(row.get("experiment_type", "")).lower()

    if "planned" in evidence or "planned" in experiment_type:
        return "Planned research"

    if "simulation" in evidence or "simulation" in experiment_type:
        return "Simulation"

    if "secondary summary" in evidence or "literature review" in evidence:
        return "Experimental work (secondary summary)"

    if "observation" in evidence:
        if "hypothesis" in evidence:
            return "Experimental observation with hypothesis"

        if "theory" in evidence:
            return "Experimental observation with theoretical interpretation"

        return "Experimental observation"

    if "theory" in evidence or "analytical theory" in experiment_type:
        return "Theoretical"

    return "Descriptive or unclear"


def get_findings_status_distribution(df):
    """Count records by documented research status."""

    statuses = df.apply(_classify_findings_status, axis=1)

    return (
        statuses.value_counts()
        .rename_axis("research_status")
        .reset_index(name="count")
    )


def get_evidence_type_distribution(df):
    """Count records by evidence type."""

    evidence_types = df.apply(_classify_evidence_type, axis=1)

    return (
        evidence_types.value_counts()
        .rename_axis("evidence_type")
        .reset_index(name="count")
    )


def get_overview_metrics(df):
    """
    Calculate high-level metrics for the analytics dashboard.
    """

    if df.empty:
        return {
            "total_experiments": 0,
            "research_programs": 0,
            "evidence_levels": 0,
            "fuel_material_entries": 0,
        }

    metrics = {
        "total_experiments": len(df),
        "research_programs": 0,
        "evidence_levels": 0,
        "fuel_material_entries": 0,
    }

    if "research_program" in df.columns:
        metrics["research_programs"] = (
            _reported_values(df["research_program"]).nunique()
        )

    if "evidence_level" in df.columns:
        metrics["evidence_levels"] = (
            _reported_values(df["evidence_level"]).nunique()
        )

    if "fuel_material" in df.columns:
        metrics["fuel_material_entries"] = (
            _reported_values(df["fuel_material"]).nunique()
        )

    return metrics


def get_category_distribution(df, column):
    """
    Count the number of experiments in each category.

    Returns a DataFrame with:
    category | count
    """

    if column not in df.columns:
        return pd.DataFrame(columns=["category", "count"])

    values = _reported_values(df[column])

    if values.empty:
        return pd.DataFrame(columns=["category", "count"])

    distribution = (
        values.value_counts()
        .rename_axis("category")
        .reset_index(name="count")
    )

    return distribution


def _classify_coverage_value(value):
    """Classify a field as reported, explicitly unavailable, or missing."""

    if pd.isna(value):
        return "missing"

    text = str(value).strip().lower()

    if not text:
        return "missing"

    # Generic placeholders without useful information.
    missing_markers = ["nan", "none", "null", "unknown"]

    if text in missing_markers:
        return "missing"

    # Explicit statements that information or results are unavailable.
    unavailable_markers = [
        "not reported",
        "not stated",
        "not specified",
        "unavailable",
        "none stated",
        "no results",
        "no measured results",
    ]

    # if any(text.startswith(marker) for marker in unavailable_markers):
    #     return "explicitly_unavailable"

    if any(marker in text for marker in unavailable_markers):
        return "explicitly_unavailable"

    return "reported"


# def get_data_coverage(df):
#     """
#     Calculate reported and missing-value counts
#     for important experiment fields.
#     """

#     coverage = []

#     total = len(df)

#     for column in COVERAGE_FIELDS:

#         if column not in df.columns:
#             continue

#         reported_count = len(
#             _reported_values(df[column])
#         )

#         missing_count = total - reported_count

#         percentage = (
#             round((reported_count / total) * 100, 1)
#             if total > 0
#             else 0.0
#         )

#         coverage.append({
#             "field": column,
#             "reported": reported_count,
#             "not_reported": missing_count,
#             "coverage_percent": percentage,
#         })

#     return pd.DataFrame(coverage)

def get_data_coverage(df):
    """
    Calculate reported, explicitly unavailable, and missing
    information for important experiment fields.
    """

    coverage = []
    total = len(df)

    for column in COVERAGE_FIELDS:

        if column not in df.columns:
            continue

        statuses = df[column].apply(_classify_coverage_value)

        reported_count = (statuses == "reported").sum()

        unavailable_count = (
            statuses == "explicitly_unavailable"
        ).sum()

        missing_count = (statuses == "missing").sum()

        documented_count = reported_count + unavailable_count

        percentage = (
            round((documented_count / total) * 100, 1)
            if total > 0
            else 0.0
        )

        coverage.append({
            "field": column,
            "reported": int(reported_count),
            "explicitly_unavailable": int(unavailable_count),
            "missing": int(missing_count),
            "coverage_percent": percentage,
        })

    return pd.DataFrame(coverage)
