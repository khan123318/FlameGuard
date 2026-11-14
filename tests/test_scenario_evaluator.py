import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from modules.scenario_retrieval import retrieve_for_scenario


def test_preset_scenario_a_electrical_gap():
    scenario = {
        "scenario_type": "Electrical equipment fire",
        "fuel_or_material": "Wiring insulation",
        "description": "Overheating wiring insulation in habitable compartment under low air circulation",
        "oxygen_percent": 21.0,
        "air_velocity_m_s": 0.05,
    }
    res = retrieve_for_scenario(scenario)
    assert res["query"] != ""
    assert any("electrical" in lim.lower() for lim in res["limitations"])
    assert any("certification" in lim.lower() for lim in res["limitations"])


def test_preset_scenario_b_pmma_finds_bass2():
    scenario = {
        "scenario_type": "Solid material flame spread",
        "fuel_or_material": "PMMA",
        "description": "Flame spread over plastic sample in opposed ventilation",
        "oxygen_percent": 21.0,
        "air_velocity_m_s": 0.10,
    }
    res = retrieve_for_scenario(scenario)
    assert len(res["evidence"]) > 0
    eids = [r["experiment_id"] for r in res["evidence"]]
    assert any(eid.startswith("FG-BASS2") for eid in eids)


def test_preset_scenario_c_sibal_finds_sibal_experiment():
    scenario = {
        "scenario_type": "Solid material flame spread",
        "fuel_or_material": "SIBAL fabric",
        "description": "Combustion and blow-off extinction behavior of cotton-fiberglass blend",
        "oxygen_percent": 18.0,
        "air_velocity_m_s": 0.20,
    }
    res = retrieve_for_scenario(scenario)
    assert len(res["evidence"]) > 0
    assert res["evidence"][0]["experiment_id"] == "FG-BASS2-004"


def test_empty_scenario_safe_handling():
    res = retrieve_for_scenario({})
    assert res["query"] == ""
    assert res["evidence"] == []
    assert len(res["limitations"]) > 0


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
