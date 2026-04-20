"""Tests for envault.pin module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import save_vault, load_vault
from envault.pin import (
    pin_var,
    unpin_var,
    is_pinned,
    list_pinned,
    assert_not_pinned,
)

PASSWORD = "test-password"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "vault.enc"
    save_vault(path, PASSWORD, {"FOO": "bar", "BAZ": "qux"})
    return path


def test_pin_var_marks_key(vault_file: Path) -> None:
    pin_var(vault_file, PASSWORD, "FOO")
    assert is_pinned(vault_file, PASSWORD, "FOO")


def test_unpin_var_removes_pin(vault_file: Path) -> None:
    pin_var(vault_file, PASSWORD, "FOO")
    unpin_var(vault_file, PASSWORD, "FOO")
    assert not is_pinned(vault_file, PASSWORD, "FOO")


def test_is_pinned_returns_false_when_not_pinned(vault_file: Path) -> None:
    assert not is_pinned(vault_file, PASSWORD, "FOO")


def test_pin_missing_key_raises(vault_file: Path) -> None:
    with pytest.raises(KeyError, match="MISSING"):
        pin_var(vault_file, PASSWORD, "MISSING")


def test_unpin_not_pinned_raises(vault_file: Path) -> None:
    with pytest.raises(KeyError, match="not pinned"):
        unpin_var(vault_file, PASSWORD, "FOO")


def test_list_pinned_returns_sorted(vault_file: Path) -> None:
    pin_var(vault_file, PASSWORD, "BAZ")
    pin_var(vault_file, PASSWORD, "FOO")
    assert list_pinned(vault_file, PASSWORD) == ["BAZ", "FOO"]


def test_list_pinned_empty_vault(vault_file: Path) -> None:
    assert list_pinned(vault_file, PASSWORD) == []


def test_assert_not_pinned_raises_when_pinned(vault_file: Path) -> None:
    pin_var(vault_file, PASSWORD, "FOO")
    with pytest.raises(ValueError, match="pinned"):
        assert_not_pinned(vault_file, PASSWORD, "FOO")


def test_assert_not_pinned_passes_when_not_pinned(vault_file: Path) -> None:
    # Should not raise
    assert_not_pinned(vault_file, PASSWORD, "FOO")


def test_pin_does_not_corrupt_other_vars(vault_file: Path) -> None:
    pin_var(vault_file, PASSWORD, "FOO")
    data = load_vault(vault_file, PASSWORD)
    assert data["FOO"] == "bar"
    assert data["BAZ"] == "qux"
