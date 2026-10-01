"""RFC 8141 URN construction (Section 4) with optional percent-encoding."""
from __future__ import annotations

from rfc8141_urn_pure._errors import URNParsingError, URNValidationError, URNEncodingError
from rfc8141_urn_pure._nid import validate_nid, normalize_nid
from rfc8141_urn_pure._nss import validate_nss, percent_encode as _pct_encode
from rfc8141_urn_pure._parser import parse


def construct(nid: str, nss: str, *, percent_encode: bool = False) -> str:
    """Construct a RFC 8141 Section 4 compliant URN string.

    Args:
        nid:          The Namespace Identifier (2-32 chars)
        nss:          The Namespace Specific String
        percent_encode: If True, percent-encodes the NSS before assembly.
                        If False, uses NSS as-is (must already be valid).

    Returns:
        The assembled URN string: "urn:<nid>:<nss>"

    Raises:
        URNParsingError: if nid or nss are invalid types or values
    """
    # --- Total over input ---
    if not isinstance(nid, str):
        raise URNParsingError(
            f"construct: nid must be str, got {type(nid).__name__}: {nid!r}"
        )
    if not isinstance(nss, str):
        raise URNParsingError(
            f"construct: nss must be str, got {type(nss).__name__}: {nss!r}"
        )

    # Normalize NID to lowercase
    nid_norm = normalize_nid(nid)

    # Validate NID
    if not validate_nid(nid_norm):
        raise URNValidationError(
            f"construct: invalid NID: {nid_norm!r}"
        )

    # Encode or validate NSS
    if percent_encode:
        nss_encoded = _pct_encode(nss)
    else:
        if not validate_nss(nss):
            raise URNValidationError(
                f"construct: invalid NSS (must be 1-255 valid NSS chars "
                f"or use percent_encode=True): {nss!r}"
            )
        nss_encoded = nss

    return f"urn:{nid_norm}:{nss_encoded}"
