"""Tests for envault.dependency."""
import pytest

from envault.vault import save_vault
from envault.dependency import (
    add_dependency,
    dependents_of,
    list_dependencies,
    remove_dependency,
    resolve_order,
)

PASSWORD = "test-secret"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.env")
    save_vault(path, PASSWORD, {"DB_URL": "postgres://", "DB_HOST": "localhost", "DB_PORT": "5432"})
    return path


def test_add_dependency_creates_entry(vault_file):
    add_dependency(vault_file, PASSWORD, "DB_URL", "DB_HOST")
    deps = list_dependencies(vault_file, "DB_URL")
    assert "DB_HOST" in deps


def test_add_dependency_deduplicates(vault_file):
    add_dependency(vault_file, PASSWORD, "DB_URL", "DB_HOST")
    add_dependency(vault_file, PASSWORD, "DB_URL", "DB_HOST")
    assert list_dependencies(vault_file, "DB_URL").count("DB_HOST") == 1


def test_add_multiple_dependencies(vault_file):
    add_dependency(vault_file, PASSWORD, "DB_URL", "DB_HOST")
    add_dependency(vault_file, PASSWORD, "DB_URL", "DB_PORT")
    deps = list_dependencies(vault_file, "DB_URL")
    assert "DB_HOST" in deps
    assert "DB_PORT" in deps


def test_add_dependency_missing_key_raises(vault_file):
    with pytest.raises(KeyError):
        add_dependency(vault_file, PASSWORD, "MISSING", "DB_HOST")


def test_add_dependency_missing_dep_raises(vault_file):
    with pytest.raises(KeyError):
        add_dependency(vault_file, PASSWORD, "DB_URL", "MISSING")


def test_self_dependency_raises(vault_file):
    with pytest.raises(ValueError):
        add_dependency(vault_file, PASSWORD, "DB_URL", "DB_URL")


def test_remove_dependency(vault_file):
    add_dependency(vault_file, PASSWORD, "DB_URL", "DB_HOST")
    remove_dependency(vault_file, "DB_URL", "DB_HOST")
    assert list_dependencies(vault_file, "DB_URL") == []


def test_remove_missing_dependency_raises(vault_file):
    with pytest.raises(KeyError):
        remove_dependency(vault_file, "DB_URL", "DB_HOST")


def test_dependents_of(vault_file):
    add_dependency(vault_file, PASSWORD, "DB_URL", "DB_HOST")
    add_dependency(vault_file, PASSWORD, "DB_URL", "DB_PORT")
    result = dependents_of(vault_file, "DB_HOST")
    assert "DB_URL" in result


def test_dependents_of_empty(vault_file):
    assert dependents_of(vault_file, "DB_HOST") == []


def test_resolve_order_leaves_first(vault_file):
    add_dependency(vault_file, PASSWORD, "DB_URL", "DB_HOST")
    order = resolve_order(vault_file)
    assert order.index("DB_HOST") < order.index("DB_URL")


def test_resolve_order_empty_vault(vault_file):
    assert resolve_order(vault_file) == []
