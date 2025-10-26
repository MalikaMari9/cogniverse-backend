# test_gmail.py
import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

def test_gmail():
    try:
        email = os.getenv("FROM_EMAIL")
        password = os.getenv("EMAIL_PASSWORD")
        
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Password length: {len(password)}")
        print(f"Password contains #: {'#' in password}")
        
        # Test SMTP connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        print("✅ SUCCESS: Gmail login worked!")
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    test_gmail()