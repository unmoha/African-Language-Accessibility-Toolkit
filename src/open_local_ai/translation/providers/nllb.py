"""NLLB-200 translation provider adapter using the CTranslate2 runtime."""

from importlib import import_module
from pathlib import Path
from typing import Protocol, cast

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

_NLLB_CODES: dict[str, str] = {
    "am": "amh_Ethi",
    "om": "orm_Latn",
    "ti": "tir_Ethi",
    "en": "eng_Latn",
}


class _CT2Result(Protocol):
    hypotheses: list[list[str]]


class _CT2Translator(Protocol):
    def translate_batch(
        self,
        source: list[list[str]],
        *,
        target_prefix: list[list[str]],
        beam_size: int,
    ) -> list[_CT2Result]: ...


class _CT2Module(Protocol):
    def Translator(self, model_path: str, *, device: str) -> _CT2Translator: ...


class _SpmProcessor(Protocol):
    def encode_as_pieces(self, text: str) -> list[str]: ...

    def decode_pieces(self, pieces: list[str]) -> str: ...


class _SpmModule(Protocol):
    def SentencePieceProcessor(self, *, model_file: str) -> _SpmProcessor: ...


def _load_ctranslate2() -> _CT2Module | None:
    try:
        module = import_module("ctranslate2")
    except ImportError:
        return None
    return cast(_CT2Module, module)


def _load_sentencepiece() -> _SpmModule | None:
    try:
        module = import_module("sentencepiece")
    except ImportError:
        return None
    return cast(_SpmModule, module)


class NllbTranslationProvider(TranslationProvider):
    """Translate with a locally converted NLLB-200 model; never downloads anything."""

    def __init__(
        self,
        model_dir: str | Path,
        tokenizer_path: str | Path,
        *,
        device: str = "cpu",
        beam_size: int = 4,
    ) -> None:
        if beam_size < 1:
            raise InvalidInputError("beam_size must be at least 1.")
        self._model_dir = Path(model_dir)
        self._tokenizer_path = Path(tokenizer_path)
        self._device = device
        self._beam_size = beam_size
        self._engine: tuple[_CT2Translator, _SpmProcessor] | None = None

    @property
    def is_local(self) -> bool:
        return True

    @property
    def requires_network(self) -> bool:
        return False

    def is_available(self) -> bool:
        return _load_ctranslate2() is not None and _load_sentencepiece() is not None

    def supports_language(self, language: str) -> bool:
        return language in _NLLB_CODES

    def supports_pair(self, source: str, target: str) -> bool:
        return source in _NLLB_CODES and target in _NLLB_CODES and source != target

    def translate(self, request: TranslationRequest) -> TranslationResult:
        ct2 = _load_ctranslate2()
        spm = _load_sentencepiece()
        if ct2 is None or spm is None:
            raise ProviderUnavailableError(
                "CTranslate2 or SentencePiece is not installed. "
                "Install the 'nllb' extra."
            )
        if not self.supports_language(request.source):
            raise UnsupportedLanguageError(request.source)
        if not self.supports_language(request.target):
            raise UnsupportedLanguageError(request.target)
        if not self.supports_pair(request.source, request.target):
            raise UnsupportedLanguagePairError(request.source, request.target)
        if not self._model_dir.is_dir():
            raise ModelNotInstalledError(
                f"NLLB model directory not found: {self._model_dir}"
            )
        if not self._tokenizer_path.is_file():
            raise ModelNotInstalledError(
                f"NLLB tokenizer file not found: {self._tokenizer_path}"
            )

        source_code = _NLLB_CODES[request.source]
        target_code = _NLLB_CODES[request.target]

        try:
            translator, processor = self._load_engine(ct2, spm)
            lines = request.text.split("\n")
            indexes = [i for i, line in enumerate(lines) if line.strip()]
            batch = [
                [source_code, *processor.encode_as_pieces(lines[i]), "</s>"]
                for i in indexes
            ]
            results = translator.translate_batch(
                batch,
                target_prefix=[[target_code] for _ in batch],
                beam_size=self._beam_size,
            )
            for index, result in zip(indexes, results, strict=True):
                pieces = result.hypotheses[0]
                if pieces and pieces[0] == target_code:
                    pieces = pieces[1:]
                lines[index] = processor.decode_pieces(pieces)
            translated_text = "\n".join(lines)
            if not translated_text.strip():
                raise TranslationError("The NLLB model returned an empty translation.")
        except (
            UnsupportedLanguageError,
            UnsupportedLanguagePairError,
            ModelNotInstalledError,
            ProviderUnavailableError,
            TranslationError,
        ):
            raise
        except Exception as exc:
            raise TranslationError("NLLB failed to translate the request.") from exc

        return TranslationResult(
            text=translated_text,
            source=request.source,
            target=request.target,
        )

    def _load_engine(
        self, ct2: _CT2Module, spm: _SpmModule
    ) -> tuple[_CT2Translator, _SpmProcessor]:
        if self._engine is None:
            translator = ct2.Translator(str(self._model_dir), device=self._device)
            processor = spm.SentencePieceProcessor(model_file=str(self._tokenizer_path))
            self._engine = (translator, processor)
        return self._engine
