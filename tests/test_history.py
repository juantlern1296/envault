"""Tests for envault.history."""
import pytest
import time
from pathlib import Path
from envault.history import record_change, get_history, clear_history, _history_path


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.enc")


def test_get_history_empty(vault_file):
    assert get_history(vault_file, "FOO") == []


def test_record_set_creates_entry(vault_file):
    record_change(vault_file, "FOO", "set")
    history = get_history(vault_file, "FOO")
    assert len(history) == 1
    assert history[0]["action"] == "set"
    assert "ts" in history[0]


def test_record_delete_stores_old_value(vault_file):
    record_change(vault_file, "BAR", "delete", old_value="secret123")
    history = get_history(vault_file, "BAR")
    assert history[0]["action"] == "delete"
    assert history[0]["old_value"] == "secret123"


def test_multiple_changes_ordered(vault_file):
    record_change(vault_file, "KEY", "set")
    time.sleep(0.01)
    record_change(vault_file, "KEY", "set")
    history = get_history(vault_file, "KEY")
    assert len(history) == 2
    assert history[0]["ts"] <= history[1]["ts"]


def test_clear_history_for_key(vault_file):
    record_change(vault_file, "A", "set")
    record_change(vault_file, "B", "set")
    clear_history(vault_file, "A")
    assert get_history(vault_file, "A") == []
    assert len(get_history(vault_file, "B")) == 1


def test_clear_all_history(vault_file):
    record_change(vault_file, "A", "set")
    record_change(vault_file, "B", "set")
    clear_history(vault_file)
    hp = _history_path(vault_file)
    assert not hp.exists()


def test_history_file_location(vault_file):
    record_change(vault_file, "X", "set")
    hp = _history_path(vault_file)
    assert hp.exists()
    assert hp.name == "vault.history.json"
