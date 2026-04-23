"""CLI tests for migrate commands."""

import pytest
from click.testing import CliRunner

from envault.cli_migrate import migrate_group
from envault.migrate import _MIGRATIONS, register_migration
from envault.vault import save_vault


@pytest.fixture(autouse=True)
def _clean_registry():
    original = dict(_MIGRATIONS)
    yield
    _MIGRATIONS.clear()
    _MIGRATIONS.update(original)


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_env(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, "secret", {})
    return {"ENVAULT_PATH": path, "ENVAULT_PASSWORD": "secret"}


def _run(runner, vault_env, *args):
    return runner.invoke(migrate_group, list(args), env=vault_env, catch_exceptions=False)


def test_run_no_migrations_prints_message(runner, vault_env):
    result = _run(runner, vault_env, "run")
    assert result.exit_code == 0
    assert "no migrations" in result.output


def test_run_applies_and_prints(runner, vault_env):
    @register_migration("cli_v1")
    def _(data):
        data["A"] = "1"
        return data

    result = _run(runner, vault_env, "run")
    assert result.exit_code == 0
    assert "applied" in result.output
    assert "cli_v1" in result.output


def test_status_shows_pending(runner, vault_env):
    @register_migration("cli_v2")
    def _(data):
        return data

    result = _run(runner, vault_env, "status")
    assert result.exit_code == 0
    assert "pending" in result.output
    assert "cli_v2" in result.output


def test_run_error_exits_nonzero(runner, vault_env):
    result = runner.invoke(
        migrate_group,
        ["run", "--version", "does_not_exist"],
        env=vault_env,
        catch_exceptions=False,
    )
    assert result.exit_code != 0
