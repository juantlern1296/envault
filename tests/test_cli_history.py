"""Tests for CLI history commands."""
import pytest
from click.testing import CliRunner
from envault.cli_history import history_group
from envault.history import record_change


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_env(tmp_path):
    vault_path = str(tmp_path / "vault.enc")
    return {"ENVAULT_PATH": vault_path}, vault_path


def _run(runner, vault_env, *args):
    env, _ = vault_env
    return runner.invoke(history_group, list(args), env=env)


def test_show_empty(runner, vault_env):
    result = _run(runner, vault_env, "show", "FOO")
    assert result.exit_code == 0
    assert "No history" in result.output


def test_show_entries(runner, vault_env):
    env, vault_path = vault_env
    record_change(vault_path, "DB_URL", "set")
    record_change(vault_path, "DB_URL", "delete", old_value="postgres://")
    result = runner.invoke(history_group, ["show", "DB_URL"], env=env)
    assert result.exit_code == 0
    assert "set" in result.output
    assert "delete" in result.output
    assert "postgres://" in result.output


def test_clear_key(runner, vault_env):
    env, vault_path = vault_env
    record_change(vault_path, "X", "set")
    result = runner.invoke(history_group, ["clear", "X"], env=env)
    assert result.exit_code == 0
    assert "Cleared history for 'X'" in result.output


def test_clear_all(runner, vault_env):
    env, vault_path = vault_env
    record_change(vault_path, "A", "set")
    result = runner.invoke(history_group, ["clear", "--all"], env=env)
    assert result.exit_code == 0
    assert "Cleared all history" in result.output


def test_clear_no_args_exits_nonzero(runner, vault_env):
    result = _run(runner, vault_env, "clear")
    assert result.exit_code != 0
