"""Tests for envault.lock."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from envault.lock import (
    VaultLock,
    acquire_lock,
    is_locked,
    release_lock,
)


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    p = tmp_path / "vault.env"
    p.write_bytes(b"")
    return p


def test_acquire_creates_lock_file(vault_file):
    lock = acquire_lock(vault_file)
    assert lock.exists()
    release_lock(lock)


def test_release_removes_lock_file(vault_file):
    lock = acquire_lock(vault_file)
    release_lock(lock)
    assert not lock.exists()


def test_release_missing_lock_does_not_raise(vault_file):
    lock = vault_file.with_suffix(".lock")
    release_lock(lock)  # should not raise


def test_is_locked_false_when_no_lock(vault_file):
    assert not is_locked(vault_file)


def test_is_locked_true_when_locked(vault_file):
    lock = acquire_lock(vault_file)
    assert is_locked(vault_file)
    release_lock(lock)


def test_context_manager_acquires_and_releases(vault_file):
    with VaultLock(vault_file):
        assert is_locked(vault_file)
    assert not is_locked(vault_file)


def test_context_manager_releases_on_exception(vault_file):
    with pytest.raises(RuntimeError):
        with VaultLock(vault_file):
            assert is_locked(vault_file)
            raise RuntimeError("boom")
    assert not is_locked(vault_file)


def test_acquire_times_out_when_already_locked(vault_file):
    lock = acquire_lock(vault_file)
    try:
        with pytest.raises(TimeoutError, match="vault lock"):
            acquire_lock(vault_file, timeout=0.3)
    finally:
        release_lock(lock)


def test_concurrent_writers_serialize(vault_file):
    """Only one thread should hold the lock at a time."""
    results: list[str] = []
    errors: list[Exception] = []

    def writer(name: str):
        try:
            with VaultLock(vault_file, timeout=5):
                results.append(f"{name}-enter")
                time.sleep(0.05)
                results.append(f"{name}-exit")
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=writer, args=(f"t{i}",)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    # Each enter must be immediately followed by its matching exit
    for i in range(0, len(results), 2):
        name = results[i].split("-")[0]
        assert results[i] == f"{name}-enter"
        assert results[i + 1] == f"{name}-exit"
