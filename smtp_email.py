import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys


def sendemail():
    fromaddr = "{}".format(format(sys.argv[1]))
    toaddr = "{}".format(format(sys.argv[3]))
    toaddrs = [toaddr]

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Pandora Honeypot Network Intrusion Logs"
    body = '''Dear Sir/Madam,
    These logs include all the information regarding the intrusions in your home network.
    Regards,
    Pandora
    '''
    msg.attach(MIMEText(body, 'plain'))

    filename = "/var/log/psad/honeypotslogger"
    f = open(filename)
    attachment = MIMEText(f.read())
    attachment.add_header('Content-Disposition',
                          'attachment', filename="Logs")
    msg.attach(attachment)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login("{}".format(sys.argv[1]), "{}".format(sys.argv[2]))
    text = msg.as_string()
    server.sendmail(fromaddr, toaddrs, text)
    server.quit()


sendemail()
