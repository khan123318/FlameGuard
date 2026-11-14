"""Compare selected FlameGuard combustion experiments."""

import pandas as pd


DEFAULT_COMPARISON_FIELDS = [
    "research_program",
    "fuel_material",
    "environment",
    "objective",
    "variables_studied",
    "findings",
    "safety_relevance",
    "evidence_level",
    "limitations",
]


def compare_experiments(experiments, experiment_ids, fields=None):
    """
    Compare two or more experiments side by side.

    Args:
        experiments: DataFrame containing experiment records.
        experiment_ids: List or tuple of experiment IDs.
        fields: Optional list of fields to compare.

    Returns:
        DataFrame with comparison fields as rows and experiment IDs
        as columns.
    """

    if not isinstance(experiments, pd.DataFrame):
        raise TypeError("experiments must be a pandas DataFrame.")

    if "experiment_id" not in experiments.columns:
        raise ValueError(
            "The DataFrame must contain an 'experiment_id' column."
        )

    if not isinstance(experiment_ids, (list, tuple)):
        raise TypeError("experiment_ids must be a list or tuple.")

    if len(experiment_ids) < 2:
        raise ValueError("Select at least two experiments to compare.")

    if any(
        value is None or str(value).strip() == ""
        for value in experiment_ids
    ):
        raise ValueError("Experiment IDs cannot be empty.")

    if len(set(experiment_ids)) != len(experiment_ids):
        raise ValueError("Duplicate experiment IDs are not allowed.")

    if fields is None:
        fields = DEFAULT_COMPARISON_FIELDS

    elif not isinstance(fields, (list, tuple)):
        raise TypeError("fields must be a list or tuple.")

    if not fields:
        raise ValueError("At least one comparison field is required.")

    if any(
        not isinstance(field, str) or not field.strip()
        for field in fields
    ):
        raise ValueError(
            "Every comparison field must be a non-empty string."
        )

    if len(set(fields)) != len(fields):
        raise ValueError("Duplicate comparison fields are not allowed.")

    required_columns = ["experiment_id"] + list(fields)

    missing_columns = [
        column
        for column in required_columns
        if column not in experiments.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    selected = experiments[
        experiments["experiment_id"].isin(experiment_ids)
    ].copy()

    found_ids = selected["experiment_id"].tolist()

    missing_ids = [
        experiment_id
        for experiment_id in experiment_ids
        if experiment_id not in found_ids
    ]

    if missing_ids:
        raise ValueError(
            "Unknown experiment ID(s): "
            + ", ".join(str(value) for value in missing_ids)
        )

    # Remove duplicate records while keeping the first occurrence.
    selected = selected.drop_duplicates(
        subset="experiment_id",
        keep="first"
    )

    # Preserve the order selected by the user.
    selected = selected.set_index("experiment_id")
    selected = selected.reindex(experiment_ids)

    comparison = selected[list(fields)].transpose()

    comparison.index.name = "Parameter"

    return comparison