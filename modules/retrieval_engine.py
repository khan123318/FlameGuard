import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from modules.data_loader import load_experiments
except ImportError:
    from data_loader import load_experiments

SEARCH_COLUMNS = [
    "experiment_name", "objective", "fuel_material", "environment",
    "variables_studied", "findings", "safety_relevance", "limitations",
]

OUTPUT_FIELDS = [
    "experiment_id", "experiment_name", "research_program", "fuel_material",
    "findings", "safety_relevance", "evidence_level", "limitations",
    "source_url", "relevance_score",
]


def build_index(df):
    text = df[SEARCH_COLUMNS].astype(str).agg(" ".join, axis=1)
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(text)
    return vectorizer, matrix


def apply_filters(df, filters):
    if not filters:
        return df
    for column, value in filters.items():
        if column in df.columns:
            df = df[df[column].astype(str).str.contains(str(value), case=False, regex=False)]
    return df


def search(query, filters=None, top_k=5):
    df = load_experiments()
    vectorizer, matrix = build_index(df)
    scores = cosine_similarity(vectorizer.transform([query]), matrix).ravel()
    df = df.assign(relevance_score=scores.round(3))
    df = apply_filters(df, filters)
    df = df[df["relevance_score"] > 0]
    return df.sort_values("relevance_score", ascending=False).head(top_k)


def retrieve_research(query, filters=None, top_k=5):
    result = search(query, filters, top_k)
    return result[OUTPUT_FIELDS].to_dict("records")


if __name__ == "__main__":
    tests = [
        ("flame spread oxygen", None),
        ("flame spread oxygen", {"research_program": "BASS"}),
        ("extinction", {"research_program": "FLEX"}),
        ("fire safety", {"material_class": "Polymer"}),
    ]
    for q, f in tests:
        print("\nQuery:", q, "| filters:", f)
        out = search(q, f)
        print(out[["experiment_id", "research_program", "relevance_score"]].to_string(index=False))
    records = retrieve_research("cool flame extinction", top_k=3)
    print("\nretrieve_research returned", len(records), "records; fields:", list(records[0].keys()))