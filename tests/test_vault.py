"""Tests for vault.py — encrypted env var storage."""

import pytest
from pathlib import Path

from envault.vault import load_vault, save_vault, set_var, get_var, delete_var, list_vars
from envault.crypto import decrypt

PASSWORD = "hunter2"


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / ".envault")


def test_load_empty_vault_returns_empty_dict(vault_file):
    result = load_vault(PASSWORD, vault_file)
    assert result == {}


def test_save_and_load_roundtrip(vault_file):
    data = {"API_KEY": "abc123", "DEBUG": "true"}
    save_vault(data, PASSWORD, vault_file)
    loaded = load_vault(PASSWORD, vault_file)
    assert loaded == data


def test_vault_file_is_encrypted_on_disk(vault_file):
    save_vault({"SECRET": "mysecret"}, PASSWORD, vault_file)
    raw = Path(vault_file).read_text()
    assert "mysecret" not in raw
    assert "SECRET" not in raw


def test_set_var_creates_entry(vault_file):
    set_var("FOO", "bar", PASSWORD, vault_file)
    assert get_var("FOO", PASSWORD, vault_file) == "bar"


def test_set_var_updates_existing(vault_file):
    set_var("FOO", "bar", PASSWORD, vault_file)
    set_var("FOO", "baz", PASSWORD, vault_file)
    assert get_var("FOO", PASSWORD, vault_file) == "baz"


def test_get_var_missing_key_returns_none(vault_file):
    assert get_var("MISSING", PASSWORD, vault_file) is None


def test_delete_var_removes_key(vault_file):
    set_var("TO_DELETE", "gone", PASSWORD, vault_file)
    result = delete_var("TO_DELETE", PASSWORD, vault_file)
    assert result is True
    assert get_var("TO_DELETE", PASSWORD, vault_file) is None


def test_delete_var_nonexistent_returns_false(vault_file):
    assert delete_var("NOPE", PASSWORD, vault_file) is False


def test_list_vars_returns_all(vault_file):
    set_var("A", "1", PASSWORD, vault_file)
    set_var("B", "2", PASSWORD, vault_file)
    result = list_vars(PASSWORD, vault_file)
    assert result == {"A": "1", "B": "2"}
