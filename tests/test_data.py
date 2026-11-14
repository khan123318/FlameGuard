import sys
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
DATA = ROOT / "data"


def read(name):
    return pd.read_csv(DATA / name, encoding="utf-8")


def is_nasa_https(url):
    parsed = urlparse(str(url))
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and (host == "nasa.gov" or host.endswith(".nasa.gov"))


def test_experiment_columns_and_unique_ids():
    exp = read("combustion_experiments.csv")
    assert exp.shape[1] == 17
    assert len(exp) >= 15
    assert exp["experiment_id"].is_unique


def test_experiment_urls_are_nasa_https():
    exp = read("combustion_experiments.csv")
    assert exp["source_url"].map(is_nasa_https).all()


def test_key_experiment_columns_not_empty():
    exp = read("combustion_experiments.csv")
    key = ["experiment_name", "findings", "limitations", "source_url", "evidence_level"]
    assert not exp[key].isna().any().any()


def test_loader_returns_all_experiments():
    from modules.data_loader import load_experiments
    assert len(load_experiments()) == len(read("combustion_experiments.csv"))


def test_passage_ids_unique_and_linked_to_experiments():
    exp = read("combustion_experiments.csv")
    psg = read("research_passages.csv")
    assert psg["passage_id"].is_unique
    assert psg["experiment_id"].isin(exp["experiment_id"]).all()


def test_passages_have_text_page_and_section():
    psg = read("research_passages.csv")
    assert not psg[["passage_text", "page_number", "section_name"]].isna().any().any()
    assert psg["page_number"].map(lambda v: float(v).is_integer()).all()


def test_no_duplicate_passages():
    psg = read("research_passages.csv")
    assert not psg.duplicated(["experiment_id", "passage_text"]).any()


def test_source_register_is_nasa_https_and_unique():
    reg = read("research_source_register.csv")
    assert reg["source_id"].is_unique
    assert reg["source_url"].map(is_nasa_https).all()


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
