#!/usr/bin/env python3
"""Fuzz harness for rfc8141-urn-pure resolver surface (resolve_ni / resolve_tag)."""
import sys
import atheris

with atheris.instrument_imports():
    from rfc8141_urn_pure import (
        resolve_ni,
        resolve_tag,
        URNParsingError,
        URNResolveError,
    )


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    fn_name = fdp.ConsumeUnicodeNoSurrogates(8)
    arg = fdp.ConsumeUnicodeNoSurrogates(255)

    try:
        if fn_name == "ni":
            resolve_ni(arg)
        elif fn_name == "tag":
            resolve_tag(arg)
        # else: junk
    except (URNParsingError, URNResolveError):
        pass  # expected domain errors
    except (ValueError, TypeError, AttributeError):
        raise  # uncaught — Invariant 21 violation


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()