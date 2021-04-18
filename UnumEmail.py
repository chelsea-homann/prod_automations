# coding: utf-8

import sys
import smtplib
import email
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


def send_email(sender, recipients, subject, body,
               file_attached = False, attachment = None, attach_path = None):
    """
    
    Parameters:
    -------------------------------------
    
    sender: (str) Can be from any alias Ex: do_not_reply@estevan.com
    recipients: (list) List of email addresses you would like email sent to. Can be single address
    subject: (str) Subject line of email
    body: (str) Body of email with any message
    file_attached: (bool) Indicator if you will be needing to send an email attachement 
    attachement: (str) file name with extension
    attach_path: (str) String of file path with file name and extension. Ex: ./attachement.csv
    
    -----------------------
    returns: empty dict if successful
    """
    server = smtplib.SMTP('mail.unum.com', port = 25)
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    body = MIMEText(body)
    msg.attach(body)
    
    if file_attached == True:
        part = MIMEBase('application', "octet-stream")
        if len(attach_path) == 0:
            raise RuntimeError("\nNeed file path of attachement. Ex: './attachement.csv'")
            sys.exit()
        part.set_payload(open(attach_path, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename = attachment)
        msg.attach(part)
    
    return server.sendmail(sender, recipients, msg.as_string())

