import json


def _status_icon(result: dict) -> str:
    avail = result.get("available")
    if avail is True:
        return "\u2713"
    if avail is False:
        return "\u2717"
    if result.get("skipped"):
        return "-"
    # For repo checks without an "available" key
    if "exact_matches" in result:
        if result["exact_matches"]:
            return "\u2717"
        if result["similar"]:
            return "~"
        return "\u2713"
    return "~"


def _status_text(check_name: str, result: dict) -> str:
    if result.get("error"):
        if result.get("skipped"):
            return f"skipped ({result['error']})"
        return f"check failed ({result['error']})"

    if check_name == "GitHub repos":
        exact = result.get("exact_matches", [])
        similar = result.get("similar", [])
        if exact:
            names = ", ".join(r["fullName"] for r in exact[:3])
            return f"exact match: {names}"
        if similar:
            return f"{len(similar)} similar repo{'s' if len(similar) != 1 else ''} found"
        return "no exact matches"

    avail = result.get("available")
    if avail is True:
        parts = ["available"]
        if result.get("note"):
            parts.append(f"({result['note']})")
        return " ".join(parts)
    if avail is False:
        parts = ["taken" if check_name != ".com domain" and check_name != ".ai domain" else "registered"]
        if result.get("summary"):
            parts.append(f'\u2014 "{result["summary"]}"')
        if result.get("ip"):
            parts.append(f"({result['ip']})")
        return " ".join(parts)
    if result.get("note"):
        return result["note"]
    return "inconclusive"


def _short_status(check_name: str, result: dict) -> str:
    if result.get("error"):
        if result.get("skipped"):
            return "skipped"
        return "error"

    if check_name == "GitHub repos":
        exact = result.get("exact_matches", [])
        similar = result.get("similar", [])
        if exact:
            return "exact match"
        if similar:
            return f"{len(similar)} similar"
        return "none"

    avail = result.get("available")
    if avail is True:
        return "\u2713 avail"
    if avail is False:
        if check_name in (".com domain", ".ai domain"):
            return "registered"
        return "\u2717 taken"
    return "?"


def format_single(name: str, results: dict) -> str:
    lines = [f"  Name: {name}", ""]
    for check_name, result in results.items():
        icon = _status_icon(result)
        text = _status_text(check_name, result)
        lines.append(f"  {icon} {check_name:<14} {text}")
    return "\n".join(lines)


def format_table(all_results: dict[str, dict]) -> str:
    headers = ["Name", "PyPI", "GitHub org", "Repos", ".com", ".ai"]
    check_keys = ["PyPI", "GitHub org", "GitHub repos", ".com domain", ".ai domain"]
    short_headers = ["Name", "PyPI", "GitHub org", "Repos", ".com", ".ai"]

    rows = []
    for name, results in all_results.items():
        row = [name]
        for key in check_keys:
            row.append(_short_status(key, results.get(key, {})))
        rows.append(row)

    # Calculate column widths
    col_widths = [len(h) for h in short_headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # Format
    lines = []
    header_line = "  " + "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(short_headers))
    lines.append(header_line)
    for row in rows:
        line = "  " + "  ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
        lines.append(line)
    return "\n".join(lines)


def format_json(all_results: dict[str, dict], single: bool = False) -> str:
    if single:
        name = next(iter(all_results))
        obj = {"name": name, "checks": all_results[name]}
        return json.dumps(obj, indent=2)
    items = [{"name": name, "checks": checks} for name, checks in all_results.items()]
    return json.dumps(items, indent=2)
