
import streamlit as st

from modules.retrieval_engine import retrieve_research
from modules.ai_assistant import generate_research_answer


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FlameGuard | AI Research Assistant",
    page_icon="🔥",
    layout="wide"
)


# ============================================================
# DESIGN SYSTEM
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(ellipse at 15% 0%, rgba(15, 76, 129, 0.20), transparent 38%),
        radial-gradient(ellipse at 90% 15%, rgba(249, 115, 22, 0.07), transparent 30%),
        #07111f;
    color: #e8f0fa;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #0a1727;
    border-right: 1px solid rgba(148, 163, 184, 0.12);
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #cbd5e1;
}

h1, h2, h3 {
    color: #f1f5f9 !important;
    letter-spacing: -0.5px;
}

p {
    color: #a9b9cc;
}

/* Page hero */

.ai-hero {
    padding: 42px 45px;
    border-radius: 22px;
    border: 1px solid rgba(56, 189, 248, 0.24);
    background:
        radial-gradient(circle at 90% 20%, rgba(249, 115, 22, 0.15), transparent 27%),
        linear-gradient(120deg, #10243b, #0b192c 65%, #101c30);
    box-shadow: 0 18px 55px rgba(0, 0, 0, 0.22);
    margin-bottom: 30px;
}

.ai-kicker {
    color: #38bdf8;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 3px;
    margin-bottom: 15px;
}

.ai-heading {
    color: #f8fafc;
    font-size: clamp(30px, 5vw, 48px);
    font-weight: 850;
    letter-spacing: -2px;
    line-height: 1.1;
}

.ai-heading span {
    color: #fb923c;
}

.ai-description {
    color: #a9bed4;
    font-size: 15px;
    line-height: 1.8;
    max-width: 760px;
    margin-top: 16px;
}

.ai-status {
    display: inline-block;
    margin-top: 20px;
    padding: 8px 14px;
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 30px;
    color: #7dd3fc;
    background: rgba(14, 165, 233, 0.08);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.4px;
}

/* Section labels */

.section-kicker {
    color: #38bdf8;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2.3px;
    margin-bottom: 8px;
}

/* Research input */

.stTextArea textarea {
    background: #0b1929 !important;
    color: #e2e8f0 !important;
    border: 1px solid #29415b !important;
    border-radius: 12px !important;
    font-size: 15px !important;
}

.stTextArea textarea:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 1px #38bdf8 !important;
}

/* Buttons */

.stButton > button,
.stFormSubmitButton > button {
    border-radius: 10px;
    border: 1px solid rgba(56, 189, 248, 0.45);
    background: linear-gradient(100deg, #0284c7, #0369a1);
    color: white;
    font-weight: 750;
    min-height: 45px;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    border-color: #7dd3fc;
    background: #075985;
    color: white;
}

/* Result cards */

.result-card {
    background: linear-gradient(145deg, #102238, #0c1929);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 16px;
    padding: 22px 25px;
    margin-bottom: 16px;
}

.result-label {
    color: #38bdf8;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.8px;
    margin-bottom: 12px;
}

.result-text {
    color: #d5e1ee;
    font-size: 14px;
    line-height: 1.8;
}

.source-card {
    background: #0d1c2e;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-left: 3px solid #38bdf8;
    border-radius: 10px;
    padding: 16px 19px;
    margin-bottom: 12px;
}

.source-title {
    color: #e2eaf4;
    font-weight: 750;
    font-size: 14px;
}

.source-meta {
    color: #91a8bf;
    font-size: 12px;
    margin-top: 7px;
}

.warning-note {
    background: rgba(249, 115, 22, 0.07);
    border: 1px solid rgba(249, 115, 22, 0.25);
    border-radius: 12px;
    padding: 16px 19px;
    color: #fdba74;
    font-size: 13px;
    line-height: 1.7;
    margin-top: 20px;
}

hr {
    border-color: rgba(148, 163, 184, 0.14);
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HERO SECTION
# ============================================================

st.markdown("""
<div class="ai-hero">
<div class="ai-kicker">FLAMEGUARD • RESEARCH INTELLIGENCE</div>
<div class="ai-heading">AI RESEARCH <span>ASSISTANT</span></div>
<div class="ai-description">
Explore microgravity combustion research through an evidence-grounded
AI assistant. Ask scientific questions, retrieve relevant NASA research,
and examine findings with their supporting sources and limitations.
</div>
<div class="ai-status">◈ NASA-GROUNDED RESEARCH DISCOVERY</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# RESEARCH QUESTION INPUT
# ============================================================

st.markdown(
    '<div class="section-kicker">01 / RESEARCH QUERY</div>',
    unsafe_allow_html=True
)

st.subheader("What would you like to investigate?")

st.write(
    "Enter a question about combustion experiments, flame behavior, "
    "materials, or spacecraft fire-safety research."
)

example_questions = [
    "What have NASA experiments observed about flame behavior in microgravity?",
    "How does microgravity affect flame spread over solid materials?",
    "What findings are available from the BASS-II experiments?",
    "What is known about cool flames in microgravity?",
    "What are the limitations of current microgravity combustion research?"
]

selected_example = st.selectbox(
    "Explore an example question",
    options=["Choose an example..."] + example_questions
)

default_question = (
    selected_example if selected_example != "Choose an example..."
    else ""
)

with st.form("research_question_form"):
    user_question = st.text_area(
        "Your research question",
        value=default_question,
        placeholder=(
            "Example: What have NASA experiments observed "
            "about flame behavior in microgravity?"
        ),
        height=130
    )

    submitted = st.form_submit_button(
        "⌕  Search NASA Research Evidence",
        use_container_width=True
    )


# ============================================================
# RESEARCH PROCESSING
# ============================================================

if submitted:

    if not user_question.strip():
        st.warning("Please enter a research question before searching.")

    else:
        with st.spinner(
            "Retrieving scientific evidence and generating your analysis..."
        ):
            try:
                evidence = retrieve_research(
                    user_question.strip(),
                    top_k=5
                )

                result = generate_research_answer(
                    user_question.strip(),
                    evidence
                )

                st.session_state["ai_research_result"] = result
                st.session_state["ai_research_question"] = user_question.strip()

            except Exception:
                st.error(
                    "The research assistant could not complete your request. "
                    "Please check the application configuration and try again."
                )
                st.exception(Exception(
                    "Research processing failed. See the application traceback."
                ))


# ============================================================
# DISPLAY RESEARCH RESULTS
# ============================================================

result = st.session_state.get("ai_research_result")
previous_question = st.session_state.get("ai_research_question")

if result:

    st.divider()

    st.markdown(
        '<div class="section-kicker">02 / RESEARCH ANALYSIS</div>',
        unsafe_allow_html=True
    )

    st.subheader("Research Results")

    st.markdown(
        f"**Research question:** {previous_question}"
    )

    st.markdown("""
    <div class="result-card">
    <div class="result-label">AI-GENERATED RESEARCH ANSWER</div>
    """, unsafe_allow_html=True)

    st.write(result.get("answer", "No answer was returned."))

    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # KEY FINDINGS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-kicker">03 / KEY FINDINGS</div>',
        unsafe_allow_html=True
    )

    st.subheader("Scientific Findings")

    findings = result.get("key_findings", [])

    if findings:
        for finding in findings:
            st.markdown(
                f"""
                <div class="result-card">
                <div class="result-text">◈ {finding}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No separate key findings were returned.")

    # --------------------------------------------------------
    # SCIENTIFIC EXPLANATION
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-kicker">04 / SCIENTIFIC INTERPRETATION</div>',
        unsafe_allow_html=True
    )

    st.subheader("Scientific Explanation")

    explanation = result.get(
        "scientific_explanation",
        "No scientific explanation was returned."
    )

    st.markdown(
        f"""
        <div class="result-card">
        <div class="result-text">{explanation}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # SAFETY IMPLICATIONS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-kicker">05 / MISSION RELEVANCE</div>',
        unsafe_allow_html=True
    )

    st.subheader("Safety Implications")

    safety = result.get(
        "safety_implications",
        "No safety implications were returned."
    )

    st.markdown(
        f"""
        <div class="result-card">
        <div class="result-text">{safety}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # LIMITATIONS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-kicker">06 / EVIDENCE BOUNDARIES</div>',
        unsafe_allow_html=True
    )

    st.subheader("Research Limitations")

    limitations = result.get("limitations", [])

    if limitations:
        for limitation in limitations:
            st.warning(limitation)
    else:
        st.info("No separate limitations were returned.")

    # --------------------------------------------------------
    # SOURCES
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-kicker">07 / SOURCE TRACEABILITY</div>',
        unsafe_allow_html=True
    )

    st.subheader("Research Sources")

    sources = result.get("sources", [])

    if sources:

        for index, source in enumerate(sources, start=1):

            title = source.get("source_title", "Untitled source")
            experiment = source.get("experiment_name")
            page_number = source.get("page_number")
            source_url = source.get("source_url")

            st.markdown(
                f"""
                <div class="source-card">
                <div class="source-title">{index:02d} / {title}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if experiment:
                st.caption(f"Experiment: {experiment}")

            if page_number is not None:
                st.caption(f"Page: {page_number}")

            if source_url:
                st.markdown(f"[Open original research source]({source_url})")

    else:
        st.info("No source references were returned for this answer.")

    # --------------------------------------------------------
    # SCIENTIFIC DISCLAIMER
    # --------------------------------------------------------

    st.markdown("""
    <div class="warning-note">
    <strong>SCIENTIFIC CAUTION</strong><br>
    AI-generated explanations are research-support outputs.
    Interpretations must be evaluated against the original scientific
    sources. Retrieved evidence does not constitute a validated
    spacecraft fire-safety assessment or operational safety threshold.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown("""
<div style="text-align:center; color:#64748b; font-size:12px; padding:20px 0;">
FLAMEGUARD · NASA SPACE APPS CHALLENGE 2026 · TEAM NST
<br><br>
Evidence-grounded research discovery for microgravity combustion science.
</div>
""", unsafe_allow_html=True)
