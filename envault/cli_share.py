"""CLI commands for sharing variables via encrypted tokens."""

import click
from envault.cli import get_password
from envault.share import create_share_token, import_share_token


@click.group("share")
def share_group():
    """Share variables securely with others."""


@share_group.command("create")
@click.argument("key")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file.")
@click.option("--share-password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password to encrypt the share token.")
def cmd_create(key, vault, share_password):
    """Create a share token for KEY."""
    password = get_password()
    try:
        token = create_share_token(vault, password, key, share_password)
        click.echo(f"Share token for '{key}':")
        click.echo(token)
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@share_group.command("import")
@click.argument("token")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file.")
@click.option("--key", default=None, help="Override the variable name when importing.")
@click.option("--share-password", prompt=True, hide_input=True, help="Password used to encrypt the share token.")
def cmd_import(token, vault, key, share_password):
    """Import a shared variable from TOKEN into the vault."""
    password = get_password()
    try:
        stored_key = import_share_token(vault, password, token, share_password, override_key=key)
        click.echo(f"Imported variable as '{stored_key}'.")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
