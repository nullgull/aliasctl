from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Input, Button, Label, TextArea, Static
from aliasctl.mail import send_email


class EmailApp(App):
	CSS_PATH = "tui.css"

	def __init__(self, alias=None, recipient=None, message_id=None):
		super().__init__()
		self.alias = alias
		self.recipient = recipient
		self.message_id = message_id

	def compose(self) -> ComposeResult:
		yield Label("Compose Mail", id="title")
		yield Grid(id="form-grid")
		yield Button("Send", id="send", variant="success")
		yield Static("", id="status")

	async def on_mount(self) -> None:
		form = self.query_one("#form-grid", Grid)

		await form.mount_all([
			Label("From:"), Input(value=self.alias or "", id="from"),
			Label("To:"), Input(value=self.recipient or "", id="to"),
			Label("Message-ID:"), Input(value=self.message_id or "", id="msg_id"),
			Label("Subject:"), Input("", id="subject"),
			Label("Message Body:", id="body_label"),
			TextArea(id="body", text="")
		])

	def on_button_pressed(self, event: Button.Pressed) -> None:
			if event.button.id == "send":
				from_alias = self.query_one("#from", Input).value.strip()
				to_email = self.query_one("#to", Input).value.strip()
				msg_id = self.query_one("#msg_id", Input).value.strip()
				subject = self.query_one("#subject", Input).value.strip()
				body = self.query_one("#body", TextArea).text.strip()
				status = self.query_one("#status", Static)

				if not (from_alias and to_email and body):
					status.update("❌ Missing required fields.")
					return

				try:
					send_email(from_alias, to_email, subject, body, msg_id)
					status.update("✅ Email sent successfully!")
				except Exception as e:
					status.update(f"❌ Failed to send email: {e}")

