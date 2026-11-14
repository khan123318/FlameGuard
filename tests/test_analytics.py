
import pandas as pd
import pytest

from modules.analytics import (

    COVERAGE_FIELDS,
    get_experiment_data,
    get_overview_metrics,
    get_category_distribution,
    get_data_coverage,
    get_findings_status_distribution,
    get_evidence_type_distribution,
    _is_missing_value,
    _classify_findings_status,
    _classify_evidence_type,
    _classify_coverage_value,
)


def test_get_experiment_data():
    df = get_experiment_data()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 15
    assert "experiment_id" in df.columns


def test_overview_metrics():
    df = pd.DataFrame({
        "research_program": ["FLEX", "BASS-II", "FLEX"],
        "evidence_level": ["Observation", "Simulation", "Observation"],
        "fuel_material": ["Methanol", "PMMA", "Methanol"],
    })

    result = get_overview_metrics(df)

    assert result == {
        "total_experiments": 3,
        "research_programs": 2,
        "evidence_levels": 2,
        "fuel_material_entries": 2,
    }


def test_overview_metrics_empty_dataframe():
    result = get_overview_metrics(pd.DataFrame())

    assert result["total_experiments"] == 0
    assert result["research_programs"] == 0


def test_missing_value_detection():
    assert _is_missing_value(None)
    assert _is_missing_value("not reported")
    assert _is_missing_value("Not stated in sources")
    assert _is_missing_value("unknown")
    assert not _is_missing_value("Methanol")
    assert not _is_missing_value("O2/N2 at 1 atm")


def test_category_distribution():
    df = pd.DataFrame({
        "research_program": ["FLEX", "BASS-II", "FLEX", "not reported"]
    })

    result = get_category_distribution(df, "research_program")

    counts = dict(zip(result["category"], result["count"]))

    assert counts == {"FLEX": 2, "BASS-II": 1}


def test_category_distribution_invalid_column():
    df = pd.DataFrame({"research_program": ["FLEX"]})

    result = get_category_distribution(df, "invalid_column")

    assert list(result.columns) == ["category", "count"]
    assert result.empty


def test_data_coverage():
    df = pd.DataFrame({
        "research_program": ["FLEX", "BASS-II", "not reported"],
        "fuel_material": ["Methanol", "PMMA", "Heptane"],
        "environment": ["1 atm", "not stated", "0.7 atm"],
        "variables_studied": ["Oxygen", "Flow", "Oxygen"],
        "findings": ["Result A", "Result B", "Result C"],
        "safety_relevance": ["Relevant", "Relevant", "not reported"],
        "evidence_level": ["Observation", "Simulation", "Theory"],
        "limitations": ["None", "Unknown", "Limited"],
    })

    result = get_data_coverage(df)

    program = result[result["field"] == "research_program"].iloc[0]
    environment = result[result["field"] == "environment"].iloc[0]

    assert program["reported"] == 2
    assert program["explicitly_unavailable"] == 1
    assert program["coverage_percent"] == 100.0
    
    assert environment["reported"] == 2
    assert environment["explicitly_unavailable"] == 1
    assert environment["missing"] == 0
    assert environment["coverage_percent"] == 100.0

def test_findings_status_classification():
    row = pd.Series({
        "evidence_level": "Planned or descriptive",
        "experiment_type": "Planned experiment",
        "findings": "No results.",
    })

    assert (
        _classify_findings_status(row)
        == "Planned; no results reported"
    )

def test_evidence_type_classification():
    row = pd.Series({
        "evidence_level": "Simulation",
        "experiment_type": "Numerical simulation",
    })

    assert _classify_evidence_type(row) == "Simulation"

def test_findings_status_distribution():
    df = pd.DataFrame({
        "evidence_level": ["Planned", "Simulation"],
        "experiment_type": ["Planned experiment", "Numerical simulation"],
        "findings": ["No results", "Simulation results reported"],
    })

    result = get_findings_status_distribution(df)

    assert result["count"].sum() == 2

def test_evidence_type_distribution():
    df = pd.DataFrame({
        "evidence_level": ["Simulation", "Theory", "Planned"],
        "experiment_type": [
            "Numerical simulation",
            "Analytical theory",
            "Planned experiment",
        ],
    })

    result = get_evidence_type_distribution(df)

    assert result["count"].sum() == 3

def test_missing_value_detection_preserves_partial_information():
    assert _is_missing_value("Not stated in S2") is True
    assert _is_missing_value("Unknown fuel; methanol") is False
    assert _is_missing_value("Methanol; oxygen concentration unknown") is False
    assert _is_missing_value("None stated. Additional context is available.") is False

def test_data_coverage_empty_dataframe():
    df = pd.DataFrame(columns=COVERAGE_FIELDS)

    result = get_data_coverage(df)

    assert not result.empty
    assert (result["reported"] == 0).all()
    # assert (result["not_reported"] == 0).all()
    
    assert (result["explicitly_unavailable"] == 0).all()
    assert (result["missing"] == 0).all()
    assert (result["coverage_percent"] == 0.0).all()


def test_data_coverage_missing_column():
    df = pd.DataFrame({
        "research_program": ["FLEX", "BASS-II"]
    })

    result = get_data_coverage(df)

    assert "research_program" in result["field"].values
    assert "fuel_material" not in result["field"].values



def test_coverage_classification():
    assert _classify_coverage_value("Methanol") == "reported"
    assert _classify_coverage_value("Indirect") == "reported"
    assert _classify_coverage_value("No data; see source") == "reported"

    assert (
        _classify_coverage_value("Not stated in S2")
        == "explicitly_unavailable"
    )
    assert (
        _classify_coverage_value("No measured results in sources read")
        == "explicitly_unavailable"
    )
    assert (
        _classify_coverage_value("None stated")
        == "explicitly_unavailable"
    )

    assert (
    _classify_coverage_value(
        "A test point ran, but no measured results were available."
    )
    == "explicitly_unavailable"
    )

    assert _classify_coverage_value("") == "missing"
    assert _classify_coverage_value(None) == "missing"
    assert _classify_coverage_value("unknown") == "missing"


def test_actual_dataset_coverage():
    df = get_experiment_data()
    coverage = get_data_coverage(df)

    environment = coverage[
        coverage["field"] == "environment"
    ].iloc[0]

    findings = coverage[
        coverage["field"] == "findings"
    ].iloc[0]

    safety = coverage[
        coverage["field"] == "safety_relevance"
    ].iloc[0]

    assert environment["reported"] == 13
    assert environment["explicitly_unavailable"] == 2

    assert findings["reported"] == 13
    assert findings["explicitly_unavailable"] == 2

    assert safety["reported"] == 14
    assert safety["explicitly_unavailable"] == 1