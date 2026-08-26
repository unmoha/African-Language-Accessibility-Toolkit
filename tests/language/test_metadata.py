import pytest

from open_local_ai import InvalidInputError, UnknownLanguageError
from open_local_ai.language import Language, get_language, supported_languages


@pytest.mark.parametrize(
    ("code", "name", "native_name"),
    [("am", "Amharic", "አማርኛ"), ("en", "English", "English")],
)
def test_language_preserves_metadata(code: str, name: str, native_name: str) -> None:
    language = Language(code, name, native_name)

    assert language.code == code
    assert language.name == name
    assert language.native_name == native_name
    assert language == Language(code, name, native_name)
    assert language.__slots__ == ("code", "name", "native_name")


def test_language_is_immutable() -> None:
    language = Language("am", "Amharic", "አማርኛ")

    with pytest.raises(AttributeError):
        language.code = "en"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("code", "name", "native_name"),
    [
        (1, "Name", "Native"),
        ("", "Name", "Native"),
        (" ", "Name", "Native"),
        ("am", 1, "Native"),
        ("am", "", "Native"),
        ("am", "Name", 1),
        ("am", "Name", " "),
    ],
)
def test_language_rejects_invalid_metadata(
    code: object, name: object, native_name: object
) -> None:
    with pytest.raises(InvalidInputError):
        Language(code, name, native_name)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("code", "name", "native_name"),
    [
        ("am", "Amharic", "አማርኛ"),
        ("om", "Afaan Oromo", "Afaan Oromoo"),
        ("ti", "Tigrinya", "ትግርኛ"),
        ("en", "English", "English"),
    ],
)
def test_canonical_languages(code: str, name: str, native_name: str) -> None:
    assert get_language(code) == Language(code, name, native_name)


@pytest.mark.parametrize("code", ["xyz", "AM", "Am", " am ", "", " ", 1])
def test_unknown_language_codes_raise(code: object) -> None:
    with pytest.raises(UnknownLanguageError) as error:
        get_language(code)

    assert error.value.code == code


def test_supported_languages_is_deterministic_and_isolated() -> None:
    languages = supported_languages()

    assert isinstance(languages, tuple)
    assert [language.code for language in languages] == ["am", "om", "ti", "en"]
    assert len(languages) == 4
    assert languages == supported_languages()

    with pytest.raises(TypeError):
        languages[0] = languages[1]  # type: ignore[index]

    with pytest.raises(AttributeError):
        languages[0].name = "Changed"  # type: ignore[misc]
