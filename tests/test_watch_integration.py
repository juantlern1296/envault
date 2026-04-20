"""Integration tests: VaultWatcher + real vault read/write."""

import time
from pathlib import Path

import pytest

from envault.vault import save_vault, set_var, load_vault
from envault.watch import VaultWatcher


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    p = tmp_path / "vault.enc"
    save_vault(str(p), "pw", {})
    return p


def test_detects_new_key_added(vault_file: Path) -> None:
    events: list[str] = []

    def on_change(path: str) -> None:
        data = load_vault(path, "pw")
        events.extend(data.keys())

    with VaultWatcher(str(vault_file), on_change, interval=0.05):
        time.sleep(0.1)
        set_var(str(vault_file), "pw", "NEW_KEY", "hello")
        time.sleep(0.4)

    assert "NEW_KEY" in events


def test_detects_multiple_writes(vault_file: Path) -> None:
    change_count = [0]

    def on_change(path: str) -> None:
        change_count[0] += 1

    with VaultWatcher(str(vault_file), on_change, interval=0.05):
        time.sleep(0.1)
        set_var(str(vault_file), "pw", "A", "1")
        time.sleep(0.3)
        set_var(str(vault_file), "pw", "B", "2")
        time.sleep(0.3)

    assert change_count[0] >= 2


def test_no_spurious_events_when_idle(vault_file: Path) -> None:
    events: list[int] = []

    with VaultWatcher(str(vault_file), lambda _: events.append(1), interval=0.05):
        time.sleep(0.5)

    assert events == []
