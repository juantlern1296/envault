"""CLI commands for profile management."""
import os
import click
from envault.cli import get_password
from envault.profile import (
    set_profile_var,
    get_profile_var,
    delete_profile_var,
    list_profiles,
    list_profile_vars,
)


@click.group("profile")
def profile_group():
    """Manage named profiles (dev, prod, etc.)."""


@profile_group.command("set")
@click.argument("profile")
@click.argument("key")
@click.argument("value")
def cmd_set(profile, key, value):
    """Set a variable in a profile."""
    vault = os.environ["ENVAULT_PATH"]
    password = get_password()
    set_profile_var(vault, password, profile, key, value)
    click.echo(f"[{profile}] {key} set.")


@profile_group.command("get")
@click.argument("profile")
@click.argument("key")
def cmd_get(profile, key):
    """Get a variable from a profile."""
    vault = os.environ["ENVAULT_PATH"]
    password = get_password()
    try:
        value = get_profile_var(vault, password, profile, key)
        click.echo(value)
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_group.command("delete")
@click.argument("profile")
@click.argument("key")
def cmd_delete(profile, key):
    """Delete a variable from a profile."""
    vault = os.environ["ENVAULT_PATH"]
    password = get_password()
    try:
        delete_profile_var(vault, password, profile, key)
        click.echo(f"[{profile}] {key} deleted.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_group.command("list")
@click.argument("profile", required=False)
def cmd_list(profile):
    """List profiles or variables within a profile."""
    vault = os.environ["ENVAULT_PATH"]
    password = get_password()
    if profile:
        vars_ = list_profile_vars(vault, password, profile)
        for k, v in vars_.items():
            click.echo(f"{k}={v}")
    else:
        profiles = list_profiles(vault, password)
        for name, keys in profiles.items():
            click.echo(f"{name}: {', '.join(keys)}")
