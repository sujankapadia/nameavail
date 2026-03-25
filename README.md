# nameavail

CLI tool that checks whether a project name is available across package registries, GitHub, and domains.

## Install

```bash
pip install nameavail
```

Requires Python 3.11+. No pip dependencies.

## Usage

```bash
# Check a single name
nameavail myproject

# Check against npm or crates.io instead of PyPI
nameavail myproject --ecosystem node
nameavail myproject -e rust

# Check multiple names at once
nameavail foo bar baz

# Machine-readable JSON output
nameavail myproject --json
```

### Single name output

```
  Name: reelspec

  ✓ PyPI          available
  ✓ GitHub org    available
  ✓ GitHub repos  no exact matches
  ✓ .com domain   available
  ✓ .ai domain    available (based on DNS — verify with a registrar before purchasing)
```

### Multiple names output

```
  Name         PyPI       GitHub org  Repos        .com        .ai
  reelspec     ✓ avail    ✓ avail     none         ✓ avail     ✓ avail
  flask        ✗ taken    ✗ taken     exact match  registered  registered
```

### JSON output

```bash
nameavail reelspec --json
```

```json
{
  "name": "reelspec",
  "checks": {
    "PyPI": {"available": true},
    "GitHub org": {"available": true},
    "GitHub repos": {"exact_matches": [], "similar": []},
    ".com domain": {"available": true},
    ".ai domain": {"available": true, "note": "based on DNS — verify with a registrar before purchasing"}
  }
}
```

## Checks

| Check | Method | Ecosystem |
|-------|--------|-----------|
| **PyPI** | HTTP request to pypi.org | `--ecosystem python` (default) |
| **npm** | HTTP request to registry.npmjs.org | `--ecosystem node` |
| **crates.io** | HTTP request to crates.io API | `--ecosystem rust` |
| **GitHub org** | HTTP request to github.com/{name} | All |
| **GitHub repos** | `gh search repos` via CLI | All |
| **.com domain** | `whois` lookup | All |
| **.ai domain** | DNS lookup via `dig` | All |

## System requirements

| Tool | Used for | Required? |
|------|----------|-----------|
| `whois` | .com domain check | Optional (pre-installed on macOS) |
| `dig` | .ai domain check | Optional (pre-installed on macOS, `dnsutils` on Linux) |
| `gh` | GitHub repo search | Optional (install from [cli.github.com](https://cli.github.com)) |

If a tool is missing, that check is skipped gracefully — all other checks still run.

## Development

```bash
git clone https://github.com/sujankapadia/nameavail.git
cd nameavail
pip install -e .

# Run unit tests (no network)
pytest tests/ -m "not integration"

# Run integration tests (hits real APIs)
pytest tests/test_integration.py

# Run all tests
pytest tests/
```

## License

MIT
