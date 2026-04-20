"""CLI command for watching a vault file for changes."""

import os
import click
from envault.watch import VaultWatcher
from envault.vault import load_vault
from envault.audit import log_event


@click.group("watch")
def watch_group() -> None:
    """Watch a vault for live changes."""


@watch_group.command("start")
@click.option("--vault", default=None, envvar="ENVAULT_VAULT", show_default=True, help="Path to vault file.")
@click.option("--password", default=None, envvar="ENVAULT_PASSWORD", help="Vault password.")
@click.option("--interval", default=1.0, show_default=True, help="Poll interval in seconds.")
def cmd_watch(vault: str, password: str, interval: float) -> None:
    """Watch a vault file and print changed keys when it is modified."""
    if not vault:
        click.echo("Error: vault path required (--vault or ENVAULT_VAULT).", err=True)
        raise SystemExit(1)
    if not password:
        password = click.prompt("Vault password", hide_input=True)

    previous: dict = {}

    def on_change(path: str) -> None:
        nonlocal previous
        try:
            current = load_vault(path, password)
        except Exception as exc:  # noqa: BLE001
            click.echo(f"[watch] Could not read vault: {exc}", err=True)
            return

        added = set(current) - set(previous)
        removed = set(previous) - set(current)
        changed = {k for k in current if k in previous and current[k] != previous[k]}

        for k in sorted(added):
            click.echo(f"[+] {k}")
            log_event("watch_added", {"key": k})
        for k in sorted(removed):
            click.echo(f"[-] {k}")
            log_event("watch_removed", {"key": k})
        for k in sorted(changed):
            click.echo(f"[~] {k}")
            log_event("watch_changed", {"key": k})

        previous = current

    # Seed initial state
    try:
        previous = load_vault(vault, password)
    except FileNotFoundError:
        previous = {}

    click.echo(f"Watching {vault} (interval={interval}s) — Ctrl-C to stop.")
    with VaultWatcher(vault, on_change, interval=interval):
        try:
            while True:
                import time
                time.sleep(0.5)
        except KeyboardInterrupt:
            click.echo("\nStopped watching.")
