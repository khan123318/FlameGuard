import streamlit as st

from modules.retrieval_engine import retrieve_research
from modules.ai_assistant import generate_research_answer

# Page configuration
st.set_page_config(
    page_title="FlameGuard | AI Research Assistant",
    page_icon="🤖",
    layout="wide"
)

# Header
st.title("NASA AI Research Assistant")
st.write(
    "Ask scientific questions grounded strictly in empirical NASA microgravity combustion research. "
    "All responses are synthesized directly from local NASA flight evidence, technical publications, and conference proceedings."
)

st.info(
    "**Evidence Grounding Guarantee:** Responses are built exclusively from retrieved NASA experiment passages. "
    "Every finding cites the original NASA document title, page number, and section."
)

st.divider()

# Suggested research questions
st.subheader("1. Sample Research Prompts")
st.write("Click any sample question or type your own below:")

c1, c2 = st.columns(2)
with c1:
    btn1 = st.button("What is a cool flame and how does it extinguish?")
    btn2 = st.button("How does sample thickness affect flame spread over PMMA?")
with c2:
    btn3 = st.button("What are the blow-off extinction conditions for SIBAL fabric?")
    btn4 = st.button("How effective is carbon dioxide as a fire suppressant in space?")

# Determine initial question text
default_query = ""
if btn1:
    default_query = "What is a cool flame and how does it extinguish?"
elif btn2:
    default_query = "How does sample thickness affect flame spread over PMMA?"
elif btn3:
    default_query = "What are the blow-off extinction conditions for SIBAL fabric?"
elif btn4:
    default_query = "How effective is carbon dioxide as a fire suppressant in space?"

# Input box
st.subheader("2. Ask Your Question")
user_query = st.text_area(
    "Enter research query:",
    value=default_query,
    placeholder="e.g. Can flames burn without visible light in microgravity?",
    height=100
)

col_search, col_topk = st.columns([4, 1])
with col_topk:
    top_k = st.slider("Top Evidence Records", min_value=1, max_value=8, value=5)

with col_search:
    search_clicked = st.button("Generate Evidence-Grounded Answer", type="primary")

# Execute search & synthesis
if search_clicked or default_query:
    if not user_query.strip():
        st.warning("Please enter a research question.")
    else:
        with st.spinner("Retrieving NASA evidence and synthesizing grounded explanation..."):
            try:
                # 1. Retrieve local NASA evidence
                evidence = retrieve_research(user_query, top_k=top_k)

                # 2. Synthesize evidence-grounded response
                result = generate_research_answer(user_query, evidence)

                st.success(f"Analysis complete. Synthesized from {len(evidence)} retrieved NASA evidence passages.")

                # Section: Answer
                st.subheader("Synthesis & Summary")
                st.write(result.get("answer", "No answer generated."))

                # Section: Key Findings
                st.subheader("Key Empirical Findings")
                findings = result.get("key_findings", [])
                if findings:
                    for f in findings:
                        st.markdown(f"- {f}")
                else:
                    st.write("No specific findings reported.")

                # Section: Scientific Explanation
                st.subheader("Scientific Explanation")
                st.write(result.get("scientific_explanation", "No explanation available."))

                # Section: Safety Implications
                st.subheader("Spacecraft Fire Safety Implications")
                st.write(result.get("safety_implications", "No safety implications reported."))

                # Section: Limitations
                st.subheader("Evidence Limitations & Hedges")
                limitations = result.get("limitations", [])
                if limitations:
                    for lim in limitations:
                        st.warning(f"⚠️ {lim}")

                # Section: Citations & Passages
                st.subheader("Cited NASA Sources & Exact Passages")
                sources = result.get("sources", [])
                if sources:
                    for i, src in enumerate(sources, start=1):
                        title = src.get("source_title", "NASA Document")
                        exp_name = src.get("experiment_name", "Microgravity Experiment")
                        url = src.get("source_url", "#")
                        page = src.get("page_number", "not reported")

                        with st.expander(f"**Source {i}: {title}**"):
                            st.markdown(f"**Experiment:** {exp_name}")
                            st.markdown(f"**Page Citation:** {page}")
                            st.markdown(f"**Source Link:** [{url}]({url})")

                # Show retrieved passages details
                if evidence:
                    with st.expander("🔍 View Raw Retrieved Passages"):
                        for item in evidence:
                            st.markdown(f"**[{item['experiment_id']}] {item['experiment_name']}** (Score: {item['relevance_score']})")
                            st.caption(f"Source: {item['source_title']} | Page: {item['page_number']} | Section: {item['section_name']}")
                            st.markdown(f"> *\"{item['matched_passage']}\"*")
                            st.divider()

            except Exception as e:
                st.error("Error generating answer.")
                st.exception(e)
