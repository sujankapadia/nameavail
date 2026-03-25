from .http import check_registry

CRATES_URL = "https://crates.io/api/v1/crates/{name}"


def check_crates(name: str) -> dict:
    return check_registry(
        url=CRATES_URL.format(name=name),
        extract=lambda data: {
            "summary": data.get("crate", {}).get("description", ""),
            "version": data.get("crate", {}).get("max_version", ""),
        },
    )
