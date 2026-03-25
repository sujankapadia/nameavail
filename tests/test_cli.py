"""Tests for CLI argument parsing, validation, and orchestration."""

import json
from unittest.mock import patch

import pytest

from nameavail.cli import validate_name, run


MOCK_RESULTS = {
    "PyPI": {"available": True},
    "GitHub org": {"available": True},
    "GitHub repos": {"exact_matches": [], "similar": []},
    ".com domain": {"available": True},
    ".ai domain": {"available": True},
}


# ===========================================================================
# validate_name — V1..V6
# ===========================================================================

class TestValidateName:
    def test_valid_names_v1(self):
        assert validate_name("flask") is None
        assert validate_name("my-project") is None
        assert validate_name("my_project") is None
        assert validate_name("a123") is None

    def test_empty_v2(self):
        assert validate_name("") is not None

    def test_too_long_v3(self):
        assert validate_name("a" * 101) is not None

    def test_starts_with_digit_v4(self):
        assert validate_name("1abc") is not None

    def test_uppercase_v5(self):
        assert validate_name("Flask") is not None

    def test_special_chars_v6(self):
        assert validate_name("my.project") is not None
        assert validate_name("my project") is not None


# ===========================================================================
# run — R1..R7
# ===========================================================================

class TestRun:
    @patch("nameavail.cli.check_name", return_value=MOCK_RESULTS)
    def test_single_name_r1(self, mock_check, capsys):
        rc = run(["reelspec"])
        assert rc == 0
        output = capsys.readouterr().out
        assert "reelspec" in output
        mock_check.assert_called_once_with("reelspec", "python")

    @patch("nameavail.cli.check_name", return_value=MOCK_RESULTS)
    def test_json_output_r2(self, mock_check, capsys):
        rc = run(["reelspec", "--json"])
        assert rc == 0
        data = json.loads(capsys.readouterr().out)
        assert data["name"] == "reelspec"

    @patch("nameavail.cli.check_name", return_value=MOCK_RESULTS)
    def test_bulk_names_r3(self, mock_check, capsys):
        rc = run(["aaa", "bbb"])
        assert rc == 0
        output = capsys.readouterr().out
        assert "aaa" in output
        assert "bbb" in output

    def test_invalid_name_r4(self, capsys):
        rc = run(["Invalid"])
        assert rc == 1
        assert "Error" in capsys.readouterr().err

    @patch("nameavail.cli.check_name", return_value=MOCK_RESULTS)
    def test_ecosystem_node_r5(self, mock_check, capsys):
        rc = run(["reelspec", "--ecosystem", "node"])
        assert rc == 0
        mock_check.assert_called_once_with("reelspec", "node")

    @patch("nameavail.cli.check_name", return_value=MOCK_RESULTS)
    def test_ecosystem_rust_short_flag_r6(self, mock_check, capsys):
        rc = run(["reelspec", "-e", "rust"])
        assert rc == 0
        mock_check.assert_called_once_with("reelspec", "rust")

    def test_invalid_ecosystem_r7(self):
        with pytest.raises(SystemExit):
            run(["reelspec", "--ecosystem", "java"])
