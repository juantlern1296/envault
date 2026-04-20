"""Watch a vault file for changes and trigger a callback."""

import time
import os
import threading
from typing import Callable, Optional


class VaultWatcher:
    """Poll a vault file for modifications and invoke a callback on change."""

    def __init__(
        self,
        vault_path: str,
        callback: Callable[[str], None],
        interval: float = 1.0,
    ) -> None:
        self.vault_path = vault_path
        self.callback = callback
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_mtime: Optional[float] = self._mtime()

    def _mtime(self) -> Optional[float]:
        try:
            return os.path.getmtime(self.vault_path)
        except FileNotFoundError:
            return None

    def _run(self) -> None:
        while not self._stop_event.is_set():
            current = self._mtime()
            if current != self._last_mtime:
                self._last_mtime = current
                try:
                    self.callback(self.vault_path)
                except Exception:  # noqa: BLE001
                    pass
            self._stop_event.wait(self.interval)

    def start(self) -> None:
        """Start watching in a background thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the background watcher thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self.interval + 1)
            self._thread = None

    def __enter__(self) -> "VaultWatcher":
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()
