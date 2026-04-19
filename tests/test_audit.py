"""Tests for envault.audit module."""

import pytest
from pathlib import Path
from envault.audit import log_event, read_log, clear_log


@pytest.fixture
def log_file(tmp_path):
    return tmp_path / "test_audit.log"


def test_log_creates_file(log_file):
    log_event("set", key="FOO", log_path=log_file)
    assert log_file.exists()


def test_log_entry_fields(log_file):
    log_event("set", key="BAR", vault_path="/tmp/vault", success=True, log_path=log_file)
    entries = read_log(log_file)
    assert len(entries) == 1
    e = entries[0]
    assert e["action"] == "set"
    assert e["key"] == "BAR"
    assert e["vault"] == "/tmp/vault"
    assert e["success"] is True
    assert "timestamp" in e


def test_multiple_entries(log_file):
    log_event("set", key="A", log_path=log_file)
    log_event("get", key="B", log_path=log_file)
    log_event("delete", key="A", success=False, log_path=log_file)
    entries = read_log(log_file)
    assert len(entries) == 3
    assert entries[1]["action"] == "get"


def test_read_empty_log(log_file):
    assert read_log(log_file) == []


def test_clear_log(log_file):
    log_event("set", key="X", log_path=log_file)
    clear_log(log_file)
    assert not log_file.exists()
    assert read_log(log_file) == []


def test_failed_event_recorded(log_file):
    log_event("get", key="MISSING", success=False, log_path=log_file)
    entries = read_log(log_file)
    assert entries[0]["success"] is False
