"""CLI commands for vault snapshots."""
import click
from envault.cli import get_password
from envault.snapshot import create_snapshot, list_snapshots, restore_snapshot, delete_snapshot


@click.group("snapshot")
def snapshot_group():
    """Manage vault snapshots."""


@snapshot_group.command("create")
@click.argument("name")
@click.option("--vault", envvar="ENVAULT_PATH", required=True)
def cmd_create(name, vault):
    """Create a snapshot of the current vault state."""
    password = get_password()
    create_snapshot(vault, password, name)
    click.echo(f"Snapshot '{name}' created.")


@snapshot_group.command("list")
@click.option("--vault", envvar="ENVAULT_PATH", required=True)
def cmd_list(vault):
    """List all snapshots."""
    snaps = list_snapshots(vault)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for s in snaps:
        import datetime
        ts = datetime.datetime.fromtimestamp(s["ts"]).strftime("%Y-%m-%d %H:%M:%S")
        click.echo(f"{s['name']:<20} {ts}  ({s['count']} vars)")


@snapshot_group.command("restore")
@click.argument("name")
@click.option("--vault", envvar="ENVAULT_PATH", required=True)
def cmd_restore(name, vault):
    """Restore vault to a saved snapshot."""
    password = get_password()
    try:
        restore_snapshot(vault, password, name)
        click.echo(f"Vault restored to snapshot '{name}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@snapshot_group.command("delete")
@click.argument("name")
@click.option("--vault", envvar="ENVAULT_PATH", required=True)
def cmd_delete(name, vault):
    """Delete a snapshot."""
    try:
        delete_snapshot(vault, name)
        click.echo(f"Snapshot '{name}' deleted.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
