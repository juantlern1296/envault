"""CLI commands for vault integrity verification."""

from __future__ import annotations

import os
import sys

import click

from envault.verify import verify_vault, summarise_report


@click.group("verify")
def verify_group() -> None:
    """Verify vault integrity."""


@verify_group.command("run")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--quiet", "-q", is_flag=True, help="Only print failures.")
def cmd_run(vault: str, password: str, quiet: bool) -> None:
    """Decrypt every entry and report any that fail."""
    if not os.path.exists(vault):
        click.echo(f"Vault not found: {vault}", err=True)
        sys.exit(1)

    report = verify_vault(vault, password)

    if quiet:
        for r in report.failed:
            click.echo(f"FAIL  {r.key}: {r.error}")
    else:
        click.echo(summarise_report(report))

    if not report.success:
        sys.exit(1)


@verify_group.command("status")
@click.option("--vault", envvar="ENVAULT_PATH", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def cmd_status(vault: str, password: str) -> None:
    """Print a one-line summary of vault health."""
    if not os.path.exists(vault):
        click.echo(f"Vault not found: {vault}", err=True)
        sys.exit(1)

    report = verify_vault(vault, password)
    total = len(report.results)
    failed = len(report.failed)

    if report.success:
        click.echo(f"vault OK — {total} entries verified")
    else:
        click.echo(f"vault DEGRADED — {failed}/{total} entries failed", err=True)
        sys.exit(1)
