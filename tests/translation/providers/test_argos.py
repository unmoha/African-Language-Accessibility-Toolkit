from dataclasses import dataclass, field
from types import ModuleType

import pytest

from open_local_ai import (
    ModelNotInstalledError,
    ProviderUnavailableError,
    TranslationError,
    TranslationRequest,
    UnsupportedLanguageError,
    UnsupportedLanguagePairError,
)
from open_local_ai.translation.providers import argos
from open_local_ai.translation.providers.argos import ArgosTranslationProvider


@dataclass
class FakeTranslation:
    prefix: str = "translated:"
    error: Exception | None = None

    def translate(self, input_text: str) -> str:
        if self.error is not None:
            raise self.error
        return f"{self.prefix}{input_text}"


@dataclass
class FakeLanguage:
    code: str
    translations: dict[str, FakeTranslation] = field(default_factory=dict)

    def get_translation(self, to: "FakeLanguage") -> FakeTranslation | None:
        return self.translations.get(to.code)


@dataclass
class FakeArgosTranslate:
    languages: list[FakeLanguage]

    def get_installed_languages(self) -> list[FakeLanguage]:
        return self.languages


class FakeTranslateModule(ModuleType):
    def __init__(self, languages: list[FakeLanguage]) -> None:
        super().__init__("argostranslate.translate")
        self._argos = FakeArgosTranslate(languages)

    def get_installed_languages(self) -> list[FakeLanguage]:
        return self._argos.get_installed_languages()


def install_fake_argos(
    monkeypatch: pytest.MonkeyPatch,
    languages: list[FakeLanguage],
) -> None:
    fake_module = FakeTranslateModule(languages)
    monkeypatch.setattr(argos, "import_module", lambda _: fake_module)


def make_pair() -> tuple[FakeLanguage, FakeLanguage]:
    source = FakeLanguage("xx")
    target = FakeLanguage("yy")
    source.translations[target.code] = FakeTranslation()
    return source, target


def test_provider_reports_local_offline_behavior() -> None:
    provider = ArgosTranslationProvider()

    assert provider.is_local is True
    assert provider.requires_network is False


def test_provider_is_unavailable_when_argos_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing(_: str) -> ModuleType:
        raise ImportError("Argos is not installed")

    monkeypatch.setattr(argos, "import_module", missing)
    provider = ArgosTranslationProvider()

    assert provider.is_available() is False
    assert provider.supports_language("en") is False
    assert provider.supports_pair("en", "xx") is False
    with pytest.raises(ProviderUnavailableError):
        provider.translate(TranslationRequest("Hello", "en", "xx"))


def test_installed_language_and_direct_pair_are_supported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, target = make_pair()
    install_fake_argos(monkeypatch, [source, target])
    provider = ArgosTranslationProvider()

    assert provider.is_available() is True
    assert provider.supports_language("xx") is True
    assert provider.supports_language("zz") is False
    assert provider.supports_pair("xx", "yy") is True


def test_canonical_metadata_alone_does_not_imply_provider_support(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_fake_argos(monkeypatch, [])
    provider = ArgosTranslationProvider()

    assert provider.supports_language("am") is False
    assert provider.supports_pair("am", "en") is False


def test_both_languages_without_direct_pair_are_unsupported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = FakeLanguage("xx")
    target = FakeLanguage("yy")
    install_fake_argos(monkeypatch, [source, target])

    assert ArgosTranslationProvider().supports_pair("xx", "yy") is False


def test_translation_returns_request_languages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, target = make_pair()
    install_fake_argos(monkeypatch, [source, target])

    result = ArgosTranslationProvider().translate(
        TranslationRequest("Hello", "xx", "yy")
    )

    assert result.text == "translated:Hello"
    assert result.source == "xx"
    assert result.target == "yy"


@pytest.mark.parametrize(
    ("translation_request", "expected"),
    [
        (TranslationRequest("Hello", "missing", "yy"), UnsupportedLanguageError),
        (TranslationRequest("Hello", "xx", "missing"), UnsupportedLanguageError),
        (
            TranslationRequest("Hello", "xx", "yy"),
            UnsupportedLanguagePairError,
        ),
    ],
)
def test_translation_rejects_unavailable_capabilities(
    monkeypatch: pytest.MonkeyPatch,
    translation_request: TranslationRequest,
    expected: type[Exception],
) -> None:
    source = FakeLanguage("xx")
    target = FakeLanguage("yy")
    install_fake_argos(monkeypatch, [source, target])

    with pytest.raises(expected):
        ArgosTranslationProvider().translate(translation_request)


def test_translation_maps_missing_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, target = make_pair()
    source.translations[target.code] = FakeTranslation(
        error=ModelNotInstalledError("model missing")
    )
    install_fake_argos(monkeypatch, [source, target])

    with pytest.raises(ModelNotInstalledError):
        ArgosTranslationProvider().translate(TranslationRequest("Hello", "xx", "yy"))


def test_translation_wraps_unexpected_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, target = make_pair()
    source.translations[target.code] = FakeTranslation(error=RuntimeError("failure"))
    install_fake_argos(monkeypatch, [source, target])

    with pytest.raises(TranslationError) as error:
        ArgosTranslationProvider().translate(TranslationRequest("Hello", "xx", "yy"))

    assert isinstance(error.value.__cause__, RuntimeError)


def test_capability_checks_do_not_update_or_download(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, target = make_pair()
    install_fake_argos(monkeypatch, [source, target])
    provider = ArgosTranslationProvider()

    assert provider.supports_language("xx") is True
    assert provider.supports_pair("xx", "yy") is True
