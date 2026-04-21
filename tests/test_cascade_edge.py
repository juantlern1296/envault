"""Edge-case tests for envault.cascade."""

from __future__ import annotations

import pytest

from envault.vault import set_var, get_var
from envault.cascade import cascade_var, cascade_all, CascadeError


PASSWORD = "edge-pass"


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "vault.enc")


def test_cascade_empty_target_list_returns_empty_result(vault_file):
    set_var(vault_file, PASSWORD, "SRC", "v")
    result = cascade_var(vault_file, PASSWORD, "SRC", [])
    assert result.updated == []
    assert result.skipped == []
    assert result.failed == []


def test_cascade_empty_string_value(vault_file):
    set_var(vault_file, PASSWORD, "SRC", "")
    cascade_var(vault_file, PASSWORD, "SRC", ["DST"])
    assert get_var(vault_file, PASSWORD, "DST") == ""


def test_cascade_source_equals_target_overwrites_itself(vault_file):
    set_var(vault_file, PASSWORD, "KEY", "same")
    result = cascade_var(vault_file, PASSWORD, "KEY", ["KEY"])
    assert result.updated == ["KEY"]
    assert get_var(vault_file, PASSWORD, "KEY") == "same"


def test_cascade_all_empty_mapping_returns_empty(vault_file):
    results = cascade_all(vault_file, PASSWORD, {})
    assert results == []


def test_cascade_all_missing_source_raises(vault_file):
    set_var(vault_file, PASSWORD, "GOOD", "ok")
    with pytest.raises(CascadeError):
        cascade_all(vault_file, PASSWORD, {"GOOD": ["X"], "BAD": ["Y"]})


def test_cascade_preserves_other_keys(vault_file):
    set_var(vault_file, PASSWORD, "SRC", "val")
    set_var(vault_file, PASSWORD, "UNRELATED", "untouched")
    cascade_var(vault_file, PASSWORD, "SRC", ["DST"])
    assert get_var(vault_file, PASSWORD, "UNRELATED") == "untouched"
