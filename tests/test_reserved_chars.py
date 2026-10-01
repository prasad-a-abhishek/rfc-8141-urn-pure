"""Test reserved character detection per RFC 8141 Section 3.2.2."""
import pytest
from rfc8141_urn_pure import parse


class TestReservedChars:
    """Reserved character detection — AC5."""

    RESERVED_CHARS = "!$&'()*+,/:;=?@[] "

    def test_colon_in_nss(self):
        u = parse("urn:example:a:b:c")
        assert u.nss == "a:b:c"

    def test_at_in_nss(self):
        u = parse("urn:example:user@domain.com")
        assert u.nss == "user@domain.com"

    def test_subdelims_all(self):
        u = parse("urn:example:!$&'()*+,;=")
        assert u.nss == "!$&'()*+,;="

    def test_space_detected(self):
        # Space must not appear unencoded in NSS
        with pytest.raises(Exception):
            parse("urn:example:hello world")

    def test_slash_in_nss(self):
        u = parse("urn:example:a/b")
        assert u.nss == "a/b"

    def test_question_mark_in_nss(self):
        u = parse("urn:example:a?b")
        assert u.nss == "a?b"

    def test_hash_in_nss(self):
        u = parse("urn:example:a#b")
        assert u.nss == "a#b"

    def test_brackets_in_nss(self):
        u = parse("urn:example:a[b]")
        assert u.nss == "a[b]"

    def test_percent_encoded_reserved(self):
        # Reserved chars should be percent-encoded if needed
        u = parse("urn:example:hello%20world")
        assert u.nss == "hello%20world"


class TestNamespaceSpecificSyntax:
    """RFC 8141 Section 3.2.3 namespace-specific syntax — AC6."""

    def test_equals_in_nss(self):
        u = parse("urn:example:a=b")
        assert u.nss == "a=b"

    def test_plus_in_nss(self):
        u = parse("urn:example:a+b")
        assert u.nss == "a+b"

    def test_semicolon_in_nss(self):
        u = parse("urn:example:a;b")
        assert u.nss == "a;b"

    def test_ampersand_in_nss(self):
        u = parse("urn:example:a&b")
        assert u.nss == "a&b"

    def test_dollar_in_nss(self):
        u = parse("urn:example:a$b")
        assert u.nss == "a$b"
