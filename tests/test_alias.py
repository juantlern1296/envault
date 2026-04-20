"""Tests for envault.alias."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import save_vault, load_vault
from envault.alias import (
    add_alias,
    remove_alias,
    resolve_alias,
    get_via_alias,
    list_aliases,
)

PASSWORD = "test-password"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "vault.enc"
    save_vault(path, PASSWORD, {"MY_KEY": "hello", "OTHER": "world"})
    return path


def test_add_alias_creates_mapping(vault_file: Path) -> None:
    add_alias(vault_file, PASSWORD, "mk", "MY_KEY")
    aliases = list_aliases(vault_file, PASSWORD)
    assert aliases["mk"] == "MY_KEY"


def test_add_alias_missing_key_raises(vault_file: Path) -> None:
    with pytest.raises(KeyError, match="MISSING"):
        add_alias(vault_file, PASSWORD, "bad", "MISSING")


def test_resolve_alias_returns_key(vault_file: Path) -> None:
    add_alias(vault_file, PASSWORD, "mk", "MY_KEY")
    assert resolve_alias(vault_file, PASSWORD, "mk") == "MY_KEY"


def test_resolve_alias_unknown_returns_none(vault_file: Path) -> None:
    assert resolve_alias(vault_file, PASSWORD, "nope") is None


def test_get_via_alias_returns_value(vault_file: Path) -> None:
    add_alias(vault_file, PASSWORD, "mk", "MY_KEY")
    assert get_via_alias(vault_file, PASSWORD, "mk") == "hello"


def test_get_via_alias_missing_raises(vault_file: Path) -> None:
    with pytest.raises(KeyError, match="ghost"):
        get_via_alias(vault_file, PASSWORD, "ghost")


def test_remove_alias(vault_file: Path) -> None:
    add_alias(vault_file, PASSWORD, "mk", "MY_KEY")
    remove_alias(vault_file, PASSWORD, "mk")
    assert resolve_alias(vault_file, PASSWORD, "mk") is None


def test_remove_alias_missing_raises(vault_file: Path) -> None:
    with pytest.raises(KeyError, match="ghost"):
        remove_alias(vault_file, PASSWORD, "ghost")


def test_list_aliases_empty(vault_file: Path) -> None:
    assert list_aliases(vault_file, PASSWORD) == {}


def test_list_aliases_multiple(vault_file: Path) -> None:
    add_alias(vault_file, PASSWORD, "mk", "MY_KEY")
    add_alias(vault_file, PASSWORD, "ot", "OTHER")
    aliases = list_aliases(vault_file, PASSWORD)
    assert len(aliases) == 2
    assert aliases["ot"] == "OTHER"


def test_alias_does_not_appear_as_regular_key(vault_file: Path) -> None:
    add_alias(vault_file, PASSWORD, "mk", "MY_KEY")
    vault = load_vault(vault_file, PASSWORD)
    # aliases live under reserved namespace, not as top-level keys
    assert "mk" not in vault
