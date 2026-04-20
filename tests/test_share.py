import pytest
import os
from click.testing import CliRunner
from envault.share import create_share_token, read_share_token, import_share_token
from envault.vault import set_var, get_var


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


PASSWORD = "vaultpass"
SHARE_PASS = "sharepass"


def test_create_and_read_share_token(vault_file):
    set_var(vault_file, PASSWORD, "API_KEY", "secret123")
    token = create_share_token(vault_file, PASSWORD, "API_KEY", SHARE_PASS)
    assert isinstance(token, str)
    assert len(token) > 0
    data = read_share_token(token, SHARE_PASS)
    assert data["key"] == "API_KEY"
    assert data["value"] == "secret123"


def test_create_share_token_missing_key_raises(vault_file):
    with pytest.raises(KeyError):
        create_share_token(vault_file, PASSWORD, "MISSING", SHARE_PASS)


def test_read_share_token_wrong_password_raises(vault_file):
    set_var(vault_file, PASSWORD, "FOO", "bar")
    token = create_share_token(vault_file, PASSWORD, "FOO", SHARE_PASS)
    with pytest.raises(ValueError):
        read_share_token(token, "wrongpass")


def test_read_share_token_corrupted_raises():
    with pytest.raises(ValueError):
        read_share_token("notavalidtoken!!", SHARE_PASS)


def test_import_share_token(vault_file, tmp_path):
    set_var(vault_file, PASSWORD, "DB_URL", "postgres://localhost/db")
    token = create_share_token(vault_file, PASSWORD, "DB_URL", SHARE_PASS)
    dest = str(tmp_path / "dest_vault.json")
    key = import_share_token(dest, PASSWORD, token, SHARE_PASS)
    assert key == "DB_URL"
    assert get_var(dest, PASSWORD, "DB_URL") == "postgres://localhost/db"


def test_import_share_token_override_key(vault_file, tmp_path):
    set_var(vault_file, PASSWORD, "OLD_KEY", "value42")
    token = create_share_token(vault_file, PASSWORD, "OLD_KEY", SHARE_PASS)
    dest = str(tmp_path / "dest2.json")
    key = import_share_token(dest, PASSWORD, token, SHARE_PASS, override_key="NEW_KEY")
    assert key == "NEW_KEY"
    assert get_var(dest, PASSWORD, "NEW_KEY") == "value42"
