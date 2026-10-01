"""Test NID validation per RFC 8141 Section 2.1."""
import pytest
from rfc8141_urn_pure._nid import validate_nid, normalize_nid


class TestValidateNID:
    """RFC 8141 NID validation — AC2."""

    def test_valid_2_char(self):
        assert validate_nid("ab") is True

    def test_valid_3_char(self):
        assert validate_nid("abc") is True

    def test_valid_32_char(self):
        nid = "a" + "b" * 30 + "c"
        assert len(nid) == 32
        assert validate_nid(nid) is True

    def test_invalid_1_char(self):
        assert validate_nid("a") is False

    def test_invalid_33_char(self):
        nid = "a" + "b" * 32
        assert validate_nid(nid) is False

    def test_invalid_empty(self):
        assert validate_nid("") is False

    def test_starts_with_letter(self):
        assert validate_nid("abc") is True

    def test_starts_with_digit(self):
        assert validate_nid("1abc") is True

    def test_starts_with_hyphen_invalid(self):
        assert validate_nid("-abc") is False

    def test_contains_hyphen_middle(self):
        assert validate_nid("a-b") is True

    def test_contains_hyphen_end(self):
        assert validate_nid("ab-") is True

    def test_uppercase_letters_allowed(self):
        assert validate_nid("ABC") is True

    def test_mixed_case_allowed(self):
        assert validate_nid("Abc-Def") is True

    def test_normalized_to_lowercase(self):
        assert normalize_nid("ABC") == "abc"

    def test_special_chars_rejected(self):
        assert validate_nid("ab@cd") is False
        assert validate_nid("ab cd") is False
        assert validate_nid("ab:cd") is False

    def test_non_string_rejected(self):
        assert validate_nid(None) is False
        assert validate_nid(123) is False
        assert validate_nid([]) is False
