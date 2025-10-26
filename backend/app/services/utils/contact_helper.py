import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, body):
    try:
        from_email = os.getenv("FROM_EMAIL")
        email_password = os.getenv("EMAIL_PASSWORD")
        
        print(f"📧 Sending email: {from_email} → {to_email}")
        print(f"🔑 Password length: {len(email_password) if email_password else 'MISSING'}")
        print(f"🔑 Password preview: {email_password[:4]}..." if email_password else "MISSING")
        print(f"📝 Subject: {subject}")
        
        if not from_email or not email_password:
            raise ValueError("Email credentials not found in environment variables")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Create server and send
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, email_password)
        
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        
        print("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

# Specialized function for contact forms
def send_contact_notification(user_name, subject, message):
    """
    Send contact form submission using FROM_EMAIL as default sender
    """
    to_email = os.getenv("TO_EMAIL")
    
    email_body = f"""
    New Contact Form Submission:
    
    Name: {user_name}
    Contact: No email provided
    Subject: {subject}
    
    Message:
    {message}
    
    ---
    Sent from your website contact form.
    User did not provide contact email.
    """
    
    return send_email(
        to_email=to_email,
        subject=f"Contact Form: {subject}",
        body=email_body
        # No reply_to parameter since we don't have user email
    )