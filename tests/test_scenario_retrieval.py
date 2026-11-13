import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from modules.scenario_retrieval import retrieve_for_scenario


def test_material_scenario_finds_bass_evidence():
    result = retrieve_for_scenario({"fuel_or_material": "PMMA", "description": "flame spread",
                                    "oxygen_percent": 21, "air_velocity_m_s": 0.1})
    assert any(r["experiment_id"].startswith("FG-BASS2") for r in result["evidence"])


def test_unknown_material_is_reported_as_a_limitation():
    result = retrieve_for_scenario({"fuel_or_material": "wood", "description": "fire spread"})
    assert any("wood" in text for text in result["limitations"])


def test_electrical_scenario_states_dataset_gap():
    result = retrieve_for_scenario({"scenario_type": "electrical equipment fire",
                                    "description": "overheating insulation", "oxygen_percent": 21})
    assert any("electrical" in text for text in result["limitations"])


def test_empty_scenario_does_not_crash():
    result = retrieve_for_scenario({})
    assert result["evidence"] == [] and result["limitations"]


if __name__ == "__main__":
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_")]
    passed = 0
    for name, func in tests:
        try:
            func()
            print("PASS", name)
            passed += 1
        except AssertionError:
            print("FAIL", name)
    print(passed, "of", len(tests), "tests passed")