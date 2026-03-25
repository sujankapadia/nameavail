from .http import check_registry

NPM_URL = "https://registry.npmjs.org/{name}"


def check_npm(name: str) -> dict:
    return check_registry(
        url=NPM_URL.format(name=name),
        extract=lambda data: {
            "summary": data.get("description", ""),
            "version": data.get("dist-tags", {}).get("latest", ""),
        },
    )
