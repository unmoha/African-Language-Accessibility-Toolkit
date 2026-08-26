"""Provider contracts used by the core service."""

from typing import Protocol

from open_local_ai.core.models import TranslationRequest, TranslationResult


class TranslationProvider(Protocol):
    """Interface implemented by translation providers."""

    @property
    def is_local(self) -> bool:
        """Whether the provider is intended to execute locally."""
        ...

    @property
    def requires_network(self) -> bool:
        """Whether normal provider operation requires network access."""
        ...

    def is_available(self) -> bool:
        """Return whether the provider runtime is usable."""
        ...

    def supports_language(self, language: str) -> bool:
        """Return whether the provider recognizes an individual language."""
        ...

    def supports_pair(self, source: str, target: str) -> bool:
        """Return whether the provider supports a language direction."""
        ...

    def translate(self, request: TranslationRequest) -> TranslationResult:
        """Translate a validated request without downloading a model."""
        ...
