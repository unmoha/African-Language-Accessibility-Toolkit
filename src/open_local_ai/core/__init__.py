"""Core domain types for Open Local AI."""

from open_local_ai.core.exceptions import (
    InvalidInputError,
    ModelNotInstalledError,
    OpenLocalAIError,
    ProviderUnavailableError,
    TranslationError,
    UnsupportedLanguageError,
    UnsupportedLanguagePairError,
)
from open_local_ai.core.interfaces import TranslationProvider
from open_local_ai.core.models import TranslationRequest, TranslationResult
from open_local_ai.core.service import TranslationService

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
    "UnsupportedLanguageError",
    "UnsupportedLanguagePairError",
]
