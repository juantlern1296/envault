"""Tests for envault.webhook module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envault.vault import save_vault
from envault.webhook import add_webhook, remove_webhook, list_webhooks, fire_event


PASSWORD = "test-secret"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "vault.enc"
    save_vault(path, PASSWORD, {})
    return path


def test_add_webhook_creates_entry(vault_file):
    add_webhook(vault_file, PASSWORD, "slack", "https://hooks.example.com/slack", ["set", "delete"])
    hooks = list_webhooks(vault_file, PASSWORD)
    assert "slack" in hooks
    assert hooks["slack"]["url"] == "https://hooks.example.com/slack"
    assert "set" in hooks["slack"]["events"]


def test_list_webhooks_empty(vault_file):
    assert list_webhooks(vault_file, PASSWORD) == {}


def test_add_multiple_webhooks(vault_file):
    add_webhook(vault_file, PASSWORD, "a", "https://a.example.com", ["set"])
    add_webhook(vault_file, PASSWORD, "b", "https://b.example.com", ["delete"])
    hooks = list_webhooks(vault_file, PASSWORD)
    assert set(hooks.keys()) == {"a", "b"}


def test_remove_webhook(vault_file):
    add_webhook(vault_file, PASSWORD, "slack", "https://hooks.example.com", ["set"])
    remove_webhook(vault_file, PASSWORD, "slack")
    hooks = list_webhooks(vault_file, PASSWORD)
    assert "slack" not in hooks


def test_remove_missing_webhook_raises(vault_file):
    with pytest.raises(KeyError, match="not found"):
        remove_webhook(vault_file, PASSWORD, "nonexistent")


def test_fire_event_calls_subscribed_webhook(vault_file):
    add_webhook(vault_file, PASSWORD, "notify", "https://example.com/hook", ["set"])
    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_response) as mock_open:
        notified = fire_event(vault_file, PASSWORD, "set", {"key": "FOO"})
    assert "notify" in notified
    mock_open.assert_called_once()


def test_fire_event_skips_unsubscribed_webhook(vault_file):
    add_webhook(vault_file, PASSWORD, "notify", "https://example.com/hook", ["delete"])
    with patch("urllib.request.urlopen") as mock_open:
        notified = fire_event(vault_file, PASSWORD, "set", {})
    assert notified == []
    mock_open.assert_not_called()


def test_fire_event_handles_network_error(vault_file):
    import urllib.error
    add_webhook(vault_file, PASSWORD, "flaky", "https://unreachable.example.com", ["set"])
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        notified = fire_event(vault_file, PASSWORD, "set", {})
    assert notified == []
