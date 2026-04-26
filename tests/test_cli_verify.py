"""Tests for envault.cli_verify."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envault.cli_verify import verify_group
from envault.vault import set_var, save_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_env(tmp_path):
    vp = str(tmp_path / "vault.env")
    save_vault(vp, {}, "secret")
    return {"ENVAULT_PATH": vp, "ENVAULT_PASSWORD": "secret"}


def _run(runner, vault_env, *args):
    return runner.invoke(verify_group, list(args), env=vault_env)


def test_run_empty_vault_exits_zero(runner, vault_env):
    result = _run(runner, vault_env, "run")
    assert result.exit_code == 0


def test_run_valid_vault_exits_zero(runner, vault_env):
    set_var(vault_env["ENVAULT_PATH"], "secret", "FOO", "bar")
    result = _run(runner, vault_env, "run")
    assert result.exit_code == 0
    assert "FOO" in result.output


def test_run_wrong_password_exits_nonzero(runner, vault_env, tmp_path):
    set_var(vault_env["ENVAULT_PATH"], "secret", "FOO", "bar")
    bad_env = {**vault_env, "ENVAULT_PASSWORD": "wrong"}
    result = _run(runner, bad_env, "run")
    assert result.exit_code != 0


def test_run_missing_vault_exits_nonzero(runner, tmp_path):
    env = {"ENVAULT_PATH": str(tmp_path / "nope.env"), "ENVAULT_PASSWORD": "x"}
    result = _run(runner, env, "run")
    assert result.exit_code != 0


def test_status_ok_message(runner, vault_env):
    set_var(vault_env["ENVAULT_PATH"], "secret", "A", "1")
    result = _run(runner, vault_env, "status")
    assert result.exit_code == 0
    assert "OK" in result.output


def test_run_quiet_flag_suppresses_passing(runner, vault_env):
    set_var(vault_env["ENVAULT_PATH"], "secret", "KEY", "val")
    result = _run(runner, vault_env, "run", "--quiet")
    assert result.exit_code == 0
    assert "KEY" not in result.output
