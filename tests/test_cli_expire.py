"""CLI tests for the expire command group."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_expire import expire_group
from envault.expire import set_expiry
from envault.vault import save_vault

PASSWORD = "cli-test-pw"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_env(tmp_path: Path):
    vault = str(tmp_path / "vault.enc")
    save_vault(vault, PASSWORD, {"MY_KEY": "value", "OTHER": "stuff"})
    env = {"ENVAULT_VAULT": vault, "ENVAULT_PASSWORD": PASSWORD}
    return vault, env


def _run(runner: CliRunner, env: dict, *args):
    return runner.invoke(expire_group, list(args), env=env)


def test_set_and_get(runner: CliRunner, vault_env) -> None:
    vault, env = vault_env
    future = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    result = _run(runner, env, "set", "MY_KEY", future)
    assert result.exit_code == 0
    assert "MY_KEY" in result.output

    result = _run(runner, env, "get", "MY_KEY")
    assert result.exit_code == 0
    assert "MY_KEY" in result.output
    assert "valid" in result.output


def test_get_no_expiry(runner: CliRunner, vault_env) -> None:
    vault, env = vault_env
    result = _run(runner, env, "get", "MY_KEY")
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_set_missing_key_exits_nonzero(runner: CliRunner, vault_env) -> None:
    vault, env = vault_env
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    result = _run(runner, env, "set", "MISSING_KEY", future)
    assert result.exit_code != 0


def test_set_invalid_datetime_exits_nonzero(runner: CliRunner, vault_env) -> None:
    vault, env = vault_env
    result = _run(runner, env, "set", "MY_KEY", "not-a-date")
    assert result.exit_code != 0


def test_remove_expiry(runner: CliRunner, vault_env) -> None:
    vault, env = vault_env
    future = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    _run(runner, env, "set", "MY_KEY", future)
    result = _run(runner, env, "remove", "MY_KEY")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_purge_expired(runner: CliRunner, vault_env) -> None:
    vault, env = vault_env
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    _run(runner, env, "set", "MY_KEY", past)
    result = _run(runner, env, "purge")
    assert result.exit_code == 0
    assert "MY_KEY" in result.output


def test_purge_nothing_expired(runner: CliRunner, vault_env) -> None:
    vault, env = vault_env
    result = _run(runner, env, "purge")
    assert result.exit_code == 0
    assert "No expired" in result.output
