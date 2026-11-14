import streamlit as st

from modules.scenario_retrieval import retrieve_for_scenario

# Page configuration
st.set_page_config(
    page_title="FlameGuard | Safety Scenario Evaluator",
    page_icon="🛡️",
    layout="wide"
)

# Heading and overview
st.title("Spacecraft Fire Safety Scenario Evaluator")
st.write(
    "Evaluate mission fire scenarios against empirical NASA microgravity combustion research. "
    "This tool extracts relevant experiment evidence and highlights critical engineering limitations."
)

st.info(
    "**NASA Safety Notice:** Microgravity combustion data in this tool are condition-specific research "
    "observations from ISS experiments. They do not constitute official safety certifications or universal thresholds."
)

st.divider()

# Scenario selection / presets
st.subheader("1. Configure Mission Fire Scenario")

preset_choice = st.selectbox(
    "Choose a preset scenario or configure custom parameters:",
    [
        "Custom Scenario",
        "Scenario A: Electrical Equipment Overheating (Avionics / Wiring)",
        "Scenario B: Solid Polymer Flame Spread (PMMA in opposed ventilation)",
        "Scenario C: Textile Composite Flammability (SIBAL Fabric under varied O2)",
    ]
)

# Preset values
if preset_choice == "Scenario A: Electrical Equipment Overheating (Avionics / Wiring)":
    default_type = "Electrical equipment fire"
    default_material = "Wiring insulation"
    default_desc = "Overheating wiring insulation in habitable compartment under low air circulation"
    default_o2 = 21.0
    default_vel = 0.05
    default_temp = 350.0
    default_press = 101325.0
elif preset_choice == "Scenario B: Solid Polymer Flame Spread (PMMA in opposed ventilation)":
    default_type = "Solid material flame spread"
    default_material = "PMMA"
    default_desc = "Flame spread over plastic sample in opposed ventilation inside glovebox duct"
    default_o2 = 21.0
    default_vel = 0.10
    default_temp = 298.0
    default_press = 101325.0
elif preset_choice == "Scenario C: Textile Composite Flammability (SIBAL Fabric under varied O2)":
    default_type = "Solid material flame spread"
    default_material = "SIBAL fabric"
    default_desc = "Combustion and blow-off extinction behavior of cotton-fiberglass blend in concurrent flow"
    default_o2 = 18.0
    default_vel = 0.20
    default_temp = 298.0
    default_press = 101325.0
else:
    default_type = "Solid material flame spread"
    default_material = ""
    default_desc = ""
    default_o2 = 21.0
    default_vel = 0.10
    default_temp = 298.0
    default_press = 101325.0

col1, col2 = st.columns(2)

with col1:
    scenario_type = st.selectbox(
        "Scenario Type",
        [
            "Solid material flame spread",
            "Electrical equipment fire",
            "Liquid droplet fire hazard",
            "Gaseous burner surrogate",
        ],
        index=0 if "Solid" in default_type else 1
    )
    fuel_or_material = st.text_input(
        "Fuel or Material Name",
        value=default_material,
        placeholder="e.g. PMMA, SIBAL fabric, n-heptane"
    )
    description = st.text_area(
        "Scenario Description",
        value=default_desc,
        placeholder="Describe the environment, ventilation, orientation, or ignition source..."
    )

with col2:
    st.write("**Atmospheric and Ventilation Conditions:**")
    c_a, c_b = st.columns(2)
    with c_a:
        oxygen_percent = st.number_input(
            "Oxygen Concentration (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(default_o2),
            step=0.5
        )
        temperature_k = st.number_input(
            "Ambient Temperature (K)",
            min_value=100.0,
            max_value=1000.0,
            value=float(default_temp),
            step=1.0
        )
    with c_b:
        air_velocity_m_s = st.number_input(
            "Airflow Speed (m/s)",
            min_value=0.0,
            max_value=10.0,
            value=float(default_vel),
            step=0.01
        )
        pressure_pa = st.number_input(
            "Ambient Pressure (Pa)",
            min_value=10000.0,
            max_value=300000.0,
            value=float(default_press),
            step=1000.0
        )

# Evaluation trigger
if st.button("Evaluate Scenario Against NASA Research", type="primary"):
    scenario_dict = {
        "scenario_type": scenario_type,
        "fuel_or_material": fuel_or_material,
        "description": description,
        "oxygen_percent": oxygen_percent,
        "air_velocity_m_s": air_velocity_m_s,
        "temperature_k": temperature_k,
        "pressure_pa": pressure_pa,
    }

    result = retrieve_for_scenario(scenario_dict, top_k=5)
    evidence = result.get("evidence", [])
    limitations = result.get("limitations", [])
    query = result.get("query", "")

    st.divider()
    st.subheader("2. Evaluation Limitations & Safety Constraints")

    # Display limitation notices
    if limitations:
        for lim in limitations:
            if "electrical" in lim.lower() or "no retrieved evidence" in lim.lower():
                st.warning(f"⚠️ **Data Gap:** {lim}")
            else:
                st.info(f"ℹ️ **Safety Hedge:** {lim}")

    st.subheader(f"3. Retrieved NASA Research Evidence ({len(evidence)} matches)")

    if not evidence:
        st.write("No matching NASA experiment evidence was found for the given scenario parameters.")
    else:
        for i, item in enumerate(evidence, start=1):
            exp_id = item.get("experiment_id", "Unknown ID")
            exp_name = item.get("experiment_name", "Unknown Name")
            source_url = item.get("source_url", "#")
            score = item.get("relevance_score", 0.0)

            with st.expander(f"**[{exp_id}] {exp_name}** (Relevance Score: {score})", expanded=(i == 1)):
                st.markdown(f"**Research Program:** {item.get('research_program', 'not reported')}")
                st.markdown(f"**Tested Fuel/Material:** {item.get('fuel_material', 'not reported')}")
                st.markdown(f"**Primary Findings:** {item.get('findings', 'not reported')}")
                st.markdown(f"**Spacecraft Safety Relevance:** {item.get('safety_relevance', 'not reported')}")
                st.markdown(f"**Evidence Level:** `{item.get('evidence_level', 'not reported')}`")
                st.markdown(f"**Documented Limitations:** {item.get('limitations', 'not reported')}")

                passage = item.get("matched_passage", "not reported")
                if passage != "not reported":
                    st.divider()
                    st.markdown("**Matched Original NASA Passage:**")
                    st.caption(
                        f"Source: [{item.get('source_title', 'NASA Document')}]({source_url}) | "
                        f"Page: {item.get('page_number', 'N/A')} | Section: {item.get('section_name', 'N/A')}"
                    )
                    st.info(f'"{passage}"')
                else:
                    st.caption(f"Source URL: [{source_url}]({source_url})")
