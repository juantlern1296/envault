"""Tests for envault.freeze."""

from __future__ import annotations

import pytest

from envault.freeze import (
    FreezeError,
    assert_not_frozen,
    freeze_var,
    is_frozen,
    list_frozen,
    unfreeze_var,
)
from envault.vault import save_vault


PASSWORD = "testpass"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, PASSWORD, {"DB_URL": "postgres://localhost", "API_KEY": "abc123"})
    return path


def test_freeze_var_marks_key(vault_file):
    freeze_var(vault_file, PASSWORD, "DB_URL")
    assert is_frozen(vault_file, "DB_URL") is True


def test_freeze_var_missing_key_raises(vault_file):
    with pytest.raises(FreezeError, match="not found"):
        freeze_var(vault_file, PASSWORD, "NONEXISTENT")


def test_is_frozen_returns_false_when_not_frozen(vault_file):
    assert is_frozen(vault_file, "DB_URL") is False


def test_unfreeze_var_removes_freeze(vault_file):
    freeze_var(vault_file, PASSWORD, "API_KEY")
    assert is_frozen(vault_file, "API_KEY") is True
    unfreeze_var(vault_file, "API_KEY")
    assert is_frozen(vault_file, "API_KEY") is False


def test_unfreeze_var_not_frozen_raises(vault_file):
    with pytest.raises(FreezeError, match="not frozen"):
        unfreeze_var(vault_file, "DB_URL")


def test_list_frozen_returns_sorted(vault_file):
    freeze_var(vault_file, PASSWORD, "DB_URL")
    freeze_var(vault_file, PASSWORD, "API_KEY")
    result = list_frozen(vault_file)
    assert result == ["API_KEY", "DB_URL"]


def test_list_frozen_empty_when_none_frozen(vault_file):
    assert list_frozen(vault_file) == []


def test_assert_not_frozen_passes_when_unfrozen(vault_file):
    # Should not raise
    assert_not_frozen(vault_file, "DB_URL")


def test_assert_not_frozen_raises_when_frozen(vault_file):
    freeze_var(vault_file, PASSWORD, "DB_URL")
    with pytest.raises(FreezeError, match="frozen and cannot be modified"):
        assert_not_frozen(vault_file, "DB_URL")


def test_freeze_persists_across_calls(vault_file):
    freeze_var(vault_file, PASSWORD, "DB_URL")
    # Re-check in a fresh call (no in-memory state)
    assert is_frozen(vault_file, "DB_URL") is True
    assert is_frozen(vault_file, "API_KEY") is False
