"""Evidence-grounded prompt templates for FlameGuard."""

from typing import Any, Iterable, Mapping


SYSTEM_PROMPT = """
You are FlameGuard, an AI research assistant for NASA microgravity
combustion research and spacecraft fire-safety evidence.

SCIENTIFIC AND EVIDENCE RULES

1. Use only the supplied research evidence for claims about specific
   experiments, materials, measured outcomes, and NASA findings.

2. Never invent measurements, experimental conditions, thresholds,
   citations, page numbers, source titles, URLs, or experiment results.

3. Clearly distinguish experimental observations, secondary summaries,
   literature reviews, simulations, theory, hypotheses, and planned research.

4. Never present a hypothesis or preliminary interpretation as a
   confirmed experimental result.

5. Keep findings tied to the specific material, geometry, environment,
   and conditions reported in the cited research.

6. If a value or result is absent, state that it was not reported
   in the available research record.

7. Explain uncertainty and limitations, especially when evidence is
   incomplete, indirect, or not applicable to the scenario.

8. A retrieval relevance score measures textual similarity.
   It is NOT scientific certainty, evidence quality, hazard severity,
   or fire probability.

9. Missing evidence does not mean a scenario is safe.

10. Never provide spacecraft safety certification or operational
    go/no-go decisions. State that engineering validation and
    mission-specific safety review are required.

RESPONSE STYLE

- Be technically clear and concise.
- Separate supported findings from interpretation.
- Identify the supporting experiment whenever possible.
- Attach citations using the supplied source metadata.
- Explicitly state when the available evidence is insufficient.
""".strip()


RESEARCH_ANSWER_TEMPLATE = """
USER QUESTION

{question}


RETRIEVED NASA RESEARCH EVIDENCE

{evidence_text}


INSTRUCTIONS

Answer the question using the supplied evidence.

For important factual claims:
- Identify the supporting experiment.
- Identify the source where possible.
- Distinguish direct observations from secondary summaries,
  simulations, theories, and hypotheses.
- Explain relevant limitations.
- Do not extrapolate beyond the reported experimental conditions.

If the supplied records do not answer the question, state this explicitly.
""".strip()


SCENARIO_EVALUATION_TEMPLATE = """
SPACECRAFT FIRE SCENARIO

{scenario_text}


RETRIEVED RESEARCH EVIDENCE

{evidence_text}


EVIDENCE REVIEW

{evaluation_text}


INSTRUCTIONS

Explain which retrieved studies are relevant and why.

Identify differences between the spacecraft scenario and the
materials or conditions studied in the retrieved experiments.

Explain what the available dataset does not establish.

Evidence-support and evidence-gap scores are heuristic research-review
indicators only. They are NOT physical fire-risk scores, probability
estimates, severity ratings, or safety thresholds.

Never infer that a scenario is safe because evidence is limited or absent.

Do not present this analysis as a certified engineering assessment.
""".strip()


def _display_value(value: Any) -> str:
    """Convert values into readable text while handling missing values."""

    if value is None:
        return "not reported"

    try:
        if value != value:
            return "not reported"
    except (TypeError, ValueError):
        pass

    text = str(value).strip()

    if not text or text.lower() in {
        "nan",
        "none",
        "null",
        "not reported",
        "not stated",
        "not specified",
        "unavailable",
    }:
        return "not reported"

    return text


def format_evidence_for_prompt(
    evidence: Iterable[Mapping[str, Any]]
) -> str:
    """Format retrieved research records for the AI prompt."""

    if evidence is None:
        return "No research evidence was retrieved."

    blocks = []

    for index, record in enumerate(evidence, start=1):

        if not isinstance(record, Mapping):
            continue

        fields = [
            ("Experiment", record.get("experiment_name")),
            ("Experiment ID", record.get("experiment_id")),
            ("Research program", record.get("research_program")),
            ("Material/fuel", record.get("fuel_material")),
            ("Findings", record.get("findings")),
            ("Safety relevance", record.get("safety_relevance")),
            ("Evidence level", record.get("evidence_level")),
            ("Matched passage", record.get("matched_passage")),
            ("Source title", record.get("source_title")),
            ("Source type", record.get("source_type")),
            ("Page", record.get("page_number")),
            ("Section", record.get("section_name")),
            ("Source URL", record.get("source_url")),
            (
                "Retrieval relevance (text similarity only)",
                record.get("relevance_score"),
            ),
            ("Limitations", record.get("limitations")),
        ]

        lines = [f"[Evidence {index}]"]

        for label, value in fields:
            if value is not None:
                lines.append(
                    f"{label}: {_display_value(value)}"
                )

        blocks.append("\n".join(lines))

    if not blocks:
        return "No usable research evidence was retrieved."

    return "\n\n".join(blocks)


def build_research_prompt(
    question: str,
    evidence: Iterable[Mapping[str, Any]]
) -> str:
    """Build an AI prompt for a research question."""

    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string.")

    evidence_text = format_evidence_for_prompt(evidence)

    return RESEARCH_ANSWER_TEMPLATE.format(
        question=question.strip(),
        evidence_text=evidence_text,
    )


def build_scenario_prompt(
    scenario: Mapping[str, Any],
    evaluation: Mapping[str, Any]
) -> str:
    """Build an AI prompt for a spacecraft scenario evaluation."""

    if not isinstance(scenario, Mapping):
        raise TypeError("scenario must be a mapping.")

    if not isinstance(evaluation, Mapping):
        raise TypeError("evaluation must be a mapping.")

    scenario_lines = []

    for key, value in scenario.items():

        if value is not None and str(value).strip():
            scenario_lines.append(
                f"{key}: {_display_value(value)}"
            )

    scenario_text = (
        "\n".join(scenario_lines)
        if scenario_lines
        else "No scenario details supplied."
    )

    evidence = evaluation.get("evidence", [])

    evidence_text = format_evidence_for_prompt(evidence)

    limitations = evaluation.get("limitations", [])
    gap_reasons = evaluation.get("evidence_gap_reasons", [])

    evaluation_lines = [
        (
            "Evidence support score (heuristic): "
            + _display_value(
                evaluation.get("evidence_support_score")
            )
        ),
        (
            "Evidence-gap priority (heuristic): "
            + _display_value(
                evaluation.get("evidence_gap_priority")
            )
        ),
        (
            "Evidence-gap reasons: "
            + (
                "; ".join(str(item) for item in gap_reasons)
                if gap_reasons
                else "none supplied"
            )
        ),
        (
            "Limitations: "
            + (
                "; ".join(str(item) for item in limitations)
                if limitations
                else "none supplied"
            )
        ),
    ]

    return SCENARIO_EVALUATION_TEMPLATE.format(
        scenario_text=scenario_text,
        evidence_text=evidence_text,
        evaluation_text="\n".join(evaluation_lines),
    )


# Alternative names for compatibility with other modules.

build_user_prompt = build_research_prompt

format_retrieved_evidence = format_evidence_for_prompt