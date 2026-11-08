import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from modules.data_loader import load_experiments, DATA_DIR
except ImportError:
    from data_loader import load_experiments, DATA_DIR

SEARCH_COLUMNS = [
    "experiment_name", "objective", "fuel_material", "environment",
    "variables_studied", "findings", "safety_relevance", "limitations",
]

OUTPUT_FIELDS = [
    "passage_id", "experiment_id", "experiment_name", "research_program",
    "fuel_material", "findings", "safety_relevance", "evidence_level",
    "limitations", "source_title", "source_type", "source_url",
    "page_number", "section_name", "matched_passage", "relevance_score",
]

PASSAGE_KEEP = [
    "passage_id", "experiment_id", "source_title", "passage_source_type",
    "page_number", "section_name", "matched_passage",
]


def load_passages():
    path = DATA_DIR / "research_passages.csv"
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=PASSAGE_KEEP)
    df = df.rename(columns={"source_type": "passage_source_type", "passage_text": "matched_passage"})
    return df[PASSAGE_KEEP]


def build_records():
    experiments = load_experiments()
    records = experiments.merge(load_passages(), on="experiment_id", how="left")
    records["source_type"] = records["passage_source_type"].fillna(records["source_type"])
    records["page_number"] = records["page_number"].apply(
        lambda v: "not reported" if pd.isna(v) else int(v))
    for col in ["passage_id", "source_title", "section_name", "matched_passage"]:
        records[col] = records[col].fillna("not reported")
    return records


def apply_filters(df, filters):
    if not filters:
        return df
    for column, value in filters.items():
        if column in df.columns:
            df = df[df[column].astype(str).str.contains(str(value), case=False, regex=False)]
    return df


def search(query, filters=None, top_k=5):
    records = build_records()
    passage_text = records["matched_passage"].where(records["matched_passage"] != "not reported", "")
    text = records[SEARCH_COLUMNS].astype(str).agg(" ".join, axis=1) + " " + passage_text
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(text)
    scores = cosine_similarity(vectorizer.transform([query]), matrix).ravel()
    records = records.assign(relevance_score=scores.round(3))
    records = apply_filters(records, filters)
    records = records[records["relevance_score"] > 0]
    return records.sort_values("relevance_score", ascending=False).head(top_k)


def retrieve_research(query, filters=None, top_k=5):
    result = search(query, filters, top_k)
    return result[OUTPUT_FIELDS].to_dict("records")


if __name__ == "__main__":
    tests = [
        ("cool flame extinction", None),
        ("SIBAL fabric blow-off", None),
        ("flame spread", {"research_program": "BASS"}),
    ]
    for q, f in tests:
        print("\nQuery:", q, "| filters:", f)
        out = search(q, f)
        print(out[["experiment_id", "passage_id", "page_number", "relevance_score"]].to_string(index=False))
    top = retrieve_research("SIBAL fabric blow-off", top_k=3)
    print("\nretrieve_research returned", len(top), "records")
    print("Fields:", list(top[0].keys()))
    print("Best passage:", top[0]["matched_passage"])
    print("From:", top[0]["source_title"], "| page", top[0]["page_number"], "|", top[0]["section_name"])