"""Tests for the NLLB provider using fake local runtimes."""

from pathlib import Path

import pytest

from open_local_ai import TranslationService
from open_local_ai.core.exceptions import (
    InvalidInputError,
    ModelNotInstalledError,
    ProviderUnavailableError,
    TranslationError,
    UnsupportedLanguagePairError,
)
from open_local_ai.core.models import TranslationRequest
from open_local_ai.translation.providers import nllb
from open_local_ai.translation.providers.nllb import NllbTranslationProvider


class _FakeResult:
    def __init__(self, hypotheses: list[list[str]]) -> None:
        self.hypotheses = hypotheses


class _FakeTranslator:
    def __init__(self, *, fail: bool) -> None:
        self.fail = fail
        self.calls: list[tuple[list[list[str]], list[list[str]], int]] = []

    def translate_batch(
        self,
        source: list[list[str]],
        *,
        target_prefix: list[list[str]],
        beam_size: int,
    ) -> list[_FakeResult]:
        if self.fail:
            raise RuntimeError("engine exploded")
        self.calls.append((source, target_prefix, beam_size))
        return [
            _FakeResult([[target_prefix[i][0], f"translated:{source[i][1]}"]])
            for i in range(len(source))
        ]


class _FakeCT2Module:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.translators: list[_FakeTranslator] = []

    def Translator(self, model_path: str, *, device: str) -> _FakeTranslator:
        translator = _FakeTranslator(fail=self.fail)
        self.translators.append(translator)
        return translator


class _FakeProcessor:
    def encode_as_pieces(self, text: str) -> list[str]:
        return text.split()

    def decode_pieces(self, pieces: list[str]) -> str:
        return " ".join(pieces)


class _FakeSpmModule:
    def SentencePieceProcessor(self, *, model_file: str) -> _FakeProcessor:
        return _FakeProcessor()


@pytest.fixture
def ct2(monkeypatch: pytest.MonkeyPatch) -> _FakeCT2Module:
    module = _FakeCT2Module()
    monkeypatch.setattr(nllb, "_load_ctranslate2", lambda: module)
    monkeypatch.setattr(nllb, "_load_sentencepiece", lambda: _FakeSpmModule())
    return module


@pytest.fixture
def provider(tmp_path: Path) -> NllbTranslationProvider:
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    tokenizer = tmp_path / "sentencepiece.bpe.model"
    tokenizer.write_bytes(b"fake")
    return NllbTranslationProvider(model_dir, tokenizer)


def test_provider_is_local_and_offline(provider: NllbTranslationProvider) -> None:
    assert provider.is_local is True
    assert provider.requires_network is False


def test_is_available_reflects_runtime(
    monkeypatch: pytest.MonkeyPatch, provider: NllbTranslationProvider
) -> None:
    monkeypatch.setattr(nllb, "_load_ctranslate2", lambda: None)
    monkeypatch.setattr(nllb, "_load_sentencepiece", lambda: None)
    assert provider.is_available() is False


def test_is_available_when_runtime_present(
    ct2: _FakeCT2Module, provider: NllbTranslationProvider
) -> None:
    assert provider.is_available() is True


@pytest.mark.parametrize("code", ["am", "om", "ti", "en"])
def test_supports_project_languages(
    provider: NllbTranslationProvider, code: str
) -> None:
    assert provider.supports_language(code) is True


def test_rejects_unknown_language(provider: NllbTranslationProvider) -> None:
    assert provider.supports_language("fr") is False


def test_supports_pairs_but_not_identity(provider: NllbTranslationProvider) -> None:
    assert provider.supports_pair("am", "en") is True
    assert provider.supports_pair("om", "ti") is True
    assert provider.supports_pair("en", "en") is False
    assert provider.supports_pair("fr", "en") is False


def test_translate_builds_nllb_tokens(
    ct2: _FakeCT2Module, provider: NllbTranslationProvider
) -> None:
    result = provider.translate(
        TranslationRequest(text="Hello there", source="en", target="am")
    )

    assert (result.text, result.source, result.target) == (
        "translated:Hello",
        "en",
        "am",
    )
    source, target_prefix, beam_size = ct2.translators[0].calls[0]
    assert source == [["eng_Latn", "Hello", "there", "</s>"]]
    assert target_prefix == [["amh_Ethi"]]
    assert beam_size == 4


def test_translate_preserves_blank_lines(
    ct2: _FakeCT2Module, provider: NllbTranslationProvider
) -> None:
    result = provider.translate(
        TranslationRequest(text="Hello\n\nWorld", source="en", target="om")
    )

    assert result.text == "translated:Hello\n\ntranslated:World"
    assert len(ct2.translators[0].calls[0][0]) == 2


def test_engine_is_loaded_once(
    ct2: _FakeCT2Module, provider: NllbTranslationProvider
) -> None:
    request = TranslationRequest(text="Hello", source="en", target="ti")
    provider.translate(request)
    provider.translate(request)

    assert len(ct2.translators) == 1


def test_missing_runtime_raises_unavailable(
    monkeypatch: pytest.MonkeyPatch, provider: NllbTranslationProvider
) -> None:
    monkeypatch.setattr(nllb, "_load_ctranslate2", lambda: None)
    monkeypatch.setattr(nllb, "_load_sentencepiece", lambda: None)

    with pytest.raises(ProviderUnavailableError):
        provider.translate(TranslationRequest(text="Hi", source="en", target="am"))


def test_missing_model_directory_raises(ct2: _FakeCT2Module, tmp_path: Path) -> None:
    tokenizer = tmp_path / "tokenizer.model"
    tokenizer.write_bytes(b"fake")
    provider = NllbTranslationProvider(tmp_path / "missing", tokenizer)

    with pytest.raises(ModelNotInstalledError):
        provider.translate(TranslationRequest(text="Hi", source="en", target="am"))


def test_missing_tokenizer_raises(ct2: _FakeCT2Module, tmp_path: Path) -> None:
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    provider = NllbTranslationProvider(model_dir, tmp_path / "missing.model")

    with pytest.raises(ModelNotInstalledError):
        provider.translate(TranslationRequest(text="Hi", source="en", target="am"))


def test_unsupported_pair_raises(
    ct2: _FakeCT2Module, provider: NllbTranslationProvider
) -> None:
    with pytest.raises(UnsupportedLanguagePairError):
        provider.translate(TranslationRequest(text="Hi", source="en", target="en"))


def test_engine_failure_is_wrapped(
    monkeypatch: pytest.MonkeyPatch, provider: NllbTranslationProvider
) -> None:
    failing = _FakeCT2Module(fail=True)
    monkeypatch.setattr(nllb, "_load_ctranslate2", lambda: failing)
    monkeypatch.setattr(nllb, "_load_sentencepiece", lambda: _FakeSpmModule())

    with pytest.raises(TranslationError):
        provider.translate(TranslationRequest(text="Hi", source="en", target="am"))


def test_invalid_beam_size_rejected(tmp_path: Path) -> None:
    with pytest.raises(InvalidInputError):
        NllbTranslationProvider(tmp_path, tmp_path / "t.model", beam_size=0)


def test_works_through_translation_service(
    ct2: _FakeCT2Module, provider: NllbTranslationProvider
) -> None:
    service = TranslationService(provider)

    result = service.translate("Hello", "en", "ti")

    assert result.text == "translated:Hello"
    assert (result.source, result.target) == ("en", "ti")
