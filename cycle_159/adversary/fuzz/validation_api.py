#!/usr/bin/env python3
"""Fuzz harness for rfc8141-urn-pure validation API surface.

Covers validate_nid, validate_nss, percent_decode. (percent_encode is NOT in
the package's public __all__ — see F-L1 in cycle_159/adversary/VULN_AUDIT.md.)
"""
import sys
import atheris

with atheris.instrument_imports():
    from rfc8141_urn_pure import (
        validate_nid,
        validate_nss,
        percent_decode,
        URNParsingError,
        URNValidationError,
        URNEncodingError,
    )


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    fn_name = fdp.ConsumeUnicodeNoSurrogates(8)
    arg = fdp.ConsumeUnicodeNoSurrogates(255)  # NSS up to 255 chars

    try:
        if fn_name == "nid":
            validate_nid(arg)
        elif fn_name == "nss":
            validate_nss(arg)
        elif fn_name == "decode":
            percent_decode(arg)
        # else: junk
    except (URNParsingError, URNValidationError, URNEncodingError):
        pass  # expected domain errors
    except (ValueError, TypeError, AttributeError):
        raise  # uncaught — Invariant 21 violation


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()