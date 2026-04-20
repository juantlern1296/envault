import pytest
import os
from click.testing import CliRunner
from envault.cli import cli
from envault.vault import save_vault

PASSWORD = "cli-test-pass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_env(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, PASSWORD, {"DB_URL": "postgres://", "API_KEY": "abc"})
    return {"ENVAULT_PATH": path, "ENVAULT_PASSWORD": PASSWORD}


def _run(runner, vault_env, args):
    return runner.invoke(cli, args, env=vault_env, catch_exceptions=False)


def test_tag_add_and_list(runner, vault_env):
    _run(runner, vault_env, ["tag", "add", "DB_URL", "database"])
    result = _run(runner, vault_env, ["tag", "list"])
    assert "database" in result.output
    assert "DB_URL" in result.output


def test_tag_show(runner, vault_env):
    _run(runner, vault_env, ["tag", "add", "API_KEY", "secrets"])
    result = _run(runner, vault_env, ["tag", "show", "secrets"])
    assert "API_KEY" in result.output


def test_tag_remove(runner, vault_env):
    _run(runner, vault_env, ["tag", "add", "DB_URL", "temp"])
    _run(runner, vault_env, ["tag", "remove", "DB_URL", "temp"])
    result = _run(runner, vault_env, ["tag", "list"])
    assert "temp" not in result.output


def test_tag_remove_missing_exits_nonzero(runner, vault_env):
    result = runner.invoke(cli, ["tag", "remove", "DB_URL", "ghost"], env=vault_env)
    assert result.exit_code != 0


def test_show_missing_tag(runner, vault_env):
    result = _run(runner, vault_env, ["tag", "show", "nothing"])
    assert "No variables" in result.output
