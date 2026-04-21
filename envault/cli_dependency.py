"""CLI commands for variable dependency management."""
import click

from envault.cli import get_password
from envault.dependency import (
    add_dependency,
    dependents_of,
    list_dependencies,
    remove_dependency,
    resolve_order,
)


@click.group("dep")
def dep_group() -> None:
    """Manage variable dependencies."""


@dep_group.command("add")
@click.argument("key")
@click.argument("depends_on")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_add(key: str, depends_on: str, vault: str) -> None:
    """Declare that KEY depends on DEPENDS_ON."""
    password = get_password()
    try:
        add_dependency(vault, password, key, depends_on)
        click.echo(f"Added dependency: {key} -> {depends_on}")
    except (KeyError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@dep_group.command("remove")
@click.argument("key")
@click.argument("depends_on")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_remove(key: str, depends_on: str, vault: str) -> None:
    """Remove a declared dependency."""
    try:
        remove_dependency(vault, key, depends_on)
        click.echo(f"Removed dependency: {key} -> {depends_on}")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@dep_group.command("list")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_list(key: str, vault: str) -> None:
    """List keys that KEY depends on."""
    deps = list_dependencies(vault, key)
    if not deps:
        click.echo(f"{key} has no dependencies.")
    else:
        for d in deps:
            click.echo(d)


@dep_group.command("dependents")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_dependents(key: str, vault: str) -> None:
    """List keys that depend on KEY."""
    result = dependents_of(vault, key)
    if not result:
        click.echo(f"No keys depend on {key}.")
    else:
        for d in result:
            click.echo(d)


@dep_group.command("order")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_order(vault: str) -> None:
    """Print keys in dependency-resolved (topological) order."""
    order = resolve_order(vault)
    if not order:
        click.echo("No dependencies defined.")
    else:
        for key in order:
            click.echo(key)
