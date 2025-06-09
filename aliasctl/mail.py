from email.message import EmailMessage
import markdown
import subprocess


def send_email(from_alias, to_email, subject, body_markdown, message_id=None):
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
	msg.add_alternative(body_html, subtype='html')

	p = subprocess.Popen(
		["msmtp", "--from", from_alias, "--", to_email],
		stdin=subprocess.PIPE
	)

	p.communicate(msg.as_bytes())