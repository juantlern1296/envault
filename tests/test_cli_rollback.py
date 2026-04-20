"""CLI tests for rollback commands."""

import os
import pytest
from click.testing import CliRunner

from envault.cli_rollback import rollback_group
from envault.vault import save_vault
from envault.history import record_change


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_env(tmp_path):
    path = str(tmp_path / "vault.db")
    save_vault(path, "secret", {})
    env = {"ENVAULT_PASSWORD": "secret"}
    return path, env


def _run(runner, vault_env, *args):
    path, env = vault_env
    return runner.invoke(rollback_group, [*args], env=env)


def test_list_no_points(runner, vault_env):
    path, _ = vault_env
    result = _run(runner, vault_env, "list", path)
    assert result.exit_code == 0
    assert "No rollback points" in result.output


def test_list_shows_entries(runner, vault_env):
    path, _ = vault_env
    record_change(path, "set", "API_KEY", new_value="abc", old_value=None)
    result = _run(runner, vault_env, "list", path)
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "SET" in result.output


def test_apply_rolls_back(runner, vault_env):
    path, env = vault_env
    save_vault(path, "secret", {"X": "new"})
    record_change(path, "set", "X", new_value="new", old_value="old")
    result = _run(runner, vault_env, "apply", path, "0")
    assert result.exit_code == 0
    assert "Rolled back" in result.output


def test_apply_bad_index_exits_nonzero(runner, vault_env):
    path, _ = vault_env
    record_change(path, "set", "Y", new_value="v", old_value=None)
    result = _run(runner, vault_env, "apply", path, "99")
    assert result.exit_code != 0
    assert "Error" in result.output
