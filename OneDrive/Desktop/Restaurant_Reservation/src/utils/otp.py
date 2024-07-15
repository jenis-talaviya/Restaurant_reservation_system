import random
import smtplib
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime,timedelta
from src.schemas.userschemas import OtpRequest
from src.models.user_verify import OTPDetail


def generate_otp(length=6):
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))

def send_otp_via_email(sender_email, receiver_email, password, otp):
    subject = "Your OTP Code"
    message_text = f"Your OTP is {otp} which is valid for 10 minutes"

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Attach the message text
    message.attach(MIMEText(message_text, "plain"))

    # Send the email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        return True, "Mail sent successfully"
    except Exception as e:
        return False, f"Failed to send email: {e}"
    
    
    
#------------------------confirm reservation--------------------------------
def send_email(sender_email, receiver_email, password, subject, body):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Failed to send email: {e}"