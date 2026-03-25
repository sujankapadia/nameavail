"""Tests for output formatting (single, table, JSON)."""

import json

from nameavail.formatters import format_single, format_table, format_json


AVAILABLE_RESULTS = {
    "PyPI": {"available": True},
    "GitHub org": {"available": True},
    "GitHub repos": {"exact_matches": [], "similar": []},
    ".com domain": {"available": True},
    ".ai domain": {"available": True, "note": "based on DNS — verify with a registrar"},
}

TAKEN_RESULTS = {
    "PyPI": {"available": False, "summary": "A web framework", "version": "2.0"},
    "GitHub org": {"available": False},
    "GitHub repos": {
        "exact_matches": [{"fullName": "pallets/flask", "description": "Web framework"}],
        "similar": [{"fullName": "pallets/flask", "description": "Web framework"}],
    },
    ".com domain": {"available": False},
    ".ai domain": {"available": False, "ip": "1.2.3.4"},
}


# ===========================================================================
# format_single — FS1..FS4
# ===========================================================================

class TestFormatSingle:
    def test_all_available_fs1(self):
        output = format_single("reelspec", AVAILABLE_RESULTS)
        assert "Name: reelspec" in output
        assert "\u2713" in output
        assert "available" in output

    def test_all_taken_fs2(self):
        output = format_single("flask", TAKEN_RESULTS)
        assert "Name: flask" in output
        assert "\u2717" in output
        assert "taken" in output or "registered" in output
        assert "A web framework" in output

    def test_skipped_check_fs3(self):
        results = {
            "PyPI": {"available": True},
            ".com domain": {"available": None, "error": "whois not installed", "skipped": True},
        }
        output = format_single("test", results)
        assert "-" in output
        assert "skipped" in output

    def test_github_repos_similar_fs4(self):
        results = {
            "GitHub repos": {
                "exact_matches": [],
                "similar": [{"fullName": "a/b", "description": "x"}],
            },
        }
        output = format_single("test", results)
        assert "1 similar repo found" in output
        assert "~" in output


# ===========================================================================
# format_table — FT1..FT3
# ===========================================================================

class TestFormatTable:
    def test_basic_table_ft1(self):
        all_results = {
            "reelspec": AVAILABLE_RESULTS,
            "flask": TAKEN_RESULTS,
        }
        output = format_table(all_results)
        lines = output.strip().split("\n")
        assert len(lines) == 3  # header + 2 data rows
        assert "Name" in lines[0]
        assert "PyPI" in lines[0]
        assert "reelspec" in lines[1]
        assert "flask" in lines[2]

    def test_npm_registry_label_ft2(self):
        results = {
            "npm": {"available": True},
            "GitHub org": {"available": True},
            "GitHub repos": {"exact_matches": [], "similar": []},
            ".com domain": {"available": True},
            ".ai domain": {"available": True},
        }
        output = format_table({"test": results}, registry_label="npm")
        header = output.split("\n")[0]
        assert "npm" in header
        assert "PyPI" not in header

    def test_crates_registry_label_ft3(self):
        results = {
            "crates.io": {"available": False, "summary": "serde", "version": "1.0"},
            "GitHub org": {"available": False},
            "GitHub repos": {"exact_matches": [], "similar": []},
            ".com domain": {"available": False},
            ".ai domain": {"available": False},
        }
        output = format_table({"serde": results}, registry_label="crates.io")
        header = output.split("\n")[0]
        assert "crates.io" in header


# ===========================================================================
# format_json — FJ1..FJ2
# ===========================================================================

class TestFormatJson:
    def test_single_name_fj1(self):
        all_results = {"reelspec": AVAILABLE_RESULTS}
        raw = format_json(all_results, single=True)
        data = json.loads(raw)
        assert data["name"] == "reelspec"
        assert "checks" in data
        assert data["checks"]["PyPI"]["available"] is True

    def test_bulk_names_fj2(self):
        all_results = {"reelspec": AVAILABLE_RESULTS, "flask": TAKEN_RESULTS}
        raw = format_json(all_results, single=False)
        data = json.loads(raw)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "reelspec"
        assert data[1]["name"] == "flask"
