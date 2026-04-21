"""Tests for envault.cascade."""

from __future__ import annotations

import pytest

from envault.vault import set_var, get_var
from envault.cascade import cascade_var, cascade_all, CascadeError


PASSWORD = "test-pass"


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "vault.enc")


def test_cascade_copies_value(vault_file):
    set_var(vault_file, PASSWORD, "SRC", "hello")
    result = cascade_var(vault_file, PASSWORD, "SRC", ["DST1", "DST2"])
    assert get_var(vault_file, PASSWORD, "DST1") == "hello"
    assert get_var(vault_file, PASSWORD, "DST2") == "hello"
    assert result.updated == ["DST1", "DST2"]
    assert result.skipped == []
    assert result.failed == []


def test_cascade_missing_source_raises(vault_file):
    with pytest.raises(CascadeError, match="Source key"):
        cascade_var(vault_file, PASSWORD, "MISSING", ["DST"])


def test_cascade_no_overwrite_skips_existing(vault_file):
    set_var(vault_file, PASSWORD, "SRC", "new_value")
    set_var(vault_file, PASSWORD, "EXISTING", "old_value")
    result = cascade_var(
        vault_file, PASSWORD, "SRC", ["EXISTING", "NEW"], overwrite=False
    )
    assert result.skipped == ["EXISTING"]
    assert result.updated == ["NEW"]
    assert get_var(vault_file, PASSWORD, "EXISTING") == "old_value"
    assert get_var(vault_file, PASSWORD, "NEW") == "new_value"


def test_cascade_overwrite_replaces_existing(vault_file):
    set_var(vault_file, PASSWORD, "SRC", "updated")
    set_var(vault_file, PASSWORD, "DST", "stale")
    result = cascade_var(vault_file, PASSWORD, "SRC", ["DST"], overwrite=True)
    assert result.updated == ["DST"]
    assert get_var(vault_file, PASSWORD, "DST") == "updated"


def test_cascade_all_multiple_sources(vault_file):
    set_var(vault_file, PASSWORD, "A", "alpha")
    set_var(vault_file, PASSWORD, "B", "beta")
    results = cascade_all(
        vault_file, PASSWORD, {"A": ["A1", "A2"], "B": ["B1"]}
    )
    assert len(results) == 2
    assert get_var(vault_file, PASSWORD, "A1") == "alpha"
    assert get_var(vault_file, PASSWORD, "A2") == "alpha"
    assert get_var(vault_file, PASSWORD, "B1") == "beta"


def test_cascade_source_key_recorded_in_result(vault_file):
    set_var(vault_file, PASSWORD, "KEY", "val")
    result = cascade_var(vault_file, PASSWORD, "KEY", ["T"])
    assert result.source_key == "KEY"
