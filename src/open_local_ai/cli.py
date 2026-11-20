"""Command-line interface for Open Local AI."""

import argparse
import contextlib
import io
import os
import sys
from collections.abc import Sequence

from open_local_ai import TranslationProvider, TranslationService, __version__
from open_local_ai.core.exceptions import OpenLocalAIError
from open_local_ai.language.metadata import supported_languages
from open_local_ai.translation.providers.argos import ArgosTranslationProvider
from open_local_ai.translation.providers.nllb import NllbTranslationProvider

MODEL_DIR_ENV = "OPEN_LOCAL_AI_NLLB_MODEL_DIR"
TOKENIZER_ENV = "OPEN_LOCAL_AI_NLLB_TOKENIZER"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="open-local-ai",
        description="Offline-first translation with local providers.",
    )
    parser.add_argument(
        "--version", action="version", version=f"open-local-ai {__version__}"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("languages", help="List the canonical languages.")

    translate = commands.add_parser("translate", help="Translate text locally.")
    translate.add_argument(
        "--from",
        "-f",
        dest="source",
        required=True,
        metavar="LANG",
        help="Source language code, for example en.",
    )
    translate.add_argument(
        "--to",
        "-t",
        dest="target",
        required=True,
        metavar="LANG",
        help="Target language code, for example am.",
    )
    translate.add_argument(
        "--provider",
        choices=("nllb", "argos"),
        default="nllb",
        help="Translation provider (default: nllb).",
    )
    translate.add_argument(
        "--model-dir", help=f"NLLB model directory (or set {MODEL_DIR_ENV})."
    )
    translate.add_argument(
        "--tokenizer", help=f"NLLB SentencePiece file (or set {TOKENIZER_ENV})."
    )
    translate.add_argument(
        "text", nargs="?", help="Text to translate. Use - or omit to read stdin."
    )
    return parser


def _build_provider(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> TranslationProvider:
    if args.provider == "argos":
        return ArgosTranslationProvider()

    model_dir = args.model_dir or os.environ.get(MODEL_DIR_ENV)
    tokenizer = args.tokenizer or os.environ.get(TOKENIZER_ENV)
    if not model_dir or not tokenizer:
        parser.error(
            "the nllb provider needs --model-dir and --tokenizer "
            f"(or {MODEL_DIR_ENV} and {TOKENIZER_ENV})."
        )
    return NllbTranslationProvider(model_dir, tokenizer)


def _read_text(args: argparse.Namespace, parser: argparse.ArgumentParser) -> str:
    if args.text not in (None, "-"):
        return str(args.text)
    if sys.stdin.isatty():
        parser.error("no text given; pass it as an argument or pipe it on stdin.")
    return sys.stdin.read().rstrip("\r\n")


def _use_utf8_streams() -> None:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            with contextlib.suppress(ValueError, OSError):
                stream.reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return the process exit code."""
    _use_utf8_streams()
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "languages":
        for language in supported_languages():
            print(f"{language.code}\t{language.name}\t{language.native_name}")
        return 0

    text = _read_text(args, parser)
    try:
        provider = _build_provider(args, parser)
        result = TranslationService(provider).translate(text, args.source, args.target)
    except OpenLocalAIError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.text)
    return 0
