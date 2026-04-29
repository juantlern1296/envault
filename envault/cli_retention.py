"""CLI commands for retention policies."""

import click

from envault.cli import get_password
from envault.retention import (
    RetentionError,
    get_retention,
    purge_stale,
    remove_retention,
    set_retention,
    touch_key,
)


@click.group("retention")
def retention_group():
    """Manage key retention policies."""


@retention_group.command("set")
@click.argument("key")
@click.argument("days", type=int)
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_set(key: str, days: int, vault: str):
    """Set a retention policy of DAYS days for KEY."""
    password = get_password()
    try:
        set_retention(vault, password, key, days)
        click.echo(f"Retention policy set: '{key}' expires after {days} day(s) of inactivity.")
    except RetentionError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@retention_group.command("get")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_get(key: str, vault: str):
    """Show retention policy for KEY."""
    info = get_retention(vault, key)
    if info is None:
        click.echo(f"No retention policy set for '{key}'.")
    else:
        click.echo(f"{key}: {info['days']} day(s), last accessed {info['last_accessed']}")


@retention_group.command("remove")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_remove(key: str, vault: str):
    """Remove retention policy for KEY."""
    try:
        remove_retention(vault, key)
        click.echo(f"Retention policy removed for '{key}'.")
    except RetentionError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@retention_group.command("purge")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_purge(vault: str):
    """Delete all vars whose retention period has elapsed."""
    password = get_password()
    deleted = purge_stale(vault, password)
    if deleted:
        for key in deleted:
            click.echo(f"Deleted: {key}")
        click.echo(f"{len(deleted)} key(s) purged.")
    else:
        click.echo("Nothing to purge.")
