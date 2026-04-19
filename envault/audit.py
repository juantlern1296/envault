"""Audit log for tracking vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_LOG_PATH = Path.home() / ".envault" / "audit.log"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(
    action: str,
    key: Optional[str] = None,
    vault_path: Optional[str] = None,
    success: bool = True,
    log_path: Path = DEFAULT_LOG_PATH,
) -> None:
    """Append a single audit event to the log file."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": _now(),
        "action": action,
        "key": key,
        "vault": str(vault_path) if vault_path else None,
        "success": success,
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def read_log(log_path: Path = DEFAULT_LOG_PATH) -> list[dict]:
    """Return all audit log entries as a list of dicts."""
    if not log_path.exists():
        return []
    entries = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def clear_log(log_path: Path = DEFAULT_LOG_PATH) -> None:
    """Wipe the audit log."""
    if log_path.exists():
        log_path.unlink()
