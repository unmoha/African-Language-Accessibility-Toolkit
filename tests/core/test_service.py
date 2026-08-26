import pytest

from open_local_ai import (
    ModelNotInstalledError,
    OpenLocalAIError,
    ProviderUnavailableError,
    TranslationError,
    TranslationRequest,
    TranslationResult,
    TranslationService,
    UnsupportedLanguageError,
    UnsupportedLanguagePairError,
)


class FakeProvider:
    is_local = True
    requires_network = False

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.available = True
        self.languages = {"en", "am"}
        self.pairs = {("en", "am")}
        self.failure: Exception | None = None

    def is_available(self) -> bool:
        self.calls.append("available")
        return self.available

    def supports_language(self, language: str) -> bool:
        self.calls.append(f"language:{language}")
        return language in self.languages

    def supports_pair(self, source: str, target: str) -> bool:
        self.calls.append(f"pair:{source}:{target}")
        return (source, target) in self.pairs

    def translate(self, request: TranslationRequest) -> TranslationResult:
        self.calls.append("translate")
        if self.failure is not None:
            raise self.failure
        return TranslationResult("translated", request.source, request.target)


class ProviderSpecificError(OpenLocalAIError):
    """Provider-owned error that is not part of the public exception contract."""


def test_service_delegates_in_the_defined_order() -> None:
    provider = FakeProvider()

    result = TranslationService(provider).translate("Hello", "en", "am")

    assert result == TranslationResult("translated", "en", "am")
    assert provider.calls == [
        "available",
        "language:en",
        "language:am",
        "pair:en:am",
        "translate",
    ]


def test_service_rejects_unavailable_provider() -> None:
    provider = FakeProvider()
    provider.available = False

    with pytest.raises(ProviderUnavailableError):
        TranslationService(provider).translate("Hello", "en", "am")


def test_service_rejects_unsupported_language() -> None:
    provider = FakeProvider()

    with pytest.raises(UnsupportedLanguageError):
        TranslationService(provider).translate("Hello", "xx", "am")


def test_service_rejects_unsupported_pair() -> None:
    provider = FakeProvider()
    provider.languages.add("om")

    with pytest.raises(UnsupportedLanguagePairError):
        TranslationService(provider).translate("Hello", "en", "om")


def test_service_preserves_expected_provider_errors() -> None:
    provider = FakeProvider()
    provider.failure = ModelNotInstalledError("Install the required model first.")

    with pytest.raises(ModelNotInstalledError):
        TranslationService(provider).translate("Hello", "en", "am")


def test_service_wraps_unexpected_provider_errors() -> None:
    provider = FakeProvider()
    provider.failure = RuntimeError("provider detail")

    with pytest.raises(TranslationError) as error:
        TranslationService(provider).translate("Hello", "en", "am")

    assert isinstance(error.value.__cause__, RuntimeError)


def test_service_wraps_provider_specific_project_errors() -> None:
    provider = FakeProvider()
    provider.failure = ProviderSpecificError("provider detail")

    with pytest.raises(TranslationError) as error:
        TranslationService(provider).translate("Hello", "en", "am")

    assert isinstance(error.value.__cause__, ProviderSpecificError)


def test_service_rejects_result_for_different_language_pair() -> None:
    provider = FakeProvider()

    def mismatched_translation(
        request: TranslationRequest,
    ) -> TranslationResult:
        return TranslationResult("translated", request.source, "om")

    provider.translate = mismatched_translation  # type: ignore[method-assign]

    with pytest.raises(TranslationError):
        TranslationService(provider).translate("Hello", "en", "am")
