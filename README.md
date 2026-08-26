# Open Local AI

Open Local AI is an early-stage Python library project for building offline-first language and accessibility tools around local AI providers. It is intended for developers who need a stable application-facing interface while keeping translation engines and local models replaceable.

## Current status

The repository currently contains the project foundation, canonical language metadata, and an Argos Translate provider adapter. Translation is available when a suitable Argos model is installed locally.

The initial implementation scope is translation. The current provider-independent service uses adapters for verified local engines. Speech-to-text, text-to-speech, OCR, accessibility utilities, web interfaces, and remote providers are planned but are not implemented.

## Languages

Open Local AI currently defines a canonical language vocabulary containing:

- `am` - Amharic
- `om` - Afaan Oromo
- `ti` - Tigrinya
- `en` - English

Canonical recognition does not imply that a translation provider currently supports every language or language pair. Actual translation support will depend on verified provider and model availability. A language code alone will never imply that a provider supports a language or a language pair.

## Planned architecture

Applications will use a translation service through a provider abstraction:

```text
Application
	-> TranslationService
	-> TranslationProvider
	-> Concrete provider adapter
	-> Local model or engine
```

The core package will remain usable without any particular provider installed. Provider availability, supported language pairs, model installation, and network requirements will be checked explicitly. Unsupported requests will produce project-level errors rather than fallback or fabricated translations.

## Offline and privacy goals

Local providers should process text without sending it to a remote service, but offline behavior will only be claimed after the provider execution path has been verified. Remote providers, if added later, will require explicit selection.

The project will not collect user text, audio, or telemetry by default. Models will not be downloaded automatically during import, object construction, translation, or normal CLI use.

## Development

Development setup and quality checks are documented in [CONTRIBUTING.md](CONTRIBUTING.md). The current foundation supports:

```text
install -> pytest -> ruff check -> ruff format --check -> mypy
```

This project is not ready to claim working translation support. Provider behavior and language-pair support will be documented only after they are implemented and verified.

## Roadmap

1. Repository foundation
2. Core models and exceptions
3. Canonical language metadata (completed)
4. Provider interface and reusable provider contract tests (completed)
5. Verified local provider adapter (completed)
6. Translation service (completed)
7. CLI
8. Documentation and examples (completed)
9. Full quality review (completed)

The project is maintained incrementally. Features outside the current milestone should be treated as planned, not implemented.

## Argos Translation Provider

The Argos provider connects Open Local AI to locally installed Argos Translate models. Argos is optional; the core package remains usable without it.

Install the optional dependency with:

```bash
pip install "open-local-ai[argos]"
```

This installs the Argos Python dependency, but it does not install translation models. Obtain the required `.argosmodel` package separately and install it into the local Argos environment with Argos Translate's supported local installation API:

```python
import argostranslate.package

argostranslate.package.install_from_path("/path/to/your-model.argosmodel")
```

Model installation is a one-time, user-controlled setup step. Open Local AI does not automatically download models, install models, or update the Argos package index.

After a model is installed, the provider discovers the locally installed languages and direct translation relationships. Normal provider operations use that local state:

```text
Install the Argos extra
	-> obtain a .argosmodel package
	-> install the model locally
	-> create ArgosTranslationProvider
	-> translate with the installed local model
```

Model acquisition may require internet access. Translation is local when the required Argos model is already installed. The provider's normal capability and translation operations do not access remote model repositories or perform hidden model management.

### Basic usage

```python
from open_local_ai import TranslationRequest
from open_local_ai.translation.providers.argos import ArgosTranslationProvider

provider = ArgosTranslationProvider()

request = TranslationRequest(
    text="Hello, how are you?",
    source="en",
    target="es",
)

result = provider.translate(request)

print(result.text)
```

The provider can also be used through the provider-independent service:

```python
from open_local_ai import TranslationService
from open_local_ai.translation.providers.argos import ArgosTranslationProvider

provider = ArgosTranslationProvider()
service = TranslationService(provider)

result = service.translate(
    "Hello, how are you?",
    "en",
    "es",
)

print(result.text)
```

Check the current local Argos installation before translating:

```python
from open_local_ai.translation.providers.argos import ArgosTranslationProvider

provider = ArgosTranslationProvider()

if not provider.is_available():
    raise RuntimeError("Argos is unavailable")

if provider.supports_language("en"):
    print("English is available")

if provider.supports_pair("en", "es"):
    print("English -> Spanish is available")
```

`supports_language()` reports whether a language is represented by the locally installed Argos language set. `supports_pair()` reports whether a direct source-to-target relationship exists in the locally installed Argos models. A canonical language entry, a remote package index entry, or theoretical Argos support is not enough. The provider does not treat a pivot route as direct pair support.

## Language and provider support

Open Local AI's canonical language metadata describes languages known to the project. It does not mean that every provider has a locally installed model for those languages. Argos capability depends on the language and translation models installed locally.

| Language | Code | Canonical metadata | Argos locally verified |
|---|---|---|---|
| Amharic | `am` | Yes | No |
| Afaan Oromo | `om` | Yes | No |
| Tigrinya | `ti` | Yes | No |

Amharic, Afaan Oromo, and Tigrinya are canonical languages recognized by Open Local AI, but they are not currently verified as available through the Argos environment tested by this project. This does not mean Argos can never support them.

The verified `translate-en_es` model produced `Hola, ¿cómo estás?` for the example sentence above. This is an example result from that model, not a universal guarantee for every Argos model version.

## Argos errors

The adapter exposes project-level errors rather than requiring callers to depend on raw Argos exceptions:

- `ProviderUnavailableError`: the Argos Python runtime is unavailable.
- `UnsupportedLanguageError`: the requested language is not available from locally installed Argos language data.
- `UnsupportedLanguagePairError`: the requested direct source-to-target pair is not installed.
- `ModelNotInstalledError`: a required model is unavailable during translation execution.
- `TranslationError`: the translation operation failed unexpectedly.