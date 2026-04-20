"""CLI commands for alias management."""

from __future__ import annotations

import click

from envault.cli import get_password
from envault.alias import add_alias, remove_alias, resolve_alias, get_via_alias, list_aliases


@click.group("alias")
def alias_group() -> None:
    """Manage key aliases."""


@alias_group.command("add")
@click.argument("alias")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True, help="Path to vault file")
def cmd_add(alias: str, key: str, vault: str) -> None:
    """Create ALIAS pointing to KEY."""
    password = get_password()
    try:
        add_alias(vault, password, alias, key)
        click.echo(f"Alias '{alias}' -> '{key}' created.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@alias_group.command("remove")
@click.argument("alias")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True, help="Path to vault file")
def cmd_remove(alias: str, vault: str) -> None:
    """Remove ALIAS."""
    password = get_password()
    try:
        remove_alias(vault, password, alias)
        click.echo(f"Alias '{alias}' removed.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@alias_group.command("get")
@click.argument("alias")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True, help="Path to vault file")
def cmd_get(alias: str, vault: str) -> None:
    """Print the value of the variable pointed to by ALIAS."""
    password = get_password()
    try:
        value = get_via_alias(vault, password, alias)
        click.echo(value)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@alias_group.command("list")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True, help="Path to vault file")
def cmd_list(vault: str) -> None:
    """List all aliases."""
    password = get_password()
    aliases = list_aliases(vault, password)
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, key in sorted(aliases.items()):
        click.echo(f"{alias} -> {key}")
