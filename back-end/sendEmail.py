import ssl,smtplib
from dotenv import load_dotenv
import os

# !!! NOTICE !!!
# Cannot send symbol ':' 
def sendEmail(text,receive_email):
    load_dotenv()

    port = 465
    sender_email = os.getenv('SENDER_EMAIL')
    password = os.getenv('SENDER_PASSWORD')
    message = '/Subject:\n{}'.format(text)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com',port,context=context) as server:
        server.login(sender_email,password)
        server.sendmail(sender_email,receive_email,message)
        server.close()
        