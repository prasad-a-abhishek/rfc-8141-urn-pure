# Test Coverage Map

This document maps each RFC 8141 acceptance criterion to its covering test(s).

## Test Coverage Table

| Criterion | Description | Test(s) |
|-----------|-------------|---------|
| AC1: URN prefix | `urn:` prefix (case-insensitive) | `test_parse_basic.py::TestParse::test_basic_valid`, `test_parse_basic.py::TestParse::test_uppercase_urn_prefix`, `test_parse_basic.py::TestParse::test_mixed_case_urn_prefix` |
| AC2: NID validation | 2-32 chars, letter/digit first, letter/digit/hyphen rest, normalized lowercase | `test_nid_validation.py::TestValidateNID::test_valid_2_char`, `test_nid_validation.py::TestValidateNID::test_valid_32_char`, `test_nid_validation.py::TestValidateNID::test_invalid_33_char`, `test_nid_validation.py::TestValidateNID::test_invalid_hyphen_start`, `test_nid_validation.py::TestValidateNID::test_invalid_underscore`, `test_parse_edge_cases.py::TestNIDBoundary::test_nid_2_chars_valid`, `test_parse_edge_cases.py::TestNIDBoundary::test_nid_32_chars_valid` |
| AC3: NSS validation | 1-255 chars, allowed character set | `test_nss_validation.py::TestValidateNSS::test_valid_ascii_nss`, `test_nss_validation.py::TestValidateNSS::test_valid_with_percent`, `test_nss_validation.py::TestValidateNSS::test_valid_question_mark`, `test_nss_validation.py::TestValidateNSS::test_valid_hash`, `test_nss_validation.py::TestValidateNSS::test_valid_brackets` |
| AC4: Scheme | URN is a URI scheme per RFC 3986 | `test_parse_basic.py::TestParse::test_basic_valid`, `test_parse_edge_cases.py::TestParseInvalidPrefix::test_missing_urn_prefix` |
| AC5: Reserved characters | Reserved chars in NSS detected | `test_reserved_chars.py::TestReservedChars::test_detect_question_mark`, `test_reserved_chars.py::TestReservedChars::test_detect_hash`, `test_reserved_chars.py::TestReservedChars::test_detect_slash`, `test_reserved_chars.py::TestReservedChars::test_detect_bracket_open`, `test_reserved_chars.py::TestReservedChars::test_detect_bracket_close`, `test_reserved_chars.py::TestReservedChars::test_all_reserved_detected` |
| AC6: Fragment support | Fragment handling in URN | `test_parse_basic.py::TestParse::test_with_fragment`, `test_parse_edge_cases.py::TestFragmentHandling::test_fragment_hash` |
| AC7: Construct | `construct()` builds valid URN strings | `test_construct.py::TestConstruct::test_basic_construct`, `test_construct.py::TestConstruct::test_construct_with_percent_encode`, `test_construct.py::TestConstruct::test_roundtrip_parse_construct` |
| AC8: ni: resolver | RFC 6920 NI hash extraction | `test_resolve.py::TestResolveNI::test_resolve_ni_basic`, `test_resolve.py::TestResolveNI::test_resolve_ni_passthrough`, `test_resolve.py::TestResolveNI::test_resolve_ni_unsupported_alg` |
| AC9: tag: resolver | RFC 4151 TAG date/authority/object | `test_resolve.py::TestResolveTag::test_resolve_tag_basic`, `test_resolve.py::TestResolveTag::test_resolve_tag_non_urn` |
| AC10: parse total | `parse()` never raises bare exceptions | `test_exceptions.py::TestParseExceptions::test_parse_non_string`, `test_exceptions.py::TestParseExceptions::test_parse_none`, `test_exceptions.py::TestParseExceptions::test_parse_empty`, `test_exceptions.py::TestParseExceptions::test_parse_whitespace`, `test_exceptions.py::TestParseExceptions::test_parse_invalid_prefix`, `test_exceptions.py::TestParseExceptions::test_parse_double_colon` |
| AC11: validate total | `validate()` always returns bool | `test_exceptions.py::TestValidateExceptions::test_validate_non_string`, `test_exceptions.py::TestValidateExceptions::test_validate_none`, `test_exceptions.py::TestValidateExceptions::test_validate_empty`, `test_exceptions.py::TestValidateExceptions::test_validate_invalid_urn` |
| AC12: percent-encode | RFC 3986 percent-encoding | `test_nss_validation.py::TestPercentEncode::test_basic`, `test_nss_validation.py::TestPercentEncode::test_unicode_chars` |
| AC13: percent-decode | RFC 3986 percent-decoding | `test_nss_validation.py::TestPercentDecode::test_uppercase_hex`, `test_nss_validation.py::TestPercentDecode::test_lowercase_hex`, `test_nss_validation.py::TestPercentDecode::test_mixed_hex`, `test_nss_validation.py::TestPercentDecode::test_all_special_chars`, `test_nss_validation.py::TestPercentDecode::test_space`, `test_nss_validation.py::TestPercentDecode::test_incomplete_percent`, `test_nss_validation.py::TestPercentDecode::test_invalid_hex_digit`, `test_nss_validation.py::TestPercentDecode::test_surrogate_pair_rejected`, `test_nss_validation.py::TestPercentDecode::test_requires_str` |
| AC14: NSS character set | All RFC 8141 allowed chars | `test_nss_validation.py::TestValidateNSS::test_valid_question_mark`, `test_nss_validation.py::TestValidateNSS::test_valid_hash`, `test_nss_validation.py::TestValidateNSS::test_valid_brackets`, `test_nss_validation.py::TestValidateNSS::test_valid_with_slash`, `test_nss_validation.py::TestValidateNSS::test_invalid_char_at` |
| AC15: CLI | Full CLI interface | `test_cli.py::TestCLI::test_parse_subcommand`, `test_cli.py::TestCLI::test_validate_subcommand`, `test_cli.py::TestCLI::test_construct_subcommand`, `test_cli.py::TestCLI::test_resolve_ni_subcommand`, `test_cli.py::TestCLI::test_resolve_tag_subcommand`, `test_cli.py::TestCLI::test_version`, `test_cli.py::TestCLI::test_subcommand_required`, `test_cli.py::TestCLI::test_parse_invalid_urn` |

## Test File Inventory

| File | Tests | Purpose |
|------|-------|---------|
| `test_parse_basic.py` | 20 | Happy-path parsing |
| `test_parse_edge_cases.py` | 32 | NID boundary, NSS empty, percent-encoded, fragment, double-colon |
| `test_nid_validation.py` | 19 | AC2 NID rules |
| `test_nss_validation.py` | 35 | AC3 NSS rules, percent-encode/decode |
| `test_reserved_chars.py` | 12 | AC5 reserved character detection |
| `test_construct.py` | 12 | AC7 construct() |
| `test_resolve.py` | 11 | AC8/AC9 ni:/tag: resolvers |
| `test_exceptions.py` | 28 | AC10/AC11 total-over-input |
| `test_cli.py` | 34 | AC15 CLI |
| **Total** | **203** | |

## Coverage Summary

- **Total tests**: 203
- **Passing**: 203 (100%)
- **Acceptance criteria covered**: 15/15
- **Coverage (library code)**: 94% (missing: `__main__.py` CLI entry not exercised by tests, some error-branch lines)

All acceptance criteria from the RFC 8141 specification have at least one dedicated test.
