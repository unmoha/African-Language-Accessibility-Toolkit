# Open Local AI

**Offline-first translation and accessibility tools for Ethiopian languages, built around local AI providers.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-early%20stage-orange)
![Offline first](https://img.shields.io/badge/offline-first-success)

Open Local AI gives developers one stable translation interface while keeping the engines and models behind it replaceable. Text is processed locally, with no telemetry and no automatic model downloads.

## Why Open Local AI?

- **Provider-independent:** swap translation engines without changing application code.
- **Offline-first:** local providers process text without sending it to a remote service.
- **Honest by design:** unsupported requests raise clear errors, never fabricated translations.
- **Ethiopian languages:** Amharic, Afaan Oromo, and Tigrinya are built into the language metadata and supported by the NLLB provider.

## Status

| Component | State |
|---|---|
| Core models, errors, language metadata | ✅ Done |
| Provider interface and contract tests | ✅ Done |
| Argos Translate provider | ✅ Done |
| NLLB-200 provider (CTranslate2) | ✅ Implemented, unit-tested with fake runtimes |
| Translation service | ✅ Done |
| Real-model runs on sample sentences (NLLB 600M) | ✅ Done, see notes below |
| Native-speaker quality review | 🚧 Not yet done |
| CLI (`languages`, `translate`) | ✅ Done |
| Speech-to-text, text-to-speech, OCR | 🚧 Planned |

> The NLLB provider has been run against a real model (`nllb-200-distilled-600M`) on a small set of sample sentences. Amharic and Tigrinya outputs round-tripped sensibly, but one Afaan Oromo sample was mistranslated and an earlier run looped until decoding limits were added. Translation quality has not been reviewed by native speakers, so treat all output as experimental.

## Quick start

```bash
git clone https://github.com/unmoha/open-local-ai.git
cd open-local-ai
pip install -e ".[argos]"    # Argos Translate provider
pip install -e ".[nllb]"     # NLLB-200 provider (CTranslate2 + SentencePiece)
```

### Argos Translate

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

### NLLB-200 (Amharic, Afaan Oromo, Tigrinya, English)

The NLLB provider never downloads anything. You convert a model once, then point the provider at it. Do the conversion in a separate virtual environment, since it needs large dependencies and internet access:

```bash
pip install ctranslate2 transformers sentencepiece torch
ct2-transformers-converter --model facebook/nllb-200-distilled-600M --output_dir models/nllb-200-distilled-600M-ct2
```

Also place the model's `sentencepiece.bpe.model` tokenizer file (from the model's Hugging Face page) in `models/`. The `models/` folder is git-ignored.

```python
from open_local_ai import TranslationService
from open_local_ai.translation.providers.nllb import NllbTranslationProvider

provider = NllbTranslationProvider(
    "models/nllb-200-distilled-600M-ct2",
    "models/sentencepiece.bpe.model",
)
service = TranslationService(provider)
print(service.translate("Good morning, how are you?", "en", "am").text)
```

Supported directions: any pair among `am`, `om`, `ti`, and `en`, except a language to itself. A missing model or tokenizer raises `ModelNotInstalledError`.

Two decoding options guard against runaway output: `no_repeat_ngram_size` (default 3, set 0 to disable) and `max_decoding_length` (default 256, additionally capped relative to the input length). Afaan Oromo uses the NLLB code `gaz_Latn` (West Central Oromo), which does not cover every Oromo variety. Amharic and Tigrinya output defaulted to masculine singular forms in the sample run, which matters for accessibility use.

> **License notice:** NLLB-200 model weights are published by Meta under a non-commercial license (CC-BY-NC 4.0 at the time of writing). Check the current license on the model page before any commercial or redistributed use. This repository's code is MIT-licensed and does not include model weights.

## Command line

Installing the package adds an `open-local-ai` command:

```bash
open-local-ai languages
open-local-ai translate --from en --to am \
  --model-dir models/nllb-200-distilled-600M-ct2 \
  --tokenizer models/sentencepiece.bpe.model \
  "Good morning, how are you?"
```

Instead of passing model paths each time, set `OPEN_LOCAL_AI_NLLB_MODEL_DIR` and `OPEN_LOCAL_AI_NLLB_TOKENIZER`. Text can also be piped on stdin, and `--provider argos` selects the Argos provider. Exit codes: `0` success, `1` an expected translation error (printed as `error: ...`), `2` a usage mistake.

## Languages

| Language | Code | Canonical metadata | Argos verified | NLLB provider support | Quality reviewed |
|---|---|---|---|---|---|
| Amharic | `am` | ✅ | ❌ | ✅ | ❌ |
| Afaan Oromo | `om` | ✅ | ❌ | ✅ | ❌ |
| Tigrinya | `ti` | ✅ | ❌ | ✅ | ❌ |
| English | `en` | ✅ | ✅ | ✅ | ❌ |

Canonical recognition does not imply provider support, and provider support does not imply translation quality. "Quality reviewed" stays unchecked until native speakers have reviewed real output.

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
- [x] NLLB-200 provider
- [x] Run a real-model translation test (NLLB 600M, sample sentences)
- [ ] Native-speaker quality review for Amharic, Afaan Oromo, and Tigrinya
- [x] CLI
- [ ] Speech and OCR

## Contact

Anwar · [an8702299@gmail.com](mailto:an8702299@gmail.com)
