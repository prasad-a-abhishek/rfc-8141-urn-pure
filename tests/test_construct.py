"""Test construct() per RFC 8141 Section 4 — AC7."""
import pytest
from rfc8141_urn_pure import construct, parse, validate, URNParsingError, URNValidationError


class TestConstruct:
    """construct() canonical assembly — AC7."""

    def test_simple_isbn(self):
        result = construct("isbn", "0451450523")
        assert result == "urn:isbn:0451450523"

    def test_simple_example(self):
        result = construct("example", "a123")
        assert result == "urn:example:a123"

    def test_lowercase_nid_normalized(self):
        result = construct("ISBN", "0451450523")
        assert result == "urn:isbn:0451450523"

    def test_mixed_case_nid(self):
        result = construct("ExAmple", "test")
        assert result == "urn:example:test"

    def test_nid_with_hyphen(self):
        result = construct("foo-bar", "test")
        assert result == "urn:foo-bar:test"

    def test_roundtrip_parse_construct(self):
        nid = "isbn"
        nss = "0451450523"
        built = construct(nid, nss)
        parsed = parse(built)
        assert parsed.nid == nid
        assert parsed.nss == nss

    def test_percent_encode_flag(self):
        result = construct("example", "hello world", percent_encode=True)
        assert result == "urn:example:hello%20world"

    def test_percent_encode_unicode(self):
        result = construct("example", "café", percent_encode=True)
        assert "urn:example:caf" in result

    def test_nss_already_encoded_no_reencode(self):
        result = construct("example", "hello%20world", percent_encode=False)
        assert result == "urn:example:hello%20world"

    def test_nss_with_reserved_chars(self):
        result = construct("example", "a:b", percent_encode=False)
        assert result == "urn:example:a:b"

    def test_invalid_nid_too_short(self):
        with pytest.raises(URNValidationError):
            construct("a", "test")

    def test_invalid_nid_too_long(self):
        with pytest.raises(URNValidationError):
            construct("a" * 100, "test")

    def test_invalid_nss_not_encoded(self):
        # Without percent_encode=True, invalid NSS chars should raise
        with pytest.raises(URNValidationError):
            construct("example", "hello world", percent_encode=False)

    def test_construct_non_str_nid(self):
        with pytest.raises(URNParsingError):
            construct(123, "test")

    def test_construct_non_str_nss(self):
        with pytest.raises(URNParsingError):
            construct("example", None)

    def test_construct_empty_nss(self):
        with pytest.raises(URNValidationError):
            construct("example", "")

    def test_nid_digit_start(self):
        result = construct("123abc", "test")
        assert result == "urn:123abc:test"

    def test_nss_254_chars(self):
        nss = "a" * 254
        result = construct("example", nss)
        assert len(result) == len("urn:example:") + 254
