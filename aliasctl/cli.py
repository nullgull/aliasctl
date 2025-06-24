import pyperclip
import typer
from aliasctl import alias_manager
from aliasctl.ui import EmailApp
from rich.prompt import Confirm, Prompt


app = typer.Typer()


@app.command()
def create(identifier: str, custom: str = typer.Option(None)):
	alias = alias_manager.create_alias(identifier, custom)
	copy_to_clipboard(alias)


@app.command()
def get(identifier: str):
	alias = alias_manager.get_alias(identifier)

	if alias:
		copy_to_clipboard(alias)
	else:
		typer.echo(f"✖ Alias for '{identifier}' not found.")
		prompt_create(identifier)


@app.command()
def reply(identifier: str, recipient: str = typer.Option(..., help="Recipient email"),
					message_id: str = typer.Option(None, help="Message-ID of the email being replied to")):
	alias = alias_manager.get_alias(identifier)

	if not alias:
		typer.echo(f"Alias not found for identifier: {identifier}")
		raise typer.Exit(1)

	EmailApp(alias=alias, recipient=recipient, message_id=message_id).run()


@app.command()
def tui():
	EmailApp().run()


def copy_to_clipboard(alias):
	pyperclip.copy(alias)
	typer.echo(f"🐓🐓🐓 Alias {alias} copied to clipboard! 🐓🐓🐓")


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