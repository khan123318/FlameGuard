import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from modules.retrieval_engine import retrieve_research, OUTPUT_FIELDS


def test_cool_flame_query_finds_flex_005():
    result = retrieve_research("cool flame extinction")
    assert result[0]["experiment_id"] == "FG-FLEX-005"


def test_fabric_query_finds_sibal():
    result = retrieve_research("SIBAL fabric blow-off")
    assert result[0]["experiment_id"] == "FG-BASS2-004"


def test_gaseous_burner_query_finds_bre():
    ids = [r["experiment_id"] for r in retrieve_research("gaseous fuel burner", top_k=3)]
    assert "FG-BRE-001" in ids


def test_program_filter_keeps_only_bass():
    result = retrieve_research("flame spread", {"research_program": "BASS"})
    assert len(result) > 0
    assert all("BASS" in r["research_program"] for r in result)


def test_records_have_all_fields_and_source():
    for r in retrieve_research("flame extinction", top_k=5):
        assert list(r.keys()) == OUTPUT_FIELDS
        assert r["source_url"].startswith("http")
        assert r["experiment_name"] != ""


def test_passage_has_page_and_text():
    top = retrieve_research("SIBAL fabric blow-off")[0]
    assert top["matched_passage"] != "not reported"
    assert isinstance(top["page_number"], int)


def test_nonsense_query_returns_nothing():
    assert retrieve_research("zzzz qqqq") == []


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