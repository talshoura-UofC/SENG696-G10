#%%
# Importing the required libraries
import os
import pickle
import time
import json
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, timedelta
from pathlib import Path
import os
import pytz
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

# Request all access (permission to read/send/receive emails, 
# manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = 'tariq.al.shoura.development@gmail.com'


class NotificationBehav(CyclicBehaviour):
    # This behaviour is used in the notification use case, it continues
    # running awaiting notification requests, then it composses and sends
    # an email to the user with the appointment details and a calendar 
    # meeting invitation
    #    
    # Args:
    #     CyclicBehaviour (CyclicBehaviour): Spade's CyclicBehaviour


    def generate_calendar_event(self, data):
        # This funciton creates a calendar invite file containing the
        #     appointment details and saves it on the system
        #
        # Args:
        #     data (dict): a dictionary containing the appointment details
        #
        # Returns:
        #     str: the name of the calendar file on the device
        
        # Initializing a calendar object
        cal = Calendar()

        # Some properties are required to be compliant with format
        cal.add('prodid', '-//MINDCOLOGY//NOTIFICATION_AGENT//')
        cal.add('version', '2.0')

        # Adding subcomponents and event details
        event = Event()
        event.add('name', 'Notification Email')
        event.add('description', 'Dear Sir/Madam,\n\nPlease find the meeting details in this invite.\n\nMindcology Team')
        date=datetime.strptime(data["APPOINTMENT_DATE"], "%Y-%m-%d") 
        time=datetime.strptime(data["APPOINTMENT_TIME"], "%H:%M:%S").time()
        event.add('dtstart', datetime.combine(date, time))
        event.add('dtend', datetime.combine(date, time)+timedelta(minutes=29))
        event.add('summary', "Appointment Details")
        
        # Adding a dummy organizer
        organizer = vCalAddress('MAILTO:DO-NO-REPLY@MINDCOLOGY.com')
        
        # Adding some parameters of the event
        organizer.params['name'] = vText('MINDCOLOGY')
        organizer.params['role'] = vText('System Email')
        event['organizer'] = organizer
        event['location'] = vText('Calgary, ca')
        
        event['uid'] = "aibvad234289vnfskjnr49"
        event.add('priority', 5)
        
        # Add the event to the calendar object
        cal.add_component(event)
        
        # Write to disk
        directory = os.getcwd()
        f = open(os.path.join(directory, 'appointment.ics'), 'wb')
        f.write(cal.to_ical())
        f.close()
        print("Directory is:", os.path.join(directory, 'appointment.ics'))
        return 'appointment.ics'


    def gmail_authenticate(self):
        creds = None
        # The file token.pickle stores the user's access and refresh 
        # tokens, and is created automatically when the authorization
        # flow completes for the first time
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials availablle, 
        # let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
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

    # Build the required message components
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

    # Sends the email
    def send_message(self, destination, obj, body, attachments=[]):
        # get the Gmail API service
        self.service = self.gmail_authenticate()
        return self.service.users().messages().send(
        userId="me",
        body=self.build_message(destination, obj, body, attachments)
        ).execute()

    # Returns a template message filled with the appointment information
    def message_payload(self, data):
        html = """\
        <html>
        <head></head>
        <body>
            <p style="font-family:Times;">Dear Sir/Madam,<br>
            This is a confirmation email for you appointment with Dr.{firstName} {lastName}<br>
            The appointment has been scheduled on: {date} at: {time}<br><br>
            <b>Regards,</b><br>
            Mindcology Team
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
        # This is a method required part of spade's CyclicBehaviour
        # class and defines the main functionality of the behaviour
        #
        # The behaviour refreshs every 10 secs waiting for a request
        # If a request comes through it is processed and a reply is sent
        # If no request comes through the cycle repeats waiting

        print("\n\n\n====================================")
        print("Notification Behav running")
        # wait for a message for 10 seconds
        msg = await self.receive(timeout=10)  
        if msg:
            # if a message comes print a log of the details
            print("\n________________________\n", msg, "\n________________________")
            print(F"Message received with content: {msg.body}")
            print(msg.metadata)
            print("Ontology is: ", msg.metadata["ontology"])
            request = json.loads(msg.body)

            receiver_email = request["USER_EMAIL"]
            subject = 'Appointment Confirmation - Mindcology'
            payload = self.message_payload(request)
            cal = self.generate_calendar_event(request)
            out = self.send_message(receiver_email, subject, payload, [cal])
            print("Successfully Completed Behaviour\n\nemail details are:", out)
                

        else:
            print("Did not received any message after 10 seconds")
    
    async def on_end(self):
        # This is a method required part of spade's CyclicBehaviour
        # which defines the actions to be taken on the end of the behaviour
        await self.agent.stop()
    
class NotificationAgentComponent(Agent):
    # This is a empty class that extends the SPADE Agent class
    # There are no behaviours loaded into the class in the declaration
    # however, the required behaviour will be loaded at runtime
    
    async def setup(self):
        print("Starting Notification Agent")


class Notification_Agent():
    # This is our notification agent class which will create an instance
    # of the NotificationAgentComponent and load the behaviour into it.
    # The class contains the following members:
    # 1- behav <SPADE.Behaviour> where the behaviour will be 
    #       loaded at run-time
    # 2- notificationagent <NotificationAgentComponent> which will contain
    #       an instance of the class extending the agent to be able to load the
    #       behaviour into it and run it
    # 3- future <SPADE.Future> which will be used to get the outputs from
    #       the bahviours at the end of the run
    #
    # 4- loadBehaviour() which creates an instance of the behaviour
    # 5- beginCommunications() this function obtains the required 
    #       credintials of the agent and loads them in addition to the 
    #       behaviour, then it starts the agent and waits until a user
    #       interrupt killing the agent

    def loadBehaviour(self):
        # A method that creates an instance of the required behaviour
        self.behav = NotificationBehav()
    
    def beginCommunications(self):
        # This method obtains the required credintials of the agent 
        # and loads them in addition to the behaviour, then it starts
        # the agent and waits until it is interrupted 
        # terminating the agent and the application
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
    # This is main, creates an instance of our agent class and
    # calls the appropriate functions to start it.
    
    notif = Notification_Agent()
    notif.loadBehaviour()
    notif.beginCommunications()