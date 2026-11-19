"""Tests for the command-line interface."""

import io
import subprocess
import sys
from pathlib import Path

import pytest

from open_local_ai import __version__, cli
from open_local_ai.core.models import TranslationRequest, TranslationResult


class _EchoProvider:
    @property
    def is_local(self) -> bool:
        return True

    @property
    def requires_network(self) -> bool:
        return False

    def is_available(self) -> bool:
        return True

    def supports_language(self, language: str) -> bool:
        return language in {"en", "am", "om", "ti"}

    def supports_pair(self, source: str, target: str) -> bool:
        return source != target

    def translate(self, request: TranslationRequest) -> TranslationResult:
        return TranslationResult(
            text=f"[{request.target}] {request.text}",
            source=request.source,
            target=request.target,
        )


@pytest.fixture
def echo_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_build_provider", lambda args, parser: _EchoProvider())


def test_translate_prints_translation(
    echo_provider: None, capsys: pytest.CaptureFixture[str]
) -> None:
    code = cli.main(["translate", "--from", "en", "--to", "am", "Hello"])

    assert code == 0
    assert capsys.readouterr().out.strip() == "[am] Hello"


def test_translate_reads_text_from_stdin(
    echo_provider: None,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Good morning\n"))

    code = cli.main(["translate", "-f", "en", "-t", "ti"])

    assert code == 0
    assert capsys.readouterr().out.strip() == "[ti] Good morning"


def test_unsupported_language_exits_with_error(
    echo_provider: None, capsys: pytest.CaptureFixture[str]
) -> None:
    code = cli.main(["translate", "--from", "en", "--to", "xx", "Hello"])

    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert captured.err.startswith("error:")


def test_empty_text_exits_with_error(
    echo_provider: None, capsys: pytest.CaptureFixture[str]
) -> None:
    code = cli.main(["translate", "--from", "en", "--to", "am", "   "])

    assert code == 1
    assert capsys.readouterr().err.startswith("error:")


def test_languages_lists_canonical_languages(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = cli.main(["languages"])

    out = capsys.readouterr().out
    assert code == 0
    assert "am\tAmharic" in out
    assert "om\tAfaan Oromo" in out
    assert "ti\tTigrinya" in out
    assert "en\tEnglish" in out


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as info:
        cli.main(["--version"])

    assert info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_nllb_requires_model_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(cli.MODEL_DIR_ENV, raising=False)
    monkeypatch.delenv(cli.TOKENIZER_ENV, raising=False)

    with pytest.raises(SystemExit) as info:
        cli.main(["translate", "--from", "en", "--to", "am", "Hello"])

    assert info.value.code == 2


def test_nllb_paths_from_environment_fail_cleanly_when_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv(cli.MODEL_DIR_ENV, str(tmp_path / "missing-model"))
    monkeypatch.setenv(cli.TOKENIZER_ENV, str(tmp_path / "missing.model"))

    code = cli.main(["translate", "--from", "en", "--to", "am", "Hello"])

    assert code == 1
    assert capsys.readouterr().err.startswith("error:")


def test_argos_failure_is_reported_cleanly(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = cli.main(
        ["translate", "--provider", "argos", "--from", "en", "--to", "am", "Hello"]
    )

    assert code == 1
    assert capsys.readouterr().err.startswith("error:")


def test_python_dash_m_runs_the_cli() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "open_local_ai", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stdout.strip() == f"open-local-ai {__version__}"
