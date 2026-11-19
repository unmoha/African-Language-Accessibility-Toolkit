# Changelog

All notable changes to this project will be documented here.

## Unreleased

- Added the initial Python package foundation and development tooling.
- Added project documentation, contribution guidance, and MIT licensing.
- Added immutable translation request and result models, provider contracts, and project-level exceptions.
- Added canonical metadata for Amharic, Afaan Oromo, Tigrinya, and English. This does not imply provider support.
- Added an optional Argos Translate provider with local installed-language and direct-pair detection.
- Verified real Argos English-to-Spanish translation in an isolated environment; Ethiopian-language support remains unverified.
- Documented explicit local model installation and offline provider behavior.
- Renamed the repository to open-local-ai and added project links and keywords to the package metadata.
- Added an optional NLLB-200 provider (CTranslate2) for local Amharic, Afaan Oromo, Tigrinya, and English translation. Quality is not yet evaluated with native speakers.
- Fixed the NLLB language code for Afaan Oromo (now gaz_Latn, West Central Oromo). Verified with a real model for Amharic and Tigrinya; Afaan Oromo is re-verified separately.
- Added repetition blocking and an input-relative decoding length cap to the NLLB provider after a real-model run looped on a short Afaan Oromo sentence. Afaan Oromo output remains unreviewed by native speakers.
- Added the open-local-ai command-line interface (languages and translate commands) with NLLB and Argos providers.
