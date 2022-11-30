# This is the Registration agent, the agent is designed to run in a cyclic
# behaviour where it wait for incoming registration requests and trys to
# add them to the database, returning "confirm" or "failure" performative 
# to the requesting agent based on whether the credintials provided have
# been successfully added to the Users DB


#%% 
# Importing the required libraries
import time
import json
import mysql.connector
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import Directory_Facilitators as DS

# A control variable, 1: print debug information, 0: no print
DEBUG = 1

#%%
class RegistrationBehav(CyclicBehaviour):
    # This behaviour is used in the registration use case, it continues 
    # running awaiting registration requests, then trys to add the details
    # to the Users Database, returning "confirm" or "failure" performative
    # to the requesting agent based on whether the credintials provided 
    # have been successfully added to the Users DB
    #
    # Args:
    #     CyclicBehaviour (CyclicBehaviour): Spade's CyclicBehaviour

    def register_user(self, data):
        # This function is responsible for creatubg users. 
        # It returns 1 on successful creation and 0 if an error is raised
        # or a record with a matching email exists in the database
        #
        # Args:
        #     data (dict): A dictionary containing the user's information
        #
        # Returns:
        #     int: An integer indecating if the user is created (1)
        #          and (0) otherwise

        
        #defining DB credintials
        mydb = mysql.connector.connect(
            host= "25.69.251.254", #"192.168.0.101",
            user= "username",
            password= "password",
            database= "users_db",
        )
        if DEBUG: print("mydb:", mydb)

        mycursor = mydb.cursor()

        #Query to insert the given informations of the new user
        sql = (
            "INSERT INTO users_db.patients "
            "(FIRST_NAME, LAST_NAME, EMAIL, PHONE, ADDRESS, PASSWORD) "
            "VALUES (%(FirstName)s, %(LastName)s, %(Email)s, %(Phone)s,"
            "%(Address)s, %(Password)s)"
            )

        # Query execution and error handling
        try:
            mycursor.execute(sql, data)
            mydb.commit()
            mycursor.close()
            if DEBUG:
                print(mycursor.rowcount, "record inserted.")
            return 1

        except mysql.connector.Error as err:
            if DEBUG:
                print(F"Something went wrong!:\n{err}")
            mydb.commit()
            mycursor.close()
            return 0

    async def msg_response(self, msg, state):
        # This function is responsible for creating a response messeage
        # based on the registration state, where it changes the messages 
        # perfomative into "confirm" on a successful state and "failure"
        # otherwise
        #
        # Args:
        #     msg (spade.message.Message): The message template of SPADE
        #     state (bool): The state of the registration operation

        if state:
            # Set the "confirm" FIPA performative
            msg.set_metadata("performative", "confirm")
        else:
            # Set the "failutre" FIPA performative
            msg.set_metadata("performative", "failure")        
        msg.body = ""
        print("\n_______RESPONSE:_______\n",msg, "\n______________")
        await self.send(msg)
        print("Response sent!")

    async def run(self):
        # This is a method required part of spade's CyclicBehaviour
        # class and defines the main functionality of the behaviour
        #
        # The behaviour refreshs every 10 secs waiting for a request
        # If a request comes through it is processed and a reply is sent
        # If no request comes through the cycle repeats waiting

        print("\n\n\n====================================")
        print("Entering Registration Behav:")
        # wait for a message for 10 seconds
        msg = await self.receive(timeout=10) 
        if msg:
            # if a message comes print a log of the details
            print("\n________________________\n", 
                    msg, 
                    "\n________________________"
            )
            print(F"Message received with content: {msg.body}")
            print(msg.metadata)
            print("Ontology is: ", msg.metadata["ontology"])
            response = json.loads(msg.body)
            print("Email is:", response["Email"], 
                    " and password is: ", response["Password"])
            
            # Checking the database for user creation, pereparing, and
            # sending the response based on the creation result
            if self.register_user(response):
                await self.msg_response(msg.make_reply(), True)
                print("Successfully Registered User\n\n")
            else:
                await self.msg_response(msg.make_reply(), False)
                print("User Already Exists\n\n")

        else:
            print("Did not received any message after 10 seconds")

    async def on_end(self):
        # This is a method required part of spade's CyclicBehaviour
        # which defines the actions to be taken on the end of the behaviour
        await self.agent.stop()


class RegistrationAgentComponent(Agent):
    # This is a empty class that extends the SPADE Agent class
    # There are no behaviours loaded into the class in the declaration
    # however, the required behaviour will be loaded at runtime

    async def setup(self):
        print("Registration Agent started")
        


class Registration_Agent:
    # This is our registration agent class which will create an instance
    # of the RegistrationAgentComponent and load the behaviour into it.
    # The class contains the following members:
    # 1- behav <SPADE.Behaviour> where the behaviour will be 
    #       loaded at run-time
    # 2- registrationagent <RegistrationAgentComponent> which will contain
    #       an instance of the class extending the agent to be able to 
    #       load the behaviour into it and run it
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
        self.behav = RegistrationBehav()

    def beginCommunications(self):
        # This method obtains the required credintials of the agent 
        # and loads them in addition to the behaviour, then it starts
        # the agent and waits until it is interrupted 
        # terminating the agent and the application
        self.registrationagent = RegistrationAgentComponent(DS.Registration["username"], DS.Registration["password"])
        self.registrationagent.add_behaviour(self.behav)
        self.future = self.registrationagent.start()
        self.future.result()
        self.behav.join()

        print("Wait until user interrupts with ctrl+C\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
        self.registrationagent.stop()



#%% Main
if __name__ == "__main__":
    # This is main, creates an instance of our agent class and
    # calls the appropriate functions to start it.

    reg = Registration_Agent()
    reg.loadBehaviour()
    reg.beginCommunications()
    