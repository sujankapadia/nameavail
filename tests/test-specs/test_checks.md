# test_checks Spec

Source: `nameavail/checks/`
Test: `tests/test_checks.py`

## check_pypi(name)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| P1 | PyPI returns 404 | Returns available=True | User told name is taken when it's free |
| P2 | PyPI returns 200 with package metadata | Returns available=False with summary and version | User told name is available when it's taken, potential naming collision |
| P3 | PyPI returns 429 then 200 on retry | Returns available=False | Rate-limited users see false errors instead of results |
| P4 | Network unreachable | Returns available=None with error message | Unhandled exception crashes the CLI |

## check_npm(name)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| N1 | npm registry returns 404 | Returns available=True | User told name is taken when it's free |
| N2 | npm registry returns 200 with package metadata | Returns available=False with summary and version | User told name is available when it's taken |

## check_crates(name)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| CR1 | crates.io returns 404 | Returns available=True | User told crate name is taken when it's free |
| CR2 | crates.io returns 200 with crate metadata | Returns available=False with summary and version | User told crate name is available when it's taken |

## check_github_org(name)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| G1 | GitHub returns 404 | Returns available=True | User told org/user name is taken when it's free |
| G2 | GitHub returns 200 | Returns available=False | User told org/user name is available when it's taken |
| G3 | GitHub returns 500 | Returns available=None with error | Unhandled exception crashes the CLI |

## check_github_repos(name)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| GR1 | gh CLI not installed | Returns skipped with error message | Unhandled exception instead of graceful skip |
| GR2 | gh returns empty results | Returns empty exact_matches and similar | User misled about repo landscape |
| GR3 | gh returns repos with exact match | exact_matches contains the matching repo | User misses that an identically-named repo exists |
| GR4 | gh search times out | Returns available=None with timeout error | Unhandled exception crashes the CLI |
| GR5 | gh not authenticated | Returns skipped with auth error | Unhandled exception instead of graceful skip |

## check_domain_com(name)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| DC1 | whois output contains "No match" | Returns available=True | User told domain is registered when it's free |
| DC2 | whois output contains "Domain Name:" | Returns available=False | User told domain is free when it's registered |
| DC3 | whois output is ambiguous | Returns available=None with inconclusive note | False positive/negative on domain availability |
| DC4 | whois not installed | Returns skipped | Unhandled exception instead of graceful skip |
| DC5 | whois times out | Returns error with timeout message | Unhandled exception crashes the CLI |

## check_domain_ai(name)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| DA1 | dig returns no A or NS records | Returns available=True with registrar note | User told domain is taken when it's free |
| DA2 | dig returns A record with IP | Returns available=False with IP | User told domain is free when it's taken |
| DA3 | dig returns no A record but has NS record | Returns available=False | Domains with NS-only config reported as available |
| DA4 | dig not installed | Returns skipped | Unhandled exception instead of graceful skip |
