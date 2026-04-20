"""Tests for envault.import_check module."""

import pytest

from envault.import_check import (
    ConflictEntry,
    check_import_conflicts,
    summarise_conflicts,
)
from envault.vault import save_vault


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.enc")


PASSWORD = "hunter2"


def _populate(vault_file, data):
    save_vault(vault_file, PASSWORD, data)


def test_no_conflicts_when_vault_empty(vault_file):
    conflicts = check_import_conflicts(vault_file, PASSWORD, {"KEY": "val"})
    assert conflicts == []


def test_no_conflicts_when_keys_are_new(vault_file):
    _populate(vault_file, {"EXISTING": "foo"})
    conflicts = check_import_conflicts(vault_file, PASSWORD, {"NEW_KEY": "bar"})
    assert conflicts == []


def test_detects_conflicting_key(vault_file):
    _populate(vault_file, {"DB_URL": "old_value"})
    conflicts = check_import_conflicts(vault_file, PASSWORD, {"DB_URL": "new_value"})
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c.key == "DB_URL"
    assert c.existing_value == "old_value"
    assert c.incoming_value == "new_value"
    assert c.is_duplicate is False


def test_detects_duplicate_key(vault_file):
    _populate(vault_file, {"SECRET": "same"})
    conflicts = check_import_conflicts(vault_file, PASSWORD, {"SECRET": "same"})
    assert len(conflicts) == 1
    assert conflicts[0].is_duplicate is True


def test_multiple_conflicts(vault_file):
    _populate(vault_file, {"A": "1", "B": "2", "C": "3"})
    incoming = {"A": "1", "B": "99", "D": "4"}
    conflicts = check_import_conflicts(vault_file, PASSWORD, incoming)
    keys = {c.key for c in conflicts}
    assert keys == {"A", "B"}
    by_key = {c.key: c for c in conflicts}
    assert by_key["A"].is_duplicate is True
    assert by_key["B"].is_duplicate is False


def test_missing_vault_file_treated_as_empty(tmp_path):
    missing = str(tmp_path / "does_not_exist.enc")
    conflicts = check_import_conflicts(missing, PASSWORD, {"X": "y"})
    assert conflicts == []


def test_summarise_no_conflicts():
    assert summarise_conflicts([]) == "No conflicts found."


def test_summarise_shows_duplicate_and_conflict():
    entries = [
        ConflictEntry("A", "same", "same", is_duplicate=True),
        ConflictEntry("B", "old", "new", is_duplicate=False),
    ]
    summary = summarise_conflicts(entries)
    assert "[duplicate]" in summary
    assert "[conflict]" in summary
    assert "A" in summary
    assert "B" in summary
    assert "'old'" in summary
    assert "'new'" in summary
