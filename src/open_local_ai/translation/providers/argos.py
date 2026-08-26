"""Argos Translate provider adapter."""

from importlib import import_module
from typing import Protocol, cast

from open_local_ai.core.exceptions import (
    ModelNotInstalledError,
    ProviderUnavailableError,
    TranslationError,
    UnsupportedLanguageError,
    UnsupportedLanguagePairError,
)
from open_local_ai.core.interfaces import TranslationProvider
from open_local_ai.core.models import TranslationRequest, TranslationResult


class _ArgosTranslation(Protocol):
    def translate(self, input_text: str) -> str: ...


class _ArgosLanguage(Protocol):
    code: str

    def get_translation(self, to: "_ArgosLanguage") -> _ArgosTranslation | None: ...


class _ArgosTranslateModule(Protocol):
    def get_installed_languages(self) -> list[_ArgosLanguage]: ...


def _load_argos_translate() -> _ArgosTranslateModule | None:
    try:
        module = import_module("argostranslate.translate")
    except ImportError:
        return None
    return cast(_ArgosTranslateModule, module)


class ArgosTranslationProvider(TranslationProvider):
    """Use directly installed Argos translation packages without networking."""

    @property
    def is_local(self) -> bool:
        return True

    @property
    def requires_network(self) -> bool:
        return False

    def is_available(self) -> bool:
        return _load_argos_translate() is not None

    def supports_language(self, language: str) -> bool:
        languages = self._installed_languages()
        return languages is not None and any(
            installed.code == language for installed in languages
        )

    def supports_pair(self, source: str, target: str) -> bool:
        languages = self._installed_languages()
        if languages is None:
            return False
        source_language = self._language_by_code(languages, source)
        target_language = self._language_by_code(languages, target)
        if source_language is None or target_language is None:
            return False
        return source_language.get_translation(target_language) is not None

    def translate(self, request: TranslationRequest) -> TranslationResult:
        module = _load_argos_translate()
        if module is None:
            raise ProviderUnavailableError(
                "Argos Translate is not installed. Install the 'argos' extra."
            )

        try:
            languages = module.get_installed_languages()
            source_language = self._language_by_code(languages, request.source)
            target_language = self._language_by_code(languages, request.target)
            if source_language is None:
                raise UnsupportedLanguageError(request.source)
            if target_language is None:
                raise UnsupportedLanguageError(request.target)
            translation = source_language.get_translation(target_language)
            if translation is None:
                raise UnsupportedLanguagePairError(request.source, request.target)
            translated_text = translation.translate(request.text)
        except (
            UnsupportedLanguageError,
            UnsupportedLanguagePairError,
            ModelNotInstalledError,
            ProviderUnavailableError,
            TranslationError,
        ):
            raise
        except Exception as exc:
            raise TranslationError(
                "Argos Translate failed to translate the request."
            ) from exc

        return TranslationResult(
            text=translated_text,
            source=request.source,
            target=request.target,
        )

    @staticmethod
    def _language_by_code(
        languages: list[_ArgosLanguage], code: str
    ) -> _ArgosLanguage | None:
        return next((language for language in languages if language.code == code), None)

    @staticmethod
    def _installed_languages() -> list[_ArgosLanguage] | None:
        module = _load_argos_translate()
        if module is None:
            return None
        return module.get_installed_languages()
