import json
import urllib.error
import urllib.request


def check_pypi(name: str) -> dict:
    url = f"https://pypi.org/pypi/{name}/json"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return {
                "available": False,
                "summary": data["info"].get("summary", ""),
                "version": data["info"].get("version", ""),
            }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"available": True}
        if e.code == 429:
            # Retry once on rate limit
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                    return {
                        "available": False,
                        "summary": data["info"].get("summary", ""),
                        "version": data["info"].get("version", ""),
                    }
            except urllib.error.HTTPError as e2:
                if e2.code == 404:
                    return {"available": True}
                return {"available": None, "error": f"HTTP {e2.code}"}
        return {"available": None, "error": f"HTTP {e.code}"}
    except (urllib.error.URLError, TimeoutError):
        return {"available": None, "error": "connection failed"}
