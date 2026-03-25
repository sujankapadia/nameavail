import json
import shutil
import subprocess
import urllib.error
import urllib.request


def check_github_org(name: str) -> dict:
    url = f"https://github.com/{name}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", "nameavail/0.1")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"available": False}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"available": True}
        if e.code == 429:
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return {"available": False}
            except urllib.error.HTTPError as e2:
                if e2.code == 404:
                    return {"available": True}
                return {"available": None, "error": f"HTTP {e2.code}"}
        return {"available": None, "error": f"HTTP {e.code}"}
    except (urllib.error.URLError, TimeoutError):
        return {"available": None, "error": "connection failed"}


def check_github_repos(name: str) -> dict:
    if not shutil.which("gh"):
        return {"available": None, "error": "gh CLI not installed", "skipped": True}

    try:
        result = subprocess.run(
            ["gh", "search", "repos", name, "--limit", "5", "--json", "fullName,description"],
            capture_output=True,
            text=True,
            timeout=10,
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
