from email.message import EmailMessage
from pathlib import Path
import markdown
import mimetypes
import subprocess


def send_email(from_alias, to_email, subject, body_markdown, message_id=None, attachments=None):
	body_html = markdown.markdown(body_markdown)
	msg = EmailMessage()
	msg["From"] = from_alias
	msg["To"] = to_email
	msg["Subject"] = subject

	if message_id:
		message_id = f"<{message_id}>" if not message_id.startswith("<") else message_id
		msg["In-Reply-To"] = message_id
		msg["References"] = message_id

	msg.set_content(body_markdown)
	msg.add_alternative(body_html, subtype="html")

	for path in attachments or []:
		p = Path(path)
		with p.open("rb") as f:
			data = f.read()
		mtype, _ = mimetypes.guess_type(p.name)
		if mtype:
			maintype, subtype = mtype.split("/", 1)
		else:
			maintype, subtype = "application", "octet-stream"
		msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=p.name)

	p = subprocess.Popen(
		["msmtp", "--from", from_alias, "--", to_email],
		stdin=subprocess.PIPE
	)

	p.communicate(msg.as_bytes())