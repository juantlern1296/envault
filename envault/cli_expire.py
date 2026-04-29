"""CLI commands for managing key expiry dates."""

from __future__ import annotations

from datetime import datetime, timezone

import click

from envault.cli import get_password
from envault.expire import ExpireError, get_expiry, is_expired, purge_expired, remove_expiry, set_expiry


@click.group("expire")
def expire_group() -> None:
    """Manage absolute expiry dates for vault keys."""


@expire_group.command("set")
@click.argument("key")
@click.argument("expires_at")  # ISO-8601 string, e.g. 2025-12-31T00:00:00+00:00
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_set(key: str, expires_at: str, vault: str) -> None:
    """Set an absolute expiry date for KEY."""
    password = get_password()
    try:
        dt = datetime.fromisoformat(expires_at).astimezone(timezone.utc)
    except ValueError:
        click.echo(f"Invalid datetime: {expires_at}", err=True)
        raise SystemExit(1)
    try:
        set_expiry(vault, password, key, dt)
        click.echo(f"Expiry set for '{key}': {dt.isoformat()}")
    except ExpireError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@expire_group.command("get")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_get(key: str, vault: str) -> None:
    """Show the expiry date for KEY."""
    expiry = get_expiry(vault, key)
    if expiry is None:
        click.echo(f"No expiry set for '{key}'")
    else:
        status = "EXPIRED" if is_expired(vault, key) else "valid"
        click.echo(f"{key}: {expiry.isoformat()} [{status}]")


@expire_group.command("remove")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_remove(key: str, vault: str) -> None:
    """Remove the expiry policy for KEY."""
    remove_expiry(vault, key)
    click.echo(f"Expiry removed for '{key}'")


@expire_group.command("purge")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_purge(vault: str) -> None:
    """Delete all vault keys that have passed their expiry date."""
    password = get_password()
    purged = purge_expired(vault, password)
    if purged:
        for key in purged:
            click.echo(f"Purged: {key}")
    else:
        click.echo("No expired keys found.")
