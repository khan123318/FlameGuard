
REQUIRED_FIELDS = [
    "answer",
    "key_findings",
    "scientific_explanation",
    "safety_implications",
    "limitations",
    "sources"
]


def create_empty_response():
    """
    Returns an empty response following
    the standard FlameGuard response structure.
    """
    return {
        "answer": "",
        "key_findings": [],
        "scientific_explanation": "",
        "safety_implications": "",
        "limitations": [],
        "sources": []
    }


def validate_response(response):
    """
    Checks whether an AI assistant response
    follows the required structure.
    """

    if not isinstance(response, dict):
        return False

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in response:
            return False

    # Check field types
    if not isinstance(response["answer"], str):
        return False

    if not isinstance(response["key_findings"], list):
        return False

    if not isinstance(response["scientific_explanation"], str):
        return False

    if not isinstance(response["safety_implications"], str):
        return False

    if not isinstance(response["limitations"], list):
        return False

    if not isinstance(response["sources"], list):
        return False

    return True
