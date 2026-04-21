"""CLI commands for the cascade feature."""

from __future__ import annotations

import click

from envault.cascade import cascade_var, CascadeError
from envault.cli import get_password


@click.group("cascade")
def cascade_group():
    """Propagate a variable's value to other keys."""


@cascade_group.command("push")
@click.argument("source_key")
@click.argument("target_keys", nargs=-1, required=True)
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Vault file path.")
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip existing keys.")
def cmd_push(source_key, target_keys, vault, no_overwrite):
    """Copy SOURCE_KEY value to one or more TARGET_KEYS."""
    password = get_password()
    try:
        result = cascade_var(
            vault,
            password,
            source_key,
            list(target_keys),
            overwrite=not no_overwrite,
        )
    except CascadeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    for key in result.updated:
        click.echo(f"updated: {key}")
    for key in result.skipped:
        click.echo(f"skipped (exists): {key}")
    for key in result.failed:
        click.echo(f"failed: {key}", err=True)

    if result.failed:
        raise SystemExit(1)
