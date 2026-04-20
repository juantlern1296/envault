"""Tests for CLI TTL commands."""

import pytest
import os
from click.testing import CliRunner
from envault.cli import cli
from envault.vault import save_vault, set_var

PASSWORD = "testpass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_env(tmp_path):
    p = tmp_path / "vault.enc"
    save_vault(str(p), PASSWORD, {})
    return {"ENVAULT_PATH": str(p), "ENVAULT_PASSWORD": PASSWORD}


def _run(runner, vault_env, *args):
    return runner.invoke(cli, list(args), env=vault_env)


def test_ttl_set_and_get(runner, vault_env):
    # first set a variable
    _run(runner, vault_env, "set", "MY_KEY", "myval")
    result = _run(runner, vault_env, "ttl", "set", "MY_KEY", "3600")
    assert result.exit_code == 0
    assert "expires in 3600s" in result.output

    result = _run(runner, vault_env, "ttl", "get", "MY_KEY")
    assert result.exit_code == 0
    assert "MY_KEY expires at" in result.output


def test_ttl_get_no_ttl(runner, vault_env):
    _run(runner, vault_env, "set", "BARE", "val")
    result = _run(runner, vault_env, "ttl", "get", "BARE")
    assert "No TTL set" in result.output


def test_ttl_set_missing_var_exits_nonzero(runner, vault_env):
    result = _run(runner, vault_env, "ttl", "set", "GHOST", "60")
    assert result.exit_code != 0


def test_ttl_purge_expired(runner, vault_env):
    _run(runner, vault_env, "set", "STALE", "old")
    _run(runner, vault_env, "ttl", "set", "STALE", "-1")
    result = _run(runner, vault_env, "ttl", "purge")
    assert "Purged: STALE" in result.output


def test_ttl_purge_nothing(runner, vault_env):
    result = _run(runner, vault_env, "ttl", "purge")
    assert "Nothing to purge" in result.output
