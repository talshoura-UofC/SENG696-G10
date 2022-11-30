#%%
import os
import pickle
import time
import json
import mysql.connector
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
import Directory_Facilitators as DS
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = 'tariq.al.shoura.development@gmail.com'



class NotificationBehav(CyclicBehaviour):
    """
        defining behavoiur

    Args:
        CyclicBehaviour -> type cyclic
    """
    def gmail_authenticate(self):
        creds = None
        # the file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        # if there are no (valid) credentials availablle, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
        return build('gmail', 'v1', credentials=creds)

    # Adds the attachment with the given filename to the given message
    def add_attachment(self, message, filename):
        content_type, encoding = guess_mime_type(filename)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(filename, 'rb')
            msg = MIMEText(fp.read().decode(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(filename, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(filename, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(filename, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()
        filename = os.path.basename(filename)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

    def build_message(self, destination, obj, body, attachments=[]):
        if not attachments: # no attachments given
            message = MIMEText(body, 'html')
            message['to'] = destination
            message['from'] = our_email
            message['subject'] = obj
        else:
            message = MIMEMultipart()
            message['to'] = destination
            message['from'] = our_email
            message['subject'] = obj
            message.attach(MIMEText(body, 'html'))
            for filename in attachments:
                self.add_attachment(message, filename)
        return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    def send_message(self, destination, obj, body, attachments=[]):
        # get the Gmail API service
        self.service = self.gmail_authenticate()
        return self.service.users().messages().send(
        userId="me",
        body=self.build_message(destination, obj, body, attachments)
        ).execute()

    def message_payload(self, data):
        """
            body structure of confirmation email 
        """
        html = """\
        <html>
        <head></head>
        <body>
            <p style="font-family:Times;">Dear Sir/Madam,<br>
            This is a confirmation email for you appointment with Dr.{firstName} {lastName}<br>
            The appointment has been scheduled on: {date} at: {time}<br><br>
            <b>Regards,</b><br>
            System
        </body>
        </html>
        """.format(
                firstName=data["DOCTOR_FIRST_NAME"], 
                lastName=data["DOCTOR_LAST_NAME"], 
                date=data["APPOINTMENT_DATE"], 
                time=data["APPOINTMENT_TIME"]
            )
        return html

    async def run(self):

        """ 
            In this function the agent waits for a specified amount of time and listen for messages 
            then based on result of send_message method which was explained earier return success or failure flag

        """
        print("\n\n\n====================================")
        print("Notification Behav running")
        msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
        if msg:
            print("\n________________________\n", msg, "\n________________________")
            print(F"Message received with content: {msg.body}")
            print(msg.metadata)
            print("Ontology is: ", msg.metadata["ontology"])
            request = json.loads(msg.body)

            receiver_email = request["USER_EMAIL"] #"Tariq.AlShoura@ucalgary.ca" #
            subject = 'Testing Googles APIs - Completed'
            payload = self.message_payload(request)
            out = self.send_message(receiver_email, subject, payload)
            print("Successfully Completed Behaviour\n\nemail details are:", out)
                

        else:
            print("Did not received any message after 10 seconds")
            # self.kill()
    
    async def on_end(self):
        await self.agent.stop()
    
class NotificationAgentComponent(Agent):
    async def setup(self):
        print("Starting Notification Agent")


class Notification_Agent():
    """
        The actual class for notification agent which has the already explained behaviour for its only one behaviour
    """

    def loadBehaviour(self):
        self.behav = NotificationBehav()
    
    def beginCommunications(self):
        self.notificationagent = NotificationAgentComponent(DS.Notification["username"], DS.Notification["password"])
        self.notificationagent.add_behaviour(self.behav)
        self.future = self.notificationagent.start()
        self.future.result()
        self.behav.join()

        print("Wait until user interrupts with ctrl+C\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
        self.notificationagent.stop()


# %%
if __name__ == "__main__":
    notif = Notification_Agent()
    notif.loadBehaviour()
    notif.beginCommunications()

# html = """\
# <html>
#   <head></head>
#   <body>
#     <p style="font-family:Times;"><b>Hi!</b><br>
#        How are you?<br>
#        Here is a <a href="https://github.com/talshoura-UofC/SENG-696-Devs">link</a> to our github.<br><br>
#     <b>Regards,</b><br>
#     Your System
#   </body>
# </html>
# """
# receiver_email = ["Tariq.AlShoura@ucalgary.ca"]
# subject = 'Testing Googles APIs - Completed'
# nt = NotificationBehaviour()
# # nt.gmail_authenticate()
# nt.send_message(", ".join(receiver_email), subject, html)
# # %%





# # def gmail_authenticate():
# #     creds = None
# #     # the file token.pickle stores the user's access and refresh tokens, and is
# #     # created automatically when the authorization flow completes for the first time
# #     if os.path.exists("token.pickle"):
# #         with open("token.pickle", "rb") as token:
# #             creds = pickle.load(token)
# #     # if there are no (valid) credentials availablle, let the user log in.
# #     if not creds or not creds.valid:
# #         if creds and creds.expired and creds.refresh_token:
# #             creds.refresh(Request())
# #         else:
# #             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
# #             creds = flow.run_local_server(port=0)
# #         # save the credentials for the next run
# #         with open("token.pickle", "wb") as token:
# #             pickle.dump(creds, token)
# #     return build('gmail', 'v1', credentials=creds)

# # # get the Gmail API service
# # service = gmail_authenticate()


# # # %%
# # # Adds the attachment with the given filename to the given message
# # def add_attachment(message, filename):
# #     content_type, encoding = guess_mime_type(filename)
# #     if content_type is None or encoding is not None:
# #         content_type = 'application/octet-stream'
# #     main_type, sub_type = content_type.split('/', 1)
# #     if main_type == 'text':
# #         fp = open(filename, 'rb')
# #         msg = MIMEText(fp.read().decode(), _subtype=sub_type)
# #         fp.close()
# #     elif main_type == 'image':
# #         fp = open(filename, 'rb')
# #         msg = MIMEImage(fp.read(), _subtype=sub_type)
# #         fp.close()
# #     elif main_type == 'audio':
# #         fp = open(filename, 'rb')
# #         msg = MIMEAudio(fp.read(), _subtype=sub_type)
# #         fp.close()
# #     else:
# #         fp = open(filename, 'rb')
# #         msg = MIMEBase(main_type, sub_type)
# #         msg.set_payload(fp.read())
# #         fp.close()
# #     filename = os.path.basename(filename)
# #     msg.add_header('Content-Disposition', 'attachment', filename=filename)
# #     message.attach(msg)

# # def build_message(destination, obj, body, attachments=[]):
# #     if not attachments: # no attachments given
# #         message = MIMEText(body, 'html')
# #         message['to'] = destination
# #         message['from'] = our_email
# #         message['subject'] = obj
# #     else:
# #         message = MIMEMultipart()
# #         message['to'] = destination
# #         message['from'] = our_email
# #         message['subject'] = obj
# #         message.attach(MIMEText(body, 'html'))
# #         for filename in attachments:
# #             add_attachment(message, filename)
# #     return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}


# # def send_message(service, destination, obj, body, attachments=[]):
# #     return service.users().messages().send(
# #     userId="me",
# #     body=build_message(destination, obj, body, attachments)
# #     ).execute()

# # #%%
# # # test send email
# # # send_message(service, "Tariq.AlShoura@ucalgary.ca", "This is a subject", 
# # #             "This is the body of the email")

# # # %%

# # receiver_email = ["Tariq.AlShoura@ucalgary.ca", "ali.mollaahmadidehag@ucalgary.ca", "aadharsh.hariharan@ucalgary.ca"]
# # subject = 'Testing Googles APIs - Completed'
# # body = "\n\nHey, what's up?\n\n- Regards"

# # # send_message(service, ", ".join(receiver_email), subject, body)
# # # %%


# # html = """\
# # <html>
# #   <head></head>
# #   <body>
# #     <p style="font-family:Times;"><b>Hi!</b><br>
# #        How are you?<br>
# #        Here is a <a href="https://github.com/talshoura-UofC/SENG-696-Devs">link</a> to our github.<br><br>
# #     <b>Regards,</b><br>
# #     Your System
# #   </body>
# # </html>
# # """

# # send_message(service, ", ".join(receiver_email), subject, html)
# # # %%
