
import streamlit as st

from modules.retrieval_engine import retrieve_research
from modules.ai_assistant import generate_research_answer


# ---------------------------------
# PAGE CONFIGURATION
# ---------------------------------

st.set_page_config(
    page_title="FlameGuard | AI Research Assistant",
    page_icon="🔥",
    layout="wide"
)


# ---------------------------------
# PAGE HEADER
# ---------------------------------

st.title("🔥 FlameGuard")
st.subheader("AI-Powered Microgravity Combustion Research")

st.markdown(
    """
    Explore NASA combustion experiments, retrieve scientific evidence,
    and investigate spacecraft fire-safety research.
    """
)

st.divider()


# ---------------------------------
# RESEARCH QUESTION INPUT
# ---------------------------------

st.header("Ask the Research Assistant")

user_question = st.text_area(
    "Enter your research question:",
    placeholder="Example: What have NASA experiments observed about flame behavior in microgravity?",
    height=100
)

if st.button("Search Research", type="primary"):

    if not user_question.strip():
        st.warning("Please enter a research question.")

    else:
        with st.spinner("Searching NASA research evidence..."):

            try:
                # Retrieve relevant NASA research.
                evidence = retrieve_research(
                    user_question,
                    top_k=5
                )

                # Generate an evidence-grounded response.
                result = generate_research_answer(
                    user_question,
                    evidence
                )

                st.success("Research analysis completed.")

                # Display answer.
                st.subheader("Answer")
                st.write(result["answer"])

                # Display findings.
                st.subheader("Key Findings")

                for finding in result["key_findings"]:
                    st.markdown(f"- {finding}")

                # Scientific explanation.
                st.subheader("Scientific Explanation")
                st.write(result["scientific_explanation"])

                # Safety implications.
                st.subheader("Safety Implications")
                st.write(result["safety_implications"])

                # Limitations.
                st.subheader("Limitations")

                for limitation in result["limitations"]:
                    st.markdown(f"- {limitation}")

                # Sources.
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


# ---------------------------------
# FOOTER
# ---------------------------------

st.divider()

st.caption(
    "FlameGuard | NASA Space Apps Challenge 2026 | "
    "Research evidence is not a substitute for validated spacecraft safety assessments."
)
