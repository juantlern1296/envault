"""CLI commands for namespace management."""

import click
from envault.cli import get_password
from envault.namespace import (
    ns_set, ns_get, ns_delete, list_namespaces, ns_list_vars, ns_clear,
)


@click.group("ns")
def ns_group():
    """Manage namespaced environment variables."""


@ns_group.command("set")
@click.argument("namespace")
@click.argument("key")
@click.argument("value")
@click.pass_context
def cmd_set(ctx, namespace, key, value):
    """Set KEY=VALUE inside NAMESPACE."""
    vault = ctx.obj["vault"]
    password = get_password()
    ns_set(vault, password, namespace, key, value)
    click.echo(f"Set {namespace}::{key}")


@ns_group.command("get")
@click.argument("namespace")
@click.argument("key")
@click.pass_context
def cmd_get(ctx, namespace, key):
    """Get the value of KEY from NAMESPACE."""
    vault = ctx.obj["vault"]
    password = get_password()
    try:
        value = ns_get(vault, password, namespace, key)
        click.echo(value)
    except KeyError:
        click.echo(f"Key '{namespace}::{key}' not found.", err=True)
        raise SystemExit(1)


@ns_group.command("delete")
@click.argument("namespace")
@click.argument("key")
@click.pass_context
def cmd_delete(ctx, namespace, key):
    """Delete KEY from NAMESPACE."""
    vault = ctx.obj["vault"]
    password = get_password()
    try:
        ns_delete(vault, password, namespace, key)
        click.echo(f"Deleted {namespace}::{key}")
    except KeyError:
        click.echo(f"Key '{namespace}::{key}' not found.", err=True)
        raise SystemExit(1)


@ns_group.command("list")
@click.pass_context
def cmd_list(ctx, ):
    """List all namespaces."""
    vault = ctx.obj["vault"]
    password = get_password()
    namespaces = list_namespaces(vault, password)
    if not namespaces:
        click.echo("No namespaces found.")
    else:
        for ns in namespaces:
            click.echo(ns)


@ns_group.command("show")
@click.argument("namespace")
@click.pass_context
def cmd_show(ctx, namespace):
    """Show all variables in NAMESPACE."""
    vault = ctx.obj["vault"]
    password = get_password()
    vars_ = ns_list_vars(vault, password, namespace)
    if not vars_:
        click.echo(f"No variables in namespace '{namespace}'.")
    else:
        for k, v in sorted(vars_.items()):
            click.echo(f"{k}={v}")


@ns_group.command("clear")
@click.argument("namespace")
@click.pass_context
def cmd_clear(ctx, namespace):
    """Delete all variables in NAMESPACE."""
    vault = ctx.obj["vault"]
    password = get_password()
    count = ns_clear(vault, password, namespace)
    click.echo(f"Cleared {count} variable(s) from namespace '{namespace}'.")
