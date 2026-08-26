"""Immutable data models for translation requests and results."""

from dataclasses import dataclass

from open_local_ai.core.exceptions import InvalidInputError


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidInputError(f"{field_name} must be a non-empty string.")
    return value


@dataclass(frozen=True, slots=True)
class TranslationRequest:
    """A validated request for translating text between language identifiers."""

    text: str
    source: str
    target: str

    def __post_init__(self) -> None:
        _require_text(self.text, "text")
        _require_text(self.source, "source")
        _require_text(self.target, "target")


@dataclass(frozen=True, slots=True)
class TranslationResult:
    """Translated text and the language identifiers used for the request."""

    text: str
    source: str
    target: str

    def __post_init__(self) -> None:
        _require_text(self.text, "translated text")
        _require_text(self.source, "source")
        _require_text(self.target, "target")
