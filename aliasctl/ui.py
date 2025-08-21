from aliasctl.mail import send_email
from aliasctl.theme import default_theme
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Grid, VerticalGroup
from textual_fspicker import FileOpen
from textual.widgets import Input, Button, Label, TextArea, Static


class EmailApp(App):
	CSS_PATH = "ui.css"

	def __init__(self, alias=None, recipient=None, message_id=None):
		super().__init__()
		self.alias = alias
		self.recipient = recipient
		self.message_id = message_id
		self.attachments: list[str] = []


	def compose(self) -> ComposeResult:
		yield Label("Compose Mail", id="title")
		yield Grid(id="form_grid")

		yield VerticalGroup(
			Label("Message Body:", id="body_label"),
			TextArea(id="body", text=""),
			id="body_group"
		)

		yield Container(
			Button("Add Files", id="attach_pick"),
			Button("Clear", variant="warning", id="attach_clear"),
			Button("Send", variant="success", id="send"),
			Static("No attachments", id="attach_list"),
			Static("", id="status"),
			id="bottom_group"
		)


	async def on_mount(self) -> None:
		self.register_theme(default_theme)
		self.theme = "default_theme"

		form = self.query_one("#form_grid", Grid)
		await form.mount_all([
			Label("From:"), Input(value=self.alias or "", id="from"),
			Label("To:"), Input(value=self.recipient or "", id="to"),
			Label("Message-ID:"), Input(value=self.message_id or "", id="msg_id"),
			Label("Subject:"), Input("", id="subject"),
		])


	def update_attachment_list_display(self) -> None:
		attach_list = self.query_one("#attach_list", Static)

		if self.attachments:
			attach_list.update("\n".join(f"• {p}" for p in self.attachments))
		else:
			attach_list.update("No attachments")


	def on_button_pressed(self, event: Button.Pressed) -> None:
		status = self.query_one("#status", Static)

		if event.button.id == "attach_pick":
			# Must run the file dialog in a worker when waiting for dismiss
			self.run_worker(self._pick_files_worker(), exclusive=True, name="pick_files")
			return

		if event.button.id == "attach_clear":
			self.attachments.clear()
			self.update_attachment_list_display()
			return

		if event.button.id == "send":
			from_alias = self.query_one("#from", Input).value.strip()
			to_email = self.query_one("#to", Input).value.strip()
			msg_id = self.query_one("#msg_id", Input).value.strip()
			subject = self.query_one("#subject", Input).value.strip()
			body = self.query_one("#body", TextArea).text.strip()

			if not (from_alias and to_email and body):
				status.update("❌ Missing required fields.")
				return

			try:
				send_email(
					from_alias,
					to_email,
					subject,
					body,
					msg_id,
					attachments=self.attachments,
				)
				status.update("✅ Email sent successfully!")
			except Exception as e:
				status.update(f"❌ Failed to send email: {e}")


	async def _pick_files_worker(self):
		picked = await self.push_screen_wait(FileOpen(title="Select file"))
		paths = []

		if picked:
			if isinstance(picked, (list, tuple, set)):
				paths = [Path(p) for p in picked]
			else:
				paths = [Path(picked)]

		added = 0
		for p in paths:
			try:
				if p.is_file():
					self.attachments.append(str(p))
					added += 1
			except Exception:
				pass

		self.update_attachment_list_display()