"""Test parse edge cases — NID boundary, NSS empty, RFC 8141 Section 3."""
import pytest
from rfc8141_urn_pure import parse, Urn, URNParsingError, URNValidationError


class TestNIDBoundary:
    """NID boundary cases — AC2."""

    def test_nid_2_chars_valid(self):
        u = parse("urn:ab:test")
        assert u.nid == "ab"

    def test_nid_3_chars_valid(self):
        u = parse("urn:abc:test")
        assert u.nid == "abc"

    def test_nid_31_chars_valid(self):
        # 32 total: 1 first + 30 more + 1 last
        nid = "a" + "b" * 30
        assert len(nid) == 31
        u = parse(f"urn:{nid}:test")
        assert u.nid == nid

    def test_nid_32_chars_valid(self):
        nid = "a" + "b" * 31
        assert len(nid) == 32
        u = parse(f"urn:{nid}:test")
        assert u.nid == nid

    def test_nid_1_char_invalid(self):
        with pytest.raises(URNValidationError):
            parse("urn:a:test")

    def test_nid_33_chars_invalid(self):
        nid = "a" + "b" * 32
        with pytest.raises(URNValidationError):
            parse(f"urn:{nid}:test")

    def test_nid_100_chars_invalid(self):
        nid = "a" * 100
        with pytest.raises(URNValidationError):
            parse(f"urn:{nid}:test")

    def test_nid_starts_with_hyphen_invalid(self):
        with pytest.raises(URNValidationError):
            parse("urn:-ab:test")

    def test_nid_contains_hyphen_ok(self):
        u = parse("urn:a-b-c:test")
        assert u.nid == "a-b-c"

    def test_nid_ends_with_hyphen_ok(self):
        u = parse("urn:ab-:test")
        assert u.nid == "ab-"

    def test_nid_multiple_hyphens(self):
        u = parse("urn:a-b-c-d-e:test")
        assert u.nid == "a-b-c-d-e"


class TestNSSEdgeCases:
    """NSS edge cases — AC3."""

    def test_nss_single_char(self):
        u = parse("urn:example:a")
        assert u.nss == "a"

    def test_nss_254_chars_valid(self):
        nss = "a" * 254
        u = parse(f"urn:example:{nss}")
        assert len(u.nss) == 254

    def test_nss_255_chars_valid(self):
        nss = "a" * 255
        u = parse(f"urn:example:{nss}")
        assert len(u.nss) == 255

    def test_nss_256_chars_invalid(self):
        nss = "a" * 256
        with pytest.raises(URNValidationError):
            parse(f"urn:example:{nss}")

    def test_nss_empty_after_colon_invalid(self):
        with pytest.raises(URNValidationError):
            parse("urn:example:")

    def test_nss_only_percent_encoded(self):
        u = parse("urn:example:%20")
        assert u.nss == "%20"

    def test_nss_100k_chars_oversized(self):
        nss = "a" * 100_000
        with pytest.raises(URNValidationError):
            parse(f"urn:example:{nss}")


class TestReservedCharsDetection:
    """Reserved character detection — AC5."""

    def test_reserved_colon_in_nss(self):
        # Colons are allowed in NSS
        u = parse("urn:example:a:b")
        assert u.nss == "a:b"

    def test_reserved_at_in_nss(self):
        u = parse("urn:example:user@domain")
        assert u.nss == "user@domain"

    def test_reserved_ampersand_in_nss(self):
        u = parse("urn:example:a&b")
        assert u.nss == "a&b"

    def test_reserved_equals_in_nss(self):
        u = parse("urn:example:a=b")
        assert u.nss == "a=b"

    def test_reserved_plus_in_nss(self):
        u = parse("urn:example:a+b")
        assert u.nss == "a+b"


class TestPercentDecoding:
    """Percent-decoding edge cases — AC4."""

    def test_percent_00(self):
        u = parse("urn:example:hello%00world")
        assert u.nss_decoded == "hello\x00world"

    def test_percent_XX_invalid(self):
        with pytest.raises(Exception):  # URNEncodingError or URNParsingError
            parse("urn:example:hello%XXworld")

    def test_percent_u_uppercase(self):
        u = parse("urn:example:%41%42%43")
        assert u.nss_decoded == "ABC"

    def test_percent_u_lowercase(self):
        u = parse("urn:example:%61%62%63")
        assert u.nss_decoded == "abc"

    def test_surrogate_pair_rejected(self):
        # U+D800 encoded as UTF-8 is ED A0 80 — invalid UTF-8 (lone surrogate)
        with pytest.raises(Exception):
            parse("urn:example:hello%ED%A0%80world")


class TestParseInvalidPrefix:
    """Invalid URN prefix cases."""

    def test_missing_urn_prefix(self):
        with pytest.raises(URNParsingError):
            parse("isbn:0451450523")

    def test_uppercase_URN_prefix(self):
        # urn: prefix is case-insensitive per RFC 8141
        u = parse("URN:isbn:0451450523")
        assert u.nid == "isbn"

    def test_mixed_case_URN_prefix(self):
        u = parse("Urn:isbn:0451450523")
        assert u.nid == "isbn"

    def test_no_colon_after_nid(self):
        with pytest.raises(URNValidationError):
            parse("urn:isbn0451450523")

    def test_double_colon(self):
        with pytest.raises(URNValidationError):
            parse("urn:isbn::0451450523")

    def test_empty_urn(self):
        with pytest.raises(URNParsingError):
            parse("")

    def test_whitespace_urn(self):
        with pytest.raises(URNParsingError):
            parse("   ")
