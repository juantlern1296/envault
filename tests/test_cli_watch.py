"""Tests for envault.cli_watch CLI commands."""

import time
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_watch import watch_group
from envault.vault import save_vault, set_var


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_env(tmp_path: Path):
    vault = tmp_path / "vault.enc"
    password = "watchpass"
    save_vault(str(vault), password, {})
    return str(vault), password


def _run(runner, vault, password, *extra_args):
    return runner.invoke(
        watch_group,
        ["start", "--vault", vault, "--password", password, "--interval", "0.05", *extra_args],
    )


def test_watch_requires_vault(runner: CliRunner) -> None:
    result = runner.invoke(watch_group, ["start", "--password", "pw"])
    assert result.exit_code != 0
    assert "vault path required" in result.output


def test_watch_missing_vault_file(runner: CliRunner, tmp_path: Path) -> None:
    vault = str(tmp_path / "no.enc")
    # We patch time.sleep to raise KeyboardInterrupt immediately so the loop exits
    with patch("time.sleep", side_effect=KeyboardInterrupt):
        result = runner.invoke(
            watch_group,
            ["start", "--vault", vault, "--password", "pw", "--interval", "0.05"],
        )
    assert result.exit_code == 0
    assert "Watching" in result.output


def test_watch_prompts_for_password(runner: CliRunner, vault_env) -> None:
    vault, password = vault_env
    with patch("time.sleep", side_effect=KeyboardInterrupt):
        result = runner.invoke(
            watch_group,
            ["start", "--vault", vault, "--interval", "0.05"],
            input=f"{password}\n",
        )
    assert result.exit_code == 0
    assert "Watching" in result.output
