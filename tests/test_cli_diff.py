import pytest
from click.testing import CliRunner
from envault.cli_diff import diff_group
from envault.vault import save_vault
import os


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def two_vaults(tmp_path):
    p1 = str(tmp_path / "old.vault")
    p2 = str(tmp_path / "new.vault")
    pw = "testpass"
    save_vault(p1, {"A": "1", "B": "2"}, pw)
    save_vault(p2, {"A": "changed", "C": "3"}, pw)
    return p1, p2, pw


def _run(runner, args, password="testpass"):
    return runner.invoke(diff_group, args, input=password + "\n")


def test_diff_files_shows_changes(runner, two_vaults):
    p1, p2, pw = two_vaults
    result = _run(runner, ["files", p1, p2], password=pw)
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output
    assert "C" in result.output


def test_diff_files_no_diff(runner, tmp_path):
    p1 = str(tmp_path / "v1.vault")
    p2 = str(tmp_path / "v2.vault")
    pw = "testpass"
    save_vault(p1, {"X": "1"}, pw)
    save_vault(p2, {"X": "1"}, pw)
    result = _run(runner, ["files", p1, p2], password=pw)
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_diff_show_against_empty(runner, tmp_path):
    p = str(tmp_path / "v.vault")
    pw = "testpass"
    save_vault(p, {"FOO": "bar"}, pw)
    result = _run(runner, ["show", p], password=pw)
    assert result.exit_code == 0
    assert "FOO" in result.output


def test_diff_show_against_other(runner, two_vaults):
    p1, p2, pw = two_vaults
    result = _run(runner, ["show", p2, "--against", p1], password=pw)
    assert result.exit_code == 0
    assert "C" in result.output
