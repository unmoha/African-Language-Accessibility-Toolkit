"""Public API for Open Local AI."""

from open_local_ai.core import (
    InvalidInputError,
    ModelNotInstalledError,
    OpenLocalAIError,
    ProviderUnavailableError,
    TranslationError,
    TranslationProvider,
    TranslationRequest,
    TranslationResult,
    TranslationService,
    UnsupportedLanguageError,
    UnsupportedLanguagePairError,
)
from open_local_ai.core.exceptions import UnknownLanguageError

__version__ = "0.1.0.dev0"

__all__ = [
    "InvalidInputError",
    "ModelNotInstalledError",
    "OpenLocalAIError",
    "ProviderUnavailableError",
    "TranslationError",
    "TranslationProvider",
    "TranslationRequest",
    "TranslationResult",
    "TranslationService",
    "UnknownLanguageError",
    "UnsupportedLanguageError",
    "UnsupportedLanguagePairError",
    "__version__",
]
