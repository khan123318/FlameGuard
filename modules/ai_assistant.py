
"""
FlameGuard evidence-grounded assistant.

No external LLM/API call is made here.
Responses are built only from locally retrieved research evidence.
"""

from modules.response_schema import (
    create_empty_response,
    validate_response
)

from modules.evidence_validator import validate_evidence

from modules.prompt_templates import (
    SYSTEM_PROMPT,
    build_research_prompt,
)


def _clean(value):
    """Convert optional evidence fields into safe strings."""
    if value is None:
        return ""
    return str(value).strip()


def _make_source(record):
    """Preserve source metadata from retrieved evidence."""
    return {
        "experiment_name": _clean(record.get("experiment_name")),
        "source_title": _clean(record.get("source_title")),
        "source_url": _clean(record.get("source_url")),
        "source_type": _clean(record.get("source_type")),
        "page_number": record.get("page_number"),
    }


def prepare_research_prompt(question, retrieved_evidence):
    """
    Prepare an evidence-grounded prompt for a future LLM integration.

    Only records that pass the existing evidence validator
    are included in the prompt.

    This function does not make an external API call.
    """

    question = _clean(question)

    if not question:
        raise ValueError("A research question is required.")

    if not isinstance(retrieved_evidence, list):
        retrieved_evidence = []

    normalized_records = []

    for record in retrieved_evidence:

        if not isinstance(record, dict):
            continue

        normalized_record = record.copy()

        passage = _clean(
            normalized_record.get("matched_passage")
            or normalized_record.get("passage")
        )

        normalized_record["matched_passage"] = passage

        normalized_records.append(normalized_record)

    valid_records, _ = validate_evidence(normalized_records)

    if not valid_records:
        return None

    return {
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": build_research_prompt(
            question,
            valid_records
        ),
    }


def _finalize_response(response):
    """Ensure every returned response follows the required schema."""
    if validate_response(response):
        return response

    fallback = create_empty_response()
    fallback["answer"] = (
        "The assistant could not produce a valid response structure."
    )
    fallback["limitations"] = [
        "Response schema validation failed."
    ]

    return fallback


def _empty_evidence_response(rejected_records=None):
    """Return a safe response when no evidence passes validation."""

    limitations = [
        "No usable research passages passed evidence validation.",
        "Relevant NASA research records are required to answer this question.",
    ]

    if rejected_records:
        limitations.append(
            f"{len(rejected_records)} retrieved record(s) were rejected "
            "by the evidence validator."
        )

        # Include a few validation reasons to help with debugging.
        for rejected in rejected_records[:3]:
            for error in rejected.get("errors", [])[:2]:
                if error not in limitations:
                    limitations.append(error)

    response = {
        "answer": (
            "I could not find usable NASA research evidence to answer "
            "this question. No scientific conclusion should be drawn "
            "from the current search results."
        ),
        "key_findings": [],
        "scientific_explanation": (
            "No relevant research passages passed evidence validation."
        ),
        "safety_implications": (
            "No spacecraft fire-safety implication can be established "
            "from the available evidence."
        ),
        "limitations": limitations,
        "sources": [],
    }

    return _finalize_response(response)


def generate_research_answer(question, retrieved_evidence):
    """
    Build a fast, evidence-only response.

    Supports either 'passage' or 'matched_passage' as the
    retrieved research text field.

    Evidence must also contain the fields required by
    evidence_validator.py.
    """

    question = _clean(question)

    if not question:
        response = {
            "answer": "Please enter a research question.",
            "key_findings": [],
            "scientific_explanation": "",
            "safety_implications": (
                "No safety implications can be assessed without "
                "a question and relevant research evidence."
            ),
            "limitations": ["No question was provided."],
            "sources": [],
        }

        return _finalize_response(response)

    if not isinstance(retrieved_evidence, list):
        retrieved_evidence = []

    # Normalize the passage field before validation.
    normalized_records = []

    for record in retrieved_evidence:
        if not isinstance(record, dict):
            continue

        normalized_record = record.copy()

        passage = _clean(
            normalized_record.get("matched_passage")
            or normalized_record.get("passage")
        )

        normalized_record["matched_passage"] = passage

        normalized_records.append(normalized_record)

    # Validate every retrieved record.
    valid_records, rejected_records = validate_evidence(
        normalized_records
    )

    if not valid_records:
        return _empty_evidence_response(rejected_records)

    # Keep at most three validated passages.
    selected_records = valid_records[:3]

    findings = []
    sources = []

    for record in selected_records:
        passage = _clean(record.get("matched_passage"))

        findings.append(passage)
        sources.append(_make_source(record))

    experiment_names = [
        _clean(record.get("experiment_name"))
        for record in selected_records
        if _clean(record.get("experiment_name"))
    ]

    experiments_text = (
        ", ".join(dict.fromkeys(experiment_names))
        if experiment_names
        else "the retrieved research records"
    )

    answer = (
        f"I found {len(selected_records)} validated research passage(s) "
        f"associated with {experiments_text}. "
        "The evidence excerpts below show what the retrieved records "
        "actually report. They should not be interpreted as conclusions "
        "beyond the cited material."
    )

    scientific_explanation = (
        "Evidence-based explanation: the following passages are taken "
        "from the retrieved research records. Any mechanism, measurement, "
        "or experimental conclusion should be interpreted in the context "
        "of its original source and experimental conditions."
    )

    safety_implications = (
        "The retrieved passages have not independently established a "
        "spacecraft fire-safety recommendation. Any safety implication "
        "must be checked against the original source, its test conditions, "
        "and the limits of the experiment."
    )

    limitations = [
        "This response summarizes retrieved text; it does not infer "
        "unstated scientific findings.",
        "Experimental conditions and units must be checked in the "
        "original source before comparing results.",
        "The retrieved passages may not represent all available NASA "
        "research on this topic.",
    ]

    if rejected_records:
        limitations.append(
            f"{len(rejected_records)} retrieved record(s) were excluded "
            "because they failed evidence validation."
        )

    response = {
        "answer": answer,
        "key_findings": findings,
        "scientific_explanation": scientific_explanation,
        "safety_implications": safety_implications,
        "limitations": limitations,
        "sources": sources,
    }

    return _finalize_response(response)
