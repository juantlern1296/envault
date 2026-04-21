"""Tests for envault.quota."""

import pytest

from envault.quota import (
    QuotaExceeded,
    check_quota,
    delete_quota,
    get_quota,
    set_quota,
)
from envault.vault import load_vault, save_vault, set_var

PASSWORD = "test-secret"


@pytest.fixture()
def vault_file(tmp_path):
    path = tmp_path / "vault.enc"
    save_vault(path, PASSWORD, {})
    return path


def test_set_and_get_quota(vault_file):
    set_quota(vault_file, PASSWORD, "global", 10)
    assert get_quota(vault_file, PASSWORD, "global") == 10


def test_get_missing_quota_returns_none(vault_file):
    assert get_quota(vault_file, PASSWORD, "nonexistent") is None


def test_set_quota_invalid_limit_raises(vault_file):
    with pytest.raises(ValueError):
        set_quota(vault_file, PASSWORD, "global", 0)


def test_delete_quota(vault_file):
    set_quota(vault_file, PASSWORD, "prod", 5)
    delete_quota(vault_file, PASSWORD, "prod")
    assert get_quota(vault_file, PASSWORD, "prod") is None


def test_delete_missing_quota_raises(vault_file):
    with pytest.raises(KeyError):
        delete_quota(vault_file, PASSWORD, "ghost")


def test_check_quota_no_limit_passes(vault_file):
    # No quota set — should never raise
    for i in range(20):
        set_var(vault_file, PASSWORD, f"KEY_{i}", "value")
    check_quota(vault_file, PASSWORD, "global")  # no error


def test_check_quota_under_limit_passes(vault_file):
    set_quota(vault_file, PASSWORD, "global", 3)
    set_var(vault_file, PASSWORD, "A", "1")
    set_var(vault_file, PASSWORD, "B", "2")
    check_quota(vault_file, PASSWORD, "global")  # 2 < 3, OK


def test_check_quota_at_limit_raises(vault_file):
    set_quota(vault_file, PASSWORD, "global", 2)
    set_var(vault_file, PASSWORD, "X", "1")
    set_var(vault_file, PASSWORD, "Y", "2")
    with pytest.raises(QuotaExceeded):
        check_quota(vault_file, PASSWORD, "global")


def test_check_quota_namespace_counts_only_prefixed_keys(vault_file):
    set_quota(vault_file, PASSWORD, "dev", 2)
    # Add keys in 'dev' namespace
    data = load_vault(vault_file, PASSWORD)
    data["dev::KEY1"] = "a"
    data["dev::KEY2"] = "b"
    save_vault(vault_file, PASSWORD, data)
    with pytest.raises(QuotaExceeded):
        check_quota(vault_file, PASSWORD, "dev")


def test_check_quota_namespace_ignores_other_namespaces(vault_file):
    set_quota(vault_file, PASSWORD, "dev", 2)
    data = load_vault(vault_file, PASSWORD)
    data["prod::KEY1"] = "x"
    data["dev::KEY1"] = "y"
    save_vault(vault_file, PASSWORD, data)
    # Only 1 dev key — should pass
    check_quota(vault_file, PASSWORD, "dev")
