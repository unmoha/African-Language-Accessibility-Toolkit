from dataclasses import dataclass

from open_local_ai import TranslationProvider, TranslationRequest, TranslationResult


@dataclass
class FakeTranslationProvider:
    available: bool = True

    is_local = True
    requires_network = False

    def is_available(self) -> bool:
        return self.available

    def supports_language(self, language: str) -> bool:
        return language in {"en", "am"}

    def supports_pair(self, source: str, target: str) -> bool:
        return (source, target) == ("en", "am")

    def translate(self, request: TranslationRequest) -> TranslationResult:
        return TranslationResult(
            text="translated",
            source=request.source,
            target=request.target,
        )


def test_fake_provider_satisfies_translation_protocol() -> None:
    provider: TranslationProvider = FakeTranslationProvider()

    assert provider.is_local is True
    assert provider.requires_network is False
    assert provider.supports_language("en") is True
