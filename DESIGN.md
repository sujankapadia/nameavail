# nameavail — Project Name Availability Checker

CLI tool that checks whether a project name is available across all the places that matter for an open source project: package registry, GitHub, and domains.

## What It Does

```bash
$ nameavail reelspec

  Name: reelspec

  ✓ PyPI          available
  ✓ GitHub org    available
  ✓ GitHub repos  no exact matches
  ✓ .com domain   available (no whois match)
  ✓ .ai domain    available (no DNS records)

$ nameavail reelspec clipspec cutflow

  Name         PyPI       GitHub org  GitHub repos  .com        .ai
  reelspec     ✓ avail    ✓ avail     none          ✓ avail     ✓ avail
  clipspec     ✓ avail    ✓ avail     1 similar     registered  ✓ avail
  cutflow      ✓ avail    ✗ taken     2 similar     registered  ✗ taken
```

## Checks and How They Work

### 1. PyPI (Python Package Index)

**Method**: HTTP request to `https://pypi.org/pypi/{name}/json`

- **404** → available
- **200** → taken (the response includes package metadata)

If taken, show the package summary so the user knows what it is:

```python
import urllib.request, json

def check_pypi(name: str) -> dict:
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read())
            return {
                "available": False,
                "summary": data["info"]["summary"],
                "version": data["info"]["version"],
            }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"available": True}
        raise
```

### 2. GitHub Organization / User

**Method**: HTTP request to `https://github.com/{name}`

- **404** → available (no org or user with that name)
- **200** → taken

```python
def check_github_org(name: str) -> dict:
    url = f"https://github.com/{name}"
    try:
        with urllib.request.urlopen(url) as resp:
            return {"available": False}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"available": True}
        raise
```

### 3. GitHub Repositories

**Method**: `gh search repos "{name}"` via subprocess, or GitHub API

This isn't a binary available/taken check — it shows whether similar repos exist. An exact match means someone already built something with that name. Similar matches are just informational.

```python
import subprocess, json

def check_github_repos(name: str) -> dict:
    result = subprocess.run(
        ["gh", "search", "repos", name, "--limit", "5", "--json", "fullName,description"],
        capture_output=True, text=True,
    )
    repos = json.loads(result.stdout) if result.returncode == 0 else []
    exact = [r for r in repos if r["fullName"].split("/")[1].lower() == name.lower()]
    return {
        "exact_matches": exact,
        "similar": repos,
    }
```

Requires `gh` CLI installed and authenticated.

### 4. .com Domain

**Method**: `whois {name}.com` via subprocess

- Look for "No match" or "NOT FOUND" in whois output → available
- If a `Domain Name:` line exists → registered

```python
def check_domain_com(name: str) -> dict:
    result = subprocess.run(
        ["whois", f"{name}.com"],
        capture_output=True, text=True,
    )
    output = result.stdout.lower()
    if "no match" in output or "not found" in output:
        return {"available": True}
    if "domain name:" in output.lower():
        return {"available": False}
    return {"available": None, "note": "whois inconclusive"}
```

**Reliability**: Good for .com. Whois servers for .com return clear "No match" responses for unregistered domains.

### 5. .ai Domain

**Method**: `dig +short {name}.ai A` via subprocess (DNS lookup)

- No records returned → likely available
- Records returned → taken (domain resolves to an IP)

```python
def check_domain_ai(name: str) -> dict:
    result = subprocess.run(
        ["dig", "+short", f"{name}.ai", "A"],
        capture_output=True, text=True,
    )
    has_records = bool(result.stdout.strip())
    if not has_records:
        # Also check NS records
        ns_result = subprocess.run(
            ["dig", "+short", f"{name}.ai", "NS"],
            capture_output=True, text=True,
        )
        has_records = bool(ns_result.stdout.strip())

    return {
        "available": not has_records,
        "note": "based on DNS — verify with a registrar before purchasing" if not has_records else None,
        "ip": result.stdout.strip() if has_records else None,
    }
```

**Why DNS instead of whois**: The .ai whois server returns `status: ACTIVE` for the entire TLD zone, not individual domains. This caused false negatives in our testing — every .ai domain appeared "registered" even when it wasn't. DNS (`dig`) correctly identified which domains were actually in use by checking whether they resolve to an IP address.

**Limitation**: A domain can be registered but have no DNS records (parked with no website). In that case, dig reports "available" but purchase would fail. In practice, most parked domains have DNS records pointing to a parking page, so dig catches the majority of cases. Always verify with a registrar (GoDaddy, Namecheap) before purchasing.

## CLI Design

### Single name check

```bash
nameavail reelspec
```

Output: vertical format with status icons and details.

### Bulk check

```bash
nameavail reelspec clipspec shotspec cutreel
```

Output: table format, one row per name.

### JSON output (agent-friendly)

```bash
nameavail reelspec --json
```

```json
{
  "name": "reelspec",
  "checks": {
    "pypi": {"available": true},
    "github_org": {"available": true},
    "github_repos": {"exact_matches": [], "similar": []},
    "domain_com": {"available": true},
    "domain_ai": {"available": true, "note": "based on DNS — verify with a registrar before purchasing"}
  }
}
```

Bulk JSON returns an array of these objects.

### Ecosystem flag (future)

```bash
nameavail reelspec --ecosystem python   # default: PyPI
nameavail reelspec --ecosystem node     # npm instead of PyPI
nameavail reelspec --ecosystem rust     # crates.io instead of PyPI
```

Start with Python only. The flag structure makes it extensible later.

## Dependencies

Minimal — standard library only where possible:

- `urllib.request` — PyPI and GitHub HTTP checks (stdlib)
- `subprocess` — whois, dig, gh CLI calls (stdlib)
- `json` — parsing responses (stdlib)
- `argparse` — CLI argument parsing (stdlib)

No pip dependencies required. The tool should be installable with `pip install nameavail` and have zero dependencies beyond Python 3.11+ and system tools (`whois`, `dig`, `gh`).

### System tool requirements

- `whois` — pre-installed on macOS, `apt install whois` on Linux
- `dig` — pre-installed on macOS, part of `dnsutils` on Linux
- `gh` — GitHub CLI, optional (GitHub repo search won't work without it, but other checks still run)

If a system tool is missing, skip that check gracefully and note it in the output.

## Project Structure

```
nameavail/
├── nameavail/
│   ├── __init__.py
│   ├── __main__.py        # CLI entry point
│   ├── cli.py             # argparse setup, output formatting
│   ├── checks/
│   │   ├── __init__.py
│   │   ├── pypi.py
│   │   ├── github.py
│   │   ├── domain.py      # .com (whois) and .ai (DNS)
│   └── formatters.py      # table and JSON output
├── pyproject.toml
├── README.md
├── LICENSE                 # MIT
└── DESIGN.md               # this file
```

### pyproject.toml entry point

```toml
[project.scripts]
nameavail = "nameavail.__main__:main"
```

So after `pip install nameavail`, the `nameavail` command is available on PATH.

## Output Formatting

### Single name (human-readable)

```
  Name: reelspec

  ✓ PyPI          available
  ✓ GitHub org    available
  ✓ GitHub repos  no exact matches
  ✓ .com domain   available
  ✓ .ai domain    available (verify with registrar)
```

### Single name (taken example)

```
  Name: namecheck

  ✗ PyPI          taken — "CLI tool to check the availability of a package name on PyPI and TestPyPI"
  ✓ GitHub org    available
  ~ GitHub repos  3 similar repos found
  ✗ .com domain   registered
  ✗ .ai domain    registered (198.50.252.64)
```

### Bulk (human-readable table)

```
  Name         PyPI     GitHub org  Repos     .com      .ai
  reelspec     ✓        ✓           none      ✓         ✓
  clipspec     ✓        ✓           1 similar registered ✓
  cutflow      ✓        ✗           2 similar registered ✗
```

### Status icons

- `✓` — available
- `✗` — taken
- `~` — inconclusive or similar matches found
- `-` — check skipped (missing tool)

## Performance

Run all checks for a single name in parallel (threads or asyncio) since they're all independent network calls. A single name check should complete in 2-3 seconds. Bulk checks should run names in parallel too, with a concurrency limit to avoid rate limiting.

## Error Handling

- Network timeouts: 10 second timeout per check, report as "check failed" not "available"
- Rate limiting: if PyPI or GitHub returns 429, back off and retry once
- Missing tools: skip the check, show `-` in output, note which tool is missing
- Invalid names: validate name format before checking (lowercase, alphanumeric + hyphens)
