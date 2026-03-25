import json
import urllib.error
import urllib.request
from typing import Any, Callable

REQUEST_TIMEOUT = 10
USER_AGENT = "nameavail/0.1"


def fetch_json(url: str, headers: dict[str, str] | None = None) -> dict:
    """Make an HTTP GET request with retry on 429. Returns the parsed JSON response.

    Raises urllib.error.HTTPError on non-200/non-429 responses,
    and returns {"available": True} on 404.
    """
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", USER_AGENT)
    for key, value in (headers or {}).items():
        req.add_header(key, value)

    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise
        if e.code == 429:
            # Retry once on rate limit
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                return json.loads(resp.read())
        raise


def check_registry(
    url: str,
    extract: Callable[[dict[str, Any]], dict],
    headers: dict[str, str] | None = None,
) -> dict:
    """Generic registry availability check.

    Args:
        url: The registry API URL for the package.
        extract: A function that takes the parsed JSON response and returns
                 a dict with "summary" and "version" keys.
        headers: Optional extra HTTP headers.
    """
    try:
        data = fetch_json(url, headers)
        result = extract(data)
        return {"available": False, "summary": result["summary"], "version": result["version"]}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"available": True}
        return {"available": None, "error": f"HTTP {e.code}"}
    except (urllib.error.URLError, TimeoutError):
        return {"available": None, "error": "connection failed"}


def check_exists(url: str) -> dict:
    """Check if a URL returns 200 (taken) or 404 (available)."""
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as _:
            return {"available": False}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"available": True}
        if e.code == 429:
            try:
                with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as _:
                    return {"available": False}
            except urllib.error.HTTPError as e2:
                if e2.code == 404:
                    return {"available": True}
                return {"available": None, "error": f"HTTP {e2.code}"}
        return {"available": None, "error": f"HTTP {e.code}"}
    except (urllib.error.URLError, TimeoutError):
        return {"available": None, "error": "connection failed"}
