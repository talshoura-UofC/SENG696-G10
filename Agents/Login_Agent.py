# This is the Login agent, the agent is designed to run in a cyclic
# behaviour where it wait for incoming loging requests and checks the
# database for matching credintials, returning "confirm" or "failure"
# performative to the requesting agent based on whether the credintials
# provided exist and match any record in the Users DB


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
class LoginBehav(CyclicBehaviour):
    # This behaviour is used in the login use case, it continues running
    # awaiting login requests, then checks the Users Database for records
    # that matches the provided information, returning "confirm" or "failure"
    # performative to the requesting agent based on whether the credintials
    # provided exist and match any record in the Users DB
    #
    # Args:
    #     CyclicBehaviour (CyclicBehaviour): Spade's CyclicBehaviour

    def login_user(self, data):
        # This function is responsible for authenticating users. 
        # It returns 1 on successful login and 0 if an error is raised
        # or if the no records matching the data was found
        #
        # Args:
        #     data (dict): A dictionary containing the Email and Password
        #
        # Returns:
        #     int: An integer indecating if the user is authenticated (1)
        #          and (0) otherwise


        # Defining DB credintials
        mydb = mysql.connector.connect(
            host= "25.69.251.254", #"192.168.0.101",
            user= "username",
            password= "password",
            database= "users_db",
        )
        if DEBUG:
            print("mydb:", mydb)

        mycursor = mydb.cursor(dictionary=True)

        # The query for fetching user with given email and password
        sql = (
            "SELECT * FROM users_db.patients "
            "WHERE EMAIL = %(Email)s AND PASSWORD = %(Password)s"
            )

        # Query execution and error handling
        try:
            mycursor.execute(sql, data)
            results = mycursor.fetchall()
            mycursor.close()
            if DEBUG:
                print(mycursor.rowcount, "record found.")
                print(results)

            if len(results) == 1:
                mycursor.close()
                return results

            else:
                mycursor.close()
                return 0

        except mysql.connector.Error as err:
            if DEBUG:
                print(F"Something went wrong!:\n{err}")
            mycursor.close()
            return 0


    async def msg_response(self, msg, state, info=[]):
        # This function is responsible for creating a response messeage
        # based on the login state, where it changes the messages 
        # perfomative into "confirm" on a successful state and "failure"
        # otherwise
        #
        # Args:
        #     msg (spade.message.Message): The message template of SPADE
        #     state (bool): The state of the login operation
        #     info (list, optional): contains the information to be
        #       sent back to the requested. Defaults to [].

        if state:
            # Set the "confirm" FIPA performative
            msg.set_metadata("performative", "confirm")
            # Loading the user's SN in the response payload
            payload={
                "SN": info[0]["SN"],
            }
            msg.body = json.dumps(payload)

        else:
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
        print("Entering Login Behav:")
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
            request = json.loads(msg.body)
            print("Email is:", request["Email"], 
                    " and password is: ", request["Password"])
            
            # Checking the database for authentication
            response = self.login_user(request)
            print(response)

            # Preparing and sending the response based on the
            # authentication result
            if response:
                await self.msg_response(msg.make_reply(), True, response)
                print("User Authenticated\n\n")
            else:
                await self.msg_response(msg.make_reply(), False)
                print("User Denied\n\n")

        else:
            print("Did not received any message after 10 seconds")

    async def on_end(self):
        # This is a method required part of spade's CyclicBehaviour
        # which defines the actions to be taken on the end of the behaviour
        await self.agent.stop()

class LoginAgentComponent(Agent):
    # This is a empty class that extends the SPADE Agent class
    # There are no behaviours loaded into the class in the declaration
    # however, the required behaviour will be loaded at runtime
    
    async def setup(self):
        print("Login Agent started")

class Login_Agent():
    # This is our login agent class which will create an instance
    # of the LoginAgentComponent and load the behaviour into it.
    # The class contains the following members:
    # 1- behav <SPADE.Behaviour> where the behaviour will be 
    #       loaded at run-time
    # 2- loginagent <LoginAgentComponent> which will contain an instance
    #       of the class extending the agent to be able to load the
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
        self.behav = LoginBehav()

    def beginCommunications(self):
        # This method obtains the required credintials of the agent 
        # and loads them in addition to the behaviour, then it starts
        # the agent and waits until it is interrupted 
        # terminating the agent and the application
        self.loginagent = LoginAgentComponent(
            DS.Login["username"], DS.Login["password"]
        )
        self.loginagent.add_behaviour(self.behav)
        self.future = self.loginagent.start()
        self.future.result()
        self.behav.join()

        print("Wait until user interrupts with ctrl+C\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
        self.loginagent.stop()



#%% Main
if __name__ == "__main__":
    # This is main, creates an instance of our agent class and
    # calls the appropriate functions to start it.

    login = Login_Agent()
    login.loadBehaviour()
    login.beginCommunications()