# test_formatters Spec

Source: `nameavail/formatters.py`
Test: `tests/test_formatters.py`

## format_single(name, results)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| FS1 | All checks available | Output contains name, checkmarks, and "available" | User can't see positive results |
| FS2 | All checks taken | Output contains X marks, "taken"/"registered", and summary text | User can't see negative results or understand why name is taken |
| FS3 | Check was skipped (missing tool) | Shows "-" icon and "skipped" with reason | User confused about missing check output |
| FS4 | GitHub repos has similar but no exact matches | Shows "~" icon and count of similar repos | User misled about repo landscape |

## format_table(all_results, registry_label)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| FT1 | Two names with mixed results | Header row + 2 data rows with correct statuses | Bulk output is garbled or missing data |
| FT2 | registry_label="npm" | Table header shows "npm" not "PyPI" | Node users see wrong column header, confusing output |
| FT3 | registry_label="crates.io" | Table header shows "crates.io" not "PyPI" | Rust users see wrong column header |

## format_json(all_results, single)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| FJ1 | Single name, single=True | Returns JSON object with "name" and "checks" keys | Agent/script consumers get wrong JSON shape |
| FJ2 | Multiple names, single=False | Returns JSON array of objects | Agent/script consumers get wrong JSON shape for bulk queries |
