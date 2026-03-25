from .pypi import check_pypi
from .npm import check_npm
from .crates import check_crates
from .github import check_github_org, check_github_repos
from .domain import check_domain_com, check_domain_ai

REGISTRY_CHECKS = {
    "python": ("PyPI", check_pypi),
    "node": ("npm", check_npm),
    "rust": ("crates.io", check_crates),
}

COMMON_CHECKS = [
    ("GitHub org", check_github_org),
    ("GitHub repos", check_github_repos),
    (".com domain", check_domain_com),
    (".ai domain", check_domain_ai),
]

ECOSYSTEMS = list(REGISTRY_CHECKS.keys())


def get_checks(ecosystem: str) -> list[tuple[str, callable]]:
    registry = REGISTRY_CHECKS[ecosystem]
    return [registry] + COMMON_CHECKS
