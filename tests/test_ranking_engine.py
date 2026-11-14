
import pytest

from modules import ranking_engine


# =========================================================
# EVIDENCE STRENGTH TESTS
# =========================================================

@pytest.mark.parametrize(
    "evidence_level, expected_score",
    [
        ("Reported observation", 100.0),
        ("Reported observation and reported conclusion", 100.0),
        ("Observation (second stage); hypothesis (cool-flame mechanism)", 85.0),
        ("Reported observation; scaling is preliminary theory", 90.0),
        ("Reported observation; trend summary is my tally", 90.0),
        ("Simulation", 65.0),
        ("Theory, with experimental context cited from other papers", 50.0),
        ("Reported observation (secondary summary)", 45.0),
        ("Reported observation (literature review)", 45.0),
        ("Descriptive only (low)", 20.0),
        ("Planned or descriptive (low)", 10.0),
        ("not reported", 0.0),
    ],
)
def test_calculate_evidence_strength(evidence_level, expected_score):
    record = {"evidence_level": evidence_level}

    assert (
        ranking_engine.calculate_evidence_strength(record)
        == expected_score
    )


def test_evidence_strength_rejects_invalid_record():
    with pytest.raises(TypeError):
        ranking_engine.calculate_evidence_strength("invalid")


# =========================================================
# DOCUMENTATION COMPLETENESS TESTS
# =========================================================

def test_completeness_all_fields_reported():
    record = {
        field: "Available information"
        for field in ranking_engine.COMPLETENESS_FIELDS
        
    }
    record["relevance_score"] = 0.5

    assert ranking_engine.calculate_completeness(record) == 100.0


def test_completeness_all_fields_missing():
    record = {
        field: "not reported"
        for field in ranking_engine.COMPLETENESS_FIELDS
    }
    record["relevance_score"] = 0.5

    assert ranking_engine.calculate_completeness(record) == 0.0


def test_completeness_half_fields_reported():
    fields = ranking_engine.COMPLETENESS_FIELDS

    record = {
        field: (
            "Available information"
            if index < len(fields) // 2
            else "not reported"
        )
        for index, field in enumerate(fields)
    }
    record["relevance_score"] = 0.5

    expected = (
        (len(fields) // 2) / len(fields)
    ) * 100

    assert ranking_engine.calculate_completeness(record) == expected


# =========================================================
# EVIDENCE RANKING TESTS
# =========================================================

def test_rank_evidence_orders_records_by_overall_score():
    records = [
        {
            "experiment_id": "EXP-LOW",
            "evidence_level": "Planned or descriptive (low)",
            "relevance_score": 0.2,
        },
        {
            "experiment_id": "EXP-HIGH",
            "evidence_level": "Reported observation",
            "relevance_score": 0.9,
        },
    ]

    ranked = ranking_engine.rank_evidence(records)

    assert ranked[0]["experiment_id"] == "EXP-HIGH"
    assert ranked[1]["experiment_id"] == "EXP-LOW"

    assert ranked[0]["overall_score"] > ranked[1]["overall_score"]


def test_rank_evidence_preserves_original_records():
    records = [
        {
            "experiment_id": "EXP-01",
            "evidence_level": "Simulation",
            "relevance_score": 0.8,
        }
    ]

    original = records[0].copy()

    ranked = ranking_engine.rank_evidence(records)

    assert records[0] == original
    assert "overall_score" not in records[0]
    assert "overall_score" in ranked[0]


def test_rank_evidence_empty_list():
    assert ranking_engine.rank_evidence([]) == []


def test_rank_evidence_rejects_invalid_input():
    with pytest.raises(TypeError):
        ranking_engine.rank_evidence("invalid")


# =========================================================
# SCENARIO PRIORITIZATION TESTS
# =========================================================

def test_scenario_without_evidence_has_maximum_gap(monkeypatch):

    def mock_retrieval(scenario, top_k=5):
        return {
            "query": "unknown material",
            "evidence": [],
            "limitations": ["No matching evidence found."],
        }

    monkeypatch.setattr(
        ranking_engine,
        "retrieve_for_scenario",
        mock_retrieval,
    )

    result = ranking_engine.evaluate_scenario_priority(
        {"fuel_or_material": "Unknown material"}
    )

    assert result["evidence_support_score"] == 0.0
    assert result["evidence_gap_priority"] == 100.0
    assert len(result["evidence_gap_reasons"]) == 1


def test_scenario_with_evidence_gets_support_score(monkeypatch):

    def mock_retrieval(scenario, top_k=5):
        return {
            "query": "PMMA combustion",
            "evidence": [
                {
                    "evidence_level": "Reported observation",
                    "relevance_score": 0.9,
                },
                {
                    "evidence_level": "Reported observation",
                    "relevance_score": 0.8,
                },
                {
                    "evidence_level": "Simulation",
                    "relevance_score": 0.7,
                },
            ],
            "limitations": [],
        }

    monkeypatch.setattr(
        ranking_engine,
        "retrieve_for_scenario",
        mock_retrieval,
    )

    result = ranking_engine.evaluate_scenario_priority(
        {"fuel_or_material": "PMMA"}
    )

    assert result["evidence_support_score"] > 0
    assert result["evidence_gap_priority"] < 100
    assert len(result["evidence"]) == 3


def test_electrical_scenario_gap_is_flagged(monkeypatch):

    def mock_retrieval(scenario, top_k=5):
        return {
            "query": "electrical fire",
            "evidence": [],
            "limitations": [
                "Dataset lacks electrical fire experiments."
            ],
        }

    monkeypatch.setattr(
        ranking_engine,
        "retrieve_for_scenario",
        mock_retrieval,
    )

    result = ranking_engine.evaluate_scenario_priority(
        {"scenario_type": "Electrical equipment"}
    )

    assert result["evidence_gap_priority"] == 100.0
    assert any(
        "electrical" in reason.lower()
        for reason in result["evidence_gap_reasons"]
    )


def test_scenario_priority_rejects_invalid_top_k():

    with pytest.raises(ValueError):
        ranking_engine.evaluate_scenario_priority(
            {},
            top_k=0,
        )


# =========================================================
# MULTIPLE SCENARIO RANKING TESTS
# =========================================================

def test_rank_scenarios_orders_by_evidence_gap(monkeypatch):

    def mock_retrieval(scenario, top_k=5):

        if scenario["scenario_name"] == "Scenario A":
            return {
                "query": "Scenario A",
                "evidence": [
                    {
                        "evidence_level": "Reported observation",
                        "relevance_score": 0.9,
                    },
                    {
                        "evidence_level": "Reported observation",
                        "relevance_score": 0.9,
                    },
                    {
                        "evidence_level": "Reported observation",
                        "relevance_score": 0.9,
                    },
                ],
                "limitations": [],
            }

        return {
            "query": "Scenario B",
            "evidence": [],
            "limitations": ["No matching evidence found."],
        }

    monkeypatch.setattr(
        ranking_engine,
        "retrieve_for_scenario",
        mock_retrieval,
    )

    scenarios = [
        {"scenario_name": "Scenario A"},
        {"scenario_name": "Scenario B"},
    ]

    ranked = ranking_engine.rank_scenarios(scenarios)

    assert ranked[0]["scenario_name"] == "Scenario B"
    assert ranked[1]["scenario_name"] == "Scenario A"

    assert (
        ranked[0]["evidence_gap_priority"]
        > ranked[1]["evidence_gap_priority"]
    )


def test_rank_scenarios_empty_list():
    assert ranking_engine.rank_scenarios([]) == []


def test_rank_scenarios_rejects_invalid_input():

    with pytest.raises(TypeError):
        ranking_engine.rank_scenarios("invalid")

def test_experiment_record_uses_experiment_fields():

    record = {
        field: "Available information"
        for field in ranking_engine.EXPERIMENT_COMPLETENESS_FIELDS
    }

    assert ranking_engine.calculate_completeness(record) == 100.0

def test_rank_experiments_groups_passages_by_experiment():
    records = [
        {
            "experiment_id": "EXP-001",
            "experiment_name": "FLEX nitrogen tests",
            "passage_id": "PSG-001",
            "relevance_component_score": 20,
            "evidence_strength_score": 90,
            "completeness_score": 100,
        },
        {
            "experiment_id": "EXP-001",
            "experiment_name": "FLEX nitrogen tests",
            "passage_id": "PSG-002",
            "relevance_component_score": 10,
            "evidence_strength_score": 90,
            "completeness_score": 100,
        },
        {
            "experiment_id": "EXP-001",
            "experiment_name": "FLEX nitrogen tests",
            "passage_id": "PSG-003",
            "relevance_component_score": 30,
            "evidence_strength_score": 90,
            "completeness_score": 100,
        },
        {
            "experiment_id": "EXP-001",
            "experiment_name": "FLEX nitrogen tests",
            "passage_id": "PSG-004",
            "relevance_component_score": 100,
            "evidence_strength_score": 90,
            "completeness_score": 100,
        },
    ]

    ranked = ranking_engine.rank_experiments(records)

    assert len(ranked) == 1
    assert ranked[0]["experiment_id"] == "EXP-001"
    assert ranked[0]["passage_count"] == 4
    assert ranked[0]["relevance_component_score"] == 50.0
    assert ranked[0]["overall_score"] == 72.0
    assert len(ranked[0]["supporting_passages"]) == 4


def test_rank_experiments_sorts_by_overall_score():
    records = [
        {
            "experiment_id": "EXP-001",
            "experiment_name": "Experiment A",
            "relevance_component_score": 20,
            "evidence_strength_score": 50,
            "completeness_score": 50,
        },
        {
            "experiment_id": "EXP-002",
            "experiment_name": "Experiment B",
            "relevance_component_score": 80,
            "evidence_strength_score": 90,
            "completeness_score": 100,
        },
    ]

    ranked = ranking_engine.rank_experiments(records)

    assert ranked[0]["experiment_id"] == "EXP-002"
    assert ranked[1]["experiment_id"] == "EXP-001"


def test_rank_experiments_empty_records():
    assert ranking_engine.rank_experiments([]) == []


def test_rank_experiments_rejects_invalid_input():
    with pytest.raises(TypeError):
        ranking_engine.rank_experiments("invalid")
