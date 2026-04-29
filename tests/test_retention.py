"""Tests for envault.retention."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.retention import (
    RetentionError,
    get_retention,
    purge_stale,
    remove_retention,
    set_retention,
    touch_key,
)
from envault.vault import save_vault, set_var

PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / "vault.env"
    save_vault(str(p), PASSWORD, {})
    set_var(str(p), PASSWORD, "DB_URL", "postgres://localhost/db")
    set_var(str(p), PASSWORD, "API_KEY", "secret123")
    return str(p)


def test_set_retention_creates_entry(vault_file):
    set_retention(vault_file, PASSWORD, "DB_URL", 30)
    info = get_retention(vault_file, "DB_URL")
    assert info is not None
    assert info["days"] == 30
    assert "last_accessed" in info


def test_get_retention_missing_key_returns_none(vault_file):
    assert get_retention(vault_file, "NONEXISTENT") is None


def test_set_retention_missing_vault_key_raises(vault_file):
    with pytest.raises(RetentionError, match="not found"):
        set_retention(vault_file, PASSWORD, "MISSING_KEY", 7)


def test_set_retention_zero_days_raises(vault_file):
    with pytest.raises(RetentionError, match="positive"):
        set_retention(vault_file, PASSWORD, "DB_URL", 0)


def test_set_retention_negative_days_raises(vault_file):
    with pytest.raises(RetentionError, match="positive"):
        set_retention(vault_file, PASSWORD, "DB_URL", -5)


def test_touch_key_updates_timestamp(vault_file):
    set_retention(vault_file, PASSWORD, "DB_URL", 10)
    old_ts = get_retention(vault_file, "DB_URL")["last_accessed"]
    future = datetime.now(timezone.utc) + timedelta(seconds=5)
    with patch("envault.retention._now", return_value=future):
        touch_key(vault_file, "DB_URL")
    new_ts = get_retention(vault_file, "DB_URL")["last_accessed"]
    assert new_ts != old_ts


def test_purge_stale_deletes_expired_key(vault_file):
    set_retention(vault_file, PASSWORD, "API_KEY", 1)
    # backdate last_accessed by 2 days
    p = Path(vault_file).with_suffix(".retention.json")
    data = json.loads(p.read_text())
    data["API_KEY"]["last_accessed"] = (
        datetime.now(timezone.utc) - timedelta(days=2)
    ).isoformat()
    p.write_text(json.dumps(data))

    deleted = purge_stale(vault_file, PASSWORD)
    assert "API_KEY" in deleted
    assert get_retention(vault_file, "API_KEY") is None


def test_purge_stale_keeps_fresh_key(vault_file):
    set_retention(vault_file, PASSWORD, "DB_URL", 30)
    deleted = purge_stale(vault_file, PASSWORD)
    assert "DB_URL" not in deleted


def test_remove_retention_deletes_policy(vault_file):
    set_retention(vault_file, PASSWORD, "DB_URL", 7)
    remove_retention(vault_file, "DB_URL")
    assert get_retention(vault_file, "DB_URL") is None


def test_remove_retention_missing_raises(vault_file):
    with pytest.raises(RetentionError, match="no retention policy"):
        remove_retention(vault_file, "DB_URL")
