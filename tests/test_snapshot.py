import pytest
import os
from pathlib import Path
from envault.vault import save_vault
from envault.snapshot import (
    create_snapshot, list_snapshots, restore_snapshot,
    delete_snapshot, _snapshots_path
)

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / "vault.enc"
    save_vault(str(p), PASSWORD, {})
    return str(p)


def _populate(vault_file, vars_):
    save_vault(vault_file, PASSWORD, vars_)


def test_create_snapshot_stores_state(vault_file):
    _populate(vault_file, {"A": "1", "B": "2"})
    create_snapshot(vault_file, PASSWORD, "snap1")
    snaps = list_snapshots(vault_file)
    assert len(snaps) == 1
    assert snaps[0]["name"] == "snap1"
    assert snaps[0]["count"] == 2


def test_snapshots_file_created(vault_file):
    create_snapshot(vault_file, PASSWORD, "s")
    assert _snapshots_path(vault_file).exists()


def test_list_empty(vault_file):
    assert list_snapshots(vault_file) == []


def test_list_sorted_by_time(vault_file, monkeypatch):
    import envault.snapshot as sm
    times = iter([100.0, 200.0])
    monkeypatch.setattr(sm, "time", type("T", (), {"time": staticmethod(lambda: next(times))})())
    create_snapshot(vault_file, PASSWORD, "first")
    create_snapshot(vault_file, PASSWORD, "second")
    snaps = list_snapshots(vault_file)
    assert snaps[0]["name"] == "first"
    assert snaps[1]["name"] == "second"


def test_restore_snapshot(vault_file):
    _populate(vault_file, {"X": "original"})
    create_snapshot(vault_file, PASSWORD, "backup")
    _populate(vault_file, {"X": "changed", "Y": "new"})
    restore_snapshot(vault_file, PASSWORD, "backup")
    from envault.vault import load_vault
    vars_ = load_vault(vault_file, PASSWORD)
    assert vars_ == {"X": "original"}


def test_restore_missing_snapshot_raises(vault_file):
    with pytest.raises(KeyError):
        restore_snapshot(vault_file, PASSWORD, "nope")


def test_delete_snapshot(vault_file):
    create_snapshot(vault_file, PASSWORD, "to_del")
    delete_snapshot(vault_file, "to_del")
    assert list_snapshots(vault_file) == []


def test_delete_missing_snapshot_raises(vault_file):
    with pytest.raises(KeyError):
        delete_snapshot(vault_file, "ghost")
