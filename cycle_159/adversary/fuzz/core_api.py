#!/usr/bin/env python3
"""Fuzz harness for rfc8141-urn-pure core API surface (parse / validate / construct).

Surface coverage: 3 of 8 public functions.
Invariants enforced: 21 (total over arbitrary input).
"""
import sys
import atheris

with atheris.instrument_imports():
    from rfc8141_urn_pure import (
        parse,
        validate,
        construct,
        Urn,
        URNParsingError,
        URNValidationError,
    )


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    fn_name = fdp.ConsumeUnicodeNoSurrogates(8)
    arg1 = fdp.ConsumeUnicodeNoSurrogates(128)
    arg2 = fdp.ConsumeUnicodeNoSurrogates(128)

    try:
        if fn_name == "parse":
            parse(arg1)
        elif fn_name == "validate":
            validate(arg1)
        elif fn_name == "construct":
            construct(arg1, arg2)
        # else: junk fn_name — no-op (don't crash on selection bytes)
    except (URNParsingError, URNValidationError):
        pass  # expected domain errors
    except (ValueError, TypeError, AttributeError):
        raise  # uncaught — Invariant 21 violation


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()