"""Exceptions raised by the Open Local AI core domain."""


class OpenLocalAIError(Exception):
    """Base class for expected Open Local AI errors."""


class InvalidInputError(OpenLocalAIError):
    """Raised when a translation request or result has invalid values."""


class UnknownLanguageError(OpenLocalAIError):
    """Raised when a code is not a canonical Open Local AI language."""

    def __init__(self, code: object) -> None:
        self.code = code
        super().__init__(f"Unknown language code: {code!r}")


class UnsupportedLanguageError(OpenLocalAIError):
    """Raised when a provider does not support an individual language."""

    def __init__(self, language: str) -> None:
        self.language = language
        super().__init__(f"The provider does not support language {language!r}.")


class UnsupportedLanguagePairError(OpenLocalAIError):
    """Raised when a provider does not support a translation direction."""

    def __init__(self, source: str, target: str) -> None:
        self.source = source
        self.target = target
        super().__init__(
            f"The provider does not support translation from {source!r} to {target!r}."
        )


class ProviderUnavailableError(OpenLocalAIError):
    """Raised when a provider cannot run in the current environment."""


class ModelNotInstalledError(OpenLocalAIError):
    """Raised when a required translation model is not installed."""


class TranslationError(OpenLocalAIError):
    """Raised when a provider fails during translation."""
