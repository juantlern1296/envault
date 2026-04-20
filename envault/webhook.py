"""Webhook notifications for vault events."""

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

from envault.vault import load_vault, save_vault

_WEBHOOK_KEY = "__webhooks__"


def _get_webhooks(vault_path: Path, password: str) -> dict:
    data = load_vault(vault_path, password)
    raw = data.get(_WEBHOOK_KEY)
    if raw is None:
        return {}
    return json.loads(raw)


def _save_webhooks(vault_path: Path, password: str, webhooks: dict) -> None:
    data = load_vault(vault_path, password)
    data[_WEBHOOK_KEY] = json.dumps(webhooks)
    save_vault(vault_path, password, data)


def add_webhook(vault_path: Path, password: str, name: str, url: str, events: list[str]) -> None:
    """Register a named webhook for the given event types."""
    webhooks = _get_webhooks(vault_path, password)
    webhooks[name] = {"url": url, "events": events}
    _save_webhooks(vault_path, password, webhooks)


def remove_webhook(vault_path: Path, password: str, name: str) -> None:
    """Remove a registered webhook by name."""
    webhooks = _get_webhooks(vault_path, password)
    if name not in webhooks:
        raise KeyError(f"Webhook '{name}' not found")
    del webhooks[name]
    _save_webhooks(vault_path, password, webhooks)


def list_webhooks(vault_path: Path, password: str) -> dict:
    """Return all registered webhooks."""
    return _get_webhooks(vault_path, password)


def fire_event(vault_path: Path, password: str, event: str, payload: Optional[dict] = None) -> list[str]:
    """Send HTTP POST to all webhooks subscribed to the given event.
    Returns list of webhook names that were notified."""
    webhooks = _get_webhooks(vault_path, password)
    notified = []
    body = json.dumps({"event": event, "payload": payload or {}}).encode()
    for name, cfg in webhooks.items():
        if event in cfg.get("events", []):
            req = urllib.request.Request(
                cfg["url"],
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=5):
                    pass
                notified.append(name)
            except urllib.error.URLError:
                pass
    return notified
