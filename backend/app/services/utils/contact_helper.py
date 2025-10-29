import os
import smtplib
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from app.services.utils.config_helper import get_config_value
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


load_dotenv()

def send_email(db: Session, to_email: str, subject: str, body: str, reply_to: str | None = None):
    try:
        # 🔹 Try config_tbl first, fallback to env
        from_email = get_config_value(db, "fromEmail", os.getenv("FROM_EMAIL"))
        email_password = get_config_value(db, "emailPassword", os.getenv("EMAIL_PASSWORD"))
        smtp_host = get_config_value(db, "smtpHost", "smtp.gmail.com")
        smtp_port = int(get_config_value(db, "smtpPort", 587))

        print(f"📧 Sending email: {from_email} → {to_email}")
        if reply_to:
            print(f"↩️ Reply-To: {reply_to}")

        if not from_email or not email_password:
            raise ValueError("Email credentials not found in config or environment")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        if reply_to:
            msg['Reply-To'] = reply_to
        msg.attach(MIMEText(body, 'plain'))

        # Connect & send
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(from_email, email_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        print("✅ Email sent successfully!")
        return True

    except Exception as e:
        print(f"❌ Email error: {e}")
        return False
# Specialized function for contact forms
def send_contact_notification(db: Session, user_name: str, subject: str, message: str):
    to_email = get_config_value(db, "toEmail", os.getenv("TO_EMAIL"))

    email_body = f"""
    New Contact Form Submission:

    Name: {user_name}
    
    Subject: {subject}

    Message:
    {message}

    ---
    
    """

    return send_email(
        db=db,
        to_email=to_email,
        subject=f"Contact Form: {subject}",
        body=email_body
    )
