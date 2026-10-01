#!/usr/bin/env python3
"""Fuzz harness for rfc8141-urn-pure CLI surface (__main__.main()).

Exercises all 5 subcommands (parse/validate/construct/resolve-ni/resolve-tag)
plus --help and missing-subcommand paths.
"""
import io
import sys
import atheris

with atheris.instrument_imports():
    from rfc8141_urn_pure.__main__ import main


SUBCOMMANDS = ("parse", "validate", "construct", "resolve-ni", "resolve-tag", "help")


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    argc = fdp.ConsumeIntInRange(0, 8)
    argv = ["main"]  # prog name
    for idx in range(argc):
        argv.append(fdp.ConsumeUnicodeNoSurrogates(64))

    # Suppress CLI noise
    saved_out, saved_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
    try:
        try:
            main(argv)
        except SystemExit:
            pass  # argparse + return-code path
        except (ValueError, TypeError, AttributeError):
            raise  # uncaught — Invariant 21 violation on CLI
    finally:
        sys.stdout, sys.stderr = saved_out, saved_err


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()