"""RFC 8141 URN parsing, validation, and resolution — zero dependency."""
from rfc8141_urn_pure._errors import (
    URNParsingError,
    URNValidationError,
    URNEncodingError,
    URNResolveError,
)
from rfc8141_urn_pure._parser import parse, Urn
from rfc8141_urn_pure._nid import validate_nid
from rfc8141_urn_pure._nss import validate_nss, percent_decode
from rfc8141_urn_pure._construct import construct
from rfc8141_urn_pure._resolver import resolve_ni, resolve_tag

__all__ = [
    "parse",
    "validate",
    "validate_nid",
    "validate_nss",
    "construct",
    "resolve_ni",
    "resolve_tag",
    "percent_decode",
    "Urn",
    "URNParsingError",
    "URNValidationError",
    "URNEncodingError",
    "URNResolveError",
]


def validate(urn: str) -> bool:
    """Return True if the input is a valid RFC 8141 URN, False otherwise."""
    try:
        parse(urn)
        return True
    except URNParsingError:
        return False
