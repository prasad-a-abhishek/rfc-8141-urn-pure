"""Test exception safety — AC10, AC11 — Invariant 21: total over arbitrary input."""
import pytest
from rfc8141_urn_pure import (
    parse,
    validate,
    construct,
    resolve_ni,
    resolve_tag,
    validate_nid,
    validate_nss,
    Urn,
    URNParsingError,
    URNValidationError,
    URNEncodingError,
    URNResolveError,
)


class TestExceptionSafetyParse:
    """parse() never raises bare ValueError/TypeError/AttributeError — AC10."""

    def test_none_raises_urnparsingerror(self):
        with pytest.raises(URNParsingError):
            parse(None)

    def test_bytes_raises_urnparsingerror(self):
        with pytest.raises(URNParsingError):
            parse(b"urn:example:test")

    def test_int_raises_urnparsingerror(self):
        with pytest.raises(URNParsingError):
            parse(12345)

    def test_list_raises_urnparsingerror(self):
        with pytest.raises(URNParsingError):
            parse(["urn:example:test"])

    def test_dict_raises_urnparsingerror(self):
        with pytest.raises(URNParsingError):
            parse({"urn": "example:test"})

    def test_float_raises_urnparsingerror(self):
        with pytest.raises(URNParsingError):
            parse(3.14159)


class TestExceptionSafetyValidate:
    """validate() always returns bool — AC11."""

    def test_validate_none(self):
        assert validate(None) is False

    def test_validate_bytes(self):
        assert validate(b"urn:example:test") is False

    def test_validate_int(self):
        assert validate(12345) is False

    def test_validate_list(self):
        assert validate([]) is False

    def test_validate_empty(self):
        assert validate("") is False

    def test_validate_whitespace(self):
        assert validate("   ") is False

    def test_validate_malformed_url(self):
        assert validate("https://example.com") is False


class TestExceptionSafetyValidateNID:
    """validate_nid() always returns bool — AC11."""

    def test_nid_none(self):
        assert validate_nid(None) is False

    def test_nid_bytes(self):
        assert validate_nid(b"isbn") is False

    def test_nid_int(self):
        assert validate_nid(123) is False


class TestExceptionSafetyValidateNSS:
    """validate_nss() always returns bool — AC11."""

    def test_nss_none(self):
        assert validate_nss(None) is False

    def test_nss_bytes(self):
        assert validate_nss(b"hello") is False

    def test_nss_int(self):
        assert validate_nss(12345) is False


class TestExceptionSafetyConstruct:
    """construct() raises URNParsingError, not bare exceptions — AC10."""

    def test_construct_none_nid(self):
        with pytest.raises(URNParsingError):
            construct(None, "test")

    def test_construct_none_nss(self):
        with pytest.raises(URNParsingError):
            construct("example", None)

    def test_construct_int_nid(self):
        with pytest.raises(URNParsingError):
            construct(123, "test")

    def test_construct_int_nss(self):
        with pytest.raises(URNParsingError):
            construct("example", 123)

    def test_construct_oversized_nss(self):
        with pytest.raises((URNValidationError, URNParsingError)):
            construct("example", "a" * 1000)


class TestExceptionSafetyResolve:
    """resolve_ni() and resolve_tag() raise URNResolveError — AC10."""

    def test_resolve_ni_none(self):
        with pytest.raises(URNResolveError):
            resolve_ni(None)

    def test_resolve_ni_int(self):
        with pytest.raises(URNResolveError):
            resolve_ni(123)

    def test_resolve_tag_none(self):
        with pytest.raises(URNResolveError):
            resolve_tag(None)

    def test_resolve_tag_int(self):
        with pytest.raises(URNResolveError):
            resolve_tag(456)

    def test_resolve_ni_wrong_nid_type(self):
        # Valid URN string with wrong NID
        with pytest.raises(URNResolveError):
            resolve_ni("urn:isbn:0451450523")

    def test_resolve_tag_wrong_nid_type(self):
        with pytest.raises(URNResolveError):
            resolve_tag("urn:isbn:0451450523")


class TestOversizedInput:
    """Fuzz inputs: oversized NSS (100k chars) — AC13."""

    def test_parse_100k_nss_oversized(self):
        large_nss = "a" * 100_000
        with pytest.raises(URNValidationError):
            parse(f"urn:example:{large_nss}")

    def test_validate_100k_nss(self):
        large_nss = "a" * 100_000
        assert validate(f"urn:example:{large_nss}") is False

    def test_parse_10k_nss(self):
        nss = "a" * 10_000
        # This should fail validation (NSS must be <= 255)
        with pytest.raises(URNValidationError):
            parse(f"urn:example:{nss}")
