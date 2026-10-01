"""Test NSS validation per RFC 8141 Section 3."""
import pytest
from rfc8141_urn_pure._nss import validate_nss, percent_decode, percent_encode


class TestValidateNSS:
    """NSS validation — AC3."""

    def test_valid_simple(self):
        assert validate_nss("hello") is True

    def test_valid_1_char(self):
        assert validate_nss("a") is True

    def test_valid_255_chars(self):
        nss = "a" * 255
        assert validate_nss(nss) is True

    def test_invalid_256_chars(self):
        nss = "a" * 256
        assert validate_nss(nss) is False

    def test_invalid_empty(self):
        assert validate_nss("") is False

    def test_percent_encoded_valid(self):
        assert validate_nss("hello%20world") is True

    def test_percent_encoded_uppercase_hex(self):
        assert validate_nss("%41%42%43") is True  # ABC

    def test_percent_encoded_lowercase_hex(self):
        assert validate_nss("%61%62%63") is True  # abc

    def test_percent_encoded_invalid_hex(self):
        assert validate_nss("%GG") is False

    def test_incomplete_percent_encoding(self):
        assert validate_nss("hello%") is False
        assert validate_nss("hello%2") is False

    def test_embedded_percent_valid(self):
        assert validate_nss("%41%42") is True

    def test_unreserved_chars(self):
        assert validate_nss("abc-._~def") is True

    def test_subdelims_chars(self):
        assert validate_nss("!$&'()*+,;=") is True

    def test_colon_allowed(self):
        assert validate_nss("a:b:c") is True

    def test_at_allowed(self):
        assert validate_nss("user@host") is True

    def test_space_not_allowed(self):
        assert validate_nss("hello world") is False

    def test_non_string_rejected(self):
        assert validate_nss(None) is False
        assert validate_nss(123) is False


class TestPercentDecode:
    """Percent-decoding per RFC 3986 Section 2.4 — AC4."""

    def test_simple_decode(self):
        assert percent_decode("hello%20world") == "hello world"

    def test_uppercase_hex(self):
        assert percent_decode("%41%42%43") == "ABC"

    def test_lowercase_hex(self):
        assert percent_decode("%61%62%63") == "abc"

    def test_mixed_hex(self):
        # %4A = J (74), %6b = k (107)
        assert percent_decode("%4A%6b") == "Jk"

    def test_all_special_chars(self):
        assert percent_decode("%21%23%24") == "!#$"

    def test_space(self):
        assert percent_decode("%20") == " "

    def test_incomplete_percent(self):
        with pytest.raises(Exception):
            percent_decode("hello%")

    def test_invalid_hex_digit(self):
        with pytest.raises(Exception):
            percent_decode("%ZZ")

    def test_surrogate_pair_rejected(self):
        # U+D800 encoded as UTF-8 is ED A0 80 — invalid UTF-8 (lone surrogate)
        with pytest.raises(Exception):
            percent_decode("%ED%A0%80")

    def test_requires_str(self):
        with pytest.raises(Exception):
            percent_decode(None)


class TestPercentEncode:
    """Percent-encoding for NSS construction."""

    def test_encode_simple(self):
        assert percent_encode("hello world") == "hello%20world"

    def test_encode_already_allowed(self):
        assert percent_encode("abc-._~") == "abc-._~"

    def test_encode_subdelims(self):
        assert percent_encode("!$&'()*+,;=") == "!$&'()*+,;="

    def test_encode_colon_at(self):
        assert percent_encode("a:b@c") == "a:b@c"

    def test_encode_space(self):
        assert percent_encode("a b") == "a%20b"

    def test_encode_unicode(self):
        # UTF-8 encoding of é is C3 A9
        assert percent_encode("café") == "caf%C3%A9"

    def test_encode_empty(self):
        assert percent_encode("") == ""
