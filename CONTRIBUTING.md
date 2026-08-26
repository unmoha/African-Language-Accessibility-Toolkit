# Contributing

Open Local AI is in early development. Keep changes small, focused, and consistent with the current scope. Do not describe planned capabilities as implemented.

## Development setup

Use Python 3.11 or newer, then install the project with its development tools:

```bash
python -m pip install --editable ".[dev]"
```

The core package and default test suite do not require Argos. To work on the Argos provider, install its optional dependency separately:

```bash
python -m pip install --editable ".[dev,argos]"
```

The Argos Python dependency does not install translation models. Models must be obtained and installed explicitly in the local Argos environment. Open Local AI does not download models, install models, or update the Argos package index automatically.

## Quality checks

Run these commands from the repository root:

```bash
pytest
ruff check .
ruff format --check .
mypy .
git diff --check
```

Apply Ruff formatting when needed with:

```bash
ruff format .
```

## Contribution workflow

1. Make a focused change related to an open project need.
2. Add or update behavior-focused tests when implementation exists.
3. Run the complete quality checks locally.
4. Explain the scope, design decisions, and verification in the pull request.

Pull requests should avoid unrelated refactors, unnecessary dependencies, unsupported language claims, and automatic model downloads. Documentation should distinguish implemented, planned, unsupported, and unverified behavior.

## Provider and integration work

Provider tests should use deterministic fakes and must not require internet access, a user's local Argos installation, or downloaded models. Real Argos model checks belong in an explicit, isolated verification workflow and are not part of the default CI suite.

When adding a provider, keep provider-specific imports and mappings inside its adapter. Preserve the existing `TranslationProvider` contract, project-level exceptions, direct-pair semantics, and offline behavior. Do not add pivot routing or automatic model management without a separate design decision.