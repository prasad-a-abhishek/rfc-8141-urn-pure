"""Test basic parse + validate round-trip on RFC 8141 valid examples."""
import pytest
from rfc8141_urn_pure import parse, validate, Urn, URNParsingError, URNValidationError


class TestParseBasic:
    """RFC 8141 Section 2 valid examples — AC1."""

    def test_simple_isbn(self):
        u = parse("urn:isbn:0451450523")
        assert u.nid == "isbn"
        assert u.nss == "0451450523"
        assert isinstance(u, Urn)

    def test_simple_example(self):
        u = parse("urn:example:a123")
        assert u.nid == "example"
        assert u.nss == "a123"

    def test_simple_ns(self):
        u = parse("urn:ns:hello")
        assert u.nid == "ns"
        assert u.nss == "hello"

    def test_validate_isbn(self):
        assert validate("urn:isbn:0451450523") is True

    def test_validate_example(self):
        assert validate("urn:example:a123") is True

    def test_roundtrip_isbn(self):
        original = "urn:isbn:0451450523"
        u = parse(original)
        rebuilt = f"urn:{u.nid}:{u.nss}"
        assert rebuilt == original

    def test_roundtrip_example(self):
        original = "urn:example:a123"
        u = parse(original)
        rebuilt = f"urn:{u.nid}:{u.nss}"
        assert rebuilt == original

    def test_nid_normalized_lowercase(self):
        u = parse("urn:ISBN:0451450523")
        assert u.nid == "isbn"

    def test_nss_preserved_raw(self):
        u = parse("urn:example:HelloWorld")
        assert u.nss == "HelloWorld"

    def test_colon_in_nss(self):
        u = parse("urn:example:a:b:c")
        assert u.nid == "example"
        assert u.nss == "a:b:c"

    def test_at_in_nss(self):
        u = parse("urn:example:user@host")
        assert u.nid == "example"
        assert u.nss == "user@host"

    def test_dash_hyphen_in_nid(self):
        u = parse("urn:foo-bar:123")
        assert u.nid == "foo-bar"

    def test_digit_in_nid(self):
        u = parse("urn:a1b2:test")
        assert u.nid == "a1b2"

    def test_digit_start_nid(self):
        u = parse("urn:123abc:test")
        assert u.nid == "123abc"

    def test_subdelims_in_nss(self):
        u = parse("urn:example:!$&'()*+,;=")
        assert u.nss == "!$&'()*+,;="

    def test_period_in_nss(self):
        u = parse("urn:example:file.txt")
        assert u.nss == "file.txt"

    def test_tilde_in_nss(self):
        u = parse("urn:example:file~1")
        assert u.nss == "file~1"

    def test_percent_encoded_nss(self):
        u = parse("urn:example:hello%20world")
        assert u.nss == "hello%20world"

    def test_multiple_percent_encoded(self):
        u = parse("urn:example:a%3Db%2Bc")
        assert u.nss == "a%3Db%2Bc"

    def test_rqn_extracted(self):
        u = parse("urn:example:hello")
        assert u.rqn == "example:hello"

    def test_nss_decoded_simple(self):
        u = parse("urn:example:hello%20world")
        assert u.nss_decoded == "hello world"

    def test_original_preserved(self):
        original = "  urn:isbn:0451450523  "
        u = parse(original)
        assert u.original.strip() == "urn:isbn:0451450523"
