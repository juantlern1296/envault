import pytest
from envault.diff import diff_vaults, diff_vault_files, DiffEntry
from envault.vault import save_vault
import os


def test_diff_added():
    old = {}
    new = {"FOO": "bar"}
    result = diff_vaults(old, new)
    assert len(result) == 1
    assert result[0].status == "added"
    assert result[0].key == "FOO"
    assert result[0].new_value == "bar"


def test_diff_removed():
    old = {"FOO": "bar"}
    new = {}
    result = diff_vaults(old, new)
    assert len(result) == 1
    assert result[0].status == "removed"
    assert result[0].old_value == "bar"


def test_diff_changed():
    old = {"FOO": "bar"}
    new = {"FOO": "baz"}
    result = diff_vaults(old, new)
    assert len(result) == 1
    assert result[0].status == "changed"
    assert result[0].old_value == "bar"
    assert result[0].new_value == "baz"


def test_diff_unchanged_hidden_by_default():
    old = {"FOO": "bar"}
    new = {"FOO": "bar"}
    result = diff_vaults(old, new)
    assert result == []


def test_diff_unchanged_shown_when_requested():
    old = {"FOO": "bar"}
    new = {"FOO": "bar"}
    result = diff_vaults(old, new, show_unchanged=True)
    assert len(result) == 1
    assert result[0].status == "unchanged"


def test_diff_sorted_keys():
    old = {"Z": "1", "A": "2"}
    new = {"Z": "1", "B": "3"}
    result = diff_vaults(old, new)
    keys = [e.key for e in result]
    assert keys == sorted(keys)


def test_diff_vault_files(tmp_path):
    p1 = str(tmp_path / "v1.vault")
    p2 = str(tmp_path / "v2.vault")
    pw = "secret"
    save_vault(p1, {"A": "1", "B": "2"}, pw)
    save_vault(p2, {"A": "1", "C": "3"}, pw)
    result = diff_vault_files(p1, p2, pw)
    statuses = {e.key: e.status for e in result}
    assert statuses["B"] == "removed"
    assert statuses["C"] == "added"
    assert "A" not in statuses
