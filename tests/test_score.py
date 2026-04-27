"""Tests for envault.score."""
import pytest
from click.testing import CliRunner

from envault.vault import save_vault, set_var
from envault.score import score_vault, ScoreReport
from envault.cli_score import score_group


@pytest.fixture()
def vault_file(tmp_path):
    p = tmp_path / "vault.db"
    save_vault(str(p), {}, "pw")
    return str(p)


def _set(vault_file, key, value, password="pw"):
    set_var(vault_file, password, key, value)


# --- unit tests ---

def test_score_empty_vault_is_perfect(vault_file):
    report = score_vault(vault_file, "pw")
    assert report.score == 100
    assert report.grade == "A"
    assert report.deductions == []


def test_score_returns_score_report(vault_file):
    report = score_vault(vault_file, "pw")
    assert isinstance(report, ScoreReport)
    assert report.total == 100


def test_score_wrong_password_returns_zero(vault_file):
    report = score_vault(vault_file, "wrong")
    assert report.score == 0
    assert report.grade == "F"
    assert any("Cannot open vault" in d for d in report.deductions)


def test_score_percentage_calculation(vault_file):
    report = score_vault(vault_file, "pw")
    assert report.percentage == 100.0


def test_score_with_lint_issue_deducts_points(vault_file):
    # lowercase key triggers a lint warning
    _set(vault_file, "lowercase_key", "value")
    report = score_vault(vault_file, "pw")
    assert report.score < 100
    assert any("lint" in d.lower() for d in report.deductions)


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_env(vault_file):
    return {"ENVAULT_PATH": vault_file, "ENVAULT_PASSWORD": "pw"}


def test_cli_run_exits_zero_for_clean_vault(runner, vault_env):
    result = runner.invoke(score_group, ["run"], env=vault_env)
    assert "Grade: A" in result.output or "Grade: B" in result.output
    assert result.exit_code == 0


def test_cli_run_json_output(runner, vault_env):
    import json
    result = runner.invoke(score_group, ["run", "--json"], env=vault_env)
    data = json.loads(result.output)
    assert "score" in data
    assert "grade" in data
    assert "percentage" in data


def test_cli_run_missing_vault_exits_nonzero(runner, tmp_path):
    env = {"ENVAULT_PATH": str(tmp_path / "missing.db"),
           "ENVAULT_PASSWORD": "pw"}
    result = runner.invoke(score_group, ["run"], env=env)
    assert result.exit_code != 0
