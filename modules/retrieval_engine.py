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


def build_index(df):
    text = df[SEARCH_COLUMNS].astype(str).agg(" ".join, axis=1)
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(text)
    return vectorizer, matrix


def search(query, top_k=5):
    df = load_experiments()
    vectorizer, matrix = build_index(df)
    scores = cosine_similarity(vectorizer.transform([query]), matrix).ravel()
    df = df.assign(relevance_score=scores.round(3))
    df = df[df["relevance_score"] > 0]
    return df.sort_values("relevance_score", ascending=False).head(top_k)


if __name__ == "__main__":
    for q in ["cool flame extinction", "fabric blow-off oxygen", "gaseous fuel burner"]:
        print("\nQuery:", q)
        result = search(q)
        print(result[["experiment_id", "research_program", "relevance_score"]].to_string(index=False))