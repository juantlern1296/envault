"""CLI tests for the compress commands."""

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_compress import compress_group
from envault.vault import save_vault, load_vault
from envault.compress import _is_compressed


PASSWORD = "cli-test-pass"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_env(tmp_path: Path):
    path = tmp_path / "vault.enc"
    save_vault(path, PASSWORD, {"FOO": "bar", "BAZ": "qux"})
    env = {
        "ENVAULT_PATH": str(path),
        "ENVAULT_PASSWORD": PASSWORD,
    }
    return path, env


def _run(runner, env, *args):
    return runner.invoke(compress_group, list(args), env=env, catch_exceptions=False)


def test_pack_compresses_values(runner, vault_env):
    path, env = vault_env
    result = _run(runner, env, "pack", "--vault", str(path))
    assert result.exit_code == 0
    assert "Compressed 2" in result.output
    data = load_vault(path, PASSWORD)
    assert all(_is_compressed(v) for v in data.values())


def test_unpack_decompresses_values(runner, vault_env):
    path, env = vault_env
    _run(runner, env, "pack", "--vault", str(path))
    result = _run(runner, env, "unpack", "--vault", str(path))
    assert result.exit_code == 0
    assert "Decompressed 2" in result.output
    data = load_vault(path, PASSWORD)
    assert data["FOO"] == "bar"
    assert data["BAZ"] == "qux"


def test_ratio_shows_output(runner, vault_env):
    path, env = vault_env
    _run(runner, env, "pack", "--vault", str(path))
    result = _run(runner, env, "ratio", "--vault", str(path))
    assert result.exit_code == 0
    assert "FOO" in result.output
    assert "BAZ" in result.output


def test_pack_missing_vault_exits_nonzero(runner, tmp_path):
    missing = str(tmp_path / "nope.enc")
    env = {"ENVAULT_PATH": missing, "ENVAULT_PASSWORD": PASSWORD}
    result = runner.invoke(compress_group, ["pack", "--vault", missing], env=env)
    assert result.exit_code != 0


def test_ratio_no_compressed_values(runner, vault_env):
    path, env = vault_env
    result = _run(runner, env, "ratio", "--vault", str(path))
    assert result.exit_code == 0
    assert "No compressed" in result.output
