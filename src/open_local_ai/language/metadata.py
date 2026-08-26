"""Canonical language metadata for Open Local AI."""

from dataclasses import dataclass

from open_local_ai.core.exceptions import InvalidInputError, UnknownLanguageError


@dataclass(frozen=True, slots=True)
class Language:
    """Immutable metadata for a canonical language."""

    code: str
    name: str
    native_name: str

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.code, "code"),
            (self.name, "name"),
            (self.native_name, "native_name"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise InvalidInputError(f"{field_name} must be a non-empty string.")


_LANGUAGES: dict[str, Language] = {
    "am": Language(code="am", name="Amharic", native_name="አማርኛ"),
    "om": Language(code="om", name="Afaan Oromo", native_name="Afaan Oromoo"),
    "ti": Language(code="ti", name="Tigrinya", native_name="ትግርኛ"),
    "en": Language(code="en", name="English", native_name="English"),
}


def get_language(code: object) -> Language:
    """Return the canonical language for an exact code."""
    if not isinstance(code, str) or code not in _LANGUAGES:
        raise UnknownLanguageError(code)
    return _LANGUAGES[code]


def supported_languages() -> tuple[Language, ...]:
    """Return all canonical languages in deterministic order."""
    return tuple(_LANGUAGES.values())
