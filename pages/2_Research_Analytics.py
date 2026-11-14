import streamlit as st
import pandas as pd

from modules.analytics import (
    get_experiment_data,
    get_overview_metrics,
    get_category_distribution,
    get_data_coverage,
    get_findings_status_distribution,
    get_evidence_type_distribution,
)

# Page configuration
st.set_page_config(
    page_title="FlameGuard | Research Analytics",
    page_icon="📊",
    layout="wide"
)

# Load data through analytics module
df = get_experiment_data()
metrics = get_overview_metrics(df)

# Header
st.title("NASA Research & Dataset Analytics")
st.write(
    "Visual analytics and data integrity distributions across curated NASA microgravity combustion records "
    "(FLEX, BASS-II, ACME/BRE, and follow-on ISS investigations)."
)

st.divider()

# Top metric summary cards
st.subheader("1. Dataset Overview & Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Experiments", metrics.get("total_experiments", len(df)))
with col2:
    st.metric("Research Programs", metrics.get("research_programs", 0))
with col3:
    st.metric("Materials / Fuels Tested", metrics.get("fuel_material_entries", 0))
with col4:
    st.metric("Cataloged Passages", 50)

st.divider()

# Program & Material Distributions
st.subheader("2. Investigation Programs & Evidence Distributions")

tab1, tab2, tab3 = st.tabs(["Research Programs", "Evidence Types", "Findings Status"])

with tab1:
    st.write("**Distribution of Experiments by NASA Research Program:**")
    prog_df = get_category_distribution(df, "research_program")
    if not prog_df.empty:
        chart_data = prog_df.set_index("category")["count"]
        st.bar_chart(chart_data)
        st.dataframe(prog_df, hide_index=True)

with tab2:
    st.write("**Categorization of Research Evidence Quality:**")
    evidence_df = get_evidence_type_distribution(df)
    if not evidence_df.empty:
        chart_data = evidence_df.set_index("evidence_type")["count"]
        st.bar_chart(chart_data)
        st.dataframe(evidence_df, hide_index=True)

with tab3:
    st.write("**Empirical Findings & Observation Status:**")
    findings_df = get_findings_status_distribution(df)
    if not findings_df.empty:
        chart_data = findings_df.set_index("findings_status")["count"]
        st.bar_chart(chart_data)
        st.dataframe(findings_df, hide_index=True)

st.divider()

# Data Coverage & Field Completeness
st.subheader("3. Data Completeness & Schema Integrity")
st.write(
    "Evaluation of metadata completeness across 17 standardized scientific parameters. "
    "Values not reported in primary NASA literature are strictly classified as *'not reported'* rather than extrapolated."
)

coverage_df = get_data_coverage(df)
if not coverage_df.empty:
    st.dataframe(
        coverage_df.style.format({
            "total_records": "{:.0f}",
            "reported_records": "{:.0f}",
            "missing_records": "{:.0f}",
            "completeness_pct": "{:.1f}%"
        }),
        hide_index=True
    )

st.divider()

# Interactive Filter & Explorer
st.subheader("4. Filter Records by Investigation Program")
selected_program = st.selectbox(
    "Filter dataset by research program to inspect records:",
    ["All Programs"] + sorted(df["research_program"].dropna().unique().tolist())
)

if selected_program == "All Programs":
    filtered_df = df
else:
    filtered_df = df[df["research_program"] == selected_program]

st.dataframe(
    filtered_df[[
        "experiment_id",
        "experiment_name",
        "research_program",
        "fuel_material",
        "evidence_level"
    ]],
    hide_index=True
)
