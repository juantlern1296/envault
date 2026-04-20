"""Tests for envault.remind."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.vault import save_vault
from envault.remind import (
    set_reminder,
    get_reminder,
    remove_reminder,
    due_reminders,
    _reminders_path,
)


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.env")
    save_vault(path, "secret", {"API_KEY": "abc123", "DB_PASS": "hunter2"})
    return path


def test_set_reminder_creates_file(vault_file):
    set_reminder(vault_file, "secret", "API_KEY", 7)
    assert _reminders_path(vault_file).exists()


def test_set_reminder_stores_due_date(vault_file):
    fixed = datetime(2030, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    with patch("envault.remind._now", return_value=fixed):
        due = set_reminder(vault_file, "secret", "API_KEY", 3)
    assert due == fixed + timedelta(days=3)


def test_set_reminder_missing_key_raises(vault_file):
    with pytest.raises(KeyError, match="MISSING"):
        set_reminder(vault_file, "secret", "MISSING", 5)


def test_set_reminder_zero_days_raises(vault_file):
    with pytest.raises(ValueError):
        set_reminder(vault_file, "secret", "API_KEY", 0)


def test_get_reminder_returns_none_when_not_set(vault_file):
    assert get_reminder(vault_file, "API_KEY") is None


def test_get_reminder_after_set(vault_file):
    set_reminder(vault_file, "secret", "API_KEY", 10)
    result = get_reminder(vault_file, "API_KEY")
    assert isinstance(result, datetime)


def test_remove_reminder_deletes_entry(vault_file):
    set_reminder(vault_file, "secret", "API_KEY", 5)
    remove_reminder(vault_file, "API_KEY")
    assert get_reminder(vault_file, "API_KEY") is None


def test_remove_reminder_missing_raises(vault_file):
    with pytest.raises(KeyError):
        remove_reminder(vault_file, "API_KEY")


def test_due_reminders_returns_overdue(vault_file):
    past = datetime(2000, 1, 1, tzinfo=timezone.utc)
    data = {"API_KEY": past.isoformat()}
    _reminders_path(vault_file).write_text(json.dumps(data))
    items = due_reminders(vault_file)
    assert len(items) == 1
    assert items[0][0] == "API_KEY"


def test_due_reminders_excludes_future(vault_file):
    future = datetime(2099, 1, 1, tzinfo=timezone.utc)
    data = {"API_KEY": future.isoformat()}
    _reminders_path(vault_file).write_text(json.dumps(data))
    assert due_reminders(vault_file) == []


def test_due_reminders_sorted_by_date(vault_file):
    d1 = datetime(2000, 3, 1, tzinfo=timezone.utc)
    d2 = datetime(2000, 1, 1, tzinfo=timezone.utc)
    data = {"API_KEY": d1.isoformat(), "DB_PASS": d2.isoformat()}
    _reminders_path(vault_file).write_text(json.dumps(data))
    items = due_reminders(vault_file)
    assert items[0][0] == "DB_PASS"
    assert items[1][0] == "API_KEY"
