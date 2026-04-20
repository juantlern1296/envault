"""Vault locking: prevent concurrent writes by acquiring a lock file."""

from __future__ import annotations

import os
import time
from pathlib import Path

DEFAULT_TIMEOUT = 10  # seconds
DEFAULT_POLL = 0.1   # seconds


def _lock_path(vault_path: str | Path) -> Path:
    return Path(vault_path).with_suffix(".lock")


def acquire_lock(vault_path: str | Path, timeout: float = DEFAULT_TIMEOUT) -> Path:
    """Spin-wait until we can create the lock file, then return its path.

    Raises TimeoutError if the lock cannot be acquired within *timeout* seconds.
    """
    lock = _lock_path(vault_path)
    deadline = time.monotonic() + timeout
    while True:
        try:
            # Atomic O_CREAT | O_EXCL — fails if file already exists
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return lock
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Could not acquire vault lock at {lock} within {timeout}s. "
                    "Another envault process may be running."
                )
            time.sleep(DEFAULT_POLL)


def release_lock(lock_path: Path) -> None:
    """Remove the lock file, silently ignoring missing files."""
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def is_locked(vault_path: str | Path) -> bool:
    """Return True if a lock file exists for *vault_path*."""
    return _lock_path(vault_path).exists()


class VaultLock:
    """Context manager that acquires and releases a vault lock.

    Usage::

        with VaultLock(vault_path):
            save_vault(vault_path, password, data)
    """

    def __init__(self, vault_path: str | Path, timeout: float = DEFAULT_TIMEOUT):
        self._vault_path = vault_path
        self._timeout = timeout
        self._lock: Path | None = None

    def __enter__(self) -> "VaultLock":
        self._lock = acquire_lock(self._vault_path, self._timeout)
        return self

    def __exit__(self, *_):
        if self._lock is not None:
            release_lock(self._lock)
            self._lock = None
