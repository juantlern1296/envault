"""Tests for envault.expire module."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.expire import (
    ExpireError,
    get_expiry,
    is_expired,
    purge_expired,
    remove_expiry,
    set_expiry,
)
from envault.vault import save_vault

PASSWORD = "test-password"


@pytest.fixture()
def vault_file(tmp_path: Path) -> str:
    path = str(tmp_path / "vault.enc")
    save_vault(path, PASSWORD, {"API_KEY": "secret", "DB_PASS": "hunter2"})
    return path


def _future(days: int = 1) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


def _past(days: int = 1) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


def test_set_expiry_creates_file(vault_file: str, tmp_path: Path) -> None:
    set_expiry(vault_file, PASSWORD, "API_KEY", _future())
    expire_file = tmp_path / "vault.expire.json"
    assert expire_file.exists()


def test_set_expiry_stores_correct_key(vault_file: str) -> None:
    dt = _future()
    set_expiry(vault_file, PASSWORD, "API_KEY", dt)
    stored = get_expiry(vault_file, "API_KEY")
    assert stored is not None
    assert abs((stored - dt.astimezone(timezone.utc)).total_seconds()) < 1


def test_get_expiry_missing_key_returns_none(vault_file: str) -> None:
    assert get_expiry(vault_file, "MISSING") is None


def test_set_expiry_missing_vault_key_raises(vault_file: str) -> None:
    with pytest.raises(ExpireError, match="not found"):
        set_expiry(vault_file, PASSWORD, "NONEXISTENT", _future())


def test_is_expired_future_returns_false(vault_file: str) -> None:
    set_expiry(vault_file, PASSWORD, "API_KEY", _future())
    assert is_expired(vault_file, "API_KEY") is False


def test_is_expired_past_returns_true(vault_file: str) -> None:
    set_expiry(vault_file, PASSWORD, "API_KEY", _past())
    assert is_expired(vault_file, "API_KEY") is True


def test_is_expired_no_policy_returns_false(vault_file: str) -> None:
    assert is_expired(vault_file, "API_KEY") is False


def test_remove_expiry_deletes_entry(vault_file: str) -> None:
    set_expiry(vault_file, PASSWORD, "API_KEY", _future())
    remove_expiry(vault_file, "API_KEY")
    assert get_expiry(vault_file, "API_KEY") is None


def test_remove_expiry_noop_when_not_set(vault_file: str) -> None:
    # should not raise
    remove_expiry(vault_file, "API_KEY")


def test_purge_expired_removes_key(vault_file: str) -> None:
    set_expiry(vault_file, PASSWORD, "API_KEY", _past())
    purged = purge_expired(vault_file, PASSWORD)
    assert "API_KEY" in purged


def test_purge_expired_leaves_valid_keys(vault_file: str) -> None:
    set_expiry(vault_file, PASSWORD, "API_KEY", _past())
    set_expiry(vault_file, PASSWORD, "DB_PASS", _future())
    purge_expired(vault_file, PASSWORD)
    assert get_expiry(vault_file, "DB_PASS") is not None


def test_purge_expired_returns_empty_when_none_expired(vault_file: str) -> None:
    set_expiry(vault_file, PASSWORD, "API_KEY", _future())
    purged = purge_expired(vault_file, PASSWORD)
    assert purged == []
