from __future__ import absolute_import
import smtplib
from email.mime.text import MIMEText
import libethvault.config as config
from threading import Lock, Condition
from multiprocessing.dummy import Pool
import time


_mailpool = Pool(1)
_last_email_sent = 0.0


def wait_mail_delay(delay):
    global _last_email_sent
    while time.time() - _last_email_sent < delay:
        time.sleep(delay)

    _last_email_sent = time.time()


def send_to(em, msgs, subj):
    wait_mail_delay(config.CONFIG["mail_delay"])

    msg = MIMEText(msgs)

    msg["Subject"] = subj
    msg["From"] = config.CONFIG["email"]
    msg["To"] = em

    if config.CONFIG["cert"] == "":
        try:
            serv = smtplib.SMTP('127.0.0.1', port=9267)
            serv.sendmail(config.CONFIG["email"], [em], msg.as_string())
            serv.quit()
            print "Sent email to {}".format(em)
        except Exception as e:
            print "Error sending email to {}".format(em)
            print e
        # print msgs
        # print "Fake sent mail."
        return
    else:
        serv = smtplib.SMTP_SSL(keyfile=config.CONFIG["key"], certfile=config.CONFIG["cert"])

        serv.sendmail(config.CONFIG["email"], [em], msg.as_string())
        serv.quit()


def send_alert_to(em, addr, amount, dest):
    s = """You are receiving this email because a withdrawl for {1} to address {2} is pending on
the Ethereum Vault related to address {0}. If you did not initiate this withdrawal,
immediately call abort() on your vault to avoid losing funds.""".format(addr, amount, dest)

    send_to(em, s, "Pending withdrawl alert for {}".format(addr))


def send_to_async(em, msgs, subj):
    return _mailpool.apply_async(send_to, args=(em, msgs, subj))


def send_alert_to_async(em, addr, amount, dest):
    return _mailpool.apply_async(send_to, args=(em, addr, amount, dest))
