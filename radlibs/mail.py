from __future__ import unicode_literals

import os
import smtplib
from flask import render_template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Message(object):
    from_address = None
    to_addresses = None
    plaintext = None
    html = None
    _message = None

    def __init__(self,
                 subject,
                 to_addresses,
                 plaintext,
                 from_address='support@radlibs.info',
                 html=None):
        self.subject = subject
        self.from_address = from_address
        self.to_addresses = to_addresses
        self.plaintext = plaintext
        self.html = html

    def send(self):
        message = MIMEMultipart('alternative')
        message['Subject'] = self.subject
        message['From'] = self.from_address
        message['To'] = ', '.join(self.to_addresses)

        message.attach(MIMEText(self.plaintext, 'plain'))
        if self.html is not None:
            message.attach(MIMEText(self.html, 'html'))

        if 'SENDGRID_PASSWORD' in os.environ:
            smtp = smtplib.SMTP('smtp.sendgrid.net', 587)
            smtp.login(os.environ['SENDGRID_USERNAME'],
                       os.environ['SENDGRID_PASSWORD'])
            smtp.sendmail(
                self.from_address, self.to_addresses, message.as_string())


def send_verification_mail(user, verification_url):
    plaintext = """
Hello,

A person claiming to be you has signed up on http://radlibs.info. Was their claim true? Was it, indeed, you? Oh, please say it was.

Please copy and paste the link below into your favorite web browser so we can be sure it wasn't some rascal posing as you on a lark:

{0}

Thanks,
The Radlibs support team
""".format(verification_url)

    html = render_template('verification_mail.html.jinja',
                           verification_url=verification_url)

    message = Message('Please verify your email for Radlibs',
                      [user.email],
                      plaintext,
                      html=html)
    message.send()
