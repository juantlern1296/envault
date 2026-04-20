import os
import pytest
from click.testing import CliRunner
from envault.cli import cli


@pytest.fixture
def vault_env(tmp_path, monkeypatch):
    vault_path = str(tmp_path / "test.vault")
    monkeypatch.setenv("ENVAULT_PASSWORD", "testpass")
    monkeypatch.setenv("ENVAULT_VAULT", vault_path)
    return vault_path


@pytest.fixture
def runner():
    return CliRunner()


def _set(runner, key, value):
    return runner.invoke(cli, ["set", key, value])


def test_export_dotenv(runner, vault_env):
    _set(runner, "FOO", "bar")
    result = runner.invoke(cli, ["export", "--format", "dotenv"])
    assert result.exit_code == 0
    assert 'FOO="bar"' in result.output


def test_export_json(runner, vault_env):
    _set(runner, "FOO", "bar")
    result = runner.invoke(cli, ["export", "--format", "json"])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert data["FOO"] == "bar"


def test_export_to_file(runner, vault_env, tmp_path):
    _set(runner, "KEY", "val")
    out_file = str(tmp_path / "out.env")
    result = runner.invoke(cli, ["export", "-o", out_file])
    assert result.exit_code == 0
    assert os.path.exists(out_file)
    content = open(out_file).read()
    assert "KEY" in content


def test_import_dotenv(runner, vault_env, tmp_path):
    env_file = tmp_path / "vars.env"
    env_file.write_text('IMPORTED="yes"\nANOTHER="value"\n')
    result = runner.invoke(cli, ["import", str(env_file)])
    assert result.exit_code == 0
    assert "Imported 2" in result.output
    get_result = runner.invoke(cli, ["get", "IMPORTED"])
    assert "yes" in get_result.output


def test_import_skips_existing(runner, vault_env, tmp_path):
    _set(runner, "EXISTING", "original")
    env_file = tmp_path / "vars.env"
    env_file.write_text('EXISTING="overwritten"\n')
    result = runner.invoke(cli, ["import", str(env_file)])
    assert "skipped 1" in result.output
    get_result = runner.invoke(cli, ["get", "EXISTING"])
    assert "original" in get_result.output


def test_import_overwrite_flag(runner, vault_env, tmp_path):
    _set(runner, "EXISTING", "original")
    env_file = tmp_path / "vars.env"
    env_file.write_text('EXISTING="overwritten"\n')
    runner.invoke(cli, ["import", "--overwrite", str(env_file)])
    get_result = runner.invoke(cli, ["get", "EXISTING"])
    assert "overwritten" in get_result.output
