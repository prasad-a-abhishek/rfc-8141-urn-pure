"""RFC 8141 URN parser — produces Urn named tuples from URN strings."""
from __future__ import annotations

import re
from typing import Any, Optional

from rfc8141_urn_pure._errors import URNParsingError, URNValidationError
from rfc8141_urn_pure._nid import validate_nid, normalize_nid
from rfc8141_urn_pure._nss import validate_nss, percent_decode


class Urn(tuple):
    """RFC 8141 URN parsed components.

    Attributes:
        nid:     The Namespace Identifier (lowercase, 2-32 chars)
        nss:     The Namespace Specific String (raw, 1-255 chars)
        nss_decoded: The NSS with percent-encoding decoded
        rqn:     Resolvable URN Name (RFC 8141 Section 5), or None
        original: The original URN string as provided

    Urn is a tuple subclass: (nid, nss, nss_decoded, rqn, original)
    """

    __slots__ = ()

    def __new__(
        cls,
        nid: str,
        nss: str,
        nss_decoded: str,
        rqn: Optional[str],
        original: str,
    ) -> Urn:
        obj = super().__new__(cls, (nid, nss, nss_decoded, rqn, original))
        return obj

    @property
    def nid(self) -> str:
        return self[0]

    @property
    def nss(self) -> str:
        return self[1]

    @property
    def nss_decoded(self) -> str:
        return self[2]

    @property
    def rqn(self) -> Optional[str]:
        return self[3]

    @property
    def original(self) -> str:
        return self[4]

    def __repr__(self) -> str:
        return (
            f"Urn(nid={self.nid!r}, nss={self.nss!r}, "
            f"nss_decoded={self.nss_decoded!r}, rqn={self.rqn!r})"
        )


# RFC 8141 Section 2: URN = "urn:" NID ":" NSS
# NID is case-insensitive (normalized to lowercase)
# NSS is 1-255 chars from allowed set

# RFC 8141 Section 2.1 NID pattern: 2-32 chars, alphanum first, alphanum/hyphen rest
_NID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\-]{0,31}$")

# RFC 8141 Section 3 NSS character pattern
# Allowed: unreserved + sub-delims + ":" + "@" + "/" + "?" + "#" + "[" + "]" + percent
_NSS_PATTERN = re.compile(
    r"^[a-zA-Z0-9\-._~!$&'()*+,;=:@/?#\[\]%]+$"
)


def parse(urn: Any) -> Urn:
    """Parse a URN string into a Urn named tuple.

    Args:
        urn: A URN string (e.g. "urn:isbn:0451450523")

    Returns:
        Urn(nid, nss, nss_decoded, rqn, original)

    Raises:
        URNParsingError: if the input cannot be parsed as a valid URN
    """
    # --- Total-over-input: never raise bare ValueError/TypeError/AttributeError ---
    if not isinstance(urn, str):
        raise URNParsingError(
            f"parse requires str, got {type(urn).__name__}: {urn!r}"
        )

    # Strip leading/trailing whitespace
    urn_stripped = urn.strip()

    if not urn_stripped:
        raise URNParsingError("URN cannot be empty or whitespace")

    # Check urn: prefix (case-insensitive per RFC 8141 Section 2)
    if len(urn_stripped) < 4 or urn_stripped[:4].lower() != "urn:":
        raise URNParsingError(
            f"URN must start with 'urn:' (case-insensitive), got: {urn_stripped[:8]!r}"
        )

    # Remove "urn:" prefix
    rest = urn_stripped[4:]

    # Missing NID after "urn:"
    if not rest or rest[0] == ":":
        raise URNValidationError(
            f"missing NID after 'urn:': {urn_stripped!r}"
        )

    # Split on first ':' to get NID and NSS
    colon_idx = rest.find(":")
    if colon_idx == -1:
        raise URNValidationError(
            f"URN missing ':' separator between NID and NSS: {urn_stripped!r}"
        )

    nid_raw = rest[:colon_idx]
    nss = rest[colon_idx + 1:]

    # Empty NID
    if not nid_raw:
        raise URNValidationError(
            f"empty NID in URN: {urn_stripped!r}"
        )

    # Validate NID length per RFC 8141 Section 2.1 (2-32 chars)
    if not (2 <= len(nid_raw) <= 32):
        raise URNValidationError(
            f"NID must be 2-32 characters, got {len(nid_raw)}: {nid_raw!r}"
        )

    # Validate NID characters per RFC 8141 Section 2.1
    if not _NID_PATTERN.match(nid_raw):
        raise URNValidationError(
            f"invalid NID format: {nid_raw!r}"
        )

    # Normalize NID to lowercase
    nid = normalize_nid(nid_raw)

    # Empty NSS
    if not nss:
        raise URNValidationError(
            f"empty NSS in URN: {urn_stripped!r}"
        )

    # NSS cannot start with ':' (would indicate double-colon in URN)
    if nss[0] == ":":
        raise URNValidationError(
            f"double colon in URN: NSS starts with ':': {urn_stripped!r}"
        )

    # Validate NSS length per RFC 8141 Section 3 (1-255 chars)
    if not (1 <= len(nss) <= 255):
        raise URNValidationError(
            f"NSS must be 1-255 characters, got {len(nss)}: {nss!r}"
        )

    # Validate NSS characters (RFC 8141 Section 3)
    if not _NSS_PATTERN.match(nss):
        for ch in nss:
            if not (
                ch.isalnum()
                or ch in "-._~!$&'()*+,;=:@/?#[]%"
            ):
                raise URNValidationError(
                    f"invalid character in NSS: {ch!r} in {nss!r}"
                )
        raise URNValidationError(f"invalid NSS format: {nss!r}")

    # Percent-decode the NSS
    try:
        nss_decoded = _percent_decode_nss(nss)
    except Exception as e:
        raise URNParsingError(f"percent-decode failed for NSS: {e}") from e

    # Extract RQN (Resolvable URN Name) per RFC 8141 Section 5
    rqn = f"{nid}:{nss_decoded}"

    return Urn(
        nid=nid,
        nss=nss,
        nss_decoded=nss_decoded,
        rqn=rqn,
        original=urn_stripped,
    )


def _percent_decode_nss(nss: str) -> str:
    """Percent-decode NSS per RFC 8141 Section 3.2.1 / RFC 3986 Section 2.4.

    Handles uppercase/lowercase hex digits in %HH sequences.
    Raises URNEncodingError on invalid sequences.
    """
    result = []
    i = 0
    while i < len(nss):
        if nss[i] == "%":
            if i + 2 >= len(nss):
                from rfc8141_urn_pure._errors import URNEncodingError
                raise URNEncodingError(
                    f"incomplete percent-encoding at end: {nss[i:]!r}"
                )
            hi = nss[i + 1]
            lo = nss[i + 2]
            if hi not in _HEX or lo not in _HEX:
                from rfc8141_urn_pure._errors import URNEncodingError
                raise URNEncodingError(
                    f"invalid hex in percent-encoding: {nss[i:i+3]!r}"
                )
            byte_val = int(hi, 16) * 16 + int(lo, 16)
            result.append(byte_val)
            i += 3
        else:
            result.append(ord(nss[i]))
            i += 1

    # Validate the decoded bytes as UTF-8 — surrogates are invalid UTF-8
    try:
        decoded = bytes(result).decode("utf-8")
    except UnicodeDecodeError as e:
        from rfc8141_urn_pure._errors import URNEncodingError
        raise URNEncodingError(
            f"percent-encoding decodes to invalid UTF-8: {e}"
        ) from e

    return decoded


_HEX = frozenset("0123456789ABCDEFabcdef")
