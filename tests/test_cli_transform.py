"""CLI tests for envault.cli_transform."""
import os
import pytest
from click.testing import CliRunner

from envault.cli_transform import transform_group
from envault.vault import save_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_env(tmp_path):
    path = tmp_path / "vault.enc"
    save_vault(str(path), "testpw", {"MY_KEY": "hello", "SPACED": "  hi  "})
    env = {"ENVAULT_PATH": str(path), "ENVAULT_PASSWORD": "testpw"}
    return env


def _run(runner, vault_env, *args):
    return runner.invoke(transform_group, list(args), env=vault_env, catch_exceptions=False)


def test_echo_upper(runner, vault_env):
    result = runner.invoke(transform_group, ["echo", "hello", "upper"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "HELLO" in result.output


def test_echo_pipeline(runner, vault_env):
    result = runner.invoke(
        transform_group, ["echo", "  world  ", "strip", "upper"], catch_exceptions=False
    )
    assert result.exit_code == 0
    assert "WORLD" in result.output


def test_echo_unknown_transform_exits_nonzero(runner, vault_env):
    result = runner.invoke(transform_group, ["echo", "val", "noop_fake"])
    assert result.exit_code != 0


def test_run_transforms_and_saves(runner, vault_env):
    result = _run(runner, vault_env, "run", "MY_KEY", "upper")
    assert result.exit_code == 0
    assert "MY_KEY" in result.output
    assert "HELLO" in result.output


def test_run_dry_run_does_not_save(runner, vault_env):
    result = _run(runner, vault_env, "run", "MY_KEY", "upper", "--dry-run")
    assert result.exit_code == 0
    assert "dry-run" in result.output
    assert "HELLO" in result.output


def test_run_missing_key_exits_nonzero(runner, vault_env):
    result = runner.invoke(
        transform_group,
        ["run", "DOES_NOT_EXIST", "upper"],
        env=vault_env,
    )
    assert result.exit_code != 0


def test_list_shows_transforms(runner, vault_env):
    result = runner.invoke(transform_group, ["list"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "upper" in result.output
    assert "lower" in result.output
    assert "base64encode" in result.output
