# 🔥 FlameGuard — AI & Data Engineering Core

**Project:** FlameGuard (AI-Powered Fire Safety Research Dashboard)  
**Event:** NASA Space Apps Challenge 2026 (Team NST, Karachi)  
**Challenge Theme:** "Flame in Freefall: AI-Powered Fire Safety Insights from Microgravity Combustion Data"  
**Lead AI & Data Engineer (Member 2):** Syed Abdullah Hussain (`ssyedabdullah1050`)

---

## 👨‍💻 Engineering Ownership & Deliverables (Member 2)

As the **AI and Data Engineer (Member 2)**, I was responsible for designing and delivering the foundational data layer, the multi-attribute passage retrieval engine, the spacecraft fire scenario evaluator, and the automated test verification suite:

1. **Curated Microgravity Dataset:**  
   Standardized 15 microgravity combustion experiments across 17 scientific parameters, 50 passage-level NASA evidence citations, and 12 official NASA publication sources (`ntrs.nasa.gov` / `science.nasa.gov`).
2. **Passage-Level TF-IDF Search Engine (`modules/retrieval_engine.py`):**  
   High-precision text retrieval returning 16 structured citation fields with exact page numbers, section locators, and relevance scoring.
3. **Spacecraft Safety Scenario Evaluator (`modules/scenario_retrieval.py` & `pages/4_Safety_Scenario_Evaluator.py`):**  
   Scenario mapping for atmospheric oxygen (15–35%), forced flow velocity (0–50 cm/s), cabin pressure, and fuel materials with automatic NASA limitation hedges.
4. **Interactive Dashboard Pages (`pages/`):**  
   Completed multi-page Streamlit integration including Experiment Explorer, Research Analytics, Grounded AI Assistant, and Safety Scenario Evaluator.
5. **Automated Quality Assurance (`tests/`):**  
   Engineered 23 unit tests across 5 test suites with a **100% pass rate** and 100% Top-3 blind retrieval accuracy.

---

## 🏛️ System Architecture

```
NASA Technical Publications & Memorandums (NTRS / Science)
   │
   ├── data/research_source_register.csv   (12 Cataloged NASA Sources)
   ├── data/combustion_experiments.csv     (15 Experiments × 17 Parameters)
   └── data/research_passages.csv          (50 Exact Passages with Page & Section)
        │
        ├── modules/data_loader.py          ── Load, clean & enforce "not reported" (zero guessing)
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

## 📊 Standardized Datasets & Grounding

- **`data/combustion_experiments.csv` (15 Records × 17 Columns):**  
  Empirical data from **FLEX / FLEX-2** (droplet burns, cool flames), **BASS / BASS-II** (PMMA acrylic thin-films, thick slabs, rods, SIBAL cotton-fiberglass composite fabric), **ACME-BRE** (gaseous fuel emulation of condensed fuels), and **CIR**.
- **`data/research_passages.csv` (50 Passages):**  
  Direct sentence citations from NASA/TP-2015-216046, NASA/TM-20210011385, Nayagam et al. (2014), Hickman et al. (2012), and Saffire large-scale flight tests.
- **Scientific Integrity Policy:**  
  Unreported or unmeasured parameters are strictly classified as `"not reported"` rather than extrapolated.

---

## 🛡️ Mission Safety Scenario Evaluator

Evaluates mission fire hazards against real NASA test evidence while actively enforcing engineering constraints:
- **Oxygen Concentration:** 0–100% vol (Nominal cabin: 21%, Exploration atmosphere: up to 34%).
- **Forced Flow Velocity:** 0–1 m/s (Flight flows: 5–20 cm/s in BASS and Saffire).
- **Cabin Pressure:** 10 to 101.3 kPa.
- **Automated Advisory Hedges:**  
  Flags the documented NASA dataset gap for avionics wiring insulation, highlights persistent toxic gas risks (CO₂ > 8,000 ppm), and explicitly warns that microgravity test data are not flight certifications.

---

## 🧪 Comprehensive Test Suite (23 / 23 Tests PASS)

```bash
python tests/test_data.py                  # 8/8 PASS: Schema integrity & NASA HTTPS links
python tests/test_retrieval.py             # 7/7 PASS: TF-IDF scoring & filter precision
python tests/test_scenario_retrieval.py    # 4/4 PASS: Scenario queries & limitation hedges
python tests/test_scenario_evaluator.py    # 4/4 PASS: UI presets & safe error handling
python tests/test_ai_assistant.py          # PASS: Grounded evidence structure
```

---

## 💻 Running the Application

```bash
# Clone the repository
git clone https://github.com/khan123318/FlameGuard.git
cd FlameGuard

# Install dependencies
pip install -r requirements.txt

# Launch FlameGuard
streamlit run app.py
```

---
*Developed by Syed Abdullah Hussain (Member 2: AI & Data Engineer) · NASA Space Apps Challenge 2026*
