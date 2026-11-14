
import streamlit as st

try:
    from modules.scenario_retrieval import retrieve_for_scenario
except ImportError:
    from scenario_retrieval import retrieve_for_scenario


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="FlameGuard | Safety Scenario Evaluator",
    page_icon="🔥",
    layout="wide"
)


# ---------------------------------------------------------
# PREMIUM FLAMEGUARD THEME
# ---------------------------------------------------------

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at 15% 0%, #142b49 0%, transparent 42%),
        linear-gradient(145deg, #07111f 0%, #0a1728 55%, #101d30 100%);
    color: #e8f1fa;
}

[data-testid="stSidebar"] {
    background: #091526;
    border-right: 1px solid rgba(90, 190, 230, 0.15);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

h1, h2, h3 {
    color: #f1f7ff !important;
}

p, label, span {
    color: #c1d0df;
}

.fg-hero {
    padding: 2.5rem 2.8rem;
    border: 1px solid rgba(63, 190, 230, 0.28);
    border-radius: 22px;
    background: linear-gradient(
        115deg,
        rgba(17, 43, 68, 0.96),
        rgba(9, 24, 42, 0.96)
    );
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.22);
    margin-bottom: 2rem;
}

.fg-kicker {
    color: #53d5ee;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 3px;
    margin-bottom: 1rem;
}

.fg-heading {
    font-size: clamp(2rem, 5vw, 3.3rem);
    font-weight: 850;
    letter-spacing: -1.5px;
    line-height: 1.1;
    color: #f4f8ff;
}

.fg-heading span {
    color: #ff914d;
}

.fg-description {
    max-width: 800px;
    color: #bdccdc;
    font-size: 1.04rem;
    line-height: 1.8;
    margin-top: 1.1rem;
}

.fg-status {
    display: inline-block;
    margin-top: 1.4rem;
    padding: 0.5rem 0.85rem;
    border-radius: 30px;
    background: rgba(42, 190, 218, 0.10);
    border: 1px solid rgba(42, 190, 218, 0.30);
    color: #6cdeed;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
}

.section-kicker {
    color: #53d5ee;
    font-size: 0.72rem;
    font-weight: 750;
    letter-spacing: 2px;
    margin-bottom: 0.45rem;
}

.panel {
    background: rgba(16, 35, 55, 0.72);
    border: 1px solid rgba(120, 170, 205, 0.17);
    border-radius: 17px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}

.metric-card {
    background: rgba(18, 43, 66, 0.82);
    border: 1px solid rgba(83, 213, 238, 0.22);
    border-radius: 14px;
    padding: 1.2rem;
    min-height: 105px;
}

.metric-label {
    color: #91aabd;
    font-size: 0.78rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.metric-value {
    color: #f1f7ff;
    font-size: 1.8rem;
    font-weight: 800;
    margin-top: 0.35rem;
}

.warning-panel {
    background: rgba(255, 145, 77, 0.08);
    border: 1px solid rgba(255, 145, 77, 0.35);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin: 1rem 0;
}

.warning-title {
    color: #ffad73;
    font-weight: 750;
    margin-bottom: 0.4rem;
}

.evidence-panel {
    background: rgba(15, 34, 54, 0.78);
    border: 1px solid rgba(83, 213, 238, 0.19);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}

.evidence-label {
    color: #53d5ee;
    font-size: 0.7rem;
    font-weight: 750;
    letter-spacing: 1.5px;
    margin-bottom: 0.5rem;
}

.fg-footer {
    text-align: center;
    padding: 2rem 0 0.5rem;
    color: #8298ac;
    font-size: 0.78rem;
    line-height: 1.8;
}

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(100deg, #13a9c8, #2678bd);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 750;
    padding: 0.65rem 1.3rem;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    border: 1px solid #66e0f0;
    color: white;
    background: linear-gradient(100deg, #159bb9, #286da8);
}

div[data-baseweb="input"] input,
div[data-baseweb="select"] > div,
.stTextArea textarea {
    background-color: #10243a !important;
    color: #e8f1fa !important;
}

hr {
    border-color: rgba(120, 170, 205, 0.18);
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def display_value(value):
    """Convert values into readable text."""
    if value is None:
        return "Not reported"

    value = str(value).strip()

    if not value or value.lower() in ("nan", "none", "null"):
        return "Not reported"

    return value


def get_field(record, *keys):
    """Safely retrieve the first available field from a record."""
    if not isinstance(record, dict):
        return None

    for key in keys:
        value = record.get(key)

        if value is not None and str(value).strip():
            return value

    return None


def is_valid_url(url):
    """Only allow normal HTTP/HTTPS source links."""
    if not url:
        return False

    url = str(url).strip().lower()
    return url.startswith("https://") or url.startswith("http://")


# ---------------------------------------------------------
# HERO SECTION
# ---------------------------------------------------------

st.markdown("""
<div class="fg-hero">
<div class="fg-kicker">FLAMEGUARD • SCIENTIFIC DECISION SUPPORT</div>
<div class="fg-heading">SAFETY SCENARIO <span>EVALUATOR</span></div>
<div class="fg-description">
Explore spacecraft fire scenarios by defining their material and
environmental conditions. Retrieve relevant NASA combustion research,
examine supporting evidence, and understand the limitations of the
available scientific data.
</div>
<div class="fg-status">◈ EVIDENCE-GROUNDED SCENARIO EXPLORATION</div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# SCIENTIFIC DISCLAIMER
# ---------------------------------------------------------

st.markdown("""
<div class="warning-panel">
<div class="warning-title">Important scientific limitation</div>
This tool retrieves research relevant to the conditions you enter.
It does not calculate fire probability, predict flame behavior,
assign a validated risk score, establish safe operating thresholds,
or certify spacecraft fire safety. Missing evidence must not be
interpreted as absence of risk.
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# SCENARIO CONFIGURATION
# ---------------------------------------------------------

st.markdown('<div class="section-kicker">01 / CONFIGURATION</div>',
            unsafe_allow_html=True)
st.header("Define your scenario")

st.write(
    "Describe the material and environmental conditions you want "
    "to investigate. Environmental parameters are optional."
)

with st.form("scenario_form"):

    st.markdown("#### Scenario information")

    scenario_type = st.selectbox(
        "Scenario category",
        [
            "General spacecraft scenario",
            "Fuel droplet",
            "Solid material",
            "Gaseous fuel",
            "Electrical equipment"
        ]
    )

    fuel_or_material = st.text_input(
        "Fuel or material",
        placeholder="e.g. Methanol, PMMA, n-heptane"
    )

    description = st.text_area(
        "Scenario description",
        placeholder=(
            "Describe the combustion situation you want to investigate..."
        ),
        height=110
    )

    st.divider()
    st.markdown("#### Environmental conditions")

    col1, col2 = st.columns(2)

    with col1:
        include_oxygen = st.checkbox(
            "Specify oxygen concentration"
        )

        oxygen_percent = None
        if include_oxygen:
            oxygen_percent = st.number_input(
                "Oxygen concentration (%)",
                min_value=0.0,
                max_value=100.0,
                value=21.0,
                step=0.5
            )

        include_airflow = st.checkbox(
            "Specify airflow velocity"
        )

        air_velocity = None
        if include_airflow:
            air_velocity = st.number_input(
                "Airflow velocity (m/s)",
                min_value=0.0,
                value=0.1,
                step=0.1
            )

    with col2:
        include_temperature = st.checkbox(
            "Specify temperature"
        )

        temperature = None
        if include_temperature:
            temperature = st.number_input(
                "Temperature (K)",
                min_value=0.0,
                value=300.0,
                step=10.0
            )

        include_pressure = st.checkbox(
            "Specify pressure"
        )

        pressure = None
        if include_pressure:
            pressure = st.number_input(
                "Pressure (Pa)",
                min_value=0.0,
                value=101325.0,
                step=1000.0
            )

    st.divider()

    submitted = st.form_submit_button(
        "Retrieve Relevant Research",
        use_container_width=True
    )


# ---------------------------------------------------------
# RUN SCENARIO RETRIEVAL
# ---------------------------------------------------------

if submitted:

    scenario = {
        "fuel_or_material": fuel_or_material.strip(),
        "description": description.strip(),
        "scenario_type": scenario_type,
        "oxygen_percent": oxygen_percent,
        "air_velocity_m_s": air_velocity,
        "temperature_k": temperature,
        "pressure_pa": pressure
    }

    try:
        with st.spinner("Searching the research evidence database..."):
            result = retrieve_for_scenario(scenario, top_k=5)

        st.session_state["scenario_result"] = result
        st.session_state["scenario_input"] = scenario

    except Exception as error:
        st.error("The scenario retrieval process encountered an error.")
        st.exception(error)


# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------

result = st.session_state.get("scenario_result")
scenario = st.session_state.get("scenario_input", {})

if result is not None:

    st.divider()

    st.markdown(
        '<div class="section-kicker">02 / RETRIEVAL RESULTS</div>',
        unsafe_allow_html=True
    )
    st.header("Research evidence")

    evidence = result.get("evidence") or []
    query = result.get("query", "")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <div class="metric-label">Retrieved evidence records</div>
        <div class="metric-value">{len(evidence)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <div class="metric-label">Scenario category</div>
        <div class="metric-value" style="font-size:1.15rem;">
        {display_value(scenario.get("scenario_type"))}
        </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("View generated research query"):
        st.code(query if query else "No searchable query was generated.")

    if evidence:

        st.success(
            f"{len(evidence)} research record(s) were retrieved "
            "for further examination."
        )

        for index, record in enumerate(evidence, start=1):

            if not isinstance(record, dict):
                st.write(record)
                continue

            title = get_field(
                record,
                "experiment_name",
                "source_title",
                "title",
                "experiment_id"
            )

            st.markdown(f"""
            <div class="evidence-panel">
            <div class="evidence-label">RESEARCH RECORD {index:02d}</div>
            <h3>{display_value(title)}</h3>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Research program**")
                st.write(display_value(
                    get_field(record, "research_program")
                ))

                st.markdown("**Fuel or material**")
                st.write(display_value(
                    get_field(record, "fuel_material")
                ))

                st.markdown("**Evidence level**")
                st.write(display_value(
                    get_field(record, "evidence_level")
                ))

            with col2:
                st.markdown("**Experiment ID**")
                st.write(display_value(
                    get_field(record, "experiment_id")
                ))

                st.markdown("**Page number**")
                st.write(display_value(
                    get_field(record, "page_number")
                ))

                st.markdown("**Retrieval relevance score**")
                score = get_field(record, "relevance_score")
                st.write(display_value(score))

            passage = get_field(
                record,
                "matched_passage",
                "passage",
                "text"
            )

            if passage:
                st.markdown("**Retrieved research passage**")
                st.info(str(passage))

            findings = get_field(record, "findings")
            if findings:
                st.markdown("**Reported findings**")
                st.write(findings)

            safety = get_field(record, "safety_relevance")
            if safety:
                st.markdown("**Safety relevance**")
                st.write(safety)

            limitations = get_field(record, "limitations")
            if limitations:
                st.markdown("**Research limitations**")
                st.write(limitations)

            source_url = get_field(
                record,
                "source_url",
                "url"
            )

            if is_valid_url(source_url):
                st.link_button(
                    "Open research source",
                    str(source_url)
                )

            st.divider()

    else:
        st.warning(
            "No research evidence was retrieved for this scenario. "
            "Try a broader description or a different material."
        )

    # -----------------------------------------------------
    # BACKEND LIMITATIONS
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-kicker">03 / SCIENTIFIC LIMITATIONS</div>',
        unsafe_allow_html=True
    )
    st.header("Evidence limitations")

    limitations = result.get("limitations") or []

    if limitations:
        for limitation in limitations:
            st.warning(limitation)
    else:
        st.info(
            "No additional limitations were returned by the retrieval module. "
            "This does not establish that the evidence is complete."
        )

    st.markdown("""
    <div class="warning-panel">
    <div class="warning-title">How to interpret these results</div>
    Retrieved passages are research references, not direct assessments
    of the scenario you entered. Experimental findings are specific to
    their tested materials, configurations, and environmental conditions.
    Relevance scores indicate retrieval relevance, not scientific certainty,
    hazard severity, or safety confidence.
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.markdown("""
<div class="fg-footer">
<p>FLAMEGUARD · NASA SPACE APPS CHALLENGE 2026 · TEAM NST</p>
<p>Scientific evidence supports research exploration.</p>
<p>It does not replace validated spacecraft fire-safety assessments.</p>
</div>
""", unsafe_allow_html=True)
