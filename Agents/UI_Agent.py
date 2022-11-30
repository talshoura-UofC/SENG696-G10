#%% Init
import os
import sys
import time
import json
import getopt
from string import hexdigits
import hashlib
import Directory_Facilitators as DS

DEBUG = 0

import warnings
warnings.filterwarnings("ignore")

# Creating Dummy Data
# data = {
#     "FirstName": 'Tariq',
#     "LastName": 'Al Shoura',
#     "Email": 'tariq.alshoura@ucalgary.ca', 
#     "Phone": '5874295432', 
#     "Address": 'Brentwood, Calgary', 
#     "Password": 'p@s5w0rd'
# }

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
    # Hashing the Password
    SALT = "G10SENG696"
    # Adding salt at the last of the password
    DB_PASSWORD = passwrd+SALT
    # Encoding the password
    hashed = hashlib.md5(DB_PASSWORD.encode())
    hexdigits = hashed.hexdigest()
    return hexdigits



#%% Sender
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade import quit_spade

class PortalRegisterBehav(OneShotBehaviour):
    async def run(self):
        if DEBUG: print("Register Behaviour running")
        msg = Message(to=DS.Registration["username"], thread="Reg_Thread")     # Instantiate the message

        # Setting Metadata
        msg.set_metadata("performative", "query")  # Set the "query" FIPA performative
        msg.set_metadata("ontology", "SENG696-G10-Ontology")  # Set the ontology of the message content
        msg.set_metadata("thread", "SENG696-G10-Project")  # Set the thread of the message content
        msg.set_metadata("language", "JSON")       # Set the language of the message content
        
        # Setting the message content
        msg.body = json.dumps(data)

        await self.send(msg)
        if DEBUG: print("Message sent!")

        # wait for a response from Registration Agent
        msg = await self.receive(timeout=20)  # wait for a message for 10 seconds
        if msg:
            if DEBUG: print("\n________________________\n", msg, "\n________________________")

            if msg.metadata["performative"] == "confirm":
                self.exit_code = 1 #"User is Now Created!"

            else:
                self.exit_code = 2 #"User creation Failure"

        else:
            if DEBUG: print("Did not receive any feedback from Registration Agent")
            self.exit_code = 0 #"Session Timeout!"

        # stop agent from behaviour
        await self.agent.stop()

    async def on_end(self):
            await self.agent.stop()



class PortalLoginBehav(OneShotBehaviour):
    async def run(self):
        if DEBUG: print("Login Behaviour running")
        msg = Message(to=DS.Login["username"], thread="Another_Thread")     # Instantiate the message

        # Setting Metadata
        msg.set_metadata("performative", "query")  # Set the "query" FIPA performative
        msg.set_metadata("ontology", "SENG696-G10-Ontology")  # Set the ontology of the message content
        msg.set_metadata("thread", "SENG696-G10-Project")  # Set the thread of the message content
        msg.set_metadata("language", "JSON")       # Set the language of the message content
        
        loginData = {
            "Email": data["Email"],
            "Password": data["Password"]
            }

        # Setting the message content
        msg.body = json.dumps(loginData)

        await self.send(msg)
        if DEBUG: print("Message sent!")

        # wait for a response from Registration Agent
        msg = await self.receive(timeout=20)  # wait for a message for 10 seconds
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

        # stop agent from behaviour
        await self.agent.stop()

    async def on_end(self):
            await self.agent.stop()


class PortalFetchBehav(OneShotBehaviour):
    async def run(self):
        if DEBUG: print("Fetching Behaviour running")
        msg = Message(to=DS.Scheduling["username"], thread="Another_Thread")     # Instantiate the message

        # Setting Metadata
        msg.set_metadata("performative", "query")  # Set the "query" FIPA performative
        msg.set_metadata("ontology", "SENG696-G10-Ontology")  # Set the ontology of the message content
        msg.set_metadata("thread", "SENG696-G10-Project")  # Set the thread of the message content
        msg.set_metadata("language", "JSON")       # Set the language of the message content
        
        fetchingData = {
            "Doctor_ID": data["Doctor"]
        }

        # Setting the message content
        msg.body = json.dumps(fetchingData)

        await self.send(msg)
        if DEBUG: print("Message sent!")

        # wait for a response from Registration Agent
        msg = await self.receive(timeout=20)  # wait for a message for 10 seconds
        if msg:
            if DEBUG: print("\n________________________\n", msg, "\n________________________")
            print(msg.body) # MUST PRINT to backprogate the info
            self.exit_code = 1

        else:
            if DEBUG: print("Did not receive any feedback from Scheduling Agent")
            self.exit_code = 0 #"Session Timeout!"

        # stop agent from behaviour
        await self.agent.stop()

    async def on_end(self):
            await self.agent.stop()


class PortalAllocateBehav(OneShotBehaviour):
    async def run(self):
        if DEBUG: print("Allocating Behaviour running")
        msg = Message(to=DS.Scheduling["username"], thread="Another_Thread")     # Instantiate the message

        # Setting Metadata
        msg.set_metadata("performative", "propose")  # Set the "propose" FIPA performative
        msg.set_metadata("ontology", "SENG696-G10-Ontology")  # Set the ontology of the message content
        msg.set_metadata("thread", "SENG696-G10-Project")  # Set the thread of the message content
        msg.set_metadata("language", "JSON")       # Set the language of the message content
        
        allocatingData = {
            "User_ID": data["Patient"],
            "Appointment_ID": data["Appointment"],
            "User_Email": data["Email"]
        }

        # Setting the message content
        msg.body = json.dumps(allocatingData)

        await self.send(msg)
        if DEBUG: print("Message sent!")

        # wait for a response from Registration Agent
        msg = await self.receive(timeout=20)  # wait for a message for 10 seconds
        if msg:
            if DEBUG: print("\n________________________\n", msg, "\n________________________")
            if msg.metadata["performative"] == "confirm":
                self.exit_code = 1 #"Appointment Confirmed!"

            else:
                self.exit_code = 2 #"Appointment Allocation Failed"

        else:
            if DEBUG: print("Did not receive any feedback from Scheduling Agent")
            self.exit_code = 0 #"Session Timeout!"

        # stop agent from behaviour
        await self.agent.stop()

    async def on_end(self):
            await self.agent.stop()



#%%

def main(argv):
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

class PortalAgentComponent(Agent):
        async def setup(self):
            if DEBUG: print(f"{self.jid} created.")

class Portal_Agent:
    def __init__(self, usecase=0):
        self.usecase = usecase

    def selectBehaviour(self):
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
            exit(5)

    def beginCommunications(self):
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



if __name__ == "__main__":
    main(sys.argv[1:])

    ui = Portal_Agent(_CASE)
    ui.selectBehaviour()
    ui.beginCommunications()

    # # Case 1: LOGIN
    # if _CASE == 1:
    #     if DEBUG: print(_CASE, _USERNAME, _PASSWORD)
    #     behav = LoginBehav()
    #     data["Email"] = _USERNAME
    #     data["Password"] = password_hashing(_PASSWORD)
        
    # # Case 2: Registration
    # elif _CASE == 2:
    #     if DEBUG: print(_CASE, _FIRST_NAME, _LAST_NAME, _USERNAME, _MOBILE, _PASSWORD) #_ADDRESS,
    #     behav = RegisterBehav()
    #     data["FirstName"] = _FIRST_NAME
    #     data["LastName"] = _LAST_NAME
    #     data["Email"] = _USERNAME
    #     data["Phone"] = _MOBILE
    #     # if _ADDRESS:
    #     #     data["Address"] = _ADDRESS
    #     data["Password"] = password_hashing(_PASSWORD)
    
    # elif _CASE == 3:
    #     if DEBUG: print(_CASE, _DOCTOR_ID)
    #     behav = FetchBehav()
    #     data["Doctor"] = _DOCTOR_ID

    # elif _CASE == 4:
    #     if DEBUG: print(_CASE, _APPOINTMENT, _PATIENT)
    #     behav = AllocateBehav()
    #     data["Appointment"] = _APPOINTMENT
    #     data["Patient"] = _PATIENT

    # else:
    #     print("ERROR")
    #     exit(5)

    # if DEBUG: print(data)

    # agent = Portal(DS.UI["username"], DS.UI["password"])
    # agent.add_behaviour(behav)

    # # This start is in a synchronous piece of code, so it must NOT be awaited
    # future = agent.start(auto_register=True)
    # future.result()
    # behav.join()

    # while agent.is_alive():
    #     try:
    #         time.sleep(1)
    #     except KeyboardInterrupt:
    #         print(agent.stop())
    #         break
    
    # if DEBUG: print(F"Agent finished with exit code: {behav.exit_code}")

    # agent.stop()
    # quit_spade()
    
    # exit(behav.exit_code)





#     agent = Portal(USERNAME, PASSWORD)
#     behav = RegisterBehav() #LoginBehav() #
#     agent.add_behaviour(behav)

#      # This start is in a synchronous piece of code, so it must NOT be awaited
#     future = agent.start(auto_register=True)
#     future.result()
#     behav.join()

#     while agent.is_alive():
#         try:
#             time.sleep(1)
#         except KeyboardInterrupt:
#             print(agent.stop())
#             break
    
#     print(F"Agent finished with exit code: {behav.exit_code}")

#     agent.stop()

# #%%
#     quit_spade()



# %%
