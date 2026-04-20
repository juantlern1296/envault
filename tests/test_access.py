"""Tests for envault.access (role-based access control)."""

import pytest

from envault.vault import save_vault
from envault.access import grant, revoke, can, list_permissions, list_roles


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.enc")
    save_vault(path, "pass", {"API_KEY": "secret", "DB_URL": "postgres://"})
    return path


def test_grant_read_permission(vault_file):
    grant(vault_file, "pass", "reader", "API_KEY", "read")
    assert can(vault_file, "pass", "reader", "API_KEY", "read")


def test_grant_write_permission(vault_file):
    grant(vault_file, "pass", "writer", "DB_URL", "write")
    assert can(vault_file, "pass", "writer", "DB_URL", "write")


def test_can_returns_false_for_missing_permission(vault_file):
    assert not can(vault_file, "pass", "nobody", "API_KEY", "read")


def test_grant_deduplicates(vault_file):
    grant(vault_file, "pass", "reader", "API_KEY", "read")
    grant(vault_file, "pass", "reader", "API_KEY", "read")
    perms = list_permissions(vault_file, "pass", "reader")
    assert perms["read"].count("API_KEY") == 1


def test_revoke_removes_permission(vault_file):
    grant(vault_file, "pass", "reader", "API_KEY", "read")
    revoke(vault_file, "pass", "reader", "API_KEY", "read")
    assert not can(vault_file, "pass", "reader", "API_KEY", "read")


def test_revoke_missing_permission_raises(vault_file):
    with pytest.raises(KeyError):
        revoke(vault_file, "pass", "reader", "API_KEY", "read")


def test_invalid_permission_raises_on_grant(vault_file):
    with pytest.raises(ValueError, match="Unknown permission"):
        grant(vault_file, "pass", "role", "API_KEY", "execute")


def test_invalid_permission_raises_on_revoke(vault_file):
    with pytest.raises(ValueError, match="Unknown permission"):
        revoke(vault_file, "pass", "role", "API_KEY", "execute")


def test_list_permissions_unknown_role_returns_empty(vault_file):
    perms = list_permissions(vault_file, "pass", "ghost")
    assert perms == {"read": [], "write": []}


def test_list_roles_empty_when_no_grants(vault_file):
    assert list_roles(vault_file, "pass") == []


def test_list_roles_returns_all_roles(vault_file):
    grant(vault_file, "pass", "alpha", "API_KEY", "read")
    grant(vault_file, "pass", "beta", "DB_URL", "write")
    roles = list_roles(vault_file, "pass")
    assert set(roles) == {"alpha", "beta"}
