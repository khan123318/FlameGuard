
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from modules.data_loader import load_experiments
from modules.experiment_comparison import compare_experiments


def test_compare_two_experiments():

    data = load_experiments()

    ids = data["experiment_id"].head(2).tolist()

    result = compare_experiments(data, ids)

    assert len(result.columns) == 2
    assert "findings" in result.index


def test_comparison_preserves_requested_order():

    data = load_experiments()

    ids = data["experiment_id"].head(2).tolist()

    result = compare_experiments(data, ids[::-1])

    assert list(result.columns) == ids[::-1]


def test_comparison_rejects_single_experiment():

    data = load_experiments()

    ids = data["experiment_id"].head(1).tolist()

    try:
        compare_experiments(data, ids)
        assert False, "Expected ValueError"

    except ValueError:
        pass


def test_comparison_rejects_unknown_id():

    data = load_experiments()

    ids = [
        data["experiment_id"].iloc[0],
        "UNKNOWN-ID"
    ]

    try:
        compare_experiments(data, ids)
        assert False, "Expected ValueError"

    except ValueError as error:
        assert "Unknown experiment IDs" in str(error)


def test_comparison_rejects_duplicate_ids():

    data = load_experiments()

    experiment_id = data["experiment_id"].iloc[0]

    try:
        compare_experiments(
            data,
            [experiment_id, experiment_id]
        )

        assert False, "Expected ValueError"

    except ValueError:
        pass
