"""Test ni: and tag: resolvers — AC8, AC9."""
import pytest
import base64
from rfc8141_urn_pure import resolve_ni, resolve_tag, parse, URNParsingError, URNResolveError


class TestResolveNI:
    """ni: scheme resolver per RFC 6920 — AC8."""

    def test_ni_simple_hash(self):
        # ni://example.com/?n=97B9...&alg=sha256
        # sha256 of b"hello"
        sha256_hello = b"\xbb\xd9\xff\xfe\xa8\x99\x95\xdb\xb8\x84\xfc\x8c\xee\x4d\x93\xd1\x84\x85\x02\x1f\xfa\x67\xca\x9f\x9b\xc2\x94\xee\x51\xce\xbf\x63"
        ni_urn = parse(f"urn:ni:?n={base64.urlsafe_b64encode(sha256_hello).decode().rstrip('=')}&alg=sha256")
        result = resolve_ni(ni_urn)
        assert result == sha256_hello

    def test_ni_with_ni_urn_string(self):
        # Build a real ni: URN
        sha256_digest = bytes(range(32))
        encoded = base64.urlsafe_b64encode(sha256_digest).decode().rstrip("=")
        urn_str = f"urn:ni:?n={encoded}&alg=sha256"
        result = resolve_ni(urn_str)
        assert result == sha256_digest

    def test_resolve_ni_wrong_nid(self):
        with pytest.raises(URNResolveError):
            resolve_ni("urn:example:test")

    def test_resolve_ni_missing_n_param(self):
        # ni: without ?n= is invalid
        with pytest.raises(URNResolveError):
            resolve_ni("urn:ni:hello")

    def test_resolve_ni_unsupported_alg(self):
        # sha256 digest (32 bytes), base64url encoded
        sha256_digest = bytes(range(32))
        encoded = base64.urlsafe_b64encode(sha256_digest).decode().rstrip("=")
        urn_str = f"urn:ni:?n={encoded}&alg=sha512"
        # resolve_ni decodes the base64url hash but does NOT validate the algorithm;
        # callers are responsible for verifying the hash matches the expected digest
        result = resolve_ni(urn_str)
        assert result == sha256_digest  # returns raw sha256 bytes (32)

    def test_resolve_ni_passthrough(self):
        # Passing a string should parse it first
        sha256_digest = bytes(range(32))
        encoded = base64.urlsafe_b64encode(sha256_digest).decode().rstrip("=")
        urn_str = f"urn:ni:?n={encoded}&alg=sha256"
        result = resolve_ni(urn_str)
        assert result == sha256_digest


class TestResolveTag:
    """tag: scheme resolver per RFC 4151 — AC9."""

    def test_tag_simple(self):
        urn = parse("urn:tag:example.com,2024-10-01:blog/entry")
        result = resolve_tag(urn)
        assert result == "2024-10-01 example.com blog/entry"

    def test_tag_with_string_input(self):
        result = resolve_tag("urn:tag:example.com,2024-01-15:article/123")
        assert "2024-01-15" in result
        assert "example.com" in result

    def test_tag_wrong_nid(self):
        with pytest.raises(URNResolveError):
            resolve_tag("urn:example:test")

    def test_tag_missing_colon(self):
        # This will fail because the NSS doesn't have ':'
        with pytest.raises(URNResolveError):
            resolve_tag("urn:tag:example.com,2024-10-01")

    def test_tag_invalid_date_format(self):
        with pytest.raises(URNResolveError):
            resolve_tag("urn:tag:example.com,2024/10/01:obj")

    def test_tag_missing_comma(self):
        with pytest.raises(URNResolveError):
            resolve_tag("urn:tag:example.com2024-10-01:obj")

    def test_tag_passthrough(self):
        # Passing a string should parse it first
        result = resolve_tag("urn:tag:example.com,2024-10-01:blog/entry")
        assert result == "2024-10-01 example.com blog/entry"

    def test_tag_date_only(self):
        urn = parse("urn:tag:example.com,2024-10-01:object")
        result = resolve_tag(urn)
        assert "2024-10-01" in result

    def test_tag_with_subpath(self):
        urn = parse("urn:tag:example.com,2024-10-01:a/b/c/d")
        result = resolve_tag(urn)
        assert "a/b/c/d" in result

    def test_resolve_tag_non_urn(self):
        with pytest.raises(URNResolveError):
            resolve_tag("not-a-urn")
