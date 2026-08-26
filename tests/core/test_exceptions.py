from open_local_ai import (
    InvalidInputError,
    ModelNotInstalledError,
    OpenLocalAIError,
    ProviderUnavailableError,
    TranslationError,
    UnsupportedLanguageError,
    UnsupportedLanguagePairError,
)


def test_expected_exceptions_are_open_local_ai_errors() -> None:
    exceptions = [
        InvalidInputError,
        ModelNotInstalledError,
        ProviderUnavailableError,
        TranslationError,
        UnsupportedLanguageError,
        UnsupportedLanguagePairError,
    ]

    assert all(issubclass(error, OpenLocalAIError) for error in exceptions)


def test_language_errors_preserve_useful_values() -> None:
    language_error = UnsupportedLanguageError("xx")
    pair_error = UnsupportedLanguagePairError("en", "xx")

    assert language_error.language == "xx"
    assert pair_error.source == "en"
    assert pair_error.target == "xx"
    assert "xx" in str(language_error)
    assert "en" in str(pair_error)
