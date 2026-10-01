"""Test CLI — AC15."""
import pytest
import json
import subprocess
import sys


def run_cli(args, check=False, shell=False):
    """Run the CLI as a module and return (exit_code, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "rfc8141_urn_pure"] + args,
        capture_output=True,
        text=True,
        cwd="/root/projects/rfc-8141-urn-pure",
        shell=shell,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"CLI failed: {result.stderr}")
    return result.returncode, result.stdout, result.stderr


class TestCLI:
    """CLI smoke — AC15."""

    def test_help(self):
        code, stdout, stderr = run_cli(["--help"])
        assert code == 0
        assert "RFC 8141" in stdout

    def test_version(self):
        code, stdout, stderr = run_cli(["--version"])
        assert code == 0
        assert "0.1.0" in stdout

    def test_parse_valid(self):
        code, stdout, stderr = run_cli(["parse", "urn:isbn:0451450523"])
        assert code == 0
        data = json.loads(stdout)
        assert data["nid"] == "isbn"
        assert data["nss"] == "0451450523"

    def test_parse_invalid(self):
        code, stdout, stderr = run_cli(["parse", "not-a-urn"])
        assert code == 1
        assert "error" in stderr.lower()

    def test_validate_valid(self):
        code, stdout, stderr = run_cli(["validate", "urn:ietf:rfc:8141"])
        assert code == 0
        assert "valid" in stdout.lower()

    def test_validate_invalid(self):
        code, stdout, stderr = run_cli(["validate", "not-a-urn"])
        assert code == 1
        assert "invalid" in stdout.lower()

    def test_construct(self):
        code, stdout, stderr = run_cli(["construct", "isbn", "0451450523"])
        assert code == 0
        assert stdout.strip() == "urn:isbn:0451450523"

    def test_construct_with_percent_encode(self):
        code, stdout, stderr = run_cli(["construct", "example", "hello world", "--percent-encode"])
        assert code == 0
        assert "urn:example:hello%20world" in stdout

    def test_resolve_ni_valid(self):
        # sha256 of b"test"
        import base64
        digest = bytes(range(32))
        encoded = base64.urlsafe_b64encode(digest).decode().rstrip("=")
        urn = f"urn:ni:?n={encoded}&alg=sha256"
        code, stdout, stderr = run_cli(["resolve-ni", urn])
        assert code == 0
        assert stdout.strip() == digest.hex()

    def test_resolve_tag_valid(self):
        code, stdout, stderr = run_cli(
            ["resolve-tag", "urn:tag:example.com,2024-10-01:blog/entry"]
        )
        assert code == 0
        assert "2024-10-01" in stdout

    def test_subcommand_required(self):
        # No subcommand should print help + exit 2 (argparse default) or 1
        code, stdout, stderr = run_cli([])
        assert code in (1, 2)

    def test_parse_error_message(self):
        code, stdout, stderr = run_cli(["parse", ""])
        assert code == 1

    def test_resolve_ni_error(self):
        code, stdout, stderr = run_cli(["resolve-ni", "urn:isbn:0451450523"])
        assert code == 1

    def test_resolve_tag_error(self):
        code, stdout, stderr = run_cli(["resolve-tag", "urn:isbn:0451450523"])
        assert code == 1

    def test_parse_roundtrip(self):
        # parse output can be used to reconstruct the URN
        code, stdout, stderr = run_cli(["parse", "urn:example:a:b:c"])
        assert code == 0
        data = json.loads(stdout)
        assert data["nid"] == "example"
        assert data["nss"] == "a:b:c"
