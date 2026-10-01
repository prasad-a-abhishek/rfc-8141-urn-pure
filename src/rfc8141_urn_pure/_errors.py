"""Exception hierarchy for rfc8141-urn-pure."""


class URNParsingError(Exception):
    """Base exception for all URN parsing and validation errors."""

    pass


class URNValidationError(URNParsingError):
    """Raised when a URN component fails validation (NID or NSS rules)."""

    pass


class URNEncodingError(URNParsingError):
    """Raised when percent-encoding or decoding fails."""

    pass


class URNResolveError(URNParsingError):
    """Raised when URN resolution (ni: or tag:) fails."""

    pass
