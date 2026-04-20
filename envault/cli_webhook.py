"""CLI commands for managing vault webhooks."""

import click
from pathlib import Path

from envault.cli import get_password
from envault.webhook import add_webhook, remove_webhook, list_webhooks


@click.group("webhook")
def webhook_group():
    """Manage webhook notifications for vault events."""


@webhook_group.command("add")
@click.argument("name")
@click.argument("url")
@click.option("--event", "events", multiple=True, required=True,
              help="Event to subscribe to (repeatable). E.g. set, delete, rotate")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file")
def cmd_add(name, url, events, vault):
    """Register a webhook NAME pointing to URL for one or more EVENTS."""
    password = get_password()
    add_webhook(Path(vault), password, name, url, list(events))
    click.echo(f"Webhook '{name}' registered for events: {', '.join(events)}")


@webhook_group.command("remove")
@click.argument("name")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file")
def cmd_remove(name, vault):
    """Remove a registered webhook by NAME."""
    password = get_password()
    try:
        remove_webhook(Path(vault), password, name)
        click.echo(f"Webhook '{name}' removed.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@webhook_group.command("list")
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file")
def cmd_list(vault):
    """List all registered webhooks."""
    password = get_password()
    hooks = list_webhooks(Path(vault), password)
    if not hooks:
        click.echo("No webhooks registered.")
        return
    for name, cfg in hooks.items():
        events = ", ".join(cfg.get("events", []))
        click.echo(f"{name}  {cfg['url']}  [{events}]")
