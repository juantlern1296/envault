"""Edge-case tests for envault.retention."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.retention import (
    RetentionError,
    get_retention,
    purge_stale,
    set_retention,
    touch_key,
)
from envault.vault import save_vault, set_var

PASSWORD = "edge-pass"


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / "vault.env"
    save_vault(str(p), PASSWORD, {})
    return str(p)


def test_retention_file_not_created_until_set(vault_file):
    p = Path(vault_file).with_suffix(".retention.json")
    assert not p.exists()


def test_multiple_keys_independent_policies(vault_file):
    set_var(vault_file, PASSWORD, "KEY_A", "a")
    set_var(vault_file, PASSWORD, "KEY_B", "b")
    set_retention(vault_file, PASSWORD, "KEY_A", 7)
    set_retention(vault_file, PASSWORD, "KEY_B", 30)
    assert get_retention(vault_file, "KEY_A")["days"] == 7
    assert get_retention(vault_file, "KEY_B")["days"] == 30


def test_touch_nonexistent_key_is_noop(vault_file):
    # Should not raise even if key has no retention entry
    touch_key(vault_file, "NO_SUCH_KEY")


def test_purge_empty_vault_returns_empty(vault_file):
    deleted = purge_stale(vault_file, PASSWORD)
    assert deleted == []


def test_purge_exactly_at_boundary_is_deleted(vault_file):
    set_var(vault_file, PASSWORD, "EDGE_KEY", "val")
    set_retention(vault_file, PASSWORD, "EDGE_KEY", 1)
    p = Path(vault_file).with_suffix(".retention.json")
    data = json.loads(p.read_text())
    # exactly 1 day ago
    data["EDGE_KEY"]["last_accessed"] = (
        datetime.now(timezone.utc) - timedelta(days=1)
    ).isoformat()
    p.write_text(json.dumps(data))
    deleted = purge_stale(vault_file, PASSWORD)
    assert "EDGE_KEY" in deleted


def test_overwrite_retention_updates_days(vault_file):
    set_var(vault_file, PASSWORD, "MY_VAR", "x")
    set_retention(vault_file, PASSWORD, "MY_VAR", 10)
    set_retention(vault_file, PASSWORD, "MY_VAR", 99)
    assert get_retention(vault_file, "MY_VAR")["days"] == 99
