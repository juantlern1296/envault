"""Snapshot: save and restore full vault states."""
from __future__ import annotations
import json
import time
from pathlib import Path
from envault.vault import load_vault, save_vault


def _snapshots_path(vault_path: str) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".snapshots.json")


def _load_snapshots(vault_path: str) -> dict:
    sp = _snapshots_path(vault_path)
    if not sp.exists():
        return {}
    return json.loads(sp.read_text())


def _save_snapshots(vault_path: str, data: dict) -> None:
    _snapshots_path(vault_path).write_text(json.dumps(data, indent=2))


def create_snapshot(vault_path: str, password: str, name: str) -> None:
    """Save current vault state under the given name."""
    vars_ = load_vault(vault_path, password)
    snaps = _load_snapshots(vault_path)
    snaps[name] = {"ts": time.time(), "vars": vars_}
    _save_snapshots(vault_path, snaps)


def list_snapshots(vault_path: str) -> list[dict]:
    """Return snapshot metadata sorted by creation time."""
    snaps = _load_snapshots(vault_path)
    result = [
        {"name": k, "ts": v["ts"], "count": len(v["vars"])}
        for k, v in snaps.items()
    ]
    return sorted(result, key=lambda x: x["ts"])


def restore_snapshot(vault_path: str, password: str, name: str) -> None:
    """Overwrite the vault with a previously saved snapshot."""
    snaps = _load_snapshots(vault_path)
    if name not in snaps:
        raise KeyError(f"Snapshot '{name}' not found")
    save_vault(vault_path, password, snaps[name]["vars"])


def delete_snapshot(vault_path: str, name: str) -> None:
    """Remove a snapshot by name."""
    snaps = _load_snapshots(vault_path)
    if name not in snaps:
        raise KeyError(f"Snapshot '{name}' not found")
    del snaps[name]
    _save_snapshots(vault_path, snaps)
