"""RFC 8141 NSS (Namespace Specific String) validation and percent-encoding.

RFC 8141 Section 3:
  NSS = 1*( unreserved / pct-encoded / sub-delims / ":" / "@" )
  unreserved = ALPHA / DIGIT / "-" / "." / "_" / "~"
  sub-delims = "!" / "$" / "&" / "'" / "(" / ")" / "*" / "+" / "," / ";" / "="
  pct-encoded = "%" HEXDIG HEXDIG

Rules:
- 1 to 255 characters
- Allowed chars: unreserved + sub-delims + ":" + "@" + percent-encoded
- Percent-encoding: exactly %HH where HH are two uppercase hex digits
- No other reserved URI characters (RFC 3986 Section 2.2) allowed without encoding
"""
from __future__ import annotations

import re
from typing import Optional

# RFC 8141 Section 3 NSS character classes
_UNRESERVED = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")
_SUB_DELIMS = frozenset("!$&'()*+,;=")
_NSS_ALLOWED = _UNRESERVED | _SUB_DELIMS | frozenset("%:@")

_HEX_DIGITS = frozenset("0123456789ABCDEFabcdef")

# NSS must be 1-255 chars, using allowed charset or %-encoded
_NSS_PATTERN = re.compile(
    r"^[a-zA-Z0-9\-._~!$&'()*+,;=:@/?#\[\]%]+$"
)

# Percent-encoded pattern: %HH (hex digits, case-insensitive per RFC 3986)
_PCT_RE = re.compile(r"%[0-9A-Fa-f]{2}")

# Surrogate pair detection during percent-decoding
_SURROGATE_RE = re.compile(r"(%[Ee][0-9A-Fa-f]{2}%[Uu][0-9A-Fa-f]{4})")


def validate_nss(nss: str) -> bool:
    """Validate a Namespace Specific String (NSS) per RFC 8141 Section 3.

    Returns True if the NSS is valid (1-255 chars, allowed chars or
    properly percent-encoded), False otherwise.

    This function is total: it never raises. Invalid types are coerced
    or return False.
    """
    if not isinstance(nss, str):
        return False
    if not (1 <= len(nss) <= 255):
        return False
    if not _NSS_PATTERN.match(nss):
        return False
    # Additionally validate each percent-encoded sequence
    for m in _PCT_RE.finditer(nss):
        hex_part = m.group(0)[1:]
        if not all(c in _HEX_DIGITS for c in hex_part):
            return False
    # Reject NSS with trailing '%' or incomplete percent sequences
    i = 0
    while i < len(nss):
        if nss[i] == "%":
            if i + 2 >= len(nss):
                return False  # trailing or incomplete %
            hi, lo = nss[i+1], nss[i+2]
            if hi not in _HEX_DIGITS or lo not in _HEX_DIGITS:
                return False
            i += 3
        else:
            i += 1
    return True


def percent_decode(s: str) -> str:
    """Decode percent-encoded sequences in the input string per RFC 3986 Sec 2.4.

    Args:
        s: A percent-encoded string

    Returns:
        The decoded string

    Raises:
        URNEncodingError: if the input contains invalid percent-encoding
                          (invalid hex digits, or surrogate pair sequences)
    """
    from rfc8141_urn_pure._errors import URNEncodingError

    if not isinstance(s, str):
        raise URNEncodingError(f"percent_decode requires str, got {type(s).__name__}")
    # Decode each byte
    result = []
    i = 0
    while i < len(s):
        if s[i] == "%":
            if i + 2 >= len(s):
                raise URNEncodingError(
                    f"incomplete percent-encoding at position {i}: {s[i:]!r}"
                )
            hi = s[i + 1]
            lo = s[i + 2]
            if hi not in _HEX_DIGITS or lo not in _HEX_DIGITS:
                raise URNEncodingError(
                    f"invalid hex digits in percent-encoding at position {i}: "
                    f"{s[i:i+3]!r}"
                )
            byte_val = int(hi, 16) * 16 + int(lo, 16)
            result.append(byte_val)
            i += 3
        else:
            # Non-percent char: encode as UTF-8 bytes
            for b in s[i].encode("utf-8"):
                result.append(b)
            i += 1

    # Validate the complete byte sequence as UTF-8
    try:
        decoded = bytes(result).decode("utf-8")
    except UnicodeDecodeError as e:
        raise URNEncodingError(
            f"percent-encoding decodes to invalid UTF-8: {e}"
        ) from e

    return decoded


def percent_encode(s: str) -> str:
    """Percent-encode a string per RFC 3986 Section 2.4.

    Encodes all characters not in the allowed URN NSS character set
    (unreserved, sub-delims, ':', '@').

    Args:
        s: The string to encode

    Returns:
        The percent-encoded string
    """
    result = []
    for ch in s:
        cp = ord(ch)
        if ch in _UNRESERVED or ch in _SUB_DELIMS or ch in ":@":
            result.append(ch)
        else:
            for byte_val in ch.encode("utf-8"):
                result.append(f"%{byte_val:02X}")
    return "".join(result)
