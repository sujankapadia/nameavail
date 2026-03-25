import shutil
import subprocess

from .http import REQUEST_TIMEOUT


def check_domain_com(name: str) -> dict:
    if not shutil.which("whois"):
        return {"available": None, "error": "whois not installed", "skipped": True}

    domain = f"{name}.com"
    try:
        result = subprocess.run(
            ["whois", domain],
            capture_output=True,
            text=True,
            timeout=REQUEST_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return {"available": None, "error": "whois timed out"}

    output = result.stdout.lower()
    if "no match" in output or "not found" in output:
        return {"available": True}
    if "domain name:" in output:
        return {"available": False}
    return {"available": None, "note": "whois inconclusive"}


def check_domain_ai(name: str) -> dict:
    if not shutil.which("dig"):
        return {"available": None, "error": "dig not installed", "skipped": True}

    domain = f"{name}.ai"
    try:
        result = subprocess.run(
            ["dig", "+short", domain, "A"],
            capture_output=True,
            text=True,
            timeout=REQUEST_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return {"available": None, "error": "dig timed out"}

    has_records = bool(result.stdout.strip())

    if not has_records:
        try:
            ns_result = subprocess.run(
                ["dig", "+short", domain, "NS"],
                capture_output=True,
                text=True,
                timeout=REQUEST_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return {"available": None, "error": "dig timed out"}
        has_records = bool(ns_result.stdout.strip())

    if has_records:
        return {
            "available": False,
            "ip": result.stdout.strip() or None,
        }
    return {
        "available": True,
        "note": "based on DNS — verify with a registrar before purchasing",
    }
