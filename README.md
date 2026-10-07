# Open Local AI

**Offline-first translation and accessibility tools for Ethiopian languages, built around local AI providers.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-early%20stage-orange)
![Offline first](https://img.shields.io/badge/offline-first-success)

Open Local AI gives developers one stable translation interface while keeping the engines and models behind it replaceable. Text is processed locally, with no telemetry and no automatic model downloads.

## Why Open Local AI?

- **Provider-independent:** swap translation engines without changing application code.
- **Offline-first:** local providers process text without sending it to a remote service.
- **Honest by design:** unsupported requests raise clear errors, never fabricated translations.
- **Ethiopian languages:** Amharic, Afaan Oromo, and Tigrinya are built into the language metadata.

## Status

| Component | State |
|---|---|
| Core models, errors, language metadata | ✅ Done |
| Provider interface and contract tests | ✅ Done |
| Argos Translate provider | ✅ Done |
| Translation service | ✅ Done |
| CLI | 🚧 Planned |
| Speech-to-text, text-to-speech, OCR | 🚧 Planned |

> Argos currently isn't verified for Amharic, Afaan Oromo, or Tigrinya in the tested environment. Support depends on locally installed models.

## Quick start

```bash
git clone https://github.com/unmoha/African-Language-Accessibility-Toolkit.git
cd African-Language-Accessibility-Toolkit
pip install -e ".[argos]"
```

Install a model once (this step needs internet; translation afterwards is local):

```python
import argostranslate.package
argostranslate.package.install_from_path("/path/to/your-model.argosmodel")
```

Translate:

```python
from open_local_ai import TranslationService
from open_local_ai.translation.providers.argos import ArgosTranslationProvider

service = TranslationService(ArgosTranslationProvider())
result = service.translate("Hello, how are you?", "en", "es")
print(result.text)  # Hola, ¿cómo estás?
```

Check support before translating:

```python
provider = ArgosTranslationProvider()
provider.is_available()
provider.supports_language("en")
provider.supports_pair("en", "es")
```

## Languages

| Language | Code | Canonical metadata | Argos verified |
|---|---|---|---|
| Amharic | `am` | ✅ | ❌ |
| Afaan Oromo | `om` | ✅ | ❌ |
| Tigrinya | `ti` | ✅ | ❌ |
| English | `en` | ✅ | ✅ |

Canonical recognition does not imply provider support.

## Architecture

```
Application → TranslationService → TranslationProvider → Provider adapter → Local model
```

The core package works without any provider installed.

## Errors

`ProviderUnavailableError` · `UnsupportedLanguageError` · `UnsupportedLanguagePairError` · `ModelNotInstalledError` · `TranslationError`

## Privacy

No text, audio, or telemetry is collected. Models are never downloaded automatically.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md). Quality checks: `pytest` → `ruff check` → `ruff format --check` → `mypy`

## Roadmap

- [x] Core models, language metadata, provider contract
- [x] Argos provider and translation service
- [ ] CLI
- [ ] Verified Ethiopian-language models
- [ ] Speech and OCR

## Contact

Anwar · [an8702299@gmail.com](mailto:an8702299@gmail.com)
