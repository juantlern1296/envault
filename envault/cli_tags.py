"""CLI commands for tagging environment variables."""
import click
from envault.cli import get_password
from envault.tags import tag_var, untag_var, list_tags, vars_for_tag


@click.group(name="tag")
def tag_group():
    """Manage variable tags."""


@tag_group.command(name="add")
@click.argument("var")
@click.argument("tag")
@click.pass_context
def cmd_add(ctx, var, tag):
    """Add TAG to VAR."""
    vault_path = ctx.obj["vault_path"]
    password = get_password()
    tag_var(vault_path, password, var, tag)
    click.echo(f"Tagged {var!r} with {tag!r}")


@tag_group.command(name="remove")
@click.argument("var")
@click.argument("tag")
@click.pass_context
def cmd_remove(ctx, var, tag):
    """Remove TAG from VAR."""
    vault_path = ctx.obj["vault_path"]
    password = get_password()
    try:
        untag_var(vault_path, password, var, tag)
        click.echo(f"Removed tag {tag!r} from {var!r}")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tag_group.command(name="list")
@click.pass_context
def cmd_list(ctx):
    """List all tags and their variables."""
    vault_path = ctx.obj["vault_path"]
    password = get_password()
    tags = list_tags(vault_path, password)
    if not tags:
        click.echo("No tags defined.")
        return
    for tag, vars_ in sorted(tags.items()):
        click.echo(f"{tag}: {', '.join(vars_)}")


@tag_group.command(name="show")
@click.argument("tag")
@click.pass_context
def cmd_show(ctx, tag):
    """Show variables for TAG."""
    vault_path = ctx.obj["vault_path"]
    password = get_password()
    vars_ = vars_for_tag(vault_path, password, tag)
    if not vars_:
        click.echo(f"No variables tagged with {tag!r}")
    else:
        for v in vars_:
            click.echo(v)
