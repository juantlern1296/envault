"""Tests for envault/cli_namespace.py"""

import os
import pytest
from click.testing import CliRunner
from envault.cli import cli
from envault.vault import save_vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_env(tmp_path):
    path = tmp_path / "vault.enc"
    save_vault(str(path), "testpass", {})
    return {"ENVAULT_VAULT": str(path), "ENVAULT_PASSWORD": "testpass"}


def _run(runner, vault_env, *args):
    return runner.invoke(cli, ["ns"] + list(args), env=vault_env)


def test_set_and_get(runner, vault_env):
    r = _run(runner, vault_env, "set", "prod", "DB_URL", "postgres://localhost")
    assert r.exit_code == 0
    assert "prod::DB_URL" in r.output

    r = _run(runner, vault_env, "get", "prod", "DB_URL")
    assert r.exit_code == 0
    assert "postgres://localhost" in r.output


def test_get_missing_exits_nonzero(runner, vault_env):
    r = _run(runner, vault_env, "get", "prod", "MISSING")
    assert r.exit_code != 0


def test_delete_existing(runner, vault_env):
    _run(runner, vault_env, "set", "prod", "KEY", "val")
    r = _run(runner, vault_env, "delete", "prod", "KEY")
    assert r.exit_code == 0
    r = _run(runner, vault_env, "get", "prod", "KEY")
    assert r.exit_code != 0


def test_delete_missing_exits_nonzero(runner, vault_env):
    r = _run(runner, vault_env, "delete", "prod", "NOPE")
    assert r.exit_code != 0


def test_list_namespaces(runner, vault_env):
    _run(runner, vault_env, "set", "prod", "A", "1")
    _run(runner, vault_env, "set", "dev", "B", "2")
    r = _run(runner, vault_env, "list")
    assert r.exit_code == 0
    assert "prod" in r.output
    assert "dev" in r.output


def test_show_namespace(runner, vault_env):
    _run(runner, vault_env, "set", "prod", "X", "hello")
    _run(runner, vault_env, "set", "prod", "Y", "world")
    r = _run(runner, vault_env, "show", "prod")
    assert r.exit_code == 0
    assert "X=hello" in r.output
    assert "Y=world" in r.output


def test_clear_namespace(runner, vault_env):
    _run(runner, vault_env, "set", "prod", "A", "1")
    _run(runner, vault_env, "set", "prod", "B", "2")
    r = _run(runner, vault_env, "clear", "prod")
    assert r.exit_code == 0
    assert "2" in r.output
    r = _run(runner, vault_env, "show", "prod")
    assert "No variables" in r.output
