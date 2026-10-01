# Benchmark: rfc8141-urn-pure vs stdlib urllib.parse
**Environment:** Python 3.11.15 | Linux | Iterations: 5 runs × 50 iterations × 10 calls/run

| Workload | Package | Mean (s) | P95 (s) | Speedup |
|----------|---------|----------|---------|---------|
| parse_basic | rfc8141-urn-pure | 0.000002 | 0.000002 | 7.31x (us slower) |
| parse_basic | stdlib-regex | 0.000000 | 0.000000 | — |
| parse_percent_encoded | rfc8141-urn-pure | 0.000002 | 0.000002 | 9.40x (us slower) |
| parse_percent_encoded | stdlib-regex | 0.000000 | 0.000000 | — |
| validate_basic | rfc8141-urn-pure | 0.000001 | 0.000001 | 2.77x (us slower) |
| validate_basic | stdlib-urllib | 0.000001 | 0.000001 | — |
| validate_complex | rfc8141-urn-pure | 0.000002 | 0.000002 | 3.42x (us slower) |
| validate_complex | stdlib-urllib | 0.000001 | 0.000001 | — |
| construct | rfc8141-urn-pure | 0.000001 | 0.000001 | 15.21x (us slower) |
| construct | stdlib-fstring | 0.000000 | 0.000000 | — |
| resolve_ni | rfc8141-urn-pure | 0.000005 | 0.000006 | 1.36x (us slower) |
| resolve_ni | stdlib-parse-extract | 0.000004 | 0.000004 | — |
