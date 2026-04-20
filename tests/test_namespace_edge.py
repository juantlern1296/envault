"""Edge case tests for namespace module."""

import pytest
from envault.vault import save_vault, load_vault
from envault.namespace import ns_set, ns_get, ns_list_vars, list_namespaces, SEP


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "vault.enc"
    save_vault(str(path), "pw", {})
    return str(path)


def test_same_key_in_different_namespaces(vault_file):
    ns_set(vault_file, "pw", "prod", "SECRET", "prod-secret")
    ns_set(vault_file, "pw", "dev", "SECRET", "dev-secret")
    assert ns_get(vault_file, "pw", "prod", "SECRET") == "prod-secret"
    assert ns_get(vault_file, "pw", "dev", "SECRET") == "dev-secret"


def test_namespace_does_not_bleed_into_global(vault_file):
    ns_set(vault_file, "pw", "prod", "KEY", "nsval")
    data = load_vault(vault_file, "pw")
    assert "KEY" not in data
    assert f"prod{SEP}KEY" in data


def test_overwrite_var_in_namespace(vault_file):
    ns_set(vault_file, "pw", "prod", "DB", "old")
    ns_set(vault_file, "pw", "prod", "DB", "new")
    assert ns_get(vault_file, "pw", "prod", "DB") == "new"


def test_empty_value_allowed(vault_file):
    ns_set(vault_file, "pw", "prod", "EMPTY", "")
    assert ns_get(vault_file, "pw", "prod", "EMPTY") == ""


def test_namespace_with_numbers_and_hyphens(vault_file):
    ns_set(vault_file, "pw", "env-1", "PORT", "8080")
    assert ns_get(vault_file, "pw", "env-1", "PORT") == "8080"
    assert "env-1" in list_namespaces(vault_file, "pw")


def test_global_vars_not_included_in_namespaces(vault_file):
    from envault.vault import save_vault
    save_vault(vault_file, "pw", {"GLOBAL_KEY": "val", "prod::NS_KEY": "ns"})
    nss = list_namespaces(vault_file, "pw")
    assert nss == ["prod"]
    assert "GLOBAL_KEY" not in nss


def test_ns_list_vars_does_not_include_other_namespaces(vault_file):
    ns_set(vault_file, "pw", "prod", "A", "1")
    ns_set(vault_file, "pw", "staging", "B", "2")
    result = ns_list_vars(vault_file, "pw", "prod")
    assert "B" not in result
    assert "A" in result
