import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from .checks import ECOSYSTEMS, get_checks
from .formatters import format_json, format_single, format_table

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*$")
MAX_CONCURRENCY = 5


def validate_name(name: str) -> str | None:
    if not name:
        return "name cannot be empty"
    if len(name) > 100:
        return "name too long (max 100 characters)"
    if not NAME_PATTERN.match(name):
        return "name must be lowercase, start with a letter, and contain only letters, digits, hyphens, or underscores"
    return None


def check_name(name: str, ecosystem: str) -> dict:
    checks = get_checks(ecosystem)
    results = {}
    with ThreadPoolExecutor(max_workers=len(checks)) as pool:
        futures = {pool.submit(fn, name): label for label, fn in checks}
        for future in as_completed(futures):
            label = futures[future]
            try:
                results[label] = future.result()
            except Exception as e:
                results[label] = {"available": None, "error": str(e)}
    return results


def run(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="nameavail",
        description="Check project name availability across package registries, GitHub, and domains.",
    )
    parser.add_argument("names", nargs="+", help="One or more names to check")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    parser.add_argument(
        "--ecosystem", "-e",
        choices=ECOSYSTEMS,
        default="python",
        help="Package ecosystem to check (default: python)",
    )

    parsed = parser.parse_args(args)
    names: list[str] = parsed.names
    ecosystem: str = parsed.ecosystem

    # Validate all names
    for name in names:
        error = validate_name(name)
        if error:
            print(f"Error: '{name}' — {error}", file=sys.stderr)
            return 1

    # Run checks
    all_results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as pool:
        futures = {pool.submit(check_name, name, ecosystem): name for name in names}
        for future in as_completed(futures):
            name = futures[future]
            all_results[name] = future.result()

    # Preserve input order
    all_results = {name: all_results[name] for name in names}

    # Determine registry label for formatting
    checks = get_checks(ecosystem)
    registry_label = checks[0][0]

    # Output
    if parsed.json_output:
        print(format_json(all_results, single=len(names) == 1))
    elif len(names) == 1:
        print(format_single(names[0], all_results[names[0]]))
    else:
        print(format_table(all_results, registry_label=registry_label))

    return 0
