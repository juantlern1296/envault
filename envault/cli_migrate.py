"""CLI commands for vault migrations."""

import click

from envault.cli import get_password
from envault.migrate import list_migrations, run_migrations


@click.group("migrate")
def migrate_group() -> None:
    """Manage vault schema migrations."""


@migrate_group.command("run")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file.")
@click.option("--version", multiple=True, default=None, help="Specific version(s) to apply.")
def cmd_run(vault: str, version: tuple) -> None:
    """Apply pending migrations to the vault."""
    password = get_password()
    versions = list(version) if version else None
    result = run_migrations(vault, password, versions=versions)

    if result.applied:
        for v in result.applied:
            click.echo(f"applied  {v}")
    if result.skipped:
        for v in result.skipped:
            click.echo(f"skipped  {v}")
    if result.errors:
        for v, msg in result.errors.items():
            click.echo(f"error    {v}: {msg}", err=True)
        raise SystemExit(1)

    if not result.applied and not result.errors:
        click.echo("no migrations to apply")


@migrate_group.command("status")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file.")
def cmd_status(vault: str) -> None:
    """Show migration status for the vault."""
    password = get_password()
    statuses = list_migrations(vault, password)
    if not statuses:
        click.echo("no migrations registered")
        return
    for version, status in statuses.items():
        click.echo(f"{status:<10} {version}")
