"""CLI commands for value transformation pipelines."""
import click

from envault.cli import get_password
from envault.transform import (
    TransformError,
    apply_pipeline,
    list_transforms,
    transform_var,
)


@click.group("transform")
def transform_group() -> None:
    """Apply transformation pipelines to vault values."""


@transform_group.command("run")
@click.argument("key")
@click.argument("transforms", nargs=-1, required=True)
@click.option("--vault", envvar="ENVAULT_PATH", required=True, help="Path to vault file")
@click.option("--dry-run", is_flag=True, default=False, help="Print result without saving")
def cmd_run(key: str, transforms: tuple[str, ...], vault: str, dry_run: bool) -> None:
    """Apply one or more TRANSFORMs to KEY and save the result."""
    password = get_password()
    pipeline = list(transforms)
    try:
        result = transform_var(vault, password, key, pipeline, dry_run=dry_run)
    except TransformError as exc:
        raise click.ClickException(str(exc)) from exc
    if dry_run:
        click.echo(f"[dry-run] {key} => {result}")
    else:
        click.echo(f"Transformed {key}: {result}")


@transform_group.command("echo")
@click.argument("value")
@click.argument("transforms", nargs=-1, required=True)
def cmd_echo(value: str, transforms: tuple[str, ...]) -> None:
    """Apply TRANSFORMs to a raw VALUE (no vault needed)."""
    pipeline = list(transforms)
    try:
        result = apply_pipeline(value, pipeline)
    except TransformError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result)


@transform_group.command("list")
def cmd_list() -> None:
    """List all available transform names."""
    for name in list_transforms():
        click.echo(name)
