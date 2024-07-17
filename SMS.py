import smtplib
import os

carriers = {
    'att': '@mms.att.net',
    'tmobile': ' @tmomail.net',
    'verizon': '@vtext.com',
    'sprint': '@page.nextel.com'
}


def send(number, carrier, subject, message):
    # Replace the number with your own, or consider using an argument\dict for multiple people.
    to_number = f"{number}{carriers[carrier]}"
    auth = (os.environ.get('ARemail'), os.environ.get('ARpass'))

    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    # Send text message through SMS gateway of destination number
    recipients = [to_number, os.environ.get('email')]
    server.sendmail(auth[0], recipients, f"Subject: {subject}\n\n{message}")
    server.quit()