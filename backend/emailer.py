import os

EMAIL_FROM = os.getenv("EMAIL_FROM", "Advisor <noreply@example.com>")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_confirmation_email(to_email: str, to_name: str) -> bool:
    subject = "Thanks for your interest!"
    body = (
        f"Hi {to_name},\n\n"
        "We’ve received your request for a retirement/life plan. "
        "Our advisor will contact you soon.\n\n"
        "— Team"
    )

    if not SMTP_HOST or not SMTP_USERNAME or not SMTP_PASSWORD:
        print("[EMAIL → console]\nFrom:", EMAIL_FROM, "\nTo:", to_email, "\nSubj:", subject, "\n\n", body)
        return True

    try:
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("[EMAIL ERROR]", e)
        return False
