"""CLI tests for the annotate command group."""
import pytest
from click.testing import CliRunner

from envault.cli_annotate import annotate_group
from envault.vault import save_vault, set_var

PASSWORD = "test-secret"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_env(tmp_path):
    p = str(tmp_path / "vault.enc")
    save_vault(p, PASSWORD, {})
    set_var(p, PASSWORD, "DB_HOST", "localhost")
    return p


def _run(runner, vault_env, *args):
    return runner.invoke(
        annotate_group,
        list(args) + ["--vault", vault_env],
        env={"ENVAULT_PASSWORD": PASSWORD},
        catch_exceptions=False,
    )


def test_set_and_get(runner, vault_env):
    result = _run(runner, vault_env, "set", "DB_HOST", "primary host")
    assert result.exit_code == 0
    result = _run(runner, vault_env, "get", "DB_HOST")
    assert result.exit_code == 0
    assert "primary host" in result.output


def test_get_missing_annotation_exits_nonzero(runner, vault_env):
    result = _run(runner, vault_env, "get", "DB_HOST")
    assert result.exit_code != 0


def test_set_missing_key_exits_nonzero(runner, vault_env):
    result = _run(runner, vault_env, "set", "GHOST_KEY", "note")
    assert result.exit_code != 0


def test_remove_annotation(runner, vault_env):
    _run(runner, vault_env, "set", "DB_HOST", "a note")
    result = _run(runner, vault_env, "remove", "DB_HOST")
    assert result.exit_code == 0
    result = _run(runner, vault_env, "get", "DB_HOST")
    assert result.exit_code != 0


def test_list_shows_annotations(runner, vault_env):
    _run(runner, vault_env, "set", "DB_HOST", "host note")
    result = _run(runner, vault_env, "list")
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "host note" in result.output


def test_list_empty(runner, vault_env):
    result = _run(runner, vault_env, "list")
    assert result.exit_code == 0
    assert "No annotations" in result.output
