"""CLI commands for batch operations."""
import click

from envault.batch import batch_set, batch_delete, batch_get
from envault.cli import get_password


@click.group("batch")
def batch_group() -> None:
    """Perform bulk operations on vault variables."""


@batch_group.command("set")
@click.option("--vault", envvar="ENVAULT_PATH", required=True)
@click.option("--stop-on-error", is_flag=True, default=False)
@click.argument("pairs", nargs=-1, required=True)  # KEY=VALUE ...
def cmd_set(vault: str, stop_on_error: bool, pairs: tuple) -> None:
    """Set multiple KEY=VALUE pairs at once."""
    password = get_password()
    kv: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {pair!r}")
        k, v = pair.split("=", 1)
        kv[k] = v
    result = batch_set(vault, password, kv, stop_on_error=stop_on_error)
    for key in result.succeeded:
        click.echo(f"set  {key}")
    for key, err in result.failed.items():
        click.echo(f"FAIL {key}: {err}", err=True)
    if not result.ok:
        raise SystemExit(1)


@batch_group.command("delete")
@click.option("--vault", envvar="ENVAULT_PATH", required=True)
@click.option("--stop-on-error", is_flag=True, default=False)
@click.argument("keys", nargs=-1, required=True)
def cmd_delete(vault: str, stop_on_error: bool, keys: tuple) -> None:
    """Delete multiple keys at once."""
    password = get_password()
    result = batch_delete(vault, password, list(keys), stop_on_error=stop_on_error)
    for key in result.succeeded:
        click.echo(f"deleted  {key}")
    for key, err in result.failed.items():
        click.echo(f"FAIL {key}: {err}", err=True)
    if not result.ok:
        raise SystemExit(1)


@batch_group.command("get")
@click.option("--vault", envvar="ENVAULT_PATH", required=True)
@click.argument("keys", nargs=-1, required=True)
def cmd_get(vault: str, keys: tuple) -> None:
    """Retrieve multiple keys, printing KEY=VALUE lines."""
    password = get_password()
    values = batch_get(vault, password, list(keys))
    for key, val in values.items():
        if val is None:
            click.echo(f"{key}=(missing)", err=True)
        else:
            click.echo(f"{key}={val}")
