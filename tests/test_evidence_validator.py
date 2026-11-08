
from modules.evidence_validator import (
    validate_record,
    validate_evidence
)


# A valid example record for testing
# This is synthetic test data, NOT a NASA finding.
valid_record = {
    "experiment_id": "TEST-001",
    "experiment_name": "Synthetic Test Experiment",
    "matched_passage": "Synthetic research passage for testing validation.",
    "source_url": "https://ntrs.nasa.gov/test",
    "source_title": "Synthetic Test Source",
    "evidence_level": "Test"
}


def test_valid_record():
    errors = validate_record(valid_record)

    assert errors == []


def test_missing_passage():
    record = valid_record.copy()
    del record["matched_passage"]

    errors = validate_record(record)

    assert len(errors) > 0


def test_invalid_url():
    record = valid_record.copy()
    record["source_url"] = "http://example.com"

    errors = validate_record(record)

    assert len(errors) > 0


def test_placeholder_passage():
    record = valid_record.copy()
    record["matched_passage"] = "This is temporary test data."

    errors = validate_record(record)

    assert len(errors) > 0


def test_empty_evidence_list():
    valid, rejected = validate_evidence([])

    assert valid == []
    assert rejected == []


def test_multiple_records():
    invalid_record = valid_record.copy()
    invalid_record["source_url"] = "https://example.com"

    valid, rejected = validate_evidence([
        valid_record,
        invalid_record
    ])

    assert len(valid) == 1
    assert len(rejected) == 1


if __name__ == "__main__":
    test_valid_record()
    test_missing_passage()
    test_invalid_url()
    test_placeholder_passage()
    test_empty_evidence_list()
    test_multiple_records()

    print("All evidence validator tests passed!")
