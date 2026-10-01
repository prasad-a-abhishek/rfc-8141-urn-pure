# Changelog

All notable changes to this project will be documented in this file.

## 0.1.0 — 2026-10-01

### Added

- `parse(urn)` — parse URN strings into `Urn` named tuples with NID, NSS, decoded NSS, and RQN
- `validate(urn)` — check URN validity, always returns `bool` (total over input)
- `construct(nid, nss, percent_encode=False)` — build URN strings from components
- `resolve_ni(urn)` — RFC 6920 NI (Named Information) URN hash extraction
- `resolve_tag(urn)` — RFC 4151 TAG (Atom Archive) URN date/authority/object parsing
- `percent_encode(s)` / `percent_decode(s)` — RFC 3986 percent-encoding utilities
- Full exception hierarchy: `URNParsingError`, `URNValidationError`, `URNEncodingError`, `URNResolveError`
- CLI with `parse`, `validate`, `construct`, `resolve-ni`, `resolve-tag` subcommands
- 203 tests covering RFC 8141 compliance, edge cases, error paths, and CLI
