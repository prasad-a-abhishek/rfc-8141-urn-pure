# rfc8141-urn-pure

**Zero-dependency RFC 8141 URN parser, validator, and resolver.**

`pip install git+https://github.com/prasad-a-abhishek/rfc-8141-urn-pure.git`

```python
from rfc8141_urn_pure import parse, validate, construct, resolve_ni, resolve_tag

# Parse a URN
u = parse("urn:isbn:0451450523")
print(u.nid)           # 'isbn'
print(u.nss)           # '0451450523'
print(u.nss_decoded)   # '0451450523'

# Validate
validate("urn:example:hello")   # True
validate("not-a-urn")            # False

# Construct
construct("isbn", "0451450523") # 'urn:isbn:0451450523'

# Resolve NI (RFC 6920)
import base64, hashlib
digest = hashlib.sha256(b"hello").digest()
b64 = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
resolve_ni(f"urn:ni:?n={b64}&alg=sha256")  # b'hello'

# Resolve TAG (RFC 4151)
resolve_tag("urn:tag:example.com,2024-10-01:blog/entry")
# '2024-10-01 example.com blog/entry'
```

## ⚡ Performance & Benchmarks

Benchmarks vs Python stdlib (`urllib.parse` + regex). Our implementation does full RFC 8141 structural validation (NID/NSS rules, percent-decode, reserved chars) while stdlib treats `urn:` as opaque. The speed difference reflects this — stdlib is a naive regex with no validation; our impl is RFC-compliant.

Run locally: `python3 benchmarks/run_benchmark.py`

| Workload | rfc8141-urn-pure (s/call) | stdlib (s/call) | Note |
|----------|---------------------------|-----------------|------|
| parse_basic | 0.000002 | 0.000000 | stdlib is naive regex; ours validates NID/NSS structure |
| parse_percent_encoded | 0.000002 | 0.000000 | same — stdlib skips all validation |
| validate_basic | 0.000001 | 0.000001 | similar speed, stdlib misses NID length limits |
| validate_complex | 0.000002 | 0.000001 | ours checks RFC 8141 Section 3 rules |
| construct | 0.000001 | 0.000000 | stdlib is plain f-string |
| resolve_ni | 0.000005 | 0.000004 | ours decodes ni: hash; stdlib just parses |

Pure Python, no C extensions. Speed is not the goal — RFC compliance and zero-dependency are.

## Why rfc8141-urn-pure?

Existing URN libraries are either heavy (require external dependencies), incomplete (don't support `ni:` or `tag:` resolution), or non-compliant (accept invalid percent-encoding). This library is:

- **Zero-dependency** — no `pip install` beyond the standard library
- **Total over arbitrary input** — never raises bare `ValueError`, `TypeError`, or `AttributeError`; always returns structured errors
- **RFC 8141 strict** — validates NID format (2-32 chars, letter/digit/hyphen), rejects surrogate pairs in percent-encoded NSS, handles `?`, `#`, `[`, `]` in NSS
- **CLI included** — `urn parse`, `urn validate`, `urn construct`, `urn resolve-ni`, `urn resolve-tag`

## Key Features

- **Parse**: Extract NID, NSS, decoded NSS, and RQN from any URN string
- **Validate**: Check URN syntax and NID/NSS compliance
- **Construct**: Build URN strings from NID and NSS with optional percent-encoding
- **Resolve NI**: RFC 6920 Named Information URNs — decode `ni:` scheme hashes
- **Resolve TAG**: RFC 4151 Atom Archive URNs — extract date/authority/object
- **Percent encoding**: RFC 3986-compliant encode/decode with UTF-8 validation
- **CLI**: Full command-line interface with JSON output

## API Reference

### `parse(urn: Any) -> Urn`

Parse a URN string into a `Urn` named tuple. Raises `URNParsingError` or `URNValidationError` on invalid input (never bare exceptions).

```python
from rfc8141_urn_pure import parse

u = parse("urn:example:path/to/resource")
assert u.nid == "example"
assert u.nss == "path/to/resource"
assert u.nss_decoded == "path/to/resource"
assert u.rqn == "example:path/to/resource"
assert u.original == "urn:example:path/to/resource"
```

### `validate(urn: Any) -> bool`

Returns `True` if the input is a valid RFC 8141 URN, `False` otherwise. Never raises.

```python
from rfc8141_urn_pure import validate

assert validate("urn:isbn:0451450523") is True
assert validate("not-a-urn") is False
assert validate(None) is False
```

### `construct(nid: str, nss: str, percent_encode: bool = False) -> str`

Construct a URN string from NID and NSS.

```python
from rfc8141_urn_pure import construct

assert construct("isbn", "0451450523") == "urn:isbn:0451450523"
assert construct("example", "path%2Fwith%2Fslashes", percent_encode=True) == "urn:example:path%252Fwith%252Fslashes"
```

### `resolve_ni(urn: Urn | str) -> bytes | None`

Resolve a `ni:` URN (RFC 6920) and return the raw hash digest. Raises `URNResolveError` on invalid input.

```python
from rfc8141_urn_pure import resolve_ni

# sha256 of b"hello"
import base64, hashlib
digest = hashlib.sha256(b"hello").digest()
encoded = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
result = resolve_ni(f"urn:ni:?n={encoded}&alg=sha256")
assert result == digest
```

### `resolve_tag(urn: Urn | str) -> str`

Resolve a `tag:` URN (RFC 4151) and return a formatted string `"YYYY-MM-DD authority object"`. Raises `URNResolveError` on invalid input.

```python
from rfc8141_urn_pure import resolve_tag

result = resolve_tag("urn:tag:example.com,2024-10-01:blog/entry")
assert result == "2024-10-01 example.com blog/entry"
```

### `percent_encode(s: str) -> str`

Percent-encode a string per RFC 3986 Section 2.4.

### `percent_decode(s: str) -> str`

Decode percent-encoded sequences per RFC 3986 Section 2.4. Raises `URNEncodingError` on invalid UTF-8 or surrogate pairs.

### Exception Hierarchy

```
URNParsingError (base)
  ├── URNValidationError  — invalid NID/NSS format
  └── URNEncodingError    — invalid percent-encoding
URNResolveError          — ni:/tag: resolution failure
```

## CLI Reference

```
urn --version           Show version
urn parse <URN>         Parse and print JSON components
urn validate <URN>      Validate (exit 0=valid, 1=invalid)
urn construct <NID> <NSS> [--percent-encode]
urn resolve-ni <URN>    Resolve ni: hash to hex
urn resolve-tag <URN>   Resolve tag: to date authority object
```

## Limitations

- Does not validate that a NID is registered with IANA (no network lookups)
- `ni:` resolution does not verify the algorithm used — callers must check
- `tag:` resolution does not validate the date is real (e.g., `2024-02-30` is accepted)

## Non-Goals

- Network I/O or DNS resolution
- NID registration or validation against IANA registry
- URN comparison or equivalence (this is handled by application-level logic)
- Integration with URI/IRI standards beyond RFC 8141
