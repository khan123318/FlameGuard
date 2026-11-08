
from urllib.parse import urlparse


# Fields required for a traceable research record
REQUIRED_FIELDS = [
    "experiment_id",
    "experiment_name",
    "matched_passage",
    "source_url",
    "source_title",
    "evidence_level"
]


# Obvious placeholder phrases that must not enter the assistant
PLACEHOLDER_PHRASES = [
    "placeholder",
    "temporary test",
    "sample combustion experiment",
    "demo experiment",
    "used to test",
    "demonstration text"
]


def validate_record(record):
    """
    Validates one research record.

    Returns a list of errors.
    An empty list means the record passed these checks.
    """

    errors = []

    # 1. Check whether the record is a dictionary
    if not isinstance(record, dict):
        return ["Record must be a dictionary."]

    # 2. Check required fields
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"Missing field: {field}")

    # Stop further checks if required fields are missing
    if errors:
        return errors

    # 3. Check important text fields
    for field in ["experiment_id", "experiment_name",
                  "matched_passage", "source_title",
                  "evidence_level"]:

        value = record[field]

        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must contain non-empty text.")

    # 4. Check for placeholder content
    passage = record["matched_passage"]

    if isinstance(passage, str):
        passage_lower = passage.lower()

        for phrase in PLACEHOLDER_PHRASES:
            if phrase in passage_lower:
                errors.append("Placeholder research text detected.")
                break

    
    
# 5. Check source URL
    source_url = record["source_url"]

    if not isinstance(source_url, str):
        errors.append("Source URL must be text.")

    else:
        parsed_url = urlparse(source_url)
        
        hostname = (
        parsed_url.hostname.lower()
        if parsed_url.hostname
        else ""
        )
        
        if (
            parsed_url.scheme != "https"
            or not (
                hostname == "nasa.gov"
                or hostname.endswith(".nasa.gov")
            )
        ):
        
            errors.append("Source must use a valid HTTPS NASA URL.")
    return errors



def validate_evidence(records):
    """
    Validates multiple research records.

    Returns:
        valid_records: Records that passed validation.
        rejected_records: Records with their validation errors.
    """

    valid_records = []
    rejected_records = []

    # Check input type
    if not isinstance(records, list):
        return [], [{
            "record": records,
            "errors": ["Evidence must be provided as a list."]
        }]

    # Validate each record individually
    for record in records:

        errors = validate_record(record)

        if not errors:
            valid_records.append(record)

        else:
            rejected_records.append({
                "record": record,
                "errors": errors
            })

    return valid_records, rejected_records
