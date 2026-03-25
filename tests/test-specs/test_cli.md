# test_cli Spec

Source: `nameavail/cli.py`
Test: `tests/test_cli.py`

## validate_name(name)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| V1 | Valid names (lowercase, hyphens, underscores) | Returns None | Valid names rejected, tool unusable |
| V2 | Empty string | Returns error message | Empty input causes downstream crash |
| V3 | Over 100 characters | Returns error message | Extremely long names sent to APIs, potential abuse |
| V4 | Starts with digit | Returns error message | Invalid registry names accepted, confusing API errors |
| V5 | Contains uppercase | Returns error message | Case-sensitive registries get wrong lookup |
| V6 | Contains special characters (dots, spaces) | Returns error message | Invalid names cause API errors or wrong lookups |

## run(args)

| ID | Scenario | Assertion | Risk if broken |
|----|----------|-----------|----------------|
| R1 | Single valid name | Exit code 0, output contains name | Basic single-name flow broken |
| R2 | --json flag | Exit code 0, output is valid JSON with name and checks | JSON consumers get invalid output |
| R3 | Two valid names | Exit code 0, both names in output | Bulk check flow broken |
| R4 | Invalid name | Exit code 1, error on stderr | Invalid names silently accepted, confusing API errors |
| R5 | --ecosystem node | check_name called with ecosystem="node" | Node ecosystem flag ignored, wrong registry checked |
| R6 | -e rust (short flag) | check_name called with ecosystem="rust" | Short flag broken, inconsistent CLI behavior |
| R7 | --ecosystem java (invalid) | SystemExit raised | Unsupported ecosystem silently accepted |
