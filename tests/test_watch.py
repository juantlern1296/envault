"""Tests for envault.watch.VaultWatcher."""

import time
import pytest
from pathlib import Path
from envault.watch import VaultWatcher


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    p = tmp_path / "vault.enc"
    p.write_bytes(b"initial")
    return p


def test_callback_fires_on_modification(vault_file: Path) -> None:
    fired: list[str] = []

    watcher = VaultWatcher(str(vault_file), lambda p: fired.append(p), interval=0.05)
    watcher.start()
    time.sleep(0.1)

    vault_file.write_bytes(b"changed")
    time.sleep(0.3)
    watcher.stop()

    assert len(fired) >= 1
    assert fired[0] == str(vault_file)


def test_callback_not_fired_without_change(vault_file: Path) -> None:
    fired: list[str] = []

    watcher = VaultWatcher(str(vault_file), lambda p: fired.append(p), interval=0.05)
    watcher.start()
    time.sleep(0.3)
    watcher.stop()

    assert fired == []


def test_context_manager_starts_and_stops(vault_file: Path) -> None:
    fired: list[str] = []

    with VaultWatcher(str(vault_file), lambda p: fired.append(p), interval=0.05) as w:
        assert w._thread is not None and w._thread.is_alive()
        vault_file.write_bytes(b"new content")
        time.sleep(0.3)

    assert not w._thread or not w._thread.is_alive()
    assert len(fired) >= 1


def test_missing_vault_file_does_not_crash(tmp_path: Path) -> None:
    path = str(tmp_path / "nonexistent.enc")
    fired: list[str] = []

    watcher = VaultWatcher(path, lambda p: fired.append(p), interval=0.05)
    watcher.start()
    time.sleep(0.2)
    watcher.stop()

    # File never existed — no changes, no crash
    assert fired == []


def test_callback_exception_does_not_stop_watcher(vault_file: Path) -> None:
    call_count = 0

    def bad_callback(p: str) -> None:
        nonlocal call_count
        call_count += 1
        raise RuntimeError("boom")

    watcher = VaultWatcher(str(vault_file), bad_callback, interval=0.05)
    watcher.start()
    vault_file.write_bytes(b"trigger1")
    time.sleep(0.2)
    vault_file.write_bytes(b"trigger2")
    time.sleep(0.2)
    watcher.stop()

    # Watcher kept running despite exceptions
    assert call_count >= 2


def test_stop_is_idempotent(vault_file: Path) -> None:
    watcher = VaultWatcher(str(vault_file), lambda p: None, interval=0.05)
    watcher.start()
    watcher.stop()
    watcher.stop()  # should not raise
