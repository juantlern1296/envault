"""CLI commands for TTL management."""

import click
from envault.cli import get_password, cli
from envault.ttl import set_ttl, get_ttl, is_expired, purge_expired
import os


@cli.group("ttl")
def ttl_group():
    """Manage variable expiry (TTL)."""


@ttl_group.command("set")
@click.argument("key")
@click.argument("seconds", type=int)
@click.pass_context
def cmd_set(ctx, key, seconds):
    """Set TTL (seconds) on a variable."""
    vault_path = os.environ["ENVAULT_PATH"]
    password = get_password()
    try:
        set_ttl(vault_path, password, key, seconds)
        click.echo(f"TTL set: '{key}' expires in {seconds}s")
    except KeyError as e:
        click.echo(str(e), err=True)
        ctx.exit(1)


@ttl_group.command("get")
@click.argument("key")
@click.pass_context
def cmd_get(ctx, key):
    """Show expiry time for a variable."""
    vault_path = os.environ["ENVAULT_PATH"]
    password = get_password()
    expiry = get_ttl(vault_path, password, key)
    if expiry is None:
        click.echo(f"No TTL set for '{key}'")
    else:
        expired = is_expired(vault_path, password, key)
        status = " [EXPIRED]" if expired else ""
        click.echo(f"{key} expires at {expiry}{status}")


@ttl_group.command("purge")
@click.pass_context
def cmd_purge(ctx):
    """Remove all expired variables from the vault."""
    vault_path = os.environ["ENVAULT_PATH"]
    password = get_password()
    removed = purge_expired(vault_path, password)
    if removed:
        for k in removed:
            click.echo(f"Purged: {k}")
    else:
        click.echo("Nothing to purge.")
