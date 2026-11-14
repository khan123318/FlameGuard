
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
    "limitations"
]


def compare_experiments(experiments, experiment_ids, fields=None):
    """
    Compare two or more NASA combustion experiments.

    Parameters:
        experiments: Pandas DataFrame containing experiment records.
        experiment_ids: List of experiment IDs to compare.
        fields: Optional list of fields to compare.

    Returns:
        DataFrame with comparison parameters as rows
        and experiment IDs as columns.
    """

    # 1. Validate input
    if not isinstance(experiments, pd.DataFrame):
        raise TypeError("Experiments must be a Pandas DataFrame.")

    if "experiment_id" not in experiments.columns:
        raise ValueError("Missing experiment_id column.")

    if not isinstance(experiment_ids, (list, tuple)):
        raise TypeError("Experiment IDs must be a list or tuple.")

    if len(experiment_ids) < 2:
        raise ValueError("Select at least two experiments to compare.")

    if len(set(experiment_ids)) != len(experiment_ids):
        raise ValueError("Duplicate experiment IDs are not allowed.")

    # 2. Select comparison fields
    if fields is None:
        fields = DEFAULT_COMPARISON_FIELDS

    if not fields:
        raise ValueError("At least one comparison field is required.")

    if len(set(fields)) != len(fields):
        raise ValueError("Duplicate comparison fields are not allowed.")

    # 3. Validate available columns
    required_columns = ["experiment_id"] + fields

    missing_columns = [
        column for column in required_columns
        if column not in experiments.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing dataset columns: {missing_columns}"
        )

    # 4. Find selected experiments
    selected = experiments[
        experiments["experiment_id"].isin(experiment_ids)
    ].copy()

    # 5. Check whether all requested experiments exist
    found_ids = selected["experiment_id"].tolist()

    missing_ids = [
        experiment_id for experiment_id in experiment_ids
        if experiment_id not in found_ids
    ]

    if missing_ids:
        raise ValueError(
            f"Unknown experiment IDs: {missing_ids}"
        )

    # 6. Arrange experiments in the requested order
    selected = selected.set_index("experiment_id")
    selected = selected.reindex(experiment_ids)

    # 7. Construct comparison table
    comparison = selected[fields].T

    comparison.index.name = "Parameter"

    return comparison


if __name__ == "__main__":

    from modules.data_loader import load_experiments

    data = load_experiments()

    ids = data["experiment_id"].head(2).tolist()

    result = compare_experiments(data, ids)

    print(result)
