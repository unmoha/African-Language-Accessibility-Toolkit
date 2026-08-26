import pytest

from open_local_ai import InvalidInputError, TranslationRequest, TranslationResult


def test_request_preserves_values() -> None:
    request = TranslationRequest(text="Hello", source="en", target="am")

    assert request.text == "Hello"
    assert request.source == "en"
    assert request.target == "am"


@pytest.mark.parametrize("text", ["", "   ", "\t\n"])
def test_request_rejects_empty_text(text: str) -> None:
    with pytest.raises(InvalidInputError):
        TranslationRequest(text=text, source="en", target="am")


@pytest.mark.parametrize(
    ("field", "value"),
    [("text", 1), ("source", ""), ("target", " ")],
)
def test_request_rejects_invalid_values(field: str, value: object) -> None:
    values: dict[str, object] = {"text": "Hello", "source": "en", "target": "am"}
    values[field] = value

    with pytest.raises(InvalidInputError):
        TranslationRequest(**values)  # type: ignore[arg-type]


def test_identical_languages_are_allowed() -> None:
    request = TranslationRequest(text="Hello", source="en", target="en")

    assert request.source == request.target


def test_result_is_immutable() -> None:
    result = TranslationResult(text="ሰላም", source="am", target="en")

    with pytest.raises(AttributeError):
        result.text = "changed"  # type: ignore[misc]
