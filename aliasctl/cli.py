import pyperclip
import typer
from aliasctl import alias_manager
from aliasctl.ui import EmailApp


app = typer.Typer()

@app.command()
def create(identifier: str, custom: str = typer.Option(None)):
	alias = alias_manager.create_alias(identifier, custom)
	pyperclip.copy(alias)
	typer.echo(f"Alias: {alias} (copied to clipboard)")


@app.command()
def reply(identifier: str, recipient: str = typer.Option(..., help="Recipient email"),
					message_id: str = typer.Option(None, help="Message-ID of the email being replied to")):
	aliases = alias_manager.load_aliases()
	alias = alias_manager.get_alias(aliases, identifier)

	if not alias:
		typer.echo(f"Alias not found for identifier: {identifier}")
		raise typer.Exit(1)

	EmailApp(alias=alias, recipient=recipient, message_id=message_id).run()

@app.command()
def tui():
	EmailApp().run()

def main():
	alias_manager.ensure_config()
	app()