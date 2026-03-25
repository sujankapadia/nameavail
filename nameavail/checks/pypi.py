from .http import check_registry

PYPI_URL = "https://pypi.org/pypi/{name}/json"


def check_pypi(name: str) -> dict:
    return check_registry(
        url=PYPI_URL.format(name=name),
        extract=lambda data: {
            "summary": data["info"].get("summary", ""),
            "version": data["info"].get("version", ""),
        },
    )
