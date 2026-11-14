import streamlit as st

from modules.data_loader import load_experiments
from modules.retrieval_engine import retrieve_research
from modules.ai_assistant import generate_research_answer


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FlameGuard | Mission Control",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DESIGN SYSTEM
# ============================================================

st.markdown("""
<style>

/* Global application */
.stApp {
    background:
        radial-gradient(ellipse at 15% 0%, rgba(15, 76, 129, 0.20), transparent 38%),
        radial-gradient(ellipse at 90% 15%, rgba(249, 115, 22, 0.07), transparent 30%),
        #07111f;
    color: #e8f0fa;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0a1727;
    border-right: 1px solid rgba(148, 163, 184, 0.12);
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #cbd5e1;
}

/* Typography */
h1, h2, h3 {
    color: #f1f5f9 !important;
    letter-spacing: -0.5px;
}

p {
    color: #a9b9cc;
}

/* Hero */
.fg-hero {
    position: relative;
    overflow: hidden;
    padding: 58px 55px;
    border-radius: 24px;
    border: 1px solid rgba(56, 189, 248, 0.24);
    background:
        radial-gradient(circle at 85% 25%, rgba(249, 115, 22, 0.17), transparent 26%),
        radial-gradient(circle at 70% 80%, rgba(14, 165, 233, 0.17), transparent 32%),
        linear-gradient(120deg, #10243b 0%, #0b192c 55%, #101c30 100%);
    box-shadow: 0 18px 65px rgba(0, 0, 0, 0.25);
    margin-bottom: 30px;
}

.fg-hero::after {
    content: "";
    position: absolute;
    width: 290px;
    height: 290px;
    right: 7%;
    top: -105px;
    border: 1px solid rgba(56, 189, 248, 0.18);
    border-radius: 50%;
    box-shadow:
        0 0 0 35px rgba(56, 189, 248, 0.025),
        0 0 0 75px rgba(56, 189, 248, 0.02);
}

.fg-kicker {
    color: #38bdf8;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 3px;
    margin-bottom: 18px;
}

.fg-title {
    color: #f8fafc;
    font-size: clamp(42px, 6vw, 68px);
    line-height: 1.05;
    font-weight: 850;
    letter-spacing: -3px;
    margin: 0;
}

.fg-title span {
    color: #fb923c;
}

.fg-subtitle {
    color: #a9bed4;
    font-size: 17px;
    line-height: 1.7;
    max-width: 650px;
    margin-top: 20px;
}

.fg-status {
    display: inline-block;
    margin-top: 25px;
    padding: 9px 15px;
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 30px;
    color: #7dd3fc;
    background: rgba(14, 165, 233, 0.08);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

/* Section headings */
.fg-section-label {
    color: #38bdf8;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2.5px;
    margin-bottom: 8px;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #102238, #0c1929);
    border: 1px solid rgba(148, 163, 184, 0.13);
    padding: 20px;
    border-radius: 16px;
}

[data-testid="stMetricLabel"] {
    color: #9db1c7 !important;
}

[data-testid="stMetricValue"] {
    color: #f8fafc !important;
}

/* Navigation cards */
.feature-card {
    min-height: 170px;
    padding: 24px;
    background: linear-gradient(145deg, #11243a, #0b1929);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 17px;
    transition: all 0.25s ease;
}

.feature-card:hover {
    border-color: rgba(56, 189, 248, 0.55);
    transform: translateY(-3px);
}

.feature-icon {
    font-size: 28px;
    margin-bottom: 15px;
}

.feature-title {
    color: #f1f5f9;
    font-size: 18px;
    font-weight: 750;
    margin-bottom: 9px;
}

.feature-description {
    color: #9db1c7;
    font-size: 13px;
    line-height: 1.6;
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    border: 1px solid rgba(56, 189, 248, 0.45);
    background: linear-gradient(100deg, #0284c7, #0369a1);
    color: white;
    font-weight: 700;
    min-height: 44px;
}

.stButton > button:hover {
    border-color: #7dd3fc;
    background: #075985;
    color: white;
}

/* Input areas */
.stTextArea textarea {
    background: #0b1929 !important;
    color: #e2e8f0 !important;
    border: 1px solid #263d55 !important;
    border-radius: 12px !important;
}

/* Dividers */
hr {
    border-color: rgba(148, 163, 184, 0.14);
}

/* Footer */
.fg-footer {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    padding: 25px 0 5px 0;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD REAL RESEARCH DATA
# ============================================================

try:
    df = load_experiments()

    total_experiments = df["experiment_id"].nunique()

    def count_reported_categories(column):
        if column not in df.columns:
            return 0

        values = df[column].astype(str).str.strip()

        unavailable = {
            "",
            "not reported",
            "not stated",
            "not specified",
            "unavailable",
            "unknown",
            "none",
            "nan"
        }

        return values[
            ~values.str.lower().isin(unavailable)
        ].nunique()

    total_programs = count_reported_categories("research_program")
    evidence_categories = count_reported_categories("evidence_level")

except Exception as error:
    st.error("Unable to load the combustion research dataset.")
    st.exception(error)
    st.stop()


# ============================================================
# HERO SECTION
# ============================================================

st.markdown("""
<div class="fg-hero">
<div class="fg-kicker">SPACE RESEARCH • COMBUSTION INTELLIGENCE</div>
<h1 class="fg-title">FLAME<span>GUARD</span></h1>
<div class="fg-subtitle">
Investigating flame behavior in microgravity.
Exploring NASA combustion research, interpreting scientific
evidence, and supporting spacecraft fire-safety research.
</div>
<div class="fg-status">◈ RESEARCH INTELLIGENCE PLATFORM</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# RESEARCH OVERVIEW
# ============================================================

st.markdown(
    '<div class="fg-section-label">MISSION OVERVIEW</div>',
    unsafe_allow_html=True
)

st.header("Research at a Glance")

st.write(
    "A live overview of the combustion experiment dataset "
    "currently available in FlameGuard."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Experiments",
        total_experiments,
        help="Unique experiment records in the loaded dataset."
    )

with col2:
    st.metric(
        "Research Programs",
        total_programs,
        help="Distinct reported research programs."
    )

with col3:
    st.metric(
        "Evidence Categories",
        evidence_categories,
        help="Distinct reported evidence classifications."
    )


# ============================================================
# PLATFORM NAVIGATION
# ============================================================

st.divider()

st.markdown(
    '<div class="fg-section-label">EXPLORE THE PLATFORM</div>',
    unsafe_allow_html=True
)

st.header("Your Research Workspace")

st.write(
    "Move from raw experimental records to scientific insights "
    "and evidence-grounded research assistance."
)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔬</div>
        <div class="feature-title">Experiment Explorer</div>
        <div class="feature-description">
            Explore NASA combustion experiments, search research
            records, filter materials and compare experimental findings.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.page_link(
        "pages/1_Experiment_Explorer.py",
        label="Explore Experiments →",
        icon="🔬"
    )

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Research Analytics</div>
        <div class="feature-description">
            Investigate evidence distributions, findings status,
            research coverage and scientific data characteristics.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.page_link(
        "pages/2_Research_Analytics.py",
        label="View Research Analytics →",
        icon="📊"
    )

col3, col4 = st.columns(2, gap="large")

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <div class="feature-title">AI Research Assistant</div>
        <div class="feature-description">
            Ask scientific questions and retrieve relevant
            NASA-grounded research evidence.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.page_link(
        "pages/3_AI_Research_Assistant.py",
        label="Open AI Assistant →",
        icon="🧠"
    )

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <div class="feature-title">Safety Scenario Evaluator</div>
        <div class="feature-description">
            Investigate spacecraft fire-safety scenarios using
            relevant research and clearly stated limitations.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.page_link(
        "pages/4_Safety_Scenario_Evaluator.py",
        label="Explore Safety Scenarios →",
        icon="🛡️"
    )


# ============================================================
# AI RESEARCH ASSISTANT
# ============================================================

st.divider()

st.markdown(
    '<div class="fg-section-label">SCIENTIFIC INTELLIGENCE</div>',
    unsafe_allow_html=True
)

st.header("Ask the Research Assistant")

st.write(
    "Investigate microgravity combustion using an evidence-grounded "
    "research workflow."
)

user_question = st.text_area(
    "What would you like to investigate?",
    placeholder=(
        "Example: What have NASA experiments observed "
        "about flame behavior in microgravity?"
    ),
    height=110,
    key="homepage_research_question"
)

if st.button("Search Research Evidence", type="primary"):

    if not user_question.strip():
        st.warning("Please enter a research question.")

    else:
        with st.spinner("Retrieving and analyzing research evidence..."):

            try:
                evidence = retrieve_research(
                    user_question,
                    top_k=5
                )

                result = generate_research_answer(
                    user_question,
                    evidence
                )

                st.success("Research analysis completed.")

                st.subheader("Answer")
                st.write(result["answer"])

                st.subheader("Key Findings")

                for finding in result["key_findings"]:
                    st.markdown(f"- {finding}")

                st.subheader("Scientific Explanation")
                st.write(result["scientific_explanation"])

                st.subheader("Safety Implications")
                st.write(result["safety_implications"])

                st.subheader("Limitations")

                for limitation in result["limitations"]:
                    st.markdown(f"- {limitation}")

                st.subheader("Research Sources")

                for source in result["sources"]:

                    title = source.get(
                        "source_title",
                        "Untitled source"
                    )

                    st.markdown(f"**{title}**")

                    if source.get("experiment_name"):
                        st.caption(
                            f"Experiment: {source['experiment_name']}"
                        )

                    if source.get("source_url"):
                        st.markdown(
                            f"[Open original source]({source['source_url']})"
                        )

                    if source.get("page_number") is not None:
                        st.caption(
                            f"Page: {source['page_number']}"
                        )

            except Exception as error:
                st.error(
                    "Something went wrong while processing your question."
                )
                st.exception(error)



# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown("""
<div class="fg-footer">
<p>FLAMEGUARD · NASA SPACE APPS CHALLENGE 2026 · TEAM NST</p>
<p>Research evidence supports scientific exploration.</p>
<p>It does not replace validated spacecraft fire-safety assessments.</p>
</div>
""", unsafe_allow_html=True)