"""RFC 8141 URN resolution: ni: (RFC 6920) and tag: (RFC 4151) schemes.

These resolvers extract scheme-specific information from URN strings
that use the 'ni' or 'tag' namespace identifiers.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

from rfc8141_urn_pure._errors import URNResolveError, URNParsingError
from rfc8141_urn_pure._parser import Urn


def resolve_ni(urn: Urn | str) -> bytes | None:
    """Resolve a URN with the 'ni' (Named Information) scheme per RFC 6920.

    RFC 6920 Section 2.1 defines the 'ni' URN scheme:
      ni://<authority>/<nis-specific-part>

    The NSS of a 'ni:' URN is parsed as:
      ?n=<hash小子>&alg=<algorithm>

    Args:
        urn: A Urn named tuple or a URN string with nid='ni'

    Returns:
        The raw hash digest as bytes, or None if the hash cannot be extracted

    Raises:
        URNResolveError: if the input is not a valid ni: URN or
                        the algorithm is unsupported
    """
    if isinstance(urn, str):
        from rfc8141_urn_pure._parser import parse as _parse
        try:
            urn = _parse(urn)
        except URNParsingError as e:
            raise URNResolveError(
                f"resolve_ni requires a valid URN string, got: {urn!r}"
            ) from e

    if not isinstance(urn, Urn):
        raise URNResolveError(
            f"resolve_ni requires a Urn, got {type(urn).__name__}"
        )

    if urn.nid != "ni":
        raise URNResolveError(
            f"resolve_ni requires nid='ni', got nid={urn.nid!r}"
        )

    nss = urn.nss

    # RFC 6920: NSS is query-string style: ?n=<hash>&alg=<algorithm>
    params: dict[str, str] = {}
    if "?" in nss:
        query_part = nss.split("?", 1)[1]
        for pair in query_part.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params[k] = v

    if "n" not in params:
        raise URNResolveError(
            f"ni: URN missing 'n' parameter in NSS: {urn.nss!r}"
        )

    hash_b64url = params["n"]
    alg = params.get("alg", "sha256")

    # Decode base64url to bytes
    try:
        import base64
        digest_bytes = base64.urlsafe_b64decode(
            hash_b64url + "=" * (4 - len(hash_b64url) % 4)
        )
    except Exception as e:
        raise URNResolveError(
            f"ni: failed to decode base64url hash {hash_b64url!r}: {e}"
        ) from e

    return digest_bytes


def resolve_tag(urn: Urn | str) -> str:
    r"""Resolve a URN with the 'tag' (Atom Archive) scheme per RFC 4151.

    RFC 4151 Section 2:
      tag:<authority>:<date>:<object>

    The NSS format is: <authority>,<date>:<object>
    Example: urn:tag:example.com,2024-10-01:blog/entry

    Args:
        urn: A Urn named tuple or a URN string with nid='tag'

    Returns:
        A formatted tag string: "<date> <authority> <object>"

    Raises:
        URNResolveError: if the input is not a valid tag: URN or
                        the date/authority cannot be parsed
    """
    if isinstance(urn, str):
        from rfc8141_urn_pure._parser import parse as _parse
        try:
            urn = _parse(urn)
        except URNParsingError as e:
            raise URNResolveError(
                f"resolve_tag requires a valid URN string, got: {urn!r}"
            ) from e

    if not isinstance(urn, Urn):
        raise URNResolveError(
            f"resolve_tag requires a Urn, got {type(urn).__name__}"
        )

    if urn.nid != "tag":
        raise URNResolveError(
            f"resolve_tag requires nid='tag', got nid={urn.nid!r}"
        )

    nss = urn.nss  # raw NSS from the URN

    # RFC 4151: tag:<authority>,<date>:<object>
    if ":" not in nss:
        raise URNResolveError(
            f"tag: NSS missing ':' separator: {nss!r}"
        )

    date_authority_part, obj = nss.split(":", 1)

    if "," not in date_authority_part:
        raise URNResolveError(
            f"tag: NSS missing ',' in authority,date part: {date_authority_part!r}"
        )

    # Date format: YYYY-MM-DD
    last_comma = date_authority_part.rfind(",")
    authority = date_authority_part[:last_comma]
    date_str = date_authority_part[last_comma + 1:]

    # Validate date format
    _DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if not _DATE_RE.match(date_str):
        raise URNResolveError(
            f"tag: invalid date format in NSS (expected YYYY-MM-DD): {date_str!r}"
        )

    return f"{date_str} {authority} {obj}"
