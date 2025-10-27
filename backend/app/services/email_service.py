import smtplib, ssl, os
from email.mime.text import MIMEText
from app.services.utils.config_helper import get_config_value, get_int_config, get_bool_config
from app.services.logging_service import system_logger

def send_email_html(db, to_email: str, subject: str, html_body: str):
    """Reusable HTML email sender that uses config_tbl or .env values."""
    smtp_host = get_config_value(db, "smtpHost", "smtp.gmail.com")
    smtp_port = get_int_config(db, "smtpPort", 465)
    from_email = get_config_value(db, "fromEmail", os.getenv("FROM_EMAIL"))
    email_password = get_config_value(db, "emailPassword", os.getenv("EMAIL_PASSWORD"))

    use_test_override = get_bool_config(db, "useTestEmailOverride", False)
    to_email_override = get_config_value(db, "toEmail", None) if use_test_override else None
    actual_recipient = to_email_override or to_email

    msg = MIMEText(html_body, "html")
    msg["Subject"] = subject
    msg["From"] = f"CogniVerse <{from_email}>"
    msg["To"] = actual_recipient

    try:
        context = ssl.create_default_context()
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                server.login(from_email, email_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls(context=context)
                server.login(from_email, email_password)
                server.send_message(msg)
        print(f"📤 Email sent successfully to {actual_recipient}")
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        system_logger.log_action_sync(
            db=db,
            action_type="EMAIL_SEND_ERROR",
            user_id=None,
            details=f"{subject} → {str(e)}",
            status="failed",
        )
