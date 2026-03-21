"""
Email Notification Utility
==========================
Sends email notifications via SMTP for automation job status alerts.
Supports plain text messages with optional file attachments.

Configuration:
    Set SMTP_HOST and SMTP_PORT environment variables, or pass them directly.

Usage:
    from email_notification import send_email

    send_email(
        sender='noreply@example.com',
        recipients=['team@example.com'],
        subject='Job Completed',
        body='The automation finished successfully.',
        smtp_host='mail.example.com',
        smtp_port=25
    )

    # With attachment
    send_email(
        sender='noreply@example.com',
        recipients=['team@example.com'],
        subject='Report Ready',
        body='See attached.',
        smtp_host='mail.example.com',
        smtp_port=25,
        attachment_name='report.csv',
        attachment_path='./output/report.csv'
    )
"""

import os
import sys
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


def send_email(sender, recipients, subject, body,
               smtp_host=None, smtp_port=None,
               attachment_name=None, attachment_path=None):
    """
    Send an email notification via SMTP.

    Parameters
    ----------
    sender : str
        Sender email address (can be an alias, e.g. 'noreply@example.com').
    recipients : list[str]
        List of recipient email addresses.
    subject : str
        Email subject line.
    body : str
        Email body text.
    smtp_host : str, optional
        SMTP server hostname. Falls back to SMTP_HOST env var.
    smtp_port : int, optional
        SMTP server port. Falls back to SMTP_PORT env var (default 25).
    attachment_name : str, optional
        Filename for the attachment as it appears in the email.
    attachment_path : str, optional
        Local file path to the attachment. Required if attachment_name is set.

    Returns
    -------
    dict
        Empty dict on success (from smtplib.sendmail).
    """
    host = smtp_host or os.environ.get('SMTP_HOST', 'localhost')
    port = int(smtp_port or os.environ.get('SMTP_PORT', 25))

    server = smtplib.SMTP(host, port=port)
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    msg.attach(MIMEText(body))

    if attachment_name and attachment_path:
        if not os.path.exists(attachment_path):
            raise FileNotFoundError(f"Attachment not found: {attachment_path}")
        part = MIMEBase('application', 'octet-stream')
        with open(attachment_path, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=attachment_name)
        msg.attach(part)

    result = server.sendmail(sender, recipients, msg.as_string())
    server.quit()
    return result
