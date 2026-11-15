
import streamlit as st
import plotly.express as px
import pandas as pd

from modules.analytics import (
    ANALYTICS_CATEGORIES,
    get_experiment_data,
    get_overview_metrics,
    get_category_distribution,
    get_evidence_type_distribution,
    get_findings_status_distribution,
    get_data_coverage,
)

from modules.retrieval_engine import retrieve_research

from modules.ranking_engine import (
    rank_evidence,
    rank_experiments,
)

st.set_page_config(
    page_title="FlameGuard | Research Analytics",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# THEME
# ---------------------------------------------------------

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

.analytics-hero {
    padding: 2.2rem 2.5rem;
    border: 1px solid rgba(68, 205, 230, 0.25);
    border-radius: 22px;
    background: linear-gradient(120deg, rgba(16, 43, 65, 0.96),
                                rgba(13, 27, 46, 0.94));
    margin-bottom: 1.8rem;
}

.analytics-kicker {
    color: #42d7e9;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 3px;
    margin-bottom: 0.8rem;
}

.analytics-title {
    color: #f3f8ff;
    font-size: clamp(2rem, 4vw, 3.3rem);
    font-weight: 850;
    line-height: 1.1;
    margin: 0;
}

.analytics-title span {
    color: #43d5e8;
}

.analytics-description {
    color: #a9bdd0;
    font-size: 1rem;
    line-height: 1.8;
    max-width: 850px;
    margin-top: 1rem;
}

.analytics-status {
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
    min-height: 125px;
}

.metric-label {
    color: #9eb5c9;
    font-size: 0.78rem;
    font-weight: 650;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.metric-value {
    color: #f4f9ff;
    font-size: 2.1rem;
    font-weight: 850;
    margin-top: 0.35rem;
}

.metric-accent {
    color: #42d7e9;
}

.chart-panel {
    background: rgba(15, 32, 51, 0.72);
    border: 1px solid rgba(105, 160, 190, 0.16);
    border-radius: 17px;
    padding: 1rem 1rem 0.4rem 1rem;
}

.note-panel {
    background: rgba(244, 135, 65, 0.08);
    border-left: 3px solid #f28b45;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    color: #c4d1de;
    font-size: 0.86rem;
}

div[data-testid="stMetric"] {
    background: transparent;
}

.stSelectbox label, .stMultiSelect label {
    color: #c7d8e8 !important;
}

hr {
    border-color: rgba(120, 170, 200, 0.18);
}

.fg-footer {
    text-align: center;
    color: #7890a7;
    font-size: 0.76rem;
    line-height: 1.8;
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------

st.markdown("""
<div class="analytics-hero">
<div class="analytics-kicker">FLAMEGUARD • SCIENTIFIC DATA INTELLIGENCE</div>
<h1 class="analytics-title">RESEARCH <span>ANALYTICS</span></h1>
<div class="analytics-description">
Explore the landscape of microgravity combustion research.
Examine experiment records, compare evidence categories, investigate
documented findings, and understand where scientific information
is available or remains unreported.
</div>
<div class="analytics-status">◈ CURATED RESEARCH DATASET • ANALYTICAL OVERVIEW</div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

try:
    df = get_experiment_data()

    if df is None or df.empty:
        st.warning("The experiment dataset is currently empty.")
        st.stop()

except Exception as error:
    st.error("The research dataset could not be loaded.")
    st.exception(error)
    st.stop()


# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------

st.markdown('<div class="section-heading">Explore the dataset</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Filter records to investigate specific research areas.</div>',
    unsafe_allow_html=True
)

filter_col1, filter_col2 = st.columns(2)

filtered_df = df.copy()

with filter_col1:
    if "research_program" in df.columns:
        program_options = sorted(
            df["research_program"].dropna().astype(str).unique().tolist()
        )
        selected_programs = st.multiselect(
            "Research programs",
            options=program_options,
            default=program_options,
            help="Select one or more research programs."
        )
        filtered_df = filtered_df[
            filtered_df["research_program"].astype(str).isin(selected_programs)
        ]

with filter_col2:
    if "evidence_level" in df.columns:
        evidence_options = sorted(
            df["evidence_level"].dropna().astype(str).unique().tolist()
        )
        selected_evidence = st.multiselect(
            "Evidence levels",
            options=evidence_options,
            default=evidence_options,
            help="Filter records by their documented evidence level."
        )
        filtered_df = filtered_df[
            filtered_df["evidence_level"].astype(str).isin(selected_evidence)
        ]

if filtered_df.empty:
    st.info("No records match the selected filters. Adjust your selections to continue.")
    st.stop()


# ---------------------------------------------------------
# OVERVIEW METRICS
# ---------------------------------------------------------

metrics = get_overview_metrics(filtered_df)

st.markdown('<div class="section-heading">Dataset at a glance</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">A high-level view of the currently selected records.</div>',
    unsafe_allow_html=True
)

metric_columns = st.columns(4)

metric_items = [
    ("EXPERIMENT RECORDS", metrics["total_experiments"]),
    ("RESEARCH PROGRAMS", metrics["research_programs"]),
    ("EVIDENCE LEVELS", metrics["evidence_levels"]),
    ("FUEL MATERIALS", metrics["fuel_material_entries"]),
]

for column, (label, value) in zip(metric_columns, metric_items):
    with column:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value metric-accent">{value}</div>
        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------
# RESEARCH LANDSCAPE
# ---------------------------------------------------------

st.markdown('<div class="section-heading">Research landscape</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Explore how the curated records are distributed across research dimensions.</div>',
    unsafe_allow_html=True
)

available_categories = [
    category for category in ANALYTICS_CATEGORIES
    if category in filtered_df.columns
]

if available_categories:
    selected_category = st.selectbox(
        "Choose a research dimension",
        options=available_categories,
        format_func=lambda value: value.replace("_", " ").title()
    )

    category_data = get_category_distribution(
        filtered_df,
        selected_category
    )

    if not category_data.empty:
        chart_col1, chart_col2 = st.columns([1.15, 0.85])

        with chart_col1:
            fig = px.bar(
                category_data.sort_values("count", ascending=True),
                x="count",
                y="category",
                orientation="h",
                text="count",
                color="count",
                color_continuous_scale=["#176b83", "#39d5e5"],
                title=f"Records by {selected_category.replace('_', ' ').title()}",
            )
            fig.update_traces(
                textposition="outside",
                cliponaxis=False,
                marker_line_width=0
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#dceaf5",
                title_font_size=16,
                coloraxis_showscale=False,
                margin=dict(l=10, r=25, t=55, b=20),
                xaxis_title="Number of records",
                yaxis_title="",
            )
            st.plotly_chart(fig, use_container_width=True)

        with chart_col2:
            pie = px.pie(
                category_data,
                names="category",
                values="count",
                hole=0.62,
                title="Category share",
                color_discrete_sequence=[
                    "#35cfe0", "#f28b45", "#6387d8",
                    "#7bd6a3", "#a58be8", "#d9b45e"
                ],
            )
            pie.update_traces(
                textposition="inside",
                textinfo="percent",
                hole=0.62
            )
            pie.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#dceaf5",
                title_font_size=16,
                margin=dict(l=10, r=10, t=55, b=15),
                legend_title_text=""
            )
            st.plotly_chart(pie, use_container_width=True)
    else:
        st.info("No reported values are available for this research dimension.")
else:
    st.info("No supported research-category columns were found.")



# ---------------------------------------------------------
# QUERY-BASED RESEARCH RANKING
# ---------------------------------------------------------

st.markdown(
    '<div class="section-heading">Query-Based Research Ranking</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-caption">'
    'Search NASA combustion research and identify the most relevant '
    'experiments, with traceable supporting passages.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="note-panel">
Enter a scientific research question to retrieve and rank relevant
research. Scores are heuristic research-ranking indicators, not
scientific certainty, physical fire risk, or safety assessments.
</div>
""", unsafe_allow_html=True)

with st.form("research_ranking_form"):
    research_query = st.text_input(
        "Research question",
        placeholder="e.g. How does oxygen concentration affect flame extinction in microgravity?"
    )

    submitted = st.form_submit_button(
        "Search and Rank Experiments",
        use_container_width=True
    )

current_filtered_ids = sorted(
    filtered_df["experiment_id"].astype(str).unique().tolist()
)

if submitted:
    if not research_query.strip():
        st.warning("Please enter a research question.")

    else:
        try:
            with st.spinner("Searching NASA research passages..."):

                # Retrieve relevant passages from the research corpus.
                retrieved_records = retrieve_research(
                    research_query.strip(),
                    top_k=50
                )

                # Respect the research-program and evidence-level filters.
                retrieved_records = [
                    record
                    for record in retrieved_records
                    if str(record.get("experiment_id"))
                    in current_filtered_ids
                ]

                # Rank individual research passages.
                ranked_passages = rank_evidence(retrieved_records)

                # Group and rank distinct experiments.
                experiment_results = rank_experiments(ranked_passages)

                st.session_state["analytics_ranked_experiments"] = (
                    experiment_results
                )

                st.session_state["analytics_ranking_query"] = (
                    research_query.strip()
                )

                st.session_state["analytics_ranking_filter_ids"] = (
                    current_filtered_ids
                )

        except Exception as error:
            st.error("Research ranking could not be completed.")
            st.exception(error)


# Display the latest results if they belong to the current filters.
saved_results = st.session_state.get(
    "analytics_ranked_experiments"
)

saved_filter_ids = st.session_state.get(
    "analytics_ranking_filter_ids"
)

if saved_results is not None:

    if saved_filter_ids != current_filtered_ids:
        st.info(
            "The dataset filters have changed. Run the search again "
            "to generate rankings for the selected records."
        )

    elif not saved_results:
        st.warning(
            "No relevant research passages were found for this query "
            "within the selected filters."
        )

    else:
        st.markdown("**Experiment ranking results**")

        st.caption(
            f"Search query: {st.session_state['analytics_ranking_query']}"
        )

        ranking_table = pd.DataFrame([
            {
                "Experiment": item["experiment_name"],
                "Experiment ID": item["experiment_id"],
                "Supporting passages": item["passage_count"],
                "Relevance": item["relevance_component_score"],
                "Evidence strength": item["evidence_strength_score"],
                "Completeness": item["completeness_score"],
                "Overall score": item["overall_score"],
            }
            for item in saved_results
        ])

        st.dataframe(
            ranking_table,
            hide_index=True,
            use_container_width=True
        )

        st.markdown("**Explore supporting research**")

        for index, experiment in enumerate(saved_results, start=1):

            with st.expander(
                f"{index}. {experiment['experiment_name']} "
                f"— Score: {experiment['overall_score']:.2f}"
            ):

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Relevance",
                    f"{experiment['relevance_component_score']:.2f}"
                )

                col2.metric(
                    "Evidence strength",
                    f"{experiment['evidence_strength_score']:.2f}"
                )

                col3.metric(
                    "Completeness",
                    f"{experiment['completeness_score']:.2f}"
                )

                st.caption(
                    f"Experiment ID: {experiment['experiment_id']} | "
                    f"Supporting passages: {experiment['passage_count']}"
                )

                st.markdown("**Ranking explanation**")

                for reason in experiment["ranking_reasons"]:
                    st.write(f"• {reason}")

                st.markdown("**Supporting NASA research passages**")

                for passage_number, passage in enumerate(
                    experiment["supporting_passages"],
                    start=1
                ):

                    st.markdown(
                        f"**Passage {passage_number}: "
                        f"{passage.get('passage_id', 'Not available')}**"
                    )

                    st.write(
                        passage.get(
                            "matched_passage",
                            "Passage text unavailable."
                        )
                    )

                    st.caption(
                        f"Source: {passage.get('source_title', 'Not reported')} "
                        f"| Page: {passage.get('page_number', 'Not reported')} "
                        f"| Section: {passage.get('section_name', 'Not reported')}"
                    )

                    source_url = passage.get("source_url")

                    if (
                        isinstance(source_url, str)
                        and source_url.startswith("https://")
                    ):
                        st.markdown(
                            f"[Open NASA source]({source_url})"
                        )

                    st.divider()


# ---------------------------------------------------------
# EVIDENCE COMPOSITION
# ---------------------------------------------------------

st.markdown('<div class="section-heading">Evidence composition</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Records are grouped by the evidence type documented in the dataset.</div>',
    unsafe_allow_html=True
)

evidence_data = get_evidence_type_distribution(filtered_df)

if not evidence_data.empty:
    col1, col2 = st.columns([1, 1])

    with col1:
        evidence_fig = px.bar(
            evidence_data.sort_values("count", ascending=True),
            x="count",
            y="evidence_type",
            orientation="h",
            text="count",
            color="count",
            color_continuous_scale=["#24516b", "#39d5e5"],
            title="Records by evidence type"
        )
        evidence_fig.update_traces(textposition="outside",
                cliponaxis=False)
        evidence_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dceaf5",
            coloraxis_showscale=False,
            title_font_size=16,
            margin=dict(l=10, r=25, t=55, b=20),
            xaxis_title="Number of records",
            yaxis_title=""
        )
        st.plotly_chart(evidence_fig, use_container_width=True)

    with col2:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        st.markdown("**Evidence category breakdown**")
        st.dataframe(
            evidence_data,
            hide_index=True,
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Evidence classifications are not available for these records.")

st.markdown("""
<div class="note-panel">
Evidence categories describe the nature of the available records.
A simulation, theoretical interpretation, planned investigation,
or secondary summary should not be treated as equivalent to a
direct experimental observation.
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# FINDINGS STATUS
# ---------------------------------------------------------

st.markdown('<div class="section-heading">Research findings status</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">What does the available dataset actually document about research outcomes?</div>',
    unsafe_allow_html=True
)

findings_data = get_findings_status_distribution(filtered_df)

if not findings_data.empty:
    findings_fig = px.bar(
        findings_data.sort_values("count", ascending=True),
        x="count",
        y="research_status",
        orientation="h",
        text="count",
        color="research_status",
        color_discrete_sequence=[
            "#35cfe0", "#f28b45", "#6387d8",
            "#7bd6a3", "#a58be8"
        ],
        title="Documented findings status"
    )
    findings_fig.update_traces(textposition="outside",
                cliponaxis=False)
    findings_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#dceaf5",
        showlegend=False,
        title_font_size=16,
        margin=dict(l=10, r=25, t=55, b=20),
        xaxis_title="Number of records",
        yaxis_title=""
    )
    st.plotly_chart(findings_fig, use_container_width=True)
else:
    st.info("Findings status could not be calculated.")


# ---------------------------------------------------------
# DATA COMPLETENESS
# ---------------------------------------------------------

st.markdown('<div class="section-heading">Dataset completeness</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Understand which fields contain reported information, explicitly unavailable information, or missing values.</div>',
    unsafe_allow_html=True
)

coverage = get_data_coverage(filtered_df)

if not coverage.empty:
    coverage_col1, coverage_col2 = st.columns([1.25, 0.75])

    with coverage_col1:
        coverage_long = coverage.melt(
            id_vars=["field"],
            value_vars=[
                "reported",
                "explicitly_unavailable",
                "missing"
            ],
            var_name="information_status",
            value_name="record_count"
        )

        coverage_fig = px.bar(
            coverage_long,
            x="record_count",
            y="field",
            color="information_status",
            orientation="h",
            barmode="stack",
            title="Information status by research field",
            color_discrete_map={
                "reported": "#35cfe0",
                "explicitly_unavailable": "#f28b45",
                "missing": "#65758b"
            },
            category_orders={
                "information_status": [
                    "reported",
                    "explicitly_unavailable",
                    "missing"
                ]
            }
        )
        coverage_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dceaf5",
            title_font_size=16,
            margin=dict(l=10, r=15, t=55, b=20),
            xaxis_title="Number of records",
            yaxis_title="",
            legend_title_text="Information status"
        )
        st.plotly_chart(coverage_fig, use_container_width=True)

    with coverage_col2:
        percentage_fig = px.bar(
            coverage.sort_values("coverage_percent", ascending=True),
            x="coverage_percent",
            y="field",
            orientation="h",
            text="coverage_percent",
            title="Documented information coverage",
            color="coverage_percent",
            color_continuous_scale=["#24516b", "#35cfe0"]
        )
        percentage_fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
                cliponaxis=False
        )
        percentage_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dceaf5",
            coloraxis_showscale=False,
            title_font_size=16,
            margin=dict(l=10, r=60, t=55, b=20),
            xaxis_title="Coverage (%)",
            yaxis_title="",
            xaxis_range=[0, 125]
        )
        st.plotly_chart(percentage_fig, use_container_width=True)

    st.caption(
        "Documented coverage includes both reported values and explicit "
        "statements that information or results are unavailable. "
        "It does not mean that every field contains measured results."
    )

    with st.expander("View detailed data coverage table"):
        st.dataframe(
            coverage.rename(columns={
                "field": "Research field",
                "reported": "Reported",
                "explicitly_unavailable": "Explicitly unavailable",
                "missing": "Missing",
                "coverage_percent": "Documented coverage (%)"
            }),
            hide_index=True,
            use_container_width=True
        )
else:
    st.info("Data coverage information is not available.")


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.markdown("""
<div class="fg-footer">
<p>FLAMEGUARD · NASA SPACE APPS CHALLENGE 2026 · TEAM NST</p>
<p>Analytics describe the curated dataset, not the complete body of combustion research.</p>
<p>Research evidence supports scientific exploration and does not replace validated spacecraft fire-safety assessments.</p>
</div>
""", unsafe_allow_html=True)
