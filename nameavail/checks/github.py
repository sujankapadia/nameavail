import json
import shutil
import subprocess

from .http import REQUEST_TIMEOUT, check_exists

GITHUB_URL = "https://github.com/{name}"


def check_github_org(name: str) -> dict:
    return check_exists(GITHUB_URL.format(name=name))


def check_github_repos(name: str) -> dict:
    if not shutil.which("gh"):
        return {"available": None, "error": "gh CLI not installed", "skipped": True}

    try:
        result = subprocess.run(
            ["gh", "search", "repos", name, "--limit", "5", "--json", "fullName,description"],
            capture_output=True,
            text=True,
            timeout=REQUEST_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return {"available": None, "error": "gh search timed out"}

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "auth" in stderr.lower() or "login" in stderr.lower():
            return {"available": None, "error": "gh not authenticated", "skipped": True}
        return {"available": None, "error": f"gh failed: {stderr[:80]}"}

    try:
        repos = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError:
        return {"available": None, "error": "failed to parse gh output"}

    exact = [r for r in repos if r["fullName"].split("/")[1].lower() == name.lower()]
    return {
        "exact_matches": exact,
        "similar": repos,
    }
