"""CLI commands for managing vault variable policies."""

import json
import os
import sys

import click

from envault.cli import get_password
from envault.policy import check_policies, delete_policy, get_policy, set_policy


@click.group("policy")
def policy_group() -> None:
    """Manage access policies for vault variables."""


@policy_group.command("set")
@click.argument("key")
@click.option("--required", is_flag=True, default=False, help="Key must exist.")
@click.option("--min-length", type=int, default=None, help="Minimum value length.")
@click.option("--max-length", type=int, default=None, help="Maximum value length.")
@click.option("--pattern", default=None, help="Regex the value must fully match.")
def cmd_set(key: str, required: bool, min_length, max_length, pattern) -> None:
    """Set policy rules for KEY."""
    vault_file = os.environ["ENVAULT_FILE"]
    rules: dict = {}
    if required:
        rules["required"] = True
    if min_length is not None:
        rules["min_length"] = min_length
    if max_length is not None:
        rules["max_length"] = max_length
    if pattern:
        rules["pattern"] = pattern
    if not rules:
        click.echo("No rules specified.", err=True)
        sys.exit(1)
    set_policy(vault_file, key, rules)
    click.echo(f"Policy set for '{key}'.")


@policy_group.command("get")
@click.argument("key")
def cmd_get(key: str) -> None:
    """Show policy rules for KEY."""
    vault_file = os.environ["ENVAULT_FILE"]
    policy = get_policy(vault_file, key)
    if policy is None:
        click.echo(f"No policy for '{key}'.")
    else:
        click.echo(json.dumps(policy, indent=2))


@policy_group.command("delete")
@click.argument("key")
def cmd_delete(key: str) -> None:
    """Remove policy rules for KEY."""
    vault_file = os.environ["ENVAULT_FILE"]
    try:
        delete_policy(vault_file, key)
        click.echo(f"Policy deleted for '{key}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@policy_group.command("check")
def cmd_check() -> None:
    """Validate vault contents against all defined policies."""
    vault_file = os.environ["ENVAULT_FILE"]
    password = get_password()
    violations = check_policies(vault_file, password)
    if not violations:
        click.echo("All policies satisfied.")
    else:
        for v in violations:
            click.echo(f"  VIOLATION: {v}")
        sys.exit(1)
