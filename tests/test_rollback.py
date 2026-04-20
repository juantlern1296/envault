"""Tests for envault.rollback."""

import pytest

from envault.vault import save_vault, load_vault
from envault.history import record_change
from envault.rollback import list_rollback_points, rollback_to, RollbackError


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.db")
    save_vault(path, "pw", {})
    return path


def test_list_empty_returns_empty(vault_file):
    points = list_rollback_points(vault_file, "pw")
    assert points == []


def test_list_returns_entries_newest_first(vault_file):
    record_change(vault_file, "set", "FOO", new_value="bar", old_value=None)
    record_change(vault_file, "set", "FOO", new_value="baz", old_value="bar")
    points = list_rollback_points(vault_file, "pw")
    assert len(points) == 2
    # Most recent first
    assert points[0]["old_value"] == "bar"
    assert points[1]["old_value"] is None


def test_rollback_undoes_set_to_new_key(vault_file):
    save_vault(vault_file, "pw", {"FOO": "bar"})
    record_change(vault_file, "set", "FOO", new_value="bar", old_value=None)
    rollback_to(vault_file, "pw", 0)
    data = load_vault(vault_file, "pw")
    assert "FOO" not in data


def test_rollback_restores_old_value(vault_file):
    save_vault(vault_file, "pw", {"FOO": "baz"})
    record_change(vault_file, "set", "FOO", new_value="baz", old_value="bar")
    rollback_to(vault_file, "pw", 0)
    data = load_vault(vault_file, "pw")
    assert data["FOO"] == "bar"


def test_rollback_undoes_delete(vault_file):
    save_vault(vault_file, "pw", {})
    record_change(vault_file, "delete", "FOO", new_value=None, old_value="original")
    rollback_to(vault_file, "pw", 0)
    data = load_vault(vault_file, "pw")
    assert data["FOO"] == "original"


def test_rollback_out_of_range_raises(vault_file):
    record_change(vault_file, "set", "FOO", new_value="v", old_value=None)
    with pytest.raises(RollbackError, match="out of range"):
        rollback_to(vault_file, "pw", 5)


def test_rollback_no_points_raises(vault_file):
    with pytest.raises(RollbackError, match="No rollback points"):
        rollback_to(vault_file, "pw", 0)
