import subprocess


def send_email(from_email: str, to_email: str, subject: str, body: str, message_id: str):
	if message_id and not message_id.startswith("<"):
		message_id = f"<{message_id}>"

	headers = f"""From: {from_email}
To: {to_email}
In-Reply-To: {message_id}
References: {message_id}
Subject: {subject}

"""
	message = headers + body

	subprocess.run(
		["msmtp", "-v", "--from", from_email, "--", to_email],
		input=message,
		text=True,
		check=True
	)