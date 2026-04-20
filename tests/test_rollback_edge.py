"""Edge-case tests for rollback."""

import pytest

from envault.vault import save_vault, load_vault
from envault.history import record_change
from envault.rollback import list_rollback_points, rollback_to, RollbackError


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.db")
    save_vault(path, "pw", {})
    return path


def test_rollback_negative_index_raises(vault_file):
    record_change(vault_file, "set", "K", new_value="v", old_value=None)
    with pytest.raises(RollbackError, match="out of range"):
        rollback_to(vault_file, "pw", -1)


def test_rollback_leaves_other_keys_intact(vault_file):
    save_vault(vault_file, "pw", {"OTHER": "keep", "FOO": "new"})
    record_change(vault_file, "set", "FOO", new_value="new", old_value=None)
    rollback_to(vault_file, "pw", 0)
    data = load_vault(vault_file, "pw")
    assert "OTHER" in data
    assert data["OTHER"] == "keep"
    assert "FOO" not in data


def test_rollback_delete_with_no_old_value_does_nothing(vault_file):
    save_vault(vault_file, "pw", {})
    record_change(vault_file, "delete", "GHOST", new_value=None, old_value=None)
    rollback_to(vault_file, "pw", 0)
    data = load_vault(vault_file, "pw")
    assert "GHOST" not in data


def test_multiple_rollback_points_applied_sequentially(vault_file):
    save_vault(vault_file, "pw", {"FOO": "v2"})
    record_change(vault_file, "set", "FOO", new_value="v1", old_value=None)
    record_change(vault_file, "set", "FOO", new_value="v2", old_value="v1")

    # Roll back the most recent change (v2 -> v1)
    rollback_to(vault_file, "pw", 0)
    data = load_vault(vault_file, "pw")
    assert data["FOO"] == "v1"

    # Roll back again (v1 -> gone)
    rollback_to(vault_file, "pw", 0)
    data = load_vault(vault_file, "pw")
    assert "FOO" not in data


def test_list_rollback_points_count(vault_file):
    for i in range(4):
        record_change(vault_file, "set", f"K{i}", new_value="v", old_value=None)
    points = list_rollback_points(vault_file, "pw")
    assert len(points) == 4
