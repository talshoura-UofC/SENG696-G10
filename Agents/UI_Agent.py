# This is the Portal agent, the agent is designed to be called through
# the CLI or similar methods where arguments are passed to select
# the required behaviour and provide the needed data for the action

# The output of the agent is given on the stdout (CLI output), which
# is then fetched by calling party to examin the response

# There are 4 behaviours defined here, where each behaviour is
# responsible for one of the use cases that this agent is involved in
# these use cases/behaviours are:
#     1- Login    2-Registration    3-Fetching Appointment
#     4- Allocating Appointment

# There is one empty defined agent class which extends the Spade's Agent
# and the required behaviour will be loaded into the class at run-time


#%%
# Importing the required libraries
import os
import sys
import time
import json
import getopt
import hashlib
from string import hexdigits
import Directory_Facilitators as DS
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade import quit_spade

# A control variable, 1: print debug information, 0: no print
DEBUG = 0

# Defining the data template and container to be used to transfer
# the information between the different funcitons and components
data = {
    "FirstName": '',
    "LastName": '',
    "Email": '', 
    "Phone": '', 
    "Address": '', 
    "Password": '',
    "Doctor": '',
    "Patient": '',
    "Appointment": ''
}


def password_hashing(passwrd):
    # This function is used to create a hash of plain text password
    # 
    # Args:
    #     passwrd (str): plain text password
    #
    # Returns:
    #     str: A hash of the input represented as a hexa-digit str 


    # Adding salt at the last of the password to increase complexity
    SALT = "G10SENG696"
    DB_PASSWORD = passwrd+SALT

    # Encoding the password and converting to hexa-decimel str
    hashed = hashlib.md5(DB_PASSWORD.encode())
    hexdigits = hashed.hexdigest()
    return hexdigits



#%%
# Registration use case
class PortalRegisterBehav(OneShotBehaviour):
    # This behaviour is used in the registration use case, it runs
    # only one time sending the information needed for the registration
    # and then waits for the response to sends it back
    #
    # Args:
    #     OneShotBehaviour (OneShotBehaviour): Spade's OneShotBehaviour 

    async def run(self):
        # This is a method required part of spade's OneShotBehaviour
        # class and defines the main functionality of the behaviour
        #
        # The data is passed from using the main data container and the
        # output is passed through exit code as follows:
        #     1- Successful user creation
        #     2- User creation failed
        #     0- Session timeout i.e. response was not recieved

        if DEBUG: print("Register Behaviour running")

        # Instantiate the message and defining the recieving agent
        msg = Message(to=DS.Registration["username"], thread="Reg_Thread")     

        # Setting Metadata
        msg.set_metadata("performative", "query")   # Set the "query" FIPA performative
        msg.set_metadata("ontology", "SENG696-G10-Ontology")  # Set the ontology of the message content
        msg.set_metadata("thread", "SENG696-G10-Project")  # Set the thread of the message content
        msg.set_metadata("language", "JSON")        # Set the language of the message content
        
        # Setting the message content and sending it
        msg.body = json.dumps(data)
        await self.send(msg)
        if DEBUG: print("Message sent!")

        # wait for a response from Registration Agent
        msg = await self.receive(timeout=20)  # wait for a message for 20 seconds
        if msg:
            if DEBUG: print("\n________________________\n", msg, "\n________________________")

            if msg.metadata["performative"] == "confirm":
                self.exit_code = 1 #"User is Now Created!"

            else:
                self.exit_code = 2 #"User creation Failure"

        else:
            if DEBUG: print("Did not receive any feedback from Registration Agent")
            self.exit_code = 0 #"Session Timeout!"

        # stop agent behaviour
        await self.agent.stop()

    async def on_end(self):
        # This is a method required part of spade's OneShotBehaviour
        # which defines the actions to be taken on the end of the behaviour
        await self.agent.stop()


# Login use case
class PortalLoginBehav(OneShotBehaviour):
    # This behaviour is used in the login use case, it runs
    # only one time sending the information needed for the login
    # and then waits for the response to sends it back
    #
    # Args:
    #     OneShotBehaviour (OneShotBehaviour): Spade's OneShotBehaviour 

    async def run(self):
        # This is a method required part of spade's OneShotBehaviour
        # class and defines the main functionality of the behaviour
        #
        # The data is passed from using the main data container and the
        # output is passed through exit code as follows:
        #     1- Successful user authentication 
        #     2- User authentication failed
        #     0- Session timeout i.e. response was not recieved


        # Instantiate the message and defining the recieving agent
        if DEBUG: print("Login Behaviour running")
        msg = Message(to=DS.Login["username"], thread="Login_Thread")

        # Setting Metadata
        msg.set_metadata("performative", "query")  # Set the "query" FIPA performative
        msg.set_metadata("ontology", "SENG696-G10-Ontology")  # Set the ontology of the message content
        msg.set_metadata("thread", "SENG696-G10-Project")  # Set the thread of the message content
        msg.set_metadata("language", "JSON")        # Set the language of the message content
        
        # Packaging the required information
        loginData = {
            "Email": data["Email"],
            "Password": data["Password"]
            }

        # Setting the message content and sending it
        msg.body = json.dumps(loginData)
        await self.send(msg)
        if DEBUG: print("Message sent!")

        # wait for a response from Login Agent
        msg = await self.receive(timeout=20)  # wait for a message for 20 seconds
        if msg:
            if DEBUG: print("\n________________________\n", msg, "\n________________________")

            if msg.metadata["performative"] == "confirm":
                print(msg.body)
                self.exit_code = 1 #"User Authenticated!"

            else:
                self.exit_code = 2 #"User Denied"

        else:
            if DEBUG: print("Did not receive any feedback from Login Agent")
            self.exit_code = 0 #"Session Timeout!"

        # stop agent behaviour
        await self.agent.stop()

    async def on_end(self):
        # This is a method required part of spade's OneShotBehaviour
        # which defines the actions to be taken on the end of the behaviour
        await self.agent.stop()


# Fetching available appointments use case
class PortalFetchBehav(OneShotBehaviour):
    # This behaviour is used in the fetch appointment use case, it runs
    # only one time asking for the available appointment of a 
    # specific doctor and then waits for the response to sends it back
    #
    # Args:
    #     OneShotBehaviour (OneShotBehaviour): Spade's OneShotBehaviour 

    async def run(self):
        # This is a method required part of spade's OneShotBehaviour
        # class and defines the main functionality of the behaviour
        #
        # The data is passed from using the main data container and the
        # output is passed through stdout and exit code as follows:
        #     1- Successful information collection,
        #           the data is passed through CLI (stdout)
        #     0- Session timeout i.e. response was not recieved


        # Instantiate the message and defining the recieving agent
        if DEBUG: print("Fetching Behaviour running")
        msg = Message(to=DS.Scheduling["username"], thread="Fetching_Thread")

        # Setting Metadata
        msg.set_metadata("performative", "query")  # Set the "query" FIPA performative
        msg.set_metadata("ontology", "SENG696-G10-Ontology")  # Set the ontology of the message content
        msg.set_metadata("thread", "SENG696-G10-Project")  # Set the thread of the message content
        msg.set_metadata("language", "JSON")       # Set the language of the message content
        
        # Packaging the required information
        fetchingData = {
            "Doctor_ID": data["Doctor"]
        }

        # Setting the message content and sending it
        msg.body = json.dumps(fetchingData)
        await self.send(msg)
        if DEBUG: print("Message sent!")

        # wait for a response from Scheduling Agent
        msg = await self.receive(timeout=20)  # wait for a message for 20 seconds
        if msg:
            if DEBUG: print("\n________________________\n", msg, "\n________________________")
            
            #MUST PRINT: backpropagate the infomation on stdout to the requester
            print(msg.body) 
            self.exit_code = 1 #"Successful collection of information"

        else:
            if DEBUG: print("Did not receive any feedback from Scheduling Agent")
            self.exit_code = 0 #"Session Timeout!"

        # stop agent from behaviour
        await self.agent.stop()

    async def on_end(self):
        # This is a method required part of spade's OneShotBehaviour
        # which defines the actions to be taken on the end of the behaviour
        await self.agent.stop()

# Allocating selected appointment use case
class PortalAllocateBehav(OneShotBehaviour):
    # This behaviour is used in the allocate appointment use case, it runs
    # only one time asking to allocate a certain appointment to a 
    # specific patient and then waits for the response to sends it back
    #
    # Args:
    #     OneShotBehaviour (OneShotBehaviour): Spade's OneShotBehaviour 

    async def run(self):
        # This is a method required part of spade's OneShotBehaviour
        # class and defines the main functionality of the behaviour
        #
        # The data is passed from using the main data container and the
        # output is passed through stdout and exit code as follows:
        #     1- Successful allocation
        #     2- Failed allocation
        #     0- Session timeout i.e. response was not recieved

        # Instantiate the message and defining the recieving agent
        if DEBUG: print("Allocating Behaviour running")
        msg = Message(to=DS.Scheduling["username"], thread="Allocating_Thread")     # Instantiate the message

        # Setting Metadata
        msg.set_metadata("performative", "propose")  # Set the "propose" FIPA performative
        msg.set_metadata("ontology", "SENG696-G10-Ontology")  # Set the ontology of the message content
        msg.set_metadata("thread", "SENG696-G10-Project")  # Set the thread of the message content
        msg.set_metadata("language", "JSON")         # Set the language of the message content
        
        # Packaging the required information
        allocatingData = {
            "User_ID": data["Patient"],
            "Appointment_ID": data["Appointment"],
            "User_Email": data["Email"]
        }

        # Setting the message content and sending it
        msg.body = json.dumps(allocatingData)
        await self.send(msg)
        if DEBUG: print("Message sent!")

        # wait for a response from Registration Agent
        msg = await self.receive(timeout=20)  # wait for a message for 10 seconds
        if msg:
            if DEBUG: print("\n________________________\n", msg, "\n________________________")
            if msg.metadata["performative"] == "confirm":
                self.exit_code = 1 #"Appointment Confirmed"

            else:
                self.exit_code = 2 #"Appointment Allocation Failed"

        else:
            if DEBUG: print("Did not receive any feedback from Scheduling Agent")
            self.exit_code = 0 #"Session Timeout!"

        # stop agent from behaviour
        await self.agent.stop()

    async def on_end(self):
        # This is a method required part of spade's OneShotBehaviour
        # which defines the actions to be taken on the end of the behaviour
        await self.agent.stop()


#%%
class PortalAgentComponent(Agent):
    # This is a empty class that extends the SPADE Agent class
    # There are no behaviours loaded into the class in the declaration
    # however, the required behaviour will be loaded at runtime
    
    async def setup(self):
        if DEBUG: print(f"{self.jid} created.")

class Portal_Agent:
    # This is our protal agent class which will create an instance
    # of the PortalAgentComponent and then select which behaviour to
    # load into it.
    # The class contains the following members:
    # 1- usecase <int> which is used to indecate which use case is needed
    # 2- behav <SPADE.Behaviour> which will be loaded with the required
    #       behaviour at run-time
    # 3- portalagent <PortalAgentComponent> which will contain an instance
    #       of the class extending the agent to be able to load the
    #       behaviour into it and run it
    # 4- future <SPADE.Future> which will be used to get the outputs from
    #       the bahviours at the end of the run
    #
    # 5- init(<int>) which is the constructor of the class which takes
    #       a use case based on the args provided at run-time
    # 6- selectBehaviour() which selects the required use case and to load
    #       the data container with the required infromation for that
    #       usecase, in addition to loading the required behaviour
    # 7- beginCommunications() this function obtains the required 
    #       credintials of the agent and loads them in addition to the 
    #       behaviour, then it starts the agent and waits until it is 
    #       finished, terminating the application by returning the 
    #       propper exit code through stdout


    def __init__(self, usecase=0):
        # The constructor of the class which takes
        # a use case based on the args provided at run-time
        #
        # Args:
        #     usecase (int, optional): _description_. Defaults to 0.
        self.usecase = usecase

    def selectBehaviour(self):
        # A method that selects the required use case and to load
        # the data container with the required infromation for that

        if self.usecase == 1:
            if DEBUG: print(self.usecase, _USERNAME, _PASSWORD)
            self.behav = PortalLoginBehav()
            data["Email"] = _USERNAME
            data["Password"] = password_hashing(_PASSWORD)
            
        # Case 2: Registration
        elif self.usecase == 2:
            if DEBUG: print(self.usecase, _FIRST_NAME, _LAST_NAME, _USERNAME, _MOBILE, _PASSWORD) #_ADDRESS,
            self.behav = PortalRegisterBehav()
            data["FirstName"] = _FIRST_NAME
            data["LastName"] = _LAST_NAME
            data["Email"] = _USERNAME
            data["Phone"] = _MOBILE
            # if _ADDRESS:
            #     data["Address"] = _ADDRESS
            data["Password"] = password_hashing(_PASSWORD)
        
        elif self.usecase == 3:
            if DEBUG: print(self.usecase, _DOCTOR_ID)
            self.behav = PortalFetchBehav()
            data["Doctor"] = _DOCTOR_ID

        elif self.usecase == 4:
            if DEBUG: print(self.usecase, _USERNAME, _APPOINTMENT, _PATIENT)
            self.behav = PortalAllocateBehav()
            data["Email"] = _USERNAME
            data["Appointment"] = _APPOINTMENT
            data["Patient"] = _PATIENT

        else:
            print("ERROR")
            exit(2)

    def beginCommunications(self):
        # This method obtains the required credintials of the agent 
        # and loads them in addition to the behaviour, then it starts
        # the agent and waits until it is finished, terminating the 
        # application by returning the propper exit code through stdout

        if DEBUG: print(data)

        self.portalagent = PortalAgentComponent(DS.UI["username"], DS.UI["password"])
        self.portalagent.add_behaviour(self.behav)

        # This start is in a synchronous piece of code, so it must NOT be awaited
        self.future = self.portalagent.start(auto_register=True)
        self.future.result()
        self.behav.join()

        while self.portalagent.is_alive():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print(self.portalagent.stop())
                break
        
        if DEBUG: print(F"Agent finished with exit code: {self.behav.exit_code}")

        self.portalagent.stop()
        quit_spade()
        
        exit(self.behav.exit_code)



#%%
def main(argv):
    # Defining the main function's attributes and a help (-h) directive
    # to get details about the accepted arguments
    try:
        opts, args = getopt.getopt(argv,"hc:u:p:f:l:a:m:d:o:t:",
            ["case=","username=","password=:","firstName=", "lastName=", "address=", "mobile=",
             "doctor=", "appointment=", "patient="])
    except getopt.GetoptError:
        print('Input Error!\nUI_Agent.py -c <case> -u <username> -p <password> -f <firstName> -l <lastName> -a <address> -m <mobile> -d <doctor> -o <appointment> -t <patient>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('UI_Agent.py -c <case> -u <username> -p <password> -f <fistName> -l <lastName> -a <address> -m <mobile> -d <doctor>  -o <appointment> -t <patient>')
            sys.exit()
        elif opt in ("-c", "--case"):
            global _CASE
            _CASE = int(arg)
        elif opt in ("-u", "--username"):
            global _USERNAME
            _USERNAME = arg.lower()
        elif opt in ("-p", "--password"):
            global _PASSWORD
            _PASSWORD = arg.lower()
        elif opt in ("-f", "--firstName"):
            global _FIRST_NAME
            _FIRST_NAME = arg
        elif opt in ("-l", "--lastName"):
            global _LAST_NAME
            _LAST_NAME = arg
        elif opt in ("-a", "--address"):
            global _ADDRESS
            _ADDRESS = arg
        elif opt in ("-m", "--mobile"):
            global _MOBILE
            _MOBILE = arg
        elif opt in ("-d", "--doctor"):
            global _DOCTOR_ID
            _DOCTOR_ID = int(arg)
        elif opt in ("-o", "--appointment"):
            global _APPOINTMENT
            _APPOINTMENT = int(arg)
        elif opt in ("-t", "--patient"):
            global _PATIENT
            _PATIENT = int(arg)

#%%
if __name__ == "__main__":
    # This is main, which checks for the args passed at run-time
    # The function then creates an instance of our agent class and 
    # calls the appropriate functions to start it.

    main(sys.argv[1:])

    ui = Portal_Agent(_CASE)
    ui.selectBehaviour()
    ui.beginCommunications()
