"""CLI commands for managing webhooks."""

import click
from .webhook import add_webhook, remove_webhook, list_webhooks, fire_webhooks
from .cli import get_password


@click.group("webhook")
def webhook_group():
    """Manage webhooks triggered on vault changes."""
    pass


@webhook_group.command("add")
@click.argument("url")
@click.option("--event", default="any", show_default=True,
              help="Event type to trigger on: set, delete, rotate, any.")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True, help="Path to vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None, hidden=True)
def cmd_add(url, event, vault, password):
    """Register a webhook URL for vault events."""
    password = get_password(password)
    try:
        add_webhook(vault, password, url, event)
        click.echo(f"Webhook added: {url} (event={event})")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@webhook_group.command("remove")
@click.argument("url")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True, help="Path to vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None, hidden=True)
def cmd_remove(url, vault, password):
    """Remove a registered webhook URL."""
    password = get_password(password)
    try:
        remove_webhook(vault, password, url)
        click.echo(f"Webhook removed: {url}")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@webhook_group.command("list")
@click.option("--vault", envvar="ENVAULT_VAULT", required=True, help="Path to vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None, hidden=True)
def cmd_list(vault, password):
    """List all registered webhooks."""
    password = get_password(password)
    try:
        hooks = list_webhooks(vault, password)
        if not hooks:
            click.echo("No webhooks registered.")
            return
        click.echo(f"{'URL':<50} {'Event':<10}")
        click.echo("-" * 62)
        for hook in hooks:
            click.echo(f"{hook['url']:<50} {hook['event']:<10}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
