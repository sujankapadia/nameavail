"""Tests for registry, GitHub, and domain checks using mocked network calls."""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from nameavail.checks.pypi import check_pypi
from nameavail.checks.npm import check_npm
from nameavail.checks.crates import check_crates
from nameavail.checks.github import check_github_org, check_github_repos
from nameavail.checks.domain import check_domain_com, check_domain_ai


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(data: dict):
    """Create a mock HTTP response with JSON body."""
    resp = MagicMock()
    resp.read.return_value = json.dumps(data).encode()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def _http_error(code: int):
    from urllib.error import HTTPError
    return HTTPError(url="http://x", code=code, msg="", hdrs={}, fp=None)


# ===========================================================================
# PyPI — P1..P4
# ===========================================================================

class TestCheckPyPI:
    @patch("nameavail.checks.http.urllib.request.urlopen")
    def test_available_p1(self, mock_urlopen):
        mock_urlopen.side_effect = _http_error(404)
        result = check_pypi("nonexistent")
        assert result == {"available": True}

    @patch("nameavail.checks.http.urllib.request.urlopen")
    def test_taken_p2(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response({
            "info": {"summary": "A web framework", "version": "2.0.0"}
        })
        result = check_pypi("flask")
        assert result["available"] is False
        assert result["summary"] == "A web framework"
        assert result["version"] == "2.0.0"

    @patch("nameavail.checks.http.urllib.request.urlopen")
    def test_rate_limit_then_success_p3(self, mock_urlopen):
        mock_urlopen.side_effect = [
            _http_error(429),
            _mock_response({"info": {"summary": "pkg", "version": "1.0"}}),
        ]
        result = check_pypi("ratelimited")
        assert result["available"] is False

    @patch("nameavail.checks.http.urllib.request.urlopen")
    def test_connection_error_p4(self, mock_urlopen):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("no network")
        result = check_pypi("anything")
        assert result["available"] is None
        assert "connection failed" in result["error"]


# ===========================================================================
# npm — N1..N2
# ===========================================================================

class TestCheckNpm:
    @patch("nameavail.checks.http.urllib.request.urlopen")
    def test_available_n1(self, mock_urlopen):
        mock_urlopen.side_effect = _http_error(404)
        result = check_npm("nonexistent")
        assert result == {"available": True}

    @patch("nameavail.checks.http.urllib.request.urlopen")
    def test_taken_n2(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response({
            "description": "Fast web framework",
            "dist-tags": {"latest": "5.0.0"},
        })
        result = check_npm("express")
        assert result["available"] is False
        assert result["summary"] == "Fast web framework"
        assert result["version"] == "5.0.0"


# ===========================================================================
# crates.io — CR1..CR2
# ===========================================================================

class TestCheckCrates:
    @patch("nameavail.checks.http.urllib.request.urlopen")
    def test_available_cr1(self, mock_urlopen):
        mock_urlopen.side_effect = _http_error(404)
        result = check_crates("nonexistent")
        assert result == {"available": True}

    @patch("nameavail.checks.http.urllib.request.urlopen")
    def test_taken_cr2(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response({
            "crate": {"description": "Serialization framework", "max_version": "1.0.200"}
        })
        result = check_crates("serde")
        assert result["available"] is False
        assert result["summary"] == "Serialization framework"
        assert result["version"] == "1.0.200"


# ===========================================================================
# GitHub org — G1..G3
# ===========================================================================

class TestCheckGitHubOrg:
    @patch("nameavail.checks.http.urllib.request.urlopen")
    def test_available_g1(self, mock_urlopen):
        mock_urlopen.side_effect = _http_error(404)
        result = check_github_org("nonexistent")
        assert result == {"available": True}

    @patch("nameavail.checks.http.urllib.request.urlopen")
    def test_taken_g2(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response({})
        result = check_github_org("google")
        assert result == {"available": False}

    @patch("nameavail.checks.http.urllib.request.urlopen")
    def test_server_error_g3(self, mock_urlopen):
        mock_urlopen.side_effect = _http_error(500)
        result = check_github_org("anything")
        assert result["available"] is None
        assert "500" in result["error"]


# ===========================================================================
# GitHub repos — GR1..GR5
# ===========================================================================

class TestCheckGitHubRepos:
    @patch("nameavail.checks.github.shutil.which", return_value=None)
    def test_gh_not_installed_gr1(self, mock_which):
        result = check_github_repos("anything")
        assert result["skipped"] is True
        assert "not installed" in result["error"]

    @patch("nameavail.checks.github.subprocess.run")
    @patch("nameavail.checks.github.shutil.which", return_value="/usr/bin/gh")
    def test_no_matches_gr2(self, mock_which, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="[]", stderr=""
        )
        result = check_github_repos("nonexistent")
        assert result["exact_matches"] == []
        assert result["similar"] == []

    @patch("nameavail.checks.github.subprocess.run")
    @patch("nameavail.checks.github.shutil.which", return_value="/usr/bin/gh")
    def test_exact_match_gr3(self, mock_which, mock_run):
        repos = [
            {"fullName": "pallets/flask", "description": "Web framework"},
            {"fullName": "other/flask-admin", "description": "Admin ext"},
        ]
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(repos), stderr=""
        )
        result = check_github_repos("flask")
        assert len(result["exact_matches"]) == 1
        assert result["exact_matches"][0]["fullName"] == "pallets/flask"
        assert len(result["similar"]) == 2

    @patch("nameavail.checks.github.subprocess.run")
    @patch("nameavail.checks.github.shutil.which", return_value="/usr/bin/gh")
    def test_timeout_gr4(self, mock_which, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="gh", timeout=10)
        result = check_github_repos("anything")
        assert result["available"] is None
        assert "timed out" in result["error"]

    @patch("nameavail.checks.github.subprocess.run")
    @patch("nameavail.checks.github.shutil.which", return_value="/usr/bin/gh")
    def test_auth_failure_gr5(self, mock_which, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="",
            stderr="To get started with GitHub CLI, please run: gh auth login",
        )
        result = check_github_repos("anything")
        assert result["skipped"] is True
        assert "not authenticated" in result["error"]


# ===========================================================================
# .com domain — DC1..DC5
# ===========================================================================

class TestCheckDomainCom:
    @patch("nameavail.checks.domain.subprocess.run")
    @patch("nameavail.checks.domain.shutil.which", return_value="/usr/bin/whois")
    def test_available_dc1(self, mock_which, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout='No match for domain "NONEXISTENT.COM".', stderr=""
        )
        result = check_domain_com("nonexistent")
        assert result == {"available": True}

    @patch("nameavail.checks.domain.subprocess.run")
    @patch("nameavail.checks.domain.shutil.which", return_value="/usr/bin/whois")
    def test_registered_dc2(self, mock_which, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout="Domain Name: GOOGLE.COM\nRegistrar: MarkMonitor", stderr=""
        )
        result = check_domain_com("google")
        assert result == {"available": False}

    @patch("nameavail.checks.domain.subprocess.run")
    @patch("nameavail.checks.domain.shutil.which", return_value="/usr/bin/whois")
    def test_inconclusive_dc3(self, mock_which, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="some unexpected output", stderr=""
        )
        result = check_domain_com("weird")
        assert result["available"] is None
        assert "inconclusive" in result["note"]

    @patch("nameavail.checks.domain.shutil.which", return_value=None)
    def test_whois_not_installed_dc4(self, mock_which):
        result = check_domain_com("anything")
        assert result["skipped"] is True

    @patch("nameavail.checks.domain.subprocess.run")
    @patch("nameavail.checks.domain.shutil.which", return_value="/usr/bin/whois")
    def test_timeout_dc5(self, mock_which, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="whois", timeout=10)
        result = check_domain_com("anything")
        assert "timed out" in result["error"]


# ===========================================================================
# .ai domain — DA1..DA4
# ===========================================================================

class TestCheckDomainAi:
    @patch("nameavail.checks.domain.subprocess.run")
    @patch("nameavail.checks.domain.shutil.which", return_value="/usr/bin/dig")
    def test_available_no_records_da1(self, mock_which, mock_run):
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
        ]
        result = check_domain_ai("nonexistent")
        assert result["available"] is True
        assert "verify with a registrar" in result["note"]

    @patch("nameavail.checks.domain.subprocess.run")
    @patch("nameavail.checks.domain.shutil.which", return_value="/usr/bin/dig")
    def test_taken_a_record_da2(self, mock_which, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="93.184.216.34\n", stderr=""
        )
        result = check_domain_ai("example")
        assert result["available"] is False
        assert result["ip"] == "93.184.216.34"

    @patch("nameavail.checks.domain.subprocess.run")
    @patch("nameavail.checks.domain.shutil.which", return_value="/usr/bin/dig")
    def test_taken_ns_only_da3(self, mock_which, mock_run):
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="ns1.example.com.\n", stderr=""),
        ]
        result = check_domain_ai("parked")
        assert result["available"] is False

    @patch("nameavail.checks.domain.shutil.which", return_value=None)
    def test_dig_not_installed_da4(self, mock_which):
        result = check_domain_ai("anything")
        assert result["skipped"] is True
