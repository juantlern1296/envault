"""CLI entry point for envault."""

import os
import sys
import click

from envault.vault import set_var, get_var, delete_var, list_vars
from envault.crypto import decrypt

VAULT_FILE_ENV = "ENVAULT_FILE"
DEFAULT_VAULT = ".envault"


def get_password() -> str:
    """Read password from env var or prompt the user."""
    pw = os.environ.get("ENVAULT_PASSWORD")
    if pw:
        return pw
    return click.prompt("Vault password", hide_input=True)


@click.group()
def cli():
    """envault — securely store and sync environment variables."""


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--vault", default=None, help="Path to vault file")
def cmd_set(key, value, vault):
    """Store an environment variable in the vault."""
    vault = vault or os.environ.get(VAULT_FILE_ENV, DEFAULT_VAULT)
    password = get_password()
    set_var(key, value, password, vault)
    click.echo(f"✓ Set {key}")


@cli.command("get")
@click.argument("key")
@click.option("--vault", default=None, help="Path to vault file")
def cmd_get(key, vault):
    """Retrieve an environment variable from the vault."""
    vault = vault or os.environ.get(VAULT_FILE_ENV, DEFAULT_VAULT)
    password = get_password()
    value = get_var(key, password, vault)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        sys.exit(1)
    click.echo(value)


@cli.command("delete")
@click.argument("key")
@click.option("--vault", default=None, help="Path to vault file")
def cmd_delete(key, vault):
    """Delete an environment variable from the vault."""
    vault = vault or os.environ.get(VAULT_FILE_ENV, DEFAULT_VAULT)
    password = get_password()
    removed = delete_var(key, password, vault)
    if removed:
        click.echo(f"✓ Deleted {key}")
    else:
        click.echo(f"Key '{key}' not found.", err=True)
        sys.exit(1)


@cli.command("list")
@click.option("--vault", default=None, help="Path to vault file")
def cmd_list(vault):
    """List all keys stored in the vault."""
    vault = vault or os.environ.get(VAULT_FILE_ENV, DEFAULT_VAULT)
    password = get_password()
    data = list_vars(password, vault)
    if not data:
        click.echo("Vault is empty.")
        return
    for key, value in sorted(data.items()):
        click.echo(f"{key}={value}")


if __name__ == "__main__":
    cli()
