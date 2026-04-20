"""CLI commands for key rotation."""

import click
from envault.rotate import rotate_key
from envault.cli import get_password


@click.group("rotate")
def rotate_group():
    """Key rotation commands."""


@rotate_group.command("run")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True, help="Path to vault file.")
@click.option(
    "--old-password",
    envvar="ENVAULT_OLD_PASSWORD",
    default=None,
    help="Current vault password.",
)
@click.option(
    "--new-password",
    envvar="ENVAULT_NEW_PASSWORD",
    default=None,
    help="New vault password.",
)
def cmd_rotate(vault, old_password, new_password):
    """Re-encrypt the vault with a new password."""
    if old_password is None:
        old_password = get_password("Current password: ")
    if new_password is None:
        new_password = get_password("New password: ")
        confirm = get_password("Confirm new password: ")
        if new_password != confirm:
            click.echo("Passwords do not match.", err=True)
            raise SystemExit(1)

    try:
        count = rotate_key(vault, old_password, new_password)
        click.echo(f"Rotated {count} entr{'y' if count == 1 else 'ies'} to new password.")
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Rotation failed: {exc}", err=True)
        raise SystemExit(1)
