# FlameGuard 🔥🚀
### AI-Powered Spacecraft Fire Safety Insights from Microgravity Combustion Data


**FlameGuard** is a research-oriented decision-support prototype developed by **Team NST (Karachi)** for the NASA Space Apps Challenge 2026 challenge theme **“Flame in Freefall”** It brings together curated microgravity-combustion experiment data, traceable NASA research passages, text-based evidence retrieval, experiment analytics, and scenario-based evidence review to help users explore what published research says about fire behaviour in spacecraft-relevant environments.

> **Important scientific scope:** FlameGuard is an evidence-discovery and research-support tool. It does not simulate combustion, certify spacecraft fire safety, or calculate a validated probability of ignition, flame spread, or crew risk. Scenario results should be interpreted as research evidence and evidence gaps requiring expert review—not as physical fire-hazard predictions.

---

## Contents

- [The Challenge](#the-challenge)
- [Why FlameGuard](#why-flameguard)
- [Key Capabilities](#key-capabilities)
- [How It Works](#how-it-works)
- [Scientific Data and Sources](#scientific-data-and-sources)
- [Application Areas](#application-areas)
- [Technology](#technology)
- [Getting Started](#getting-started)
- [Using FlameGuard](#using-flameguard)
- [Quality Assurance](#quality-assurance)
- [Scientific Limitations](#scientific-limitations)
- [Team](#team)
- [Acknowledgements](#acknowledgements)
- [Project Status and Roadmap](#project-status-and-roadmap)
- [License](#license)

---

## The Challenge

Fire behaves differently in microgravity than it does under normal terrestrial gravity. The absence of buoyancy-driven convection changes flame shape, airflow interactions, heat transfer, and the transport of combustion products. This makes it important to understand experimental evidence gathered in space-relevant conditions when studying fire safety for crewed spacecraft and future exploration missions.

The project responds to the NASA Space Apps Challenge 2026 theme **“Flame in Freefall: Microgravity Combustion Data”** by organizing research evidence and making it easier to discover relevant experiments and technical findings.

Challenge information: [NASA Space Apps Challenge 2026 – Challenges](https://www.spaceappschallenge.org/2026/challenges/)

## Why FlameGuard

Scientific information about microgravity combustion is distributed across experiment datasets, technical reports, and research publications. Finding the right experiment or passage for a particular material, airflow condition, or combustion question can take time.

FlameGuard aims to make this process more accessible by:

- organizing curated experiment records in a consistent structure;
- preserving source traceability for research statements;
- retrieving relevant NASA research passages from natural-language queries;
- presenting descriptive views of the available dataset and its coverage; and
- connecting scenario inputs to relevant evidence while explicitly identifying uncertainty and missing data.

## Key Capabilities

### 1. Curated experiment data

The project data-ingestion layer loads a curated set of **15 microgravity combustion experiments** and standardizes missing values as `not reported` rather than inventing or inferring scientific measurements. The dataset covers work associated with:

- **FLEX**
- **BASS-II**
- **ACME / BRE**
- **CIR**

The curated experiment CSV contains **17 standardized scientific parameters**, according to the engineering handoff report.

### 2. NASA research passage retrieval

The retrieval engine uses **TF-IDF** and **cosine similarity** to find relevant passages in response to a user's text query. The documented research corpus contains **50 exact NASA technical sentences**. Retrieved results retain structured citation metadata, including source document details, page and section references, and other fields in the underlying record.

### 3. Scenario-based evidence review

The scenario evaluator accepts spacecraft fire-safety context such as:

- oxygen percentage;
- airflow speed; and
- material.

It builds a research query, retrieves related NASA experiments/passages, and communicates limitations where the available evidence does not adequately cover the scenario. The output is intended to help prioritize further evidence review—not to predict the physical danger of a fire.

### 4. Research analytics

The analytics workstream adds dataset-driven summaries, distributions, and data-coverage views. These describe what is present in the curated dataset; they should not be mistaken for experimentally validated risk scores.

### 5. Evidence ranking and evidence-gap prioritization

The ranking workstream separates two related but different tasks:

- **Evidence ranking:** ordering research results using text relevance, evidence strength, and record completeness.
- **Scenario evidence prioritization:** highlighting scenarios that deserve further review based on the availability, relevance, and strength of supporting evidence, as well as uncertainty and data gaps.

The documented ranking design uses the following weighted evidence-ranking components:

| Component | Weight |
|---|---:|
| Text relevance | 50% |
| Evidence strength | 30% |
| Record completeness | 20% |

These weights rank the usefulness of retrieved evidence; they are **not fire-risk probabilities or physical hazard weights**.

---

## How It Works

At a high level, the application follows this research workflow:

```text
User question or scenario
          |
          v
   Input preparation
          |
          +------------------------------+
          |                              |
          v                              v
 Curated experiment data         NASA research passages
          |                              |
          v                              v
 Data loading / cleaning          TF-IDF retrieval
          |                       + cosine similarity
          |                              |
          +---------------+--------------+
                          |
                          v
             Relevant evidence and metadata
                          |
                          v
              Scenario / analytics review
                          |
                          v
          Results, source traceability,
          limitations and evidence gaps
```

### Data ingestion

`modules/data_loader.py` loads the structured experiment dataset and handles missing values defensively. Missing scientific values are represented as `not reported`; the application does not fill them with guessed measurements.

### Passage retrieval

`modules/retrieval_engine.py` compares a query with the research passage corpus using TF-IDF vectors and cosine similarity. Results are returned with structured source metadata so that users can trace a finding back to its publication.

### Scenario retrieval

`modules/scenario_retrieval.py` converts scenario details into a retrieval query, finds related research evidence, and applies limitation messaging when the evidence base is incomplete or does not directly cover the requested conditions.

### Analytics and ranking

The analytics module summarizes the available records and their coverage. The ranking module provides explainable ordering of retrieved evidence and evidence-review priorities. These functions are deliberately kept distinct from physical combustion modelling.

---

## Scientific Data and Sources

The engineering handoff documents the following curated resources:

| Resource | Documented contents |
|---|---|
| `data/combustion_experiments.csv` | 15 experiments and 17 standardized scientific parameters |
| `data/research_passages.csv` | 50 exact NASA technical sentences with document title, page number, and section references |
| `data/research_source_register.csv` | 12 verified NASA NTRS / NASA Science publications with direct source links |

The experiment collection includes research associated with FLEX, BASS-II, ACME/BRE, and CIR.

### Source traceability

FlameGuard is designed to preserve research provenance. Retrieved passages are associated with publication metadata rather than being presented as unattributed generated facts. Users should consult the original NASA publication for full experimental context, methodology, and interpretation.

Useful starting points:

- [NASA Technical Reports Server (NTRS)](https://ntrs.nasa.gov/)
- [NASA Science](https://science.nasa.gov/)
- [NASA Space Apps Challenge 2026](https://www.spaceappschallenge.org/)

**Data note:** The documented project state also includes an `experimental_measurements.csv` file that was reported as empty during development. Therefore, analytics based on the curated experiment metadata must not be represented as analysis of a complete raw measurement time series. Confirm the current repository contents before relying on any dataset counts or filenames.

---

## Application Areas

FlameGuard is intended to support exploration and research workflows such as:

- locating published microgravity combustion experiments relevant to a material or condition;
- discovering NASA passages related to a combustion question;
- comparing the coverage of available experiment records;
- identifying where the current evidence base does not directly address a scenario; and
- helping researchers decide which questions require additional literature review or experimental evidence.

It is not a substitute for spacecraft fire-safety procedures, engineering certification, mission operations guidance, or expert hazard analysis.

---

## Technology

The documented implementation uses:

- **Python 3** for application and data-processing logic;
- **TF-IDF** for text feature extraction;
- **Cosine similarity** for passage relevance retrieval;
- **CSV** for curated experiment, passage, and source-register datasets;
- **Automated tests** for retrieval, scenario handling, and evidence validation; and
- **Git / GitHub** for source control and collaborative development.

The application work described in project discussions includes a multi-page interface with these areas:

1. Experiment Explorer
2. Research Analytics
3. AI Research Assistant
4. Safety Scenario Evaluator

The exact UI framework and dependency versions should be taken from the current repository's dependency files rather than inferred from this overview.

---

## Getting Started

### Prerequisites

- Python 3
- Git
- A terminal / command prompt

### 1. Clone the repository

```bash
git clone https://github.com/khan123318/FlameGuard.git
cd FlameGuard
```

If the repository is private, GitHub access must be granted to your account. Once the project is public, the same clone command can be used without private-repository permissions.

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

If the current application requires environment variables, create a local `.env` file using the variable names documented in the project's example configuration (if provided).

Do not commit `.env`, API keys, credentials, or other secrets. Keep the `.env` file ignored by Git and publish only a safe example file such as `.env.example`.

### 5. Run the application

The exact launch command depends on the UI framework and entry point in the current branch. For a Streamlit entry point named `app.py`, the command is:

```bash
streamlit run app.py
```

Use this command only if Streamlit is listed in `requirements.txt` and `app.py` is the actual Streamlit application entry point.

---

## Using FlameGuard

A typical exploration flow is:

1. Open the application and navigate to the Experiment Explorer.
2. Browse the curated experiment records and inspect their reported parameters.
3. Open Research Analytics to review dataset distributions and coverage.
4. Ask a research question in the AI Research Assistant to retrieve related passages.
5. Open the Safety Scenario Evaluator and enter the scenario parameters supported by the interface.
6. Review the returned evidence, source metadata, warnings, and missing-data limitations.
7. Follow the source references to the original NASA publications before drawing scientific conclusions.

The precise controls and available filters may vary by version.

---

## Quality Assurance

The engineering contribution report records the following verification results for the delivered ingestion, retrieval, and scenario-retrieval components:

| Test / validation | Reported result | What it checks |
|---|---:|---|
| `tests/test_retrieval.py` | 7 / 7 passed | Cool-flame queries, SIBAL fabric blow-off, gaseous-burner emulation, filters, schema completeness, and rejection of nonsense queries |
| `tests/test_scenario_retrieval.py` | 4 / 4 passed | Polymer hazard ranking, unknown-material limitation warning, electrical-fire dataset gap flagging, and safe handling of empty scenarios |
| Member 1 evidence validator | 65 / 65 records valid | Scientific test questions and strict HTTPS NASA-source verification |

The report states that all listed suites passed at the time of the handoff. Re-run the tests against the current checkout before publishing a new release:

```bash
python -m pytest
```

If `pytest` is not installed in the active environment:

```bash
pip install pytest
```

---

## Scientific Limitations

Responsible interpretation is central to FlameGuard.

- **Not a fire simulator:** the application does not solve combustion equations or simulate flame dynamics.
- **Not a validated risk model:** a retrieved match or ranking is not a probability of ignition, flame spread, or injury.
- **Evidence depends on the corpus:** retrieval quality is limited by the included publications and curated passages.
- **Missing data stays missing:** absent measurements are not estimated or silently filled.
- **Scenario coverage can be incomplete:** a material or condition may not have a directly comparable experiment.
- **Context matters:** experimental scale, apparatus, material preparation, atmosphere, airflow, and measurement methods affect how findings should be interpreted.
- **Expert review is necessary:** mission-level safety decisions require qualified engineering analysis and authoritative procedures.

FlameGuard should be used to find and organize evidence, expose limitations, and support further investigation.

---

## Team

**Team NST X — Karachi, Pakistan**

| Team member |
|---|---|
| **Waheeba Khan** |
| **Syed Abdullah Hussain** |
| **Faraz Ur Rehman** |
| **Farhan Rana** |
| **Amna Bibi** |
| **Talha Ahmed** |

The project was developed collaboratively. The table lists the members and roles explicitly identified in the available engineering handoff; add the remaining team members and their approved roles here before public release.

### Engineering contribution highlighted in the handoff

The report attributes the following delivered work to Syed Abdullah Hussain:

- data ingestion and missing-value handling;
- curated NASA research passage corpus and source register;
- TF-IDF / cosine-similarity passage retrieval;
- scenario-based research retrieval with explicit limitations; and
- associated automated tests and dataset curation.

The handoff records 13 commits and more than 1,350 lines of production code and structured datasets for that contribution, merged to `main` at commit `97b8a80` on 13 November 2026.

---

## Acknowledgements

- **NASA** and the **NASA Space Apps Challenge** for the challenge and publicly available scientific resources.
- NASA researchers and mission teams whose published work on microgravity combustion makes evidence-based exploration possible.
- **Team NST X** for project development and collaboration.

## Project Status and Roadmap

The engineering handoff documents the ingestion, curated research corpus, retrieval engine, and scenario-retrieval evaluator as completed and tested. Project discussions also describe analytics, experiment comparison, evidence ranking, an AI research assistant, and a four-page research interface. These additional interface and feature workstreams have evolved on separate feature branches; confirm the current `main` branch and run the full test suite before treating every listed component as part of a released build.

Potential next steps include:

- expanding the curated experiment and publication corpus;
- adding measured experimental data where reliable source datasets are available;
- improving experiment comparison and filtering;
- making evidence-ranking explanations more transparent;
- strengthening coverage and uncertainty reporting; and
- adding further tests as new datasets and features are introduced.

These are future-development directions, not claims that the work is already complete.

---

## License
## 📄 License

This project is licensed under the **MIT License**.

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the conditions of the MIT License.

The MIT License requires that the original copyright notice and permission notice be included in all copies or substantial portions of the software.

**Note:** FlameGuard is an educational and research-oriented project developed for the NASA Space Apps Challenge 2026. Its outputs are intended for research and informational purposes and should not be treated as certified spacecraft fire-safety recommendations.
---

## Project Links

- **GitHub repository:** [khan123318/FlameGuard](https://github.com/khan123318/FlameGuard)
- **NASA Space Apps Challenge:** [spaceappschallenge.org](https://www.spaceappschallenge.org/)
- **NASA NTRS:** [ntrs.nasa.gov](https://ntrs.nasa.gov/)

