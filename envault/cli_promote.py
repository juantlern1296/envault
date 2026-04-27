"""CLI commands for promoting variables between namespaces/profiles."""
from __future__ import annotations

import click

from envault.cli import get_password
from envault.promote import PromoteError, promote_all, promote_var


@click.group("promote")
def promote_group() -> None:
    """Promote variables from one namespace to another."""


@promote_group.command("var")
@click.argument("key")
@click.argument("src")
@click.argument("dst")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in destination.")
@click.pass_context
def cmd_promote_var(ctx: click.Context, key: str, src: str, dst: str, overwrite: bool) -> None:
    """Promote KEY from SRC namespace to DST namespace."""
    vault_path = ctx.obj["vault"]
    password = get_password()
    try:
        result = promote_var(vault_path, password, key, src, dst, overwrite=overwrite)
    except PromoteError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)
        return

    if result.skipped:
        click.echo(f"Skipped '{key}' (already exists in '{dst}', use --overwrite to replace)")
    elif result.overwritten:
        click.echo(f"Overwritten '{key}' in '{dst}'")
    else:
        click.echo(f"Promoted '{key}' from '{src}' to '{dst}'")


@promote_group.command("all")
@click.argument("src")
@click.argument("dst")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in destination.")
@click.option("--key", "keys", multiple=True, help="Limit promotion to specific keys (repeatable).")
@click.pass_context
def cmd_promote_all(ctx: click.Context, src: str, dst: str, overwrite: bool, keys: tuple) -> None:
    """Promote all variables from SRC namespace to DST namespace."""
    vault_path = ctx.obj["vault"]
    password = get_password()
    selected = list(keys) if keys else None
    result = promote_all(vault_path, password, src, dst, overwrite=overwrite, keys=selected)

    total = len(result.promoted) + len(result.overwritten)
    click.echo(f"Promoted: {len(result.promoted)}  Overwritten: {len(result.overwritten)}  Skipped: {len(result.skipped)}")
    if result.skipped:
        click.echo("Skipped keys (use --overwrite): " + ", ".join(result.skipped))
    if total == 0 and not result.skipped:
        click.echo(f"No variables found in namespace '{src}'")
