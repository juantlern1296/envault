"""CLI tests for the cascade push command."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envault.cli_cascade import cascade_group
from envault.vault import set_var, get_var


PASSWORD = "cli-test-pass"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_env(tmp_path):
    vault = str(tmp_path / "vault.enc")
    env = {"ENVAULT_PATH": vault, "ENVAULT_PASSWORD": PASSWORD}
    return vault, env


def _run(runner, vault_env, *args):
    vault, env = vault_env
    return runner.invoke(cascade_group, list(args), env=env)


def test_push_copies_value(runner, vault_env):
    vault, env = vault_env
    set_var(vault, PASSWORD, "SRC", "propagated")
    result = _run(runner, vault_env, "push", "SRC", "DST1", "DST2")
    assert result.exit_code == 0
    assert "updated: DST1" in result.output
    assert "updated: DST2" in result.output
    assert get_var(vault, PASSWORD, "DST1") == "propagated"


def test_push_missing_source_exits_nonzero(runner, vault_env):
    result = _run(runner, vault_env, "push", "MISSING", "DST")
    assert result.exit_code != 0


def test_push_no_overwrite_skips(runner, vault_env):
    vault, env = vault_env
    set_var(vault, PASSWORD, "SRC", "new")
    set_var(vault, PASSWORD, "DST", "old")
    result = _run(runner, vault_env, "push", "--no-overwrite", "SRC", "DST")
    assert result.exit_code == 0
    assert "skipped" in result.output
    assert get_var(vault, PASSWORD, "DST") == "old"
