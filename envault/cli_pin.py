"""CLI commands for pinning/unpinning vault variables."""

from __future__ import annotations

import os
from pathlib import Path

import click

from envault.cli import get_password
from envault.pin import pin_var, unpin_var, is_pinned, list_pinned


@click.group("pin")
def pin_group() -> None:
    """Pin variables to protect them from accidental overwrites."""


@pin_group.command("add")
@click.argument("key")
def cmd_pin(key: str) -> None:
    """Pin KEY so it cannot be overwritten."""
    vault_path = Path(os.environ["ENVAULT_PATH"])
    password = get_password()
    try:
        pin_var(vault_path, password, key)
        click.echo(f"Pinned '{key}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@pin_group.command("remove")
@click.argument("key")
def cmd_unpin(key: str) -> None:
    """Unpin KEY so it can be overwritten again."""
    vault_path = Path(os.environ["ENVAULT_PATH"])
    password = get_password()
    try:
        unpin_var(vault_path, password, key)
        click.echo(f"Unpinned '{key}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@pin_group.command("status")
@click.argument("key")
def cmd_status(key: str) -> None:
    """Show whether KEY is pinned."""
    vault_path = Path(os.environ["ENVAULT_PATH"])
    password = get_password()
    pinned = is_pinned(vault_path, password, key)
    click.echo("pinned" if pinned else "not pinned")


@pin_group.command("list")
def cmd_list() -> None:
    """List all pinned variables."""
    vault_path = Path(os.environ["ENVAULT_PATH"])
    password = get_password()
    keys = list_pinned(vault_path, password)
    if not keys:
        click.echo("No pinned variables.")
    else:
        for k in keys:
            click.echo(k)
