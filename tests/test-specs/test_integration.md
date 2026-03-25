# test_integration Spec

App: `nameavail`
Test: `tests/test_integration.py`

## Single name — available

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| INT-1 | Single available name (python) | Exit 0, all checks return results, human-readable output contains name | Core single-name flow broken end-to-end |
| INT-2 | Single available name (node) | Exit 0, npm check runs instead of PyPI | Ecosystem flag doesn't actually switch the registry |
| INT-3 | Single available name (rust) | Exit 0, crates.io check runs instead of PyPI | Ecosystem flag doesn't actually switch the registry |

## Single name — taken

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| INT-4 | Known taken name "flask" (python) | PyPI shows taken with summary, GitHub org taken | Taken packages incorrectly reported as available |
| INT-5 | Known taken name "express" (node) | npm shows taken with summary | npm check returns wrong result for known packages |
| INT-6 | Known taken name "serde" (rust) | crates.io shows taken with summary | crates.io check returns wrong result for known crates |

## Bulk names

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| INT-7 | Multiple names in table format | Exit 0, all names present in output, table has header row | Bulk output garbled or missing names |

## JSON output

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| INT-8 | Single name --json | Valid JSON with "name" and "checks" keys, all 5 check keys present | JSON consumers get malformed or incomplete output |
| INT-9 | Multiple names --json | Valid JSON array, each element has "name" and "checks" | Bulk JSON consumers get wrong structure |

## Error handling

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| INT-10 | Invalid name (uppercase) | Exit 1, error message on stderr | Invalid input not caught, confusing downstream errors |
