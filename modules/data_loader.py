from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_experiments():
    path = DATA_DIR / "combustion_experiments.csv"
    df = pd.read_csv(path, encoding="utf-8")
    df = df.drop_duplicates(subset="experiment_id")
    df = df.fillna("not reported")
    return df


if __name__ == "__main__":
    data = load_experiments()
    print(len(data), "records loaded")
    print(data[["experiment_id", "research_program"]])