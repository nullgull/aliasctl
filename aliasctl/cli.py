import pyperclip
import typer
from aliasctl import alias_manager
from aliasctl.ui import EmailApp
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

app = typer.Typer()


@app.command()
def create(identifier: str, custom: str = typer.Option(None)):
	existing_alias = alias_manager.get_alias(identifier)

	if existing_alias:
		typer.echo(f"👀 Alias already exists.")
		alias = existing_alias
	else:
		alias = alias_manager.create_alias(identifier, custom)

	copy_to_clipboard(alias)


@app.command()
def get(identifier: str):
	alias = alias_manager.get_alias(identifier)

	if alias:
		copy_to_clipboard(alias)
	else:
		alias_not_found(identifier)
		prompt_create(identifier)


@app.command()
def delete(identifier: str):
	deleted = alias_manager.delete_alias(identifier)
	typer.echo(f"✅ Deleted alias: {deleted}") if deleted else alias_not_found(identifier)


@app.command()
def list():
	rows = alias_manager.all_aliases()

	if not rows:
		typer.echo("No aliases found.")
		return

	table = Table(show_header=True, header_style="bold", show_lines=True)
	table.add_column("#", justify="right", style="dim", no_wrap=True)
	table.add_column("Identifier", style="cyan", no_wrap=True)
	table.add_column("Email")
	table.add_column("Date Added")

	for index, r in enumerate(rows, start=1):
		table.add_row(str(index), r["identifier"], r["email"], r["created"])

	Console().print(table)


@app.command()
def reply(identifier: str, recipient: str = typer.Option(..., help="Recipient email"),
					message_id: str = typer.Option(None, help="Message-ID of the email being replied to")):
	alias = alias_manager.get_alias(identifier)

	if not alias:
		alias_not_found(identifier)
		raise typer.Exit(1)

	EmailApp(alias=alias, recipient=recipient, message_id=message_id).run()


@app.command()
def tui():
	EmailApp().run()


def copy_to_clipboard(alias):
	pyperclip.copy(alias)
	typer.echo(f"🐓🐓🐓 Alias {alias} copied to clipboard! 🐓🐓🐓")


def alias_not_found(identifier):
	typer.echo(f"❌ Alias for '{identifier}' not found.")


def prompt_create(identifier):
	if Confirm.ask(f"Create an alias for {identifier}?"):
		custom = None

		if Confirm.ask("Is this a custom alias?"):
			custom = prompt_non_empty("Enter custom alias")

		alias = alias_manager.create_alias(identifier, custom)
		copy_to_clipboard(alias)
	else:
		typer.echo("❌ Aborted.")


def prompt_non_empty(prompt_text):
	while True:
		value = Prompt.ask(prompt_text)
		if value.strip():
			return value
		else:
			print("❗️ Input cannot be empty.")


def main():
	alias_manager.ensure_config()
	app()