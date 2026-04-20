"""CLI commands for diffing vault states."""
import click
from envault.diff import diff_vault_files, diff_vaults
from envault.vault import load_vault
from envault.cli import get_password

STATUS_SYMBOLS = {
    "added": ("+ ", "green"),
    "removed": ("- ", "red"),
    "changed": ("~ ", "yellow"),
    "unchanged": ("  ", "white"),
}


@click.group("diff")
def diff_group():
    """Diff vault contents."""


@diff_group.command("files")
@click.argument("old_vault", type=click.Path(exists=True))
@click.argument("new_vault", type=click.Path(exists=True))
@click.option("--show-unchanged", is_flag=True, default=False)
def cmd_diff_files(old_vault, new_vault, show_unchanged):
    """Diff two vault files."""
    password = get_password(confirm=False)
    entries = diff_vault_files(old_vault, new_vault, password, show_unchanged=show_unchanged)
    if not entries:
        click.echo("No differences found.")
        return
    for entry in entries:
        symbol, color = STATUS_SYMBOLS[entry.status]
        if entry.status == "changed":
            click.secho(f"{symbol}{entry.key}: {entry.old_value!r} -> {entry.new_value!r}", fg=color)
        elif entry.status == "added":
            click.secho(f"{symbol}{entry.key}={entry.new_value!r}", fg=color)
        elif entry.status == "removed":
            click.secho(f"{symbol}{entry.key}={entry.old_value!r}", fg=color)
        else:
            click.secho(f"{symbol}{entry.key}={entry.old_value!r}", fg=color)


@diff_group.command("show")
@click.argument("vault_path", type=click.Path(exists=True))
@click.option("--against", type=click.Path(exists=True), default=None,
              help="Compare against another vault file instead of empty baseline.")
@click.option("--show-unchanged", is_flag=True, default=False)
def cmd_diff_show(vault_path, against, show_unchanged):
    """Show diff of a vault against a baseline (or empty)."""
    password = get_password(confirm=False)
    new_data = load_vault(vault_path, password)
    old_data = load_vault(against, password) if against else {}
    entries = diff_vaults(old_data, new_data, show_unchanged=show_unchanged)
    if not entries:
        click.echo("No differences.")
        return
    for entry in entries:
        symbol, color = STATUS_SYMBOLS[entry.status]
        val = entry.new_value if entry.status in ("added", "unchanged") else entry.old_value
        if entry.status == "changed":
            click.secho(f"{symbol}{entry.key}: {entry.old_value!r} -> {entry.new_value!r}", fg=color)
        else:
            click.secho(f"{symbol}{entry.key}={val!r}", fg=color)
