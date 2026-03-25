"""Integration tests that hit real APIs. Requires network access.

Run with: pytest tests/test_integration.py -v
Skip with: pytest tests/ --ignore=tests/test_integration.py
"""

import json
import subprocess
import sys

import pytest

# All integration tests need network
pytestmark = pytest.mark.integration


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "nameavail", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


# ===========================================================================
# Single name — available (INT-1..INT-3)
# ===========================================================================

class TestSingleAvailable:
    """Use an obscure name unlikely to be taken across registries."""

    NAME = "zxqvbnm-not-a-real-pkg"

    def test_python_ecosystem_int1(self):
        result = run_cli(self.NAME)
        assert result.returncode == 0
        assert self.NAME in result.stdout
        assert "available" in result.stdout.lower() or "\u2713" in result.stdout

    def test_node_ecosystem_int2(self):
        result = run_cli(self.NAME, "--ecosystem", "node")
        assert result.returncode == 0
        output = result.stdout
        assert self.NAME in output
        # Should not mention PyPI anywhere
        assert "PyPI" not in output

    def test_rust_ecosystem_int3(self):
        result = run_cli(self.NAME, "--ecosystem", "rust")
        assert result.returncode == 0
        output = result.stdout
        assert self.NAME in output
        assert "PyPI" not in output


# ===========================================================================
# Single name — taken (INT-4..INT-6)
# ===========================================================================

class TestSingleTaken:
    def test_flask_python_int4(self):
        result = run_cli("flask")
        assert result.returncode == 0
        output = result.stdout
        # PyPI should be taken with a description
        assert "\u2717" in output
        assert "taken" in output.lower() or "registered" in output.lower()

    def test_express_node_int5(self):
        result = run_cli("express", "--ecosystem", "node")
        assert result.returncode == 0
        output = result.stdout
        assert "\u2717" in output
        assert "taken" in output.lower() or "registered" in output.lower()

    def test_serde_rust_int6(self):
        result = run_cli("serde", "--ecosystem", "rust")
        assert result.returncode == 0
        output = result.stdout
        assert "\u2717" in output
        assert "taken" in output.lower() or "registered" in output.lower()


# ===========================================================================
# Bulk names (INT-7)
# ===========================================================================

class TestBulk:
    def test_table_output_int7(self):
        result = run_cli("flask", "reelspec")
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")
        # Header + 2 data rows
        assert len(lines) >= 3
        header = lines[0]
        assert "Name" in header
        # Both names present in data rows
        body = "\n".join(lines[1:])
        assert "flask" in body
        assert "reelspec" in body


# ===========================================================================
# JSON output (INT-8..INT-9)
# ===========================================================================

class TestJsonOutput:
    EXPECTED_CHECK_KEYS = {"PyPI", "GitHub org", "GitHub repos", ".com domain", ".ai domain"}

    def test_single_json_int8(self):
        result = run_cli("reelspec", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "reelspec"
        assert "checks" in data
        assert set(data["checks"].keys()) == self.EXPECTED_CHECK_KEYS

    def test_bulk_json_int9(self):
        result = run_cli("flask", "reelspec", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "name" in item
            assert "checks" in item


# ===========================================================================
# Error handling (INT-10)
# ===========================================================================

class TestErrorHandling:
    def test_invalid_name_int10(self):
        result = run_cli("InvalidName")
        assert result.returncode == 1
        assert "Error" in result.stderr
