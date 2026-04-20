"""CLI commands for vault rollback."""

import click

from envault.cli import get_password
from envault.rollback import list_rollback_points, rollback_to, RollbackError


@click.group("rollback")
def rollback_group():
    """Rollback vault to a previous state."""


@rollback_group.command("list")
@click.argument("vault_path")
def cmd_list(vault_path: str):
    """List available rollback points for VAULT_PATH."""
    password = get_password()
    points = list_rollback_points(vault_path, password)
    if not points:
        click.echo("No rollback points available.")
        return
    for i, entry in enumerate(points):
        old = entry.get("old_value")
        old_display = repr(old) if old is not None else "<none>"
        click.echo(
            f"[{i}] {entry['timestamp']}  {entry['action'].upper():6s}  "
            f"{entry['key']}  (old={old_display})"
        )


@rollback_group.command("apply")
@click.argument("vault_path")
@click.argument("index", type=int)
def cmd_apply(vault_path: str, index: int):
    """Rollback VAULT_PATH by undoing the change at INDEX (0 = most recent)."""
    password = get_password()
    try:
        rollback_to(vault_path, password, index)
        click.echo(f"Rolled back change at index {index}.")
    except RollbackError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
