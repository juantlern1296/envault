"""CLI commands for managing per-namespace variable quotas."""

import click

from envault.cli import get_password
from envault.quota import (
    QuotaExceeded,
    check_quota,
    delete_quota,
    get_quota,
    set_quota,
)
from envault.vault import load_vault


@click.group("quota")
def quota_group():
    """Manage variable quotas per namespace."""


@quota_group.command("set")
@click.argument("namespace")
@click.argument("limit", type=int)
@click.option("--vault", envvar="ENVAULT_VAULT", required=True, help="Path to vault file.")
def cmd_set(namespace: str, limit: int, vault: str):
    """Set the maximum number of variables for NAMESPACE."""
    password = get_password()
    try:
        set_quota(vault, password, namespace, limit)
        click.echo(f"Quota for '{namespace}' set to {limit}.")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@quota_group.command("get")
@click.argument("namespace")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_get(namespace: str, vault: str):
    """Show the quota for NAMESPACE."""
    password = get_password()
    limit = get_quota(vault, password, namespace)
    if limit is None:
        click.echo(f"No quota set for '{namespace}'.")
    else:
        click.echo(f"{namespace}: {limit}")


@quota_group.command("delete")
@click.argument("namespace")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_delete(namespace: str, vault: str):
    """Remove the quota for NAMESPACE."""
    password = get_password()
    try:
        delete_quota(vault, password, namespace)
        click.echo(f"Quota for '{namespace}' removed.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@quota_group.command("check")
@click.argument("namespace")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True)
def cmd_check(namespace: str, vault: str):
    """Check whether NAMESPACE has capacity remaining."""
    password = get_password()
    try:
        check_quota(vault, password, namespace)
        click.echo(f"'{namespace}' is within quota.")
    except QuotaExceeded as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
