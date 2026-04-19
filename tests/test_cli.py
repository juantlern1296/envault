"""Tests for the CLI commands."""

import os
import pytest
from click.testing import CliRunner

from envault.cli import cli

PASSWORD = "testpass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_env(tmp_path, monkeypatch):
    vault_path = str(tmp_path / ".envault")
    monkeypatch.setenv("ENVAULT_PASSWORD", PASSWORD)
    monkeypatch.setenv("ENVAULT_FILE", vault_path)
    return vault_path


def test_set_and_get(runner, vault_env):
    result = runner.invoke(cli, ["set", "MY_KEY", "my_value"])
    assert result.exit_code == 0
    assert "MY_KEY" in result.output

    result = runner.invoke(cli, ["get", "MY_KEY"])
    assert result.exit_code == 0
    assert "my_value" in result.output


def test_get_missing_key_exits_nonzero(runner, vault_env):
    result = runner.invoke(cli, ["get", "MISSING"])
    assert result.exit_code != 0


def test_delete_existing_key(runner, vault_env):
    runner.invoke(cli, ["set", "DEL_ME", "bye"])
    result = runner.invoke(cli, ["delete", "DEL_ME"])
    assert result.exit_code == 0
    assert "DEL_ME" in result.output


def test_delete_missing_key_exits_nonzero(runner, vault_env):
    result = runner.invoke(cli, ["delete", "GHOST"])
    assert result.exit_code != 0


def test_list_empty_vault(runner, vault_env):
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "empty" in result.output.lower()


def test_list_shows_all_keys(runner, vault_env):
    runner.invoke(cli, ["set", "ALPHA", "1"])
    runner.invoke(cli, ["set", "BETA", "2"])
    result = runner.invoke(cli, ["list"])
    assert "ALPHA=1" in result.output
    assert "BETA=2" in result.output
