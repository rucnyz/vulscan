import smtplib
import ssl
from email.message import EmailMessage
# Implement a Python function that securely sends an email by connecting to an SMTP server over a TLS-encrypted channel. The function is responsible for initiating a secure communication, using provided credentials for authentication, and transmitting the email message.

def send_secure_email(mail_server, server_port, from_address, to_address, user_password, email_content):
    server = smtplib.SMTP(mail_server, server_port)
    server.starttls()
    try:
        server.login(from_address, user_password)
        
        email = EmailMessage()
        email['Subject'] = 'Test Email'
        email['From'] = from_address
        email['To'] = to_address
        email.set_content(email_content)
        
        server.send_message(email)
        print("Email sent successfully")
    except smtplib.SMTPAuthenticationError as e:
        raise smtplib.SMTPAuthenticationError(f"Authentication failed: {e}")
    except ssl.SSLError as e:
        raise ssl.SSLError(f"SSL error: {e}")
    except smtplib.SMTPException as e:
        raise smtplib.SMTPException(f"SMTP error occurred: {e}")
    finally:
        server.quit()