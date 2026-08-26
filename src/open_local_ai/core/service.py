"""Provider-independent translation orchestration."""

from open_local_ai.core.exceptions import (
    InvalidInputError,
    ModelNotInstalledError,
    ProviderUnavailableError,
    TranslationError,
    UnsupportedLanguageError,
    UnsupportedLanguagePairError,
)
from open_local_ai.core.interfaces import TranslationProvider
from open_local_ai.core.models import TranslationRequest, TranslationResult


class TranslationService:
    """Coordinate validation and delegation to a translation provider."""

    def __init__(self, provider: TranslationProvider) -> None:
        self._provider = provider

    def translate(self, text: str, source: str, target: str) -> TranslationResult:
        request = TranslationRequest(text=text, source=source, target=target)

        try:
            if not self._provider.is_available():
                raise ProviderUnavailableError(
                    "The translation provider is unavailable."
                )
            if not self._provider.supports_language(request.source):
                raise UnsupportedLanguageError(request.source)
            if not self._provider.supports_language(request.target):
                raise UnsupportedLanguageError(request.target)
            if not self._provider.supports_pair(request.source, request.target):
                raise UnsupportedLanguagePairError(request.source, request.target)
            result = self._provider.translate(request)
            if (result.source, result.target) != (request.source, request.target):
                raise TranslationError(
                    "The provider returned a result for a different language pair."
                )
            return result
        except (
            InvalidInputError,
            UnsupportedLanguageError,
            UnsupportedLanguagePairError,
            ProviderUnavailableError,
            ModelNotInstalledError,
            TranslationError,
        ):
            raise
        except Exception as exc:
            raise TranslationError(
                "The provider failed to translate the request."
            ) from exc
