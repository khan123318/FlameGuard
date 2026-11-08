import streamlit as st

from modules.data_loader import load_experiments
from modules.retrieval_engine import retrieve_research

# Page configuration
st.set_page_config(
    page_title="FlameGuard | Experiment Explorer",
    page_icon="🔥",
    layout="wide"
)

# Load experiment dataset
df = load_experiments()

# Page heading
st.title("NASA Experiment Explorer")

st.write(
    "Explore and search NASA microgravity combustion experiments."
)

# Display total experiments
st.metric(
    label="Total Experiments",
    value=len(df)
)

st.divider()

st.header("Search and Filter Experiments")

# Research query
search_query = st.text_input(
    "Search experiments",
    placeholder="Example: PMMA flame spread"
)

# Create filter options from the dataset
program_options = ["All"] + sorted(
    df["research_program"].dropna().astype(str).unique().tolist()
)

material_options = ["All"] + sorted(
    df["material_class"].dropna().astype(str).unique().tolist()
)

environment_options = ["All"] + sorted(
    df["environment"].dropna().astype(str).unique().tolist()
)

# Display filters in three columns
col1, col2, col3 = st.columns(3)

with col1:
    selected_program = st.selectbox(
        "Research Program",
        program_options
    )

with col2:
    selected_material = st.selectbox(
        "Material Class",
        material_options
    )

with col3:
    selected_environment = st.selectbox(
        "Environment",
        environment_options
    )

# Search button
if st.button("Search Experiments", type="primary"):

    if not search_query.strip():
        st.warning("Please enter a research query.")

    else:
        # Build filters dictionary
        filters = {}

        if selected_program != "All":
            filters["research_program"] = selected_program

        if selected_material != "All":
            filters["material_class"] = selected_material

        if selected_environment != "All":
            filters["environment"] = selected_environment

        try:
            with st.spinner("Searching experiments..."):

                results = retrieve_research(
                    search_query,
                    filters=filters,
                    top_k=10
                )

            st.subheader("Search Results")

            if results:
                st.success(
                    f"Found {len(results)} relevant experiments."
                )

                for index, experiment in enumerate(results, start=1):

                    with st.expander(
                        f"{index}. {experiment['experiment_name']}"
                    ):

                        st.write(
                            "**Experiment ID:**",
                            experiment["experiment_id"]
                        )

                        st.write(
                            "**Research Program:**",
                            experiment["research_program"]
                        )

                        st.write(
                            "**Fuel Material:**",
                            experiment["fuel_material"]
                        )

                        st.write(
                            "**Findings:**",
                            experiment["findings"]
                        )

                        st.write(
                            "**Safety Relevance:**",
                            experiment["safety_relevance"]
                        )

                        st.write(
                            "**Evidence Level:**",
                            experiment["evidence_level"]
                        )

                        st.write(
                            "**Limitations:**",
                            experiment["limitations"]
                        )

                        st.metric(
                            "Relevance Score",
                            experiment["relevance_score"]
                        )

                        if experiment["source_url"]:
                            st.markdown(
                                f"[Open NASA Source]({experiment['source_url']})"
                            )

            else:
                st.info(
                    "No matching experiments found. "
                    "Try a different query or filter."
                )

        except Exception as error:
            st.error("Unable to retrieve experiments.")
            st.exception(error)

st.divider()

st.header("Compare NASA Experiments")

st.write(
    "Select two or more experiments to compare their "
    "research characteristics and findings."
)

# Get available experiment IDs
experiment_ids = df["experiment_id"].dropna().tolist()

# Let users select experiments
selected_experiments = st.multiselect(
    "Choose experiments to compare:",
    options=experiment_ids
)

if len(selected_experiments) >= 2:

    # Get selected experiment records
    comparison_df = df[
        df["experiment_id"].isin(selected_experiments)
    ]

    # Select useful comparison fields
    comparison_fields = [
        "experiment_id",
        "research_program",
        "fuel_material",
        "environment",
        "objective",
        "variables_studied",
        "findings",
        "safety_relevance",
        "evidence_level",
        "limitations"
    ]

    comparison_df = comparison_df[comparison_fields]

    # Display experiments as columns
    comparison_df = comparison_df.set_index("experiment_id").T

    st.subheader("Experiment Comparison")

    st.dataframe(
        comparison_df,
        use_container_width=True
    )

elif len(selected_experiments) == 1:

    st.info("Select at least one more experiment to compare.")

else:

    st.info("Choose experiments from the dropdown to begin comparing.")
