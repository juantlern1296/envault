"""Tests for envault.checkpoint."""

from __future__ import annotations

import pytest

from envault.vault import save_vault, set_var
from envault.checkpoint import (
    CheckpointError,
    create_checkpoint,
    delete_checkpoint,
    list_checkpoints,
    restore_checkpoint,
)

PASSWORD = "test-pass"


@pytest.fixture()
def vault_file(tmp_path):
    p = str(tmp_path / "vault.enc")
    save_vault(p, PASSWORD, {})
    return p


def test_create_checkpoint_stores_state(vault_file):
    set_var(vault_file, PASSWORD, "KEY", "value1")
    create_checkpoint(vault_file, PASSWORD, "v1")
    assert "v1" in list_checkpoints(vault_file)


def test_list_checkpoints_empty(vault_file):
    assert list_checkpoints(vault_file) == []


def test_list_checkpoints_multiple(vault_file):
    set_var(vault_file, PASSWORD, "A", "1")
    create_checkpoint(vault_file, PASSWORD, "alpha")
    set_var(vault_file, PASSWORD, "B", "2")
    create_checkpoint(vault_file, PASSWORD, "beta")
    names = list_checkpoints(vault_file)
    assert names == ["alpha", "beta"]


def test_restore_checkpoint_returns_correct_state(vault_file):
    set_var(vault_file, PASSWORD, "X", "hello")
    create_checkpoint(vault_file, PASSWORD, "snap")
    set_var(vault_file, PASSWORD, "X", "changed")
    state = restore_checkpoint(vault_file, PASSWORD, "snap")
    assert state["X"] == "hello"


def test_restore_checkpoint_missing_raises(vault_file):
    with pytest.raises(CheckpointError, match="not found"):
        restore_checkpoint(vault_file, PASSWORD, "ghost")


def test_delete_checkpoint_removes_entry(vault_file):
    create_checkpoint(vault_file, PASSWORD, "tmp")
    delete_checkpoint(vault_file, "tmp")
    assert "tmp" not in list_checkpoints(vault_file)


def test_delete_missing_checkpoint_raises(vault_file):
    with pytest.raises(CheckpointError, match="not found"):
        delete_checkpoint(vault_file, "nope")


def test_create_checkpoint_empty_name_raises(vault_file):
    with pytest.raises(CheckpointError, match="empty"):
        create_checkpoint(vault_file, PASSWORD, "   ")


def test_checkpoint_does_not_affect_live_vault(vault_file):
    set_var(vault_file, PASSWORD, "K", "original")
    create_checkpoint(vault_file, PASSWORD, "before")
    set_var(vault_file, PASSWORD, "K", "updated")
    # live vault should have the updated value
    from envault.vault import get_var
    assert get_var(vault_file, PASSWORD, "K") == "updated"
    # checkpoint should still have the old one
    state = restore_checkpoint(vault_file, PASSWORD, "before")
    assert state["K"] == "original"
