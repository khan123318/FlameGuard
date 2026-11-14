# 🔥 FlameGuard

**AI-Powered Spacecraft Fire Safety Insights from Microgravity Combustion Data**  
*NASA Space Apps Challenge 2026 · Team NST (Karachi)*  
*Challenge Theme: "Flame in Freefall: Microgravity Combustion Data"*

---

## 🚀 Overview

Fire behaves fundamentally differently in microgravity. Without buoyancy-driven convection, flames do not rise; they form spherically symmetric diffusion zones, burn with low convective heat release, rely completely on forced cabin ventilation, and can sustain low-temperature, invisible **cool flames** that persist after visible extinction.

**FlameGuard** turns decades of complex NASA orbital combustion research into an accessible, searchable, and evidence-grounded safety engineering dashboard. The system enables spacecraft engineers and researchers to query microgravity findings, evaluate mission fire scenarios against empirical test data, and explore multi-parameter combustion analytics—strictly citing primary NASA technical publications with exact page and section citations.

---

## 🏛️ System Architecture

```
NASA Primary Literature (NTRS / Science.nasa.gov)
   │
   ├── data/research_source_register.csv   (12 Cataloged NASA Sources)
   ├── data/combustion_experiments.csv     (15 Experiments × 17 Parameters)
   └── data/research_passages.csv          (50 Exact Passages with Page & Section)
        │
        ├── modules/data_loader.py          ── Load, clean & enforce "not reported"
        ├── modules/retrieval_engine.py     ── Passage-level TF-IDF & Cosine Similarity (16 Fields)
        ├── modules/scenario_retrieval.py   ── Scenario mapping & NASA limitation hedges
        ├── modules/analytics.py            ── Distributions, evidence types & completeness
        └── modules/ai_assistant.py         ── Evidence-grounded synthesis (zero hallucination)
             │
             └── Streamlit Dashboard UI:
                  ├── app.py                               ── Mission Overview & Home
                  ├── pages/1_Experiment_Explorer.py       ── Multi-Attribute Search & Filter
                  ├── pages/2_Research_Analytics.py        ── Visual Distributions & Coverage
                  ├── pages/3_AI_Research_Assistant.py     ── Grounded Q&A with NASA Citations
                  └── pages/4_Safety_Scenario_Evaluator.py ── Mission Fire Risk & Parameter Assessment
```

---

## 👥 Team Roles & Responsibilities

| Role | Member | Responsibilities |
|---|---|---|
| **Member 1 (Team Lead)** | **Waheeba Khan** | Application architecture, Streamlit UI, Gemini assistant integration, evidence validator, analytics backend. |
| **Member 2 (AI & Data Engineer)** | **Syed Abdullah Hussain** | Dataset curation & schema design, passage-level TF-IDF retrieval engine, scenario retrieval & limitation hedges, test engineering. |
| **Member 3 (Materials Specialist)** | **Talha** | Solid combustion research, BASS-II acrylic polymers (thin film, rods, flat samples), SIBAL fabric, ACME-BRE emulation. |
| **Member 4 (Combustion Physics)** | **Farhan** | Microgravity droplet combustion, FLEX & FLEX-2 experiments, limiting oxygen index (LOI), cool-flame second stage burning. |
| **Member 5 (Numerical Data)** | **Amna** | Quantitative combustion measurements, burning rates, fuel droplet extinction diameters. |
| **Member 6 (Spacecraft Safety)** | **Faraz Ur Rehman** | Mission fire scenarios, forced ventilation flows, Saffire Cygnus large-scale tests, toxic gas (CO/CO₂) risk analysis. |

---

## 📊 Curated NASA Datasets

1. **`data/combustion_experiments.csv` (15 Records × 17 Columns):**  
   Standardized parameters across **FLEX, FLEX-2, BASS-II, ACME/BRE, and CIR**:
   - `experiment_id`, `experiment_name`, `research_program`, `objective`, `experiment_type`, `fuel_material`, `environment`, `variables_studied`, `findings`, `safety_relevance`, `source_url`, `source_type`, `evidence_level`, `limitations`, `material_class`, `geometry`, `evidence_location`.
2. **`data/research_passages.csv` (50 Passages):**  
   Exact technical sentences extracted directly from NASA Technical Publications, Technical Memorandums, and conference proceedings, preserving `source_title`, `page_number`, `section_name`, and clean `source_url`.
3. **`data/research_source_register.csv` (12 Sources):**  
   Catalog of official NASA publications from `ntrs.nasa.gov` and `science.nasa.gov`.

> **Zero Hallucination Policy:** If a scientific parameter or burning rate was not measured or stated in the primary NASA literature, it is strictly recorded as `"not reported"` rather than extrapolated or guessed.

---

## 🛡️ Spacecraft Safety Scenario Evaluator

The **Safety Scenario Evaluator** (`pages/4_Safety_Scenario_Evaluator.py` & `modules/scenario_retrieval.py`) models critical mission conditions:
- **Oxygen Concentration:** 0–100% vol (ISS norm 21%, exploration/EVA pre-breathe 30–34%)
- **Forced Ventilation Speed:** 0–1 m/s (BASS and Saffire flight flows 5–20 cm/s)
- **Cabin Pressure:** 10 to 101.3 kPa
- **Fuel Materials:** PMMA acrylics, SIBAL cotton-fiberglass composite fabric, liquid n-alkanes

### Enforced Safety Limitations & Data Gaps:
- **Condition-Specific Warning:** Evidence from controlled microgravity tests does not constitute a vehicle safety certification or universal flammability threshold.
- **Electrical Fire Data Gap:** Automatically detects queries for avionics wiring insulation and flags that NASA public orbital research focuses on pure droplets and structural coupons, preventing false safety assurances.
- **Toxic Gas Spikes:** Highlights that microgravity fires produce significant CO₂ (>8,000 ppm) and CO build-up without massive pressure rises, making crew toxicity the dominant hazard.

---

## 🧪 Verification & Automated Testing

FlameGuard features a comprehensive test suite with **23 automated unit tests** achieving a **100% pass rate**:

```bash
# Run all unit tests
python tests/test_data.py                  # 8/8 PASS: Schema integrity & NASA HTTPS links
python tests/test_retrieval.py             # 7/7 PASS: TF-IDF scoring & filter precision
python tests/test_scenario_retrieval.py    # 4/4 PASS: Scenario queries & limitation hedges
python tests/test_scenario_evaluator.py    # 4/4 PASS: UI presets & safe error handling
python tests/test_ai_assistant.py          # PASS: Grounded evidence structure
```

### Independent Blind Evaluation
A 10-question independent blind test suite evaluated realistic external queries not copied from dataset phrasing (e.g. SIBAL fabric blow-off, droplet vaporization without flame, CO₂ suppression). The retrieval engine achieved **10 of 10 Top-3 HITs (100% accuracy)**.

---

## 💻 Getting Started

### Prerequisites
- Python 3.10+ (tested on Python 3.14.6)
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/khan123318/FlameGuard.git
cd FlameGuard

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run app.py
```
Access the dashboard in your web browser at `http://localhost:8501`.

---

## 📜 Official Publications & References
- NASA/TP-2015-216046: *Detailed Results from the Flame Extinguishment Experiment (FLEX)*
- NASA/TM-20210011385: *Burning and Suppression of Solids-II (BASS-II) Summary Report*
- Nayagam et al. (2014): *Cool-flame extinction during n-alkane droplet combustion in microgravity*
- Hickman et al. (2012): *FLEX: A Decisive Step Forward in NASA's Combustion Research Program*
- NASA Science: *Burning Rate Emulator (BRE)* & *ACME Flight Investigations*
- NASA Saffire Flight Results: *Spacecraft Fire Safety Demonstration Project (Cygnus Flights)*

---
*Developed for NASA Space Apps Challenge 2026 · Team NST (Karachi)*
