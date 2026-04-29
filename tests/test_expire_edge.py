"""Edge-case tests for envault.expire."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.expire import (
    get_expiry,
    is_expired,
    purge_expired,
    set_expiry,
)
from envault.vault import load_vault, save_vault

PASSWORD = "edge-pw"


@pytest.fixture()
def vault_file(tmp_path: Path) -> str:
    path = str(tmp_path / "vault.enc")
    save_vault(path, PASSWORD, {"A": "1", "B": "2", "C": "3"})
    return path


def test_overwrite_expiry(vault_file: str) -> None:
    dt1 = datetime.now(timezone.utc) + timedelta(days=10)
    dt2 = datetime.now(timezone.utc) + timedelta(days=99)
    set_expiry(vault_file, PASSWORD, "A", dt1)
    set_expiry(vault_file, PASSWORD, "A", dt2)
    stored = get_expiry(vault_file, "A")
    assert abs((stored - dt2.astimezone(timezone.utc)).total_seconds()) < 1


def test_purge_removes_only_expired(vault_file: str) -> None:
    set_expiry(vault_file, PASSWORD, "A", datetime.now(timezone.utc) - timedelta(seconds=1))
    set_expiry(vault_file, PASSWORD, "B", datetime.now(timezone.utc) + timedelta(days=1))
    purged = purge_expired(vault_file, PASSWORD)
    assert purged == ["A"]
    vault = load_vault(vault_file, PASSWORD)
    assert "A" not in vault
    assert "B" in vault


def test_purge_clears_expiry_record_for_purged_key(vault_file: str) -> None:
    set_expiry(vault_file, PASSWORD, "A", datetime.now(timezone.utc) - timedelta(seconds=1))
    purge_expired(vault_file, PASSWORD)
    assert get_expiry(vault_file, "A") is None


def test_purge_empty_vault_returns_empty(tmp_path: Path) -> None:
    path = str(tmp_path / "empty.enc")
    save_vault(path, PASSWORD, {})
    result = purge_expired(path, PASSWORD)
    assert result == []


def test_multiple_keys_independent_expiry(vault_file: str) -> None:
    set_expiry(vault_file, PASSWORD, "A", datetime.now(timezone.utc) - timedelta(days=1))
    set_expiry(vault_file, PASSWORD, "B", datetime.now(timezone.utc) + timedelta(days=1))
    set_expiry(vault_file, PASSWORD, "C", datetime.now(timezone.utc) - timedelta(hours=1))
    purged = sorted(purge_expired(vault_file, PASSWORD))
    assert purged == ["A", "C"]
