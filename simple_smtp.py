import smtpd
import asyncore

server = smtpd.DebuggingServer(("127.0.0.1", 9267), None)

asyncore.loop()
