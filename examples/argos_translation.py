"""Translate text with an already-installed local Argos model.

Install the optional dependency and a compatible .argosmodel package before
running this example. Open Local AI does not download or install models.
"""

from open_local_ai import (
    ModelNotInstalledError,
    ProviderUnavailableError,
    TranslationError,
    TranslationRequest,
    UnsupportedLanguageError,
    UnsupportedLanguagePairError,
)
from open_local_ai.translation.providers.argos import ArgosTranslationProvider


def main() -> None:
    provider = ArgosTranslationProvider()
    if not provider.is_available():
        raise ProviderUnavailableError(
            "Argos is unavailable. Install the 'argos' extra first."
        )

    request = TranslationRequest(
        text="Hello, how are you?",
        source="en",
        target="es",
    )
    if not provider.supports_pair(request.source, request.target):
        raise UnsupportedLanguagePairError(request.source, request.target)

    try:
        result = provider.translate(request)
    except (ModelNotInstalledError, UnsupportedLanguageError, TranslationError) as exc:
        raise SystemExit(str(exc)) from exc

    print(result.text)


if __name__ == "__main__":
    main()
