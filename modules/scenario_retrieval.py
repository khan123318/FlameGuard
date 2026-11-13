try:
    from modules.retrieval_engine import retrieve_research
except ImportError:
    from retrieval_engine import retrieve_research

# Scenario fields and the words they add to the search
PARAMETER_WORDS = {
    "oxygen_percent": "oxygen concentration",
    "air_velocity_m_s": "airflow velocity flow speed",
    "temperature_k": "temperature",
    "pressure_pa": "pressure",
}


def build_query(scenario):
    parts = []
    for key in ("fuel_or_material", "description"):
        value = scenario.get(key)
        if value:
            parts.append(str(value))
    for key, words in PARAMETER_WORDS.items():
        if scenario.get(key) is not None:
            parts.append(words)
    return " ".join(parts)


def retrieve_for_scenario(scenario, top_k=5):
    """Find NASA evidence for a spacecraft fire scenario.

    scenario is a dictionary. All keys are optional:
    fuel_or_material, description, scenario_type, oxygen_percent,
    air_velocity_m_s, temperature_k, pressure_pa.
    """
    scenario = scenario or {}
    query = build_query(scenario)
    limitations = []

    if not query.strip():
        return {"query": "", "evidence": [],
                "limitations": ["The scenario has no searchable fields."]}

    evidence = retrieve_research(query, top_k=top_k)
    if not evidence:
        limitations.append("No evidence was found for this scenario.")

    material = str(scenario.get("fuel_or_material") or "").strip()
    if material:
        name = material.lower()
        named = any(
            name in (str(r["fuel_material"]) + " " + str(r["experiment_name"]) + " "
                     + str(r["matched_passage"])).lower()
            for r in evidence)
        if not named:
            limitations.append("No retrieved evidence names the material '" + material
                               + "'. The results describe related conditions only.")

    if "electrical" in str(scenario.get("scenario_type") or "").lower():
        limitations.append("The dataset has no electrical-equipment fire experiments. "
                           "It covers fuel droplets, solid materials and gaseous surrogate fuels.")

    limitations.append("The evidence is condition-specific (microgravity tests with specific "
                       "materials and atmospheres). It is not a safety threshold or a certification.")

    return {"query": query, "evidence": evidence, "limitations": limitations}