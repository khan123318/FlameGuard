import streamlit as st
import pandas as pd

from modules.data_loader import load_experiments
from modules.retrieval_engine import retrieve_research


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="FlameGuard | Experiment Explorer",
    page_icon="🔥",
    layout="wide"
)


# =========================================================
# CUSTOM THEME
# =========================================================

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 85% 5%, rgba(0, 190, 220, 0.10), transparent 28%),
        linear-gradient(145deg, #07111f 0%, #0b1728 55%, #101b2d 100%);
    color: #eaf3ff;
}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

[data-testid="stSidebar"] {
    background: #091525;
    border-right: 1px solid rgba(75, 190, 220, 0.15);
}

.explorer-hero {
    padding: 2.3rem 2.5rem;
    border: 1px solid rgba(68, 205, 230, 0.25);
    border-radius: 22px;
    background: linear-gradient(
        120deg,
        rgba(16, 43, 65, 0.96),
        rgba(13, 27, 46, 0.94)
    );
    margin-bottom: 1.8rem;
}

.explorer-kicker {
    color: #42d7e9;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 3px;
    margin-bottom: 0.8rem;
}

.explorer-title {
    color: #f3f8ff;
    font-size: clamp(2rem, 4vw, 3.3rem);
    font-weight: 850;
    line-height: 1.1;
    margin: 0;
}

.explorer-title span {
    color: #43d5e8;
}

.explorer-description {
    color: #a9bdd0;
    font-size: 1rem;
    line-height: 1.8;
    max-width: 850px;
    margin-top: 1rem;
}

.explorer-status {
    display: inline-block;
    margin-top: 1.2rem;
    padding: 0.45rem 0.8rem;
    border-radius: 30px;
    border: 1px solid rgba(66, 215, 233, 0.35);
    color: #62e4ed;
    font-size: 0.7rem;
    font-weight: 750;
    letter-spacing: 1.5px;
}

.section-heading {
    color: #edf6ff;
    font-size: 1.35rem;
    font-weight: 750;
    margin-top: 1.8rem;
    margin-bottom: 0.25rem;
}

.section-caption {
    color: #8fa7bc;
    font-size: 0.88rem;
    margin-bottom: 1rem;
}

.metric-card {
    background: linear-gradient(145deg, #132940, #101e30);
    border: 1px solid rgba(75, 190, 220, 0.20);
    border-radius: 16px;
    padding: 1.2rem 1.3rem;
    min-height: 112px;
}

.metric-label {
    color: #9eb5c9;
    font-size: 0.76rem;
    font-weight: 650;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.metric-value {
    color: #42d7e9;
    font-size: 2rem;
    font-weight: 850;
    margin-top: 0.35rem;
}

.experiment-card {
    background: rgba(15, 32, 51, 0.72);
    border: 1px solid rgba(105, 160, 190, 0.20);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}

.result-label {
    color: #42d7e9;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}

.note-panel {
    background: rgba(244, 135, 65, 0.08);
    border-left: 3px solid #f28b45;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    color: #c4d1de;
    font-size: 0.86rem;
}

.fg-footer {
    text-align: center;
    color: #7890a7;
    font-size: 0.76rem;
    line-height: 1.8;
    padding-top: 1rem;
}

div[data-testid="stMetric"] {
    background: transparent;
}

.stSelectbox label,
.stMultiSelect label,
.stTextInput label {
    color: #c7d8e8 !important;
}

hr {
    border-color: rgba(120, 170, 200, 0.18);
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="explorer-hero">
<div class="explorer-kicker">FLAMEGUARD • SCIENTIFIC RESEARCH DISCOVERY</div>
<h1 class="explorer-title">EXPERIMENT <span>EXPLORER</span></h1>
<div class="explorer-description">
Investigate microgravity combustion experiments through
scientific search, structured research records, and
side-by-side experiment comparisons.
Explore documented findings, experimental conditions,
materials, and safety implications.
</div>
<div class="explorer-status">◈ EXPERIMENT DATABASE • RESEARCH DISCOVERY</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def display_value(value):
    """Display missing or empty values without inventing information."""

    if value is None:
        return "Not reported in available record"

    try:
        if pd.isna(value):
            return "Not reported in available record"
    except (TypeError, ValueError):
        pass

    text = str(value).strip()

    if not text or text.lower() in ("nan", "none", "null"):
        return "Not reported in available record"

    return text


def get_options(dataframe, column):
    """Return valid filter options from an existing dataset column."""

    if column not in dataframe.columns:
        return ["All"]

    values = (
        dataframe[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[
        (values != "") &
        (~values.str.lower().isin(["nan", "none", "null"]))
    ]

    return ["All"] + sorted(values.unique().tolist())


def get_record_value(record, field):
    """Safely retrieve a field from a search result."""

    return display_value(record.get(field))


# =========================================================
# LOAD DATASET
# =========================================================

try:
    df = load_experiments()

    if df is None or df.empty:
        st.warning("The experiment dataset is currently empty.")
        st.stop()

except Exception as error:
    st.session_state.pop("experiment_search_results", None)
    st.session_state.pop("experiment_search_query", None)
    
    st.error("Unable to retrieve matching experiments.")
    st.exception(error)
    
    st.error("Unable to load the experiment dataset.")
    st.exception(error)
    st.stop()


# =========================================================
# DATASET OVERVIEW
# =========================================================

# total_experiments = len(df)

# total_programs = (
#     df["research_program"].nunique()
#     if "research_program" in df.columns
#     else 0
# )

# total_materials = (
#     df["fuel_material"].nunique()
#     if "fuel_material" in df.columns
#     else 0
# )

# total_environments = (
#     df["environment"].nunique()
#     if "environment" in df.columns
#     else 0
# )

# st.markdown(
#     '<div class="section-heading">Research database overview</div>',
#     unsafe_allow_html=True
# )

# st.markdown(
#     '<div class="section-caption">An overview of the curated experiment records available for exploration.</div>',
#     unsafe_allow_html=True
# )

# metric_columns = st.columns(4)

# metric_items = [
#     ("EXPERIMENT RECORDS", total_experiments),
#     ("RESEARCH PROGRAMS", total_programs),
#     ("FUEL MATERIALS", total_materials),
#     ("ENVIRONMENTS", total_environments)
# ]

# for column, (label, value) in zip(metric_columns, metric_items):
#     with column:
#         st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-label">{label}</div>
#             <div class="metric-value">{value}</div>
#         </div>
#         """, unsafe_allow_html=True)

# =========================================================
# DATASET OVERVIEW
# =========================================================

total_experiments = (
    df["experiment_id"].nunique()
    if "experiment_id" in df.columns
    else len(df)
)


def count_reported_categories(column):
    """Count unique, meaningful reported values in a dataset column."""

    if column not in df.columns:
        return 0

    values = df[column].dropna().astype(str).str.strip()

    missing_markers = {
        "",
        "nan",
        "none",
        "null",
        "not reported",
        "not stated",
        "not specified",
        "unavailable",
        "unknown"
    }

    values = values[
        ~values.str.lower().isin(missing_markers)
    ]

    return values.nunique()


total_programs = count_reported_categories("research_program")
total_materials = count_reported_categories("fuel_material")
total_environments = count_reported_categories("environment")


st.markdown(
    '<div class="section-heading">Research database overview</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-caption">'
    'An overview of the curated experiment records available for exploration.'
    '</div>',
    unsafe_allow_html=True
)


metric_columns = st.columns(4)

metric_items = [
    ("EXPERIMENT RECORDS", total_experiments),
    ("RESEARCH PROGRAMS", total_programs),
    ("FUEL MATERIALS", total_materials),
    ("ENVIRONMENTS", total_environments)
]


for column, (label, value) in zip(metric_columns, metric_items):
    with column:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# SEMANTIC RESEARCH SEARCH
# =========================================================

st.markdown(
    '<div class="section-heading">Search the research database</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-caption">Search for relevant combustion experiments using scientific questions or keywords.</div>',
    unsafe_allow_html=True
)

with st.form("experiment_search_form"):

    search_query = st.text_input(
        "Research query",
        placeholder="Example: PMMA flame spread in microgravity"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_program = st.selectbox(
            "Research program",
            get_options(df, "research_program")
        )

    with col2:
        selected_material = st.selectbox(
            "Material class",
            get_options(df, "material_class")
        )

    with col3:
        selected_environment = st.selectbox(
            "Environment",
            get_options(df, "environment")
        )

    search_submitted = st.form_submit_button(
        "Search experiments",
        type="primary",
        use_container_width=True
    )


if search_submitted:

    if not search_query.strip():
        st.session_state.pop("experiment_search_results", None)
        st.warning("Please enter a research query.")

    else:
        filters = {}

        if selected_program != "All":
            filters["research_program"] = selected_program

        if selected_material != "All":
            filters["material_class"] = selected_material

        if selected_environment != "All":
            filters["environment"] = selected_environment

        try:
            with st.spinner("Searching the research database..."):

                results = retrieve_research(
                    search_query.strip(),
                    filters=filters,
                    top_k=10
                )

            st.session_state["experiment_search_results"] = results
            st.session_state["experiment_search_query"] = search_query.strip()

        except Exception as error:
            st.error("Unable to retrieve matching experiments.")
            st.exception(error)


# =========================================================
# SEARCH RESULTS
# =========================================================

results = st.session_state.get("experiment_search_results")

if results is not None:

    previous_query = st.session_state.get(
        "experiment_search_query",
        ""
    )

    st.markdown(
        '<div class="section-heading">Research search results</div>',
        unsafe_allow_html=True
    )

    st.caption(f"Search query: {previous_query}")

    if results:

        st.success(
            f"Retrieved {len(results)} relevant research records."
        )

        for index, experiment in enumerate(results, start=1):

            experiment_name = get_record_value(
                experiment, "experiment_name"
            )

            experiment_id = get_record_value(
                experiment, "experiment_id"
            )

            with st.expander(
                f"{index}. {experiment_name}",
                expanded=(index == 1)
            ):

                st.markdown(
                    '<div class="result-label">EXPERIMENT IDENTIFICATION</div>',
                    unsafe_allow_html=True
                )

                info_col1, info_col2, info_col3 = st.columns(3)

                with info_col1:
                    st.write("**Experiment ID**")
                    st.write(experiment_id)

                with info_col2:
                    st.write("**Research Program**")
                    st.write(get_record_value(
                        experiment, "research_program"
                    ))

                with info_col3:
                    st.write("**Evidence Level**")
                    st.write(get_record_value(
                        experiment, "evidence_level"
                    ))

                st.divider()

                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:
                    st.markdown("**Fuel Material**")
                    st.write(get_record_value(
                        experiment, "fuel_material"
                    ))

                    st.markdown("**Material Class**")
                    st.write(get_record_value(
                        experiment, "material_class"
                    ))

                    st.markdown("**Environment**")
                    st.write(get_record_value(
                        experiment, "environment"
                    ))

                with detail_col2:
                    st.markdown("**Objective**")
                    st.write(get_record_value(
                        experiment, "objective"
                    ))

                    st.markdown("**Variables Studied**")
                    st.write(get_record_value(
                        experiment, "variables_studied"
                    ))

                st.divider()

                st.markdown("**Research Findings**")
                st.write(get_record_value(
                    experiment, "findings"
                ))

                st.markdown("**Safety Relevance**")
                st.write(get_record_value(
                    experiment, "safety_relevance"
                ))

                st.markdown("**Limitations**")
                st.write(get_record_value(
                    experiment, "limitations"
                ))

                score = experiment.get("relevance_score")

                if score is not None:
                    try:
                        if not pd.isna(score):
                            st.metric(
                                "Retrieval Relevance Score",
                                round(float(score), 4)
                            )
                    except (TypeError, ValueError):
                        pass

                source_url = experiment.get("source_url")

                #if isinstance(source_url, str) and source_url.startswith("https://"):
                if (
                    isinstance(source_url, str)
                    and source_url.strip().lower().startswith("https://")
                    ):
                    st.link_button(
                        "Open research source",
                        source_url
                    )

    else:
        st.info(
            "No matching experiments were found. "
            "Try another query or adjust your filters."
        )


# =========================================================
# EXPERIMENT COMPARISON
# =========================================================

st.divider()

st.markdown(
    '<div class="section-heading">Compare experiments</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-caption">Compare the documented characteristics and findings of two or more experiments.</div>',
    unsafe_allow_html=True
)

if "experiment_id" in df.columns:

    experiment_ids = (
        df["experiment_id"]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    selected_experiments = st.multiselect(
        "Select experiments to compare",
        options=experiment_ids,
        format_func=lambda value: str(value)
    )

    if len(selected_experiments) >= 2:

        comparison_fields = [
            "experiment_name",
            "research_program",
            "experiment_type",
            "fuel_material",
            "material_class",
            "environment",
            "objective",
            "variables_studied",
            "findings",
            "safety_relevance",
            "evidence_level",
            "limitations"
        ]

        available_fields = [
            field for field in comparison_fields
            if field in df.columns
        ]

        comparison_df = df[
            df["experiment_id"].isin(selected_experiments)
        ].copy()

        comparison_df = comparison_df[
            ["experiment_id"] + available_fields
        ]

        comparison_df = comparison_df.set_index("experiment_id").T

        comparison_df.index = [
            field.replace("_", " ").title()
            for field in comparison_df.index
        ]

        st.markdown("**Side-by-side research comparison**")

        st.dataframe(
            comparison_df,
            use_container_width=True,
            height=520
        )

        st.caption(
            "Comparisons reflect the information documented in the "
            "selected records. Missing fields are not inferred."
        )

    elif len(selected_experiments) == 1:
        st.info("Select at least one more experiment to compare.")

    else:
        st.info("Select two or more experiments to begin comparing.")

else:
    st.warning(
        "The experiment ID field is unavailable. "
        "Experiment comparison cannot be displayed."
    )


# =========================================================
# SCIENTIFIC INTERPRETATION NOTE
# =========================================================

st.divider()

st.markdown("""
<div class="note-panel">
<strong>Scientific interpretation note</strong><br><br>
Experiment records describe the evidence available in the curated
dataset. Experimental observations, simulations, theoretical
interpretations, and planned investigations represent different
types of evidence. Search relevance scores indicate retrieval
similarity; they are not measures of experimental accuracy,
scientific certainty, or fire risk.
</div>
""", unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown("""
<div class="fg-footer">
<p>FLAMEGUARD · NASA SPACE APPS CHALLENGE 2026 · TEAM NST</p>
<p>Explore the evidence. Understand the limitations. Support scientific discovery.</p>
<p>Research insights do not replace validated spacecraft fire-safety assessments.</p>
</div>
""", unsafe_allow_html=True)
