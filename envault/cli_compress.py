"""CLI commands for vault compression."""

import os
from pathlib import Path

import click

from envault.compress import compress_vault, decompress_vault, compress_ratio
from envault.cli import get_password


@click.group("compress")
def compress_group() -> None:
    """Compress or decompress vault values."""


@compress_group.command("pack")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file.")
def cmd_pack(vault: str) -> None:
    """Compress all values in the vault."""
    path = Path(vault)
    if not path.exists():
        click.echo(f"Vault not found: {vault}", err=True)
        raise SystemExit(1)
    password = get_password()
    count = compress_vault(path, password)
    click.echo(f"Compressed {count} value(s).")


@compress_group.command("unpack")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file.")
def cmd_unpack(vault: str) -> None:
    """Decompress all compressed values in the vault."""
    path = Path(vault)
    if not path.exists():
        click.echo(f"Vault not found: {vault}", err=True)
        raise SystemExit(1)
    password = get_password()
    count = decompress_vault(path, password)
    click.echo(f"Decompressed {count} value(s).")


@compress_group.command("ratio")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file.")
def cmd_ratio(vault: str) -> None:
    """Show compression ratio for each compressed key."""
    path = Path(vault)
    if not path.exists():
        click.echo(f"Vault not found: {vault}", err=True)
        raise SystemExit(1)
    password = get_password()
    ratios = compress_ratio(path, password)
    if not ratios:
        click.echo("No compressed values found.")
        return
    for key, ratio in sorted(ratios.items()):
        pct = ratio * 100
        click.echo(f"{key}: {pct:.1f}% of original size")
