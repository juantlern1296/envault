"""CLI commands for the reminder feature."""
import click
from envault.cli import get_password, cli
from envault.remind import set_reminder, get_reminder, remove_reminder, due_reminders
import os


@cli.group("remind")
def remind_group():
    """Manage key review reminders."""


@remind_group.command("set")
@click.argument("key")
@click.argument("days", type=int)
@click.pass_context
def cmd_set(ctx, key: str, days: int):
    """Set a reminder for KEY in DAYS days."""
    vault_file = os.environ["ENVAULT_FILE"]
    password = get_password()
    try:
        due = set_reminder(vault_file, password, key, days)
        click.echo(f"Reminder set for '{key}' due {due.strftime('%Y-%m-%d %H:%M UTC')}")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        ctx.exit(1)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        ctx.exit(1)


@remind_group.command("get")
@click.argument("key")
@click.pass_context
def cmd_get(ctx, key: str):
    """Show the reminder date for KEY."""
    vault_file = os.environ["ENVAULT_FILE"]
    due = get_reminder(vault_file, key)
    if due is None:
        click.echo(f"No reminder set for '{key}'")
        ctx.exit(1)
    else:
        click.echo(due.strftime("%Y-%m-%d %H:%M UTC"))


@remind_group.command("remove")
@click.argument("key")
@click.pass_context
def cmd_remove(ctx, key: str):
    """Remove the reminder for KEY."""
    vault_file = os.environ["ENVAULT_FILE"]
    try:
        remove_reminder(vault_file, key)
        click.echo(f"Reminder for '{key}' removed.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        ctx.exit(1)


@remind_group.command("due")
def cmd_due():
    """List all keys whose reminders are past due."""
    vault_file = os.environ["ENVAULT_FILE"]
    items = due_reminders(vault_file)
    if not items:
        click.echo("No reminders due.")
        return
    for key, due in items:
        click.echo(f"{key}  (was due {due.strftime('%Y-%m-%d %H:%M UTC')})")
