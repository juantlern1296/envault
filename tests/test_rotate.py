"""Tests for key rotation."""

import pytest
from click.testing import CliRunner
from envault.vault import load_vault, save_vault, set_var
from envault.rotate import rotate_key
from envault.cli_rotate import rotate_group


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    save_vault(path, "oldpass", {})
    return path


def test_rotate_reencrypts_data(vault_file):
    set_var(vault_file, "oldpass", "KEY", "value")
    count = rotate_key(vault_file, "oldpass", "newpass")
    assert count == 1
    # Old password should no longer work
    with pytest.raises(Exception):
        load_vault(vault_file, "oldpass")
    # New password should work
    data = load_vault(vault_file, "newpass")
    assert data["KEY"] == "value"


def test_rotate_empty_vault(vault_file):
    count = rotate_key(vault_file, "oldpass", "newpass")
    assert count == 0
    data = load_vault(vault_file, "newpass")
    assert data == {}


def test_rotate_missing_vault(tmp_path):
    with pytest.raises(FileNotFoundError):
        rotate_key(str(tmp_path / "missing.vault"), "a", "b")


def test_rotate_wrong_old_password(vault_file):
    with pytest.raises(Exception):
        rotate_key(vault_file, "wrongpass", "newpass")


def test_cli_rotate(vault_file):
    set_var(vault_file, "oldpass", "FOO", "bar")
    runner = CliRunner()
    result = runner.invoke(
        rotate_group,
        ["run", "--vault", vault_file, "--old-password", "oldpass", "--new-password", "newpass"],
    )
    assert result.exit_code == 0
    assert "1 entry" in result.output
    data = load_vault(vault_file, "newpass")
    assert data["FOO"] == "bar"


def test_cli_rotate_wrong_password(vault_file):
    runner = CliRunner()
    result = runner.invoke(
        rotate_group,
        ["run", "--vault", vault_file, "--old-password", "bad", "--new-password", "newpass"],
    )
    assert result.exit_code != 0
