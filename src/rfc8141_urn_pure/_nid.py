"""RFC 8141 NID (Namespace Identifier) validation.

RFC 8141 Section 2.1:
  NID = let-dig [ *31( let-dig / "-" ) let-dig ]
  let-dig = ALPHA / DIGIT

Rules:
- 2 to 32 characters total
- First character must be alphanumeric (letter or digit)
- Subsequent characters (up to 31) may be alphanumeric or hyphen
- Lowercase normalization: uppercase letters are allowed but will be
  normalized to lowercase on parse
"""
from __future__ import annotations

import re
from typing import Any


# RFC 8141 Section 2.1 formal NID rule
# 2 to 32 chars: letter/digit first, then up to 31 chars of letter/digit/hyphen
_NID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\-]{0,31}$")

# Reserved percent-encode set in NSS (RFC 8141 Section 3.2.2)
_NSS_RESERVED = frozenset(
    "!$&=()*+,/:;?@[]"
)


def validate_nid(nid: str) -> bool:
    """Validate a Namespace Identifier (NID) per RFC 8141 Section 2.1.

    Returns True if the NID is valid (2-32 chars, alphanum, hyphens allowed
    after first char), False otherwise.

    This function is total: it never raises. Invalid types are coerced
    or return False.
    """
    if not isinstance(nid, str):
        return False
    if not (2 <= len(nid) <= 32):
        return False
    if not _NID_RE.match(nid):
        return False
    return True


def normalize_nid(nid: str) -> str:
    """Return lowercase-normalized NID."""
    return nid.lower()
