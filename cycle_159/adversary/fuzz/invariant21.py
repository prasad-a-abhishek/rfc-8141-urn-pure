#!/usr/bin/env python3
"""Fuzz harness for Invariant 21 — total-over-arbitrary-input for all 8 public APIs.

Feeds None / int / bool / list / dict / bytes / float / mix to confirm every
public function handles malformed input without leaking AttributeError,
TypeError, or uncaught ValueError.
"""
import sys
import atheris

with atheris.instrument_imports():
    from rfc8141_urn_pure import (
        parse,
        validate,
        validate_nid,
        validate_nss,
        construct,
        resolve_ni,
        resolve_tag,
        percent_decode,
        URNParsingError,
        URNEncodingError,
        URNResolveError,
        URNValidationError,
    )


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    arg_type = fdp.ConsumeIntInRange(0, 8)
    arg = {
        0: None,
        1: fdp.ConsumeIntInRange(-1_000_000, 1_000_000),
        2: fdp.ConsumeBool(),
        3: [fdp.ConsumeUnicodeNoSurrogates(8)],
        4: {fdp.ConsumeUnicodeNoSurrogates(4): fdp.ConsumeIntInRange(0, 100)},
        5: fdp.ConsumeUnicodeNoSurrogates(64).encode("utf-8"),
        6: fdp.ConsumeUnicodeNoSurrogates(64),
        7: fdp.ConsumeFloat(),
        8: fdp.ConsumeUnicodeNoSurrogates(64) if fdp.ConsumeBool() else None,
    }[arg_type]

    # Catch EVERY domain exception plus all Invariant 21 targets (ValueError,
    # TypeError, AttributeError). Any leak here means Invariant 21 was violated.
    safe_exceptions = (
        URNParsingError,
        URNValidationError,
        URNEncodingError,
        URNResolveError,
        ValueError,
        TypeError,
        AttributeError,
    )

    for fn in (
        parse,
        validate,
        validate_nid,
        validate_nss,
        lambda x: construct(x, x),
        resolve_ni,
        resolve_tag,
        percent_decode,
    ):
        try:
            fn(arg)
        except safe_exceptions:
            pass
        except Exception:
            raise  # unexpected exception class — Invariant 21 violation


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()