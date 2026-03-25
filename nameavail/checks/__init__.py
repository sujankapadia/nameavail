from .pypi import check_pypi
from .github import check_github_org, check_github_repos
from .domain import check_domain_com, check_domain_ai

ALL_CHECKS = [
    ("PyPI", check_pypi),
    ("GitHub org", check_github_org),
    ("GitHub repos", check_github_repos),
    (".com domain", check_domain_com),
    (".ai domain", check_domain_ai),
]
