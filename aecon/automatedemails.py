import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import os
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64
from django.conf import settings

API_key = settings.API_KEY
def sendMail_remote(address,title,text):
    payload = {"address":address,"title":title,"text":text,"username":"sendmail","password":"awibble"}
    r = requests.post("http://www.tracsisscotland.com/crt/notify/",data=payload)
    print(r.text)


# def sendMail(to, subject, text, server="localhost",sender=None):
#     #assert type(to) == list
#     #assert type(files) == lis
#     print("trying to send mail",text)
#     if sender is None:
#         sender = "neil@tracsis-tads.com"
#     msg = MIMEMultipart()
#     msg['From'] = sender
#     msg['To'] = to
#     msg['Subject'] = subject

#     msg.attach(MIMEText(text,"html"))


    
#     smtp = smtplib.SMTP(server,1025)
#     print("sending mails error solved")
#     server.login(sender, "loveyousona")
#     smtp.sendmail(sender, to, msg.as_string())
#     smtp.close()

def sendMail(to, subject, text,**kwargs):
    sg = sendgrid.SendGridAPIClient(api_key=API_key)
    from_email =Email("automated_email@tracsis-tads.com ")
    content = Content("text/html",text)
    # to  = "rohel@divyaltech.com"
    
    if type(to) == list:
        for item in to:
            mail = Mail(from_email, To(item), subject, content)
            # Get a JSON-ready representation of the Mail object
            mail_json = mail.get()

            # Send an HTTP POST request to /mail/send
            response = sg.client.mail.send.post(request_body=mail_json)
            print(response.status_code)
            print(response.headers)
    else:

        mail = Mail(from_email, To(to), subject, content)
        # Change to your recipient# Get a JSON-ready representation of the Mail object
        mail_json = mail.get()

        # Send an HTTP POST request to /mail/send
        response = sg.client.mail.send.post(request_body=mail_json)
        print(response.status_code)
        print(response.headers)
    
    
    # from_email = email("automated_email@tracsis-tads.com ")  # Change to your verified sender


def sendMail_withAttachments(to, subject, text, attachment, **kwargs):
    sg = sendgrid.SendGridAPIClient(api_key=API_key)
    from_email = Email("automated_email@tracsis-tads.com ")
    content = Content("text/html", text)
    # to  = "rohel@divyaltech.com"

    if type(to) == list:
        for item in to:
            mail = Mail(from_email, To(item), subject, content)
            # Get a JSON-ready representation of the Mail object
            mail_json = mail.get()

            # Send an HTTP POST request to /mail/send
            response = sg.client.mail.send.post(request_body=mail_json)
            print(response.status_code)
            print(response.headers)
    else:

        mail = Mail(from_email, To(to), subject, content)
        encoded_file = base64.b64encode(attachment).decode()

        attachedFile = Attachment(
            FileContent(encoded_file),
            FileName('tracsis_data.zip'),
            FileType('application/x-zip-compressed'),
            Disposition('attachment')
        )
        mail.attachment = attachedFile
        # Change to your recipient# Get a JSON-ready representation of the Mail object
        mail_json = mail.get()

        # Send an HTTP POST request to /mail/send
        response = sg.client.mail.send.post(request_body=mail_json)
        print(response.status_code)
        print(response.headers)
    

   


# if __name__ == "__main__":
#     sendMail("neeeel@hotmail.com","test","test email from  server", sender="automated_email@tracsis-tads.com")
