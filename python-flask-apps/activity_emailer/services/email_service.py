"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-30-2026
Last Updated: 4-2-2026
Purpose: Handles the construction and sending of test, live, and settings verification emails.
"""

import smtplib
from email.message import EmailMessage
from datetime import datetime
from services.settings_service import get_or_create_settings


def build_test_mode_message(notification):
    settings = get_or_create_settings()

    original_to = notification.to_email
    original_cc = notification.cc_emails_list

    subject = f"[TEST MODE] {notification.subject}"

    body = (
        "This is a test-mode email from Activity Eligibility Emailer.\n\n"
        f"Original To: {original_to}\n"
        f"Original CC: {', '.join(original_cc) if original_cc else 'None'}\n\n"
        "Original Message:\n"
        "------------------------------\n"
        f"{notification.body}\n"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.mail_from
    msg["To"] = settings.test_email_recipient
    msg.set_content(body)

    return msg


def build_live_message(notification):
    settings = get_or_create_settings()

    msg = EmailMessage()
    msg["Subject"] = notification.subject
    msg["From"] = settings.mail_from
    msg["To"] = notification.to_email

    cc_list = notification.cc_emails_list
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)

    msg.set_content(notification.body)
    return msg


def send_email_message(message):
    settings = get_or_create_settings()

    with smtplib.SMTP(settings.mail_server, settings.mail_port) as smtp:
        if settings.mail_use_tls:
            smtp.starttls()
        if settings.mail_username and settings.mail_password:
            smtp.login(settings.mail_username, settings.mail_password)
        smtp.send_message(message)

def build_settings_test_message():
    settings = get_or_create_settings()

    msg = EmailMessage()
    msg["Subject"] = "Activity Emailer SMTP Test"
    msg["From"] = settings.mail_from
    msg["To"] = settings.test_email_recipient
    msg.set_content(
        "This is a test email from Activity Eligibility Emailer.\n\n"
        f"Sent at: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n\n"
        "Your saved email delivery settings were able to authenticate and send successfully."
    )
    return msg