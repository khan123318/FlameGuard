# FlameGuard 🔥

### Evidence discovery for spacecraft fire-safety research, built on NASA microgravity combustion data

**FlameGuard** is a research-support prototype built by **Team NST X (Virtual)** for the NASA Space Apps Challenge 2026 theme **"Flame in Freefall"**. It combines a curated set of microgravity combustion experiments, passages from NASA and related research sources, text-based retrieval, analytics, and scenario-based evidence review. It helps users find what published research says about fire behaviour in spacecraft-relevant conditions, and where the evidence is missing.

> **Scope:** FlameGuard is an evidence-discovery tool. It does not simulate combustion, certify spacecraft fire safety, or calculate the probability of ignition, flame spread or crew risk. Results are research evidence and evidence gaps that need expert review.

---

## What it does

The app is a four-page Streamlit application:

| Page | Purpose |
|---|---|
| **Experiment Explorer** | Search and filter 15 curated experiment records, and compare experiments side by side. |
| **Research Analytics** | Charts and tables describing the curated dataset: programs, evidence types, findings status and field coverage. |
| **AI Research Assistant** | Enter a research question and retrieve the most relevant passages with their sources. |
| **Safety Scenario Evaluator** | Enter a material and conditions (oxygen, airflow, temperature, pressure) and review related evidence and limitations. |

## How it works

```
User question or scenario
        |
        v
 TF-IDF + cosine similarity over research passages
        |
        v
 Relevant passages + experiment records (with source, page, section)
        |
        v
 Ranking, analytics, limitations and evidence-gap warnings
```

- `modules/data_loader.py` loads the experiment table. Values a source does not report are shown as `not reported` and are never estimated.
- `modules/retrieval_engine.py` ranks passages by TF-IDF cosine similarity. Each result carries source, page, section and a relevance score. The score shows text similarity, not scientific certainty.
- `modules/scenario_retrieval.py` turns scenario inputs into a query, retrieves related evidence and adds limitation notes, for example when no retrieved evidence names the material or the query concerns electrical fires, which the dataset does not cover.
- `modules/ranking_engine.py` and `modules/analytics.py` rank evidence and summarize dataset coverage. Ranking weights (text relevance 50%, evidence strength 30%, record completeness 20%) order the usefulness of evidence. They are not fire-risk weights.

## Data and sources

| File | Contents |
|---|---|
| `data/combustion_experiments.csv` | 15 experiments, 17 fields (FLEX, BASS-II, ACME/BRE, CIR) |
| `data/research_passages.csv` | 50 passages with source, page and section: 39 are original text from NASA reports, papers, posters and conference material, and 11 are sentences from our team's research reports that cite NASA |
| `data/research_source_register.csv` | 12 cataloged NASA sources with links. All 12 links responded (HTTP 200) when checked on 15 November 2026. This confirms the pages open, not that every passage was re-read against them |

The analytics describe the curated experiment records. They are not an analysis of raw measurement time series.

## Run it locally

```bash
git clone https://github.com/khan123318/FlameGuard.git
cd FlameGuard
pip install -r requirements.txt
python -m streamlit run app.py
```

The AI Research Assistant can use a Gemini API key. Copy `.env.example` to `.env` and add your key. Never commit `.env` or any API key.

## Tests

```bash
python -m pytest
```

Test files cover the data layer (`test_data.py`, 8 tests), retrieval (`test_retrieval.py`, 7), scenario retrieval (`test_scenario_retrieval.py`, 4), the scenario evaluator (`test_scenario_evaluator.py`, 4), the evidence validator, response schema, ranking engine and analytics. `tests/speed.py` and `tests/test_gemini.py` are helper scripts that need a Gemini key and are not unit tests.

## Limitations

- **Not a fire simulator or a validated risk model.** A match or ranking is not a probability of ignition, spread or injury.
- **Small corpus.** Only 15 experiments and 50 passages, not all microgravity combustion research.
- **Word-based retrieval.** TF-IDF matches words, not meaning. Queries that mix fire-safety wording with material names (for example polymer) can miss relevant passages.
- **Retrieval checks are informal.** We tried a small set of development questions and counted a hit when a relevant passage appeared in the top 3. This is a sanity check, not an independent evaluation.
- **11 of 50 passages come from team reports** that cite NASA, not original NASA text.
- **Coverage gaps.** Missing data stays missing, and some materials or conditions have no comparable experiment (for example, wiring and electrical fires).
- Mission-level safety decisions need qualified engineering analysis.

## Team NST X (Virtual)

| Member | Contribution |
|---|---|
| **Waheeba Khan** (Lead) | Application and pages, analytics, evidence ranking, AI assistant, deployment |
| **Syed Abdullah Hussain** | Dataset assembly, passage retrieval, scenario retrieval, tests |
| **Farhan Rana** | FLEX research records |
| **Talha Ahmed** | BASS-II and BRE materials records |
| **Amna Bibi** | Research contributor |
| **Faraz Ur Rehman** | Research contributor |

## Acknowledgements

NASA and the NASA Space Apps Challenge, and the researchers whose published microgravity combustion work this project builds on.

## License

MIT License. See `LICENSE`.

*FlameGuard is an educational and research project. Its outputs are for information and are not certified spacecraft fire-safety recommendations.*
