
from modules.response_schema import (
    create_empty_response,
    validate_response
)


def test_empty_response_structure():
    response = create_empty_response()

    assert validate_response(response) is True


def test_missing_field():
    response = create_empty_response()
    del response["sources"]

    assert validate_response(response) is False


def test_invalid_field_type():
    response = create_empty_response()
    response["key_findings"] = "This should be a list"

    assert validate_response(response) is False


def test_invalid_response():
    assert validate_response("Invalid response") is False


if __name__ == "__main__":
    test_empty_response_structure()
    test_missing_field()
    test_invalid_field_type()
    test_invalid_response()

    print("All response schema tests passed!")
