"""Tests for envault/ttl.py"""

import pytest
import time
from pathlib import Path
from envault.vault import save_vault, set_var
from envault.ttl import set_ttl, get_ttl, is_expired, purge_expired

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / "vault.enc"
    save_vault(str(p), PASSWORD, {})
    return str(p)


def test_set_ttl_stores_expiry(vault_file):
    set_var(vault_file, PASSWORD, "API_KEY", "secret")
    set_ttl(vault_file, PASSWORD, "API_KEY", 3600)
    expiry = get_ttl(vault_file, PASSWORD, "API_KEY")
    assert expiry is not None
    assert "T" in expiry  # ISO format


def test_get_ttl_missing_key_returns_none(vault_file):
    assert get_ttl(vault_file, PASSWORD, "NO_KEY") is None


def test_set_ttl_missing_var_raises(vault_file):
    with pytest.raises(KeyError):
        set_ttl(vault_file, PASSWORD, "GHOST", 60)


def test_is_expired_future(vault_file):
    set_var(vault_file, PASSWORD, "TOKEN", "abc")
    set_ttl(vault_file, PASSWORD, "TOKEN", 3600)
    assert is_expired(vault_file, PASSWORD, "TOKEN") is False


def test_is_expired_past(vault_file):
    set_var(vault_file, PASSWORD, "TOKEN", "abc")
    set_ttl(vault_file, PASSWORD, "TOKEN", -1)  # already expired
    assert is_expired(vault_file, PASSWORD, "TOKEN") is True


def test_is_expired_no_ttl(vault_file):
    set_var(vault_file, PASSWORD, "TOKEN", "abc")
    assert is_expired(vault_file, PASSWORD, "TOKEN") is False


def test_purge_expired_removes_keys(vault_file):
    set_var(vault_file, PASSWORD, "OLD", "val1")
    set_var(vault_file, PASSWORD, "NEW", "val2")
    set_ttl(vault_file, PASSWORD, "OLD", -1)
    set_ttl(vault_file, PASSWORD, "NEW", 3600)
    removed = purge_expired(vault_file, PASSWORD)
    assert "OLD" in removed
    assert "NEW" not in removed


def test_purge_expired_returns_empty_when_nothing_expired(vault_file):
    set_var(vault_file, PASSWORD, "KEY", "val")
    set_ttl(vault_file, PASSWORD, "KEY", 3600)
    assert purge_expired(vault_file, PASSWORD) == []
