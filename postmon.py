import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os
import settings
import re


def emailChecker(email):
    return True if re.match("[^@]+@[^@]+\.[^@]+", email) else False


def send(to, subject, text):
    if not emailChecker(to):
        return 
    msg = MIMEMultipart()
    msg['From'] = settings.MainConfig.MAIL_USER
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(settings.MainConfig.MAIL_USER,
                     settings.MainConfig.MAIL_PWD)
    mailServer.sendmail(settings.MainConfig.MAIL_USER, to, msg.as_string())
    mailServer.close()
