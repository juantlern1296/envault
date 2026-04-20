"""Tests for envault/namespace.py"""

import pytest
from envault.vault import save_vault
from envault.namespace import (
    ns_set, ns_get, ns_delete, list_namespaces, ns_list_vars, ns_clear, SEP,
)


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "vault.enc"
    save_vault(str(path), "pass", {})
    return str(path)


def test_set_and_get(vault_file):
    ns_set(vault_file, "pass", "prod", "DB_URL", "postgres://localhost/db")
    assert ns_get(vault_file, "pass", "prod", "DB_URL") == "postgres://localhost/db"


def test_get_missing_key_raises(vault_file):
    with pytest.raises(KeyError):
        ns_get(vault_file, "pass", "prod", "MISSING")


def test_delete_var(vault_file):
    ns_set(vault_file, "pass", "prod", "API_KEY", "secret")
    ns_delete(vault_file, "pass", "prod", "API_KEY")
    with pytest.raises(KeyError):
        ns_get(vault_file, "pass", "prod", "API_KEY")


def test_delete_missing_raises(vault_file):
    with pytest.raises(KeyError):
        ns_delete(vault_file, "pass", "prod", "NOPE")


def test_list_namespaces_empty(vault_file):
    assert list_namespaces(vault_file, "pass") == []


def test_list_namespaces_multiple(vault_file):
    ns_set(vault_file, "pass", "prod", "A", "1")
    ns_set(vault_file, "pass", "staging", "B", "2")
    ns_set(vault_file, "pass", "dev", "C", "3")
    assert list_namespaces(vault_file, "pass") == ["dev", "prod", "staging"]


def test_list_namespaces_deduplicates(vault_file):
    ns_set(vault_file, "pass", "prod", "X", "1")
    ns_set(vault_file, "pass", "prod", "Y", "2")
    assert list_namespaces(vault_file, "pass") == ["prod"]


def test_ns_list_vars(vault_file):
    ns_set(vault_file, "pass", "prod", "DB_URL", "pg")
    ns_set(vault_file, "pass", "prod", "API_KEY", "key")
    ns_set(vault_file, "pass", "staging", "DB_URL", "sqlite")
    result = ns_list_vars(vault_file, "pass", "prod")
    assert result == {"DB_URL": "pg", "API_KEY": "key"}


def test_ns_list_vars_empty_namespace(vault_file):
    assert ns_list_vars(vault_file, "pass", "ghost") == {}


def test_ns_clear_removes_all(vault_file):
    ns_set(vault_file, "pass", "prod", "A", "1")
    ns_set(vault_file, "pass", "prod", "B", "2")
    ns_set(vault_file, "pass", "staging", "C", "3")
    count = ns_clear(vault_file, "pass", "prod")
    assert count == 2
    assert ns_list_vars(vault_file, "pass", "prod") == {}
    assert ns_list_vars(vault_file, "pass", "staging") == {"C": "3"}


def test_ns_clear_empty_returns_zero(vault_file):
    assert ns_clear(vault_file, "pass", "nobody") == 0


def test_key_stored_with_separator(vault_file):
    ns_set(vault_file, "pass", "prod", "TOKEN", "abc")
    from envault.vault import load_vault
    data = load_vault(vault_file, "pass")
    assert f"prod{SEP}TOKEN" in data
