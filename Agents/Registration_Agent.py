#%% Init
import time
import json
import mysql.connector
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import Directory_Facilitators as DS

DEBUG = 1


#%% Supporting Functions





#%% reciever

class RegistrationBehav(CyclicBehaviour):
    """
        defining behavoiur

    Args:
        CyclicBehaviour -> type cyclic
    """
    def register_user(self, data):
        """
        This function is responsible for creating users
        It returns 1 on successful creation and
        returns 0 if an error is raised
        """

        #defining DB credintials
        mydb = mysql.connector.connect(
            host= "25.69.251.254", #"192.168.0.101",
            user= "username",
            password= "password",
            database= "alnasera",
        )
        if DEBUG:
            print("mydb:", mydb)

        mycursor = mydb.cursor()

        #Query for inserting the given informations for adding new user
        sql = (
            "INSERT INTO users_db.patients "
            "(FIRST_NAME, LAST_NAME, EMAIL, PHONE, ADDRESS, PASSWORD) "
            "VALUES (%(FirstName)s, %(LastName)s, %(Email)s, %(Phone)s,"
            "%(Address)s, %(Password)s)"
            )

        #Error handling for query executing
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
        """
            This function is responsible for creating messeages based on registration states
            for example in sucessful insertion it gives an confirmation for future use

        """
        if state:
            msg.set_metadata("performative", "confirm")  # Set the "confirm" FIPA performative
        else:
            msg.set_metadata("performative", "failure")        
        msg.body = ""
        print("\n_______RESPONSE:_______\n",msg, "\n______________")
        await self.send(msg)
        print("Response sent!")

    async def run(self):

        """ 
            In this function the agent waits for a specified amount of time and listen for messages 
            then based on result of register_user method which was explained earier return success or failure flag

        """

        print("\n\n\n====================================")
        print("Entering Registration Behav:")
        msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
        if msg:
            print("\n________________________\n", msg, "\n________________________")
            print(F"Message received with content: {msg.body}")
            print(msg.metadata)
            print("Ontology is: ", msg.metadata["ontology"])
            response = json.loads(msg.body)
            print("Email is:", response["Email"], " and password is: ", response["Password"])
            
            if self.register_user(response):
                await self.msg_response(msg.make_reply(), True)
                print("Successfully Registered User\n\n")
            else:
                await self.msg_response(msg.make_reply(), False)
                print("User Already Exists\n\n")

        else:
            print("Did not received any message after 10 seconds")
            # self.kill()

    async def on_end(self):
        await self.agent.stop()


class RegistrationAgentComponent(Agent):
    async def setup(self):
        print("RegistrationAgent started")
        


class Registration_Agent:

    """
        The actual class for registration agent which has the already explained behaviour for its only one behaviour
    """

    def loadBehaviour(self):
        self.behav = RegistrationBehav()

    def beginCommunications(self):
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
    reg = Registration_Agent()
    reg.loadBehaviour()
    reg.beginCommunications()
    # registrationagent = registrationagent(DS.Registration["username"], DS.Registration["password"])
    # future = registrationagent.start()
    # future.result()
    
    # print("Wait until user interrupts with ctrl+C")
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("Stopping...")
    # registrationagent.stop()

    # while True:
    #     future = registrationagent.start()
    #     future.result() # wait for receiver agent to be prepared
    #     while registrationagent.is_alive():
    #         try:
    #             print("1")
    #             time.sleep(1)
    #         except KeyboardInterrupt:
    #             registrationagent.stop()
    #             break
    #     print("looping")

    
    # print("Agents finished")
    # registrationagent.stop()
    # quit_spade()
# %%
