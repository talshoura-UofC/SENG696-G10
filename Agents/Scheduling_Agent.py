# This is the Scheduling agent, the agent is designed to run in a cyclic
# behaviour where it wait for incoming fetch or allocate requests 
# and communicates with the database to either obtain available 
# appointments or to allocate an appointment for a given user
# returning a list the avialable appoinments for the fetch appointments
# and returning "confirm" or "failure" in the case of appointment
# allocation to the requesting agent, in addition to sending a request


#%%
# Importing the required libraries
import time
import json
import mysql.connector
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
import Directory_Facilitators as DS

# A control variable, 1: print debug information, 0: no print

DEBUG = 1

# Defining the data template and container to be used to transfer
# the information between the different funcitons and components
query_data = {
    "Doctor_ID": 0
}

allocate_data = {
    "Appointment_ID": 0,
    "User_ID": 0
}


#%%
class QueryDBBehav(CyclicBehaviour):
    # This behaviour is used in the fetch appointment use case, it 
    # continues running awaiting Query requests, then checks the 
    # Appointments Database, returning the available appointments
    # to the requesting agent if they any of them exists 
    #
    # Args:
    #     CyclicBehaviour (CyclicBehaviour): Spade's CyclicBehaviour
    
    def fetch_appointments(self, data):
        # This function is responsible for fetching and returning
        # the available appointments from the database
        # 
        # Args:
        #     data (dict): A dictionary containing the required doctor's ID
        #
        # Returns:
        #     list<dict>: if successful communication with the database has
        #         concluded
        #     int: (0) if an error occurs

        # Defining DB credintials
        mydb = mysql.connector.connect(
            host= "25.69.251.254", #"192.168.0.101",
            user= "username",
            password= "password",
            database= "appointments_db",
        )
        if DEBUG: print("mydb:", mydb)

        mycursor = mydb.cursor(dictionary=True)

        # The query to fetch the upcoming available appointments based 
        # on given the provided DOCTOR_ID
        sql = (
            "SELECT "
            "   appointments_db.appointments.SN, "
            "   appointments_db.appointments.APPOINTMENT_DATE, "
            "   appointments_db.appointments.APPOINTMENT_TIME, "
            "   appointments_db.appointments.APPOINTMENT_STATUS, "
            "   appointments_db.appointments.DOCTOR_ID, "
            "   appointments_db.doctors.FIRST_NAME, "
            "   appointments_db.doctors.LAST_NAME, "
            "   appointments_db.specializations.NAME as field "
            "FROM appointments_db.appointments, appointments_db.doctors, appointments_db.specializations "
            "WHERE appointments_db.appointments.DOCTOR_ID = appointments_db.doctors.SN "
            "AND appointments_db.doctors.SPECIALIZATION = appointments_db.specializations.SN "
            "AND appointments_db.appointments.APPOINTMENT_STATUS = 'A' "
            "AND appointments_db.appointments.DOCTOR_ID = %(Doctor_ID)s "
            "AND Timestamp(appointments_db.appointments.APPOINTMENT_DATE, appointments_db.appointments.APPOINTMENT_TIME) > now()"
            )

        # Query execution and error handling
        try:
            mycursor.execute(sql, data)
            results = mycursor.fetchall()
            mycursor.close()
            if DEBUG: 
                print(mycursor.rowcount, "records found.")
                for x in results:
                    print(x)

            if DEBUG: print(json.dumps(results, indent=4, default=str))
            return json.dumps(results, default=str)

        except mysql.connector.Error as err:
            print(F"Something went wrong!:\n{err}")
            mycursor.close()
            return 0

    async def msg_response(self, msg, state):
        # This function is responsible for creating a response messeage
        # based on the fetch state, where it changes the messages 
        # perfomative into "confirm" on a successful state and "failure"
        # otherwise
        #
        # Args:
        #     msg (spade.message.Message): The message template of SPADE
        #     state (bool): The state of the fetch operation

        if state:
            # Set the "confirm" FIPA performative
            msg.set_metadata("performative", "confirm") 
        else:
            # Set the "failutre" FIPA performative
            msg.set_metadata("performative", "failure")
        
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
        print("QueryDB Behav running")
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
            print("Doctor ID is:", request["Doctor_ID"])

            # Querying the database for available appointment and
            # sending the response based on the fetching result
            response = self.fetch_appointments(request)
            if response:
                msg.body = response
                await self.msg_response(msg.make_reply(), True)
                print("Successfully Returned Data\n\n")
            else:
                msg.body = ""
                await self.msg_response(msg.make_reply(), False)
                print("Something went wrong reply")
                

        else:
            print("Did not received any message after 10 seconds")
    
    async def on_end(self):
        # This is a method required part of spade's CyclicBehaviour
        # which defines the actions to be taken on the end of the behaviour
        await self.agent.stop()



#%%
class AllocateDBBehav(CyclicBehaviour):
    # This behaviour is used in the allocate appointment use case, it 
    # continues running awaiting Query requests, then checks the 
    # Appointments Database, returning "confirm" or "failure"
    # performative to the requesting agent based on whether the
    # the appointment has been successfully allocated in the
    # Appointments DB
    #
    # Args:
    #     CyclicBehaviour (CyclicBehaviour): Spade's CyclicBehaviour
 
    def fetch_appointment_details(self, data):
        # This function is responsible for authenticating users. 
        # It returns 1 on successful login and 0 if an error is raised
        # or if the no records matching the data was found
        #
        # Args:
        #     data (dict): A dictionary containing the Appointment's SN
        #
        # Returns:
        #     dict: if successful communication with the database has
        #         concluded, contains the appointments details
        #     int: (0) if an error occurs

        # Defining DB credintials
        mydb = mysql.connector.connect(
            host= "25.69.251.254",
            user= "username",
            password= "password",
            database= "appointments_db",
        )
        if DEBUG: print("mydb:", mydb)

        mycursor = mydb.cursor(dictionary=True)

        # The query to fetch the appointment details based on the SN
        sql = (
            "SELECT "
            "   appointments_db.appointments.SN, "
            "   appointments_db.appointments.APPOINTMENT_DATE, "
            "   appointments_db.appointments.APPOINTMENT_TIME, "
            "   appointments_db.appointments.APPOINTMENT_STATUS, "
            "   appointments_db.appointments.DOCTOR_ID, "
            "   appointments_db.doctors.FIRST_NAME, "
            "   appointments_db.doctors.LAST_NAME, "
            "   appointments_db.appointments.PATIENT_ID, "
            "   appointments_db.specializations.NAME as field "
            "FROM appointments_db.appointments, appointments_db.doctors, appointments_db.specializations "
            "WHERE appointments_db.appointments.DOCTOR_ID = appointments_db.doctors.SN "
            "AND appointments_db.doctors.SPECIALIZATION = appointments_db.specializations.SN "
            "AND appointments_db.appointments.SN = %(Appointment_ID)s "
        )

        # Query execution and error handling
        try:
            mycursor.execute(sql, data)
            results = mycursor.fetchall()
            mycursor.close()
            if DEBUG: 
                print(mycursor.rowcount, "records found.")
                for x in results:
                    print(x)

            if DEBUG: print(json.dumps(results, indent=4, default=str))
            return results

        except mysql.connector.Error as err:
            print(F"Something went wrong!:\n{err}")
            mycursor.close()
            return 0


    async def send_notification(self, data):
        # This function is responsible for creating a messeage to the
        # notification agent with the details of the allocated 
        # appointment to send an email to the user
        #
        # Args:
        #     msg (spade.message.Message): The message template of SPADE
        #     data (dict): A dictionary containing the appointment details

        # Getting the appoinment details using the SN
        appointment = self.fetch_appointment_details(data)
        if appointment:
            notificationData = {
                "USER_EMAIL": data["User_Email"],
                "APPOINTMENT_DATE": appointment[0]["APPOINTMENT_DATE"],
                "APPOINTMENT_TIME": appointment[0]["APPOINTMENT_TIME"],
                "DOCTOR_FIRST_NAME": appointment[0]["FIRST_NAME"],
                "DOCTOR_LAST_NAME": appointment[0]["LAST_NAME"],
            }

            # Setting the message content
            msg = Message(to=DS.Notification["username"], thread="Another_Thread")     # Instantiate the message

            # Setting Metadata
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "SENG696-G10-Ontology")  # Set the ontology of the message content
            msg.set_metadata("thread", "SENG696-G10-Project")  # Set the thread of the message content
            msg.set_metadata("language", "JSON")        # Set the language of the message content
            
            msg.body = json.dumps(notificationData, default=str)
            if DEBUG: print("\n\nREQUESTING NOTIFICATION\n", msg)
            await self.send(msg)
            return 1

        else:
            print("Something went wrong")
            return 0


    def allocate_appointment(self, data):
        # This function is responsible for allocating an 
        # in the Appointments DB
        # 
        # Args:
        #     data (dict): A dictionary containing the Appointment's SN
        #
        # Returns:
        #     int: indecating the state of the allocation operation
        #       1- Successful appoinment allocation
        #       2- Appoinment allocation failed
        #       0- Session timeout i.e. response was not recieved

        #defining DB credintials
        mydb = mysql.connector.connect(
            host= "25.69.251.254", #"192.168.0.101",
            user= "username",
            password= "password",
            database= "alnasera",
        )
        if DEBUG: print("mydb:", mydb)

        mycursor = mydb.cursor(dictionary=True)

        # Query to allocate the appointment to the user
        sql = (
            "UPDATE appointments_db.appointments "
            "SET APPOINTMENT_STATUS = if(PATIENT_ID IS NULL, 'B', APPOINTMENT_STATUS), "
            "PATIENT_ID = if(PATIENT_ID IS NULL, %(User_ID)s, PATIENT_ID) "
            "WHERE (SN = %(Appointment_ID)s)"
        )

        # Query execution and error handling
        try:
            mycursor.execute(sql, data)
            mydb.commit()
            results = mycursor.fetchall()
            mycursor.close()
            if DEBUG:
                print(mycursor.rowcount, "records updated.")
                for x in results:
                    print(x)

            if(int(mycursor.rowcount) > 0):
                if DEBUG: print("record allocated")
                return 1
            else:
                if DEBUG: print("record cannot be allocated")
                return 2

        except mysql.connector.Error as err:
            if DEBUG: print(F"Something in connection went wrong!:\n{err}")
            mycursor.close()
            return 0

    async def msg_response(self, msg, state):
        # This function is responsible for creating a response messeage
        # based on the allocate state, where it changes the messages 
        # perfomative into "confirm" on a successful state and "failure"
        # otherwise
        #
        # Args:
        #     msg (spade.message.Message): The message template of SPADE
        #     state (bool): The state of the login operation

        if state:
            # Set the "confirm" FIPA performative
            msg.set_metadata("performative", "confirm")
        else:
            # Set the "failutre" FIPA performative
            msg.set_metadata("performative", "failure")

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
        print("AllocateDB Behav running")
        # wait for a message for 10 seconds
        msg = await self.receive(timeout=10)
        if msg:
            # if a message comes print a log of the details
            print("\n________________________\n", msg, "\n________________________")
            print(F"Message received with content: {msg.body}")
            print(msg.metadata)
            print("Ontology is: ", msg.metadata["ontology"])
            request = json.loads(msg.body)
            print("Patient ID is:", request["User_ID"], ",\t\tAppointment ID is:", request["Appointment_ID"])

            # Attempting appointment allocation in the database
            response = self.allocate_appointment(request)

            # Preparing and sending the response based on the
            # allocation result
            if response == 1:
                msg.body = json.dumps(response, default=str)
                await self.msg_response(msg.make_reply(), True)
                print("Successfully Returned Data\n")
                await self.send_notification(request)
                print("Successfully Requested Notification Data\n\n")

            else:
                msg.body = ""
                await self.msg_response(msg.make_reply(), False)
                print("Something went wrong")
                

        else:
            print("Did not received any message after 10 seconds")
    
    async def on_end(self):
        # This is a method required part of spade's CyclicBehaviour
        # which defines the actions to be taken on the end of the behaviour
        await self.agent.stop()

class SchedulingAgentComponent(Agent):
    # This is a empty class that extends the SPADE Agent class
    # There are no behaviours loaded into the class in the declaration
    # however, the required behaviour will be loaded at runtime
    
    async def setup(self):
        print("Starting Scheduling Agent")

class Scheduling_Agent():
    # This is our login agent class which will create an instance
    # of the LoginAgentComponent and load the behaviour into it.
    # The class contains the following members:
    # 1- Qbehav <SPADE.Behaviour> where the Query behaviour will be 
    #       loaded at run-time
    # 2- Abehav <SPADE.Behaviour> where the Allocate behaviour will be 
    #       loaded at run-time
    # 3- Q_template <SPADE.Behaviour> A message template where the 
    #       performative is "query"
    # 4- A_template <SPADE.Template> A message template where the 
    #       performative is "propose"
    # 3- schedulingagent <SchedulingAgentComponent> which will contain an
    #       instance of the class extending the agent to be able to load 
    #       the behaviour into it and run it
    # 4- future <SPADE.Future> which will be used to get the outputs from
    #       the bahviours at the end of the run
    #
    # 5- loadBehaviour() which creates instances of the behaviours and
    #       message templates
    # 6- beginCommunications() this function obtains the required 
    #       credintials of the agent and loads them in addition to the 
    #       behaviours, where it maps each behaviour to a certain
    #       performative using the message template to process the
    #       incoming messages correctly, then it starts the agent and 
    #       waits until a user interrupt killing the agent

    def loadBehaviour(self):
        # A method that creates instances of the required behaviours
        # and message templates
        self.Qbehav = QueryDBBehav()
        self.Q_template = Template()
        self.Q_template.set_metadata("performative", "query")
        
        self.Abehav = AllocateDBBehav()
        self.A_template = Template()
        self.A_template.set_metadata("performative", "propose")
        
        

    def beginCommunications(self):
        # This method obtains the required credintials of the agent 
        # and loads them in addition to the behaviours and their message
        # templates, then it starts the agent and waits until it is 
        # interrupted by a user terminating the agent and the application
        self.schedulingagent = SchedulingAgentComponent(
            DS.Scheduling["username"], DS.Scheduling["password"]
        )
        self.schedulingagent.add_behaviour(self.Qbehav, self.Q_template)
        self.schedulingagent.add_behaviour(self.Abehav, self.A_template)
        self.future = self.schedulingagent.start()
        self.future.result()
        self.Qbehav.join()
        self.Abehav.join()
        print("Wait until user interrupts with ctrl+C")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
        
        schedulingagent.stop()



#%%
if __name__ == "__main__":
    # This is main, creates an instance of our agent class and
    # calls the appropriate functions to start it.
    
    sch = Scheduling_Agent()
    sch.loadBehaviour()
    sch.beginCommunications()
    











#%%



## ALL DOCTORS APPOINTMENTS (FILTER FIELDS)
# SELECT
# 	appointments_db.appointments.SN,
#     appointments_db.appointments.APPOINTMENT_DATE, 
#     appointments_db.appointments.APPOINTMENT_TIME, 
#     appointments_db.appointments.APPOINTMENT_STATUS,
#     appointments_db.appointments.DOCTOR_ID,
#     appointments_db.doctors.FIRST_NAME,
#     appointments_db.doctors.LAST_NAME,
#     appointments_db.specializations.NAME as field
# FROM appointments_db.appointments, appointments_db.doctors, appointments_db.specializations
# WHERE appointments_db.appointments.DOCTOR_ID = appointments_db.doctors.SN
# AND appointments_db.doctors.SPECIALIZATION = appointments_db.specializations.SN


## FILTERING SPECIFIC DATE
# AND appointments_db.appointments.APPOINTMENT_DATE = "2022-10-28"

## DATES BIGGER THAN TODAY
# AND appointments_db.appointments.APPOINTMENT_DATE >= curdate()

## FILTERING FIELD
# AND appointments_db.specializations.NAME = "General"

## FILTERING STATUS
# AND appointments_db.appointments.APPOINTMENT_STATUS = "A"

## APPOINTMENTS AFTER NOW
# AND Timestamp(appointments_db.appointments.APPOINTMENT_DATE, appointments_db.appointments.APPOINTMENT_TIME) > now()


## FULL MIX
# SELECT
# 	appointments_db.appointments.SN,
#     appointments_db.appointments.APPOINTMENT_DATE, 
#     appointments_db.appointments.APPOINTMENT_TIME, 
#     appointments_db.appointments.APPOINTMENT_STATUS,
#     appointments_db.appointments.DOCTOR_ID,
#     appointments_db.doctors.FIRST_NAME,
#     appointments_db.doctors.LAST_NAME,
#     appointments_db.specializations.NAME as field
# FROM appointments_db.appointments, appointments_db.doctors, appointments_db.specializations
# WHERE appointments_db.appointments.DOCTOR_ID = appointments_db.doctors.SN
# AND appointments_db.doctors.SPECIALIZATION = appointments_db.specializations.SN
# AND appointments_db.appointments.APPOINTMENT_STATUS = "A"
# AND appointments_db.specializations.NAME = "General"
# AND Timestamp(appointments_db.appointments.APPOINTMENT_DATE, appointments_db.appointments.APPOINTMENT_TIME) > now()










## UPDATING THE STATUS
# UPDATE appointments_db.appointments SET APPOINTMENT_STATUS = 'B', PATIENT_ID = '58' WHERE (SN = '2')










# # %%
# import time
# import json
# import mysql.connector
# DEBUG = 1

# #defining DB credintials
# mydb = mysql.connector.connect(
#     host= "25.69.251.254", #"192.168.0.101",
#     user= "username",
#     password= "password",
#     database= "alnasera",
# )
# if DEBUG: print("mydb:", mydb)

# mycursor = mydb.cursor(dictionary=True)

# sql = (
#     "SELECT "
#     "   appointments_db.appointments.SN, "
#     "   appointments_db.appointments.APPOINTMENT_DATE, "
#     "   appointments_db.appointments.APPOINTMENT_TIME, "
#     "   appointments_db.appointments.APPOINTMENT_STATUS, "
#     "   appointments_db.appointments.DOCTOR_ID, "
#     "   appointments_db.doctors.FIRST_NAME, "
#     "   appointments_db.doctors.LAST_NAME, "
#     "   appointments_db.appointments.PATIENT_ID, "
#     "   appointments_db.specializations.NAME as field "
#     "FROM appointments_db.appointments, appointments_db.doctors, appointments_db.specializations "
#     "WHERE appointments_db.appointments.DOCTOR_ID = appointments_db.doctors.SN "
#     "AND appointments_db.doctors.SPECIALIZATION = appointments_db.specializations.SN "
#     # "AND appointments_db.appointments.SN = 1 "
#     # "AND appointments_db.appointments.APPOINTMENT_STATUS = 'A' "
#     # "AND appointments_db.specializations.NAME = %(Specialization)s "
#     # "AND appointments_db.appointments.DOCTOR_ID = %(Doctor_ID)s "
#     # "AND Timestamp(appointments_db.appointments.APPOINTMENT_DATE, appointments_db.appointments.APPOINTMENT_TIME) > now()"
#     )


# try:
#     mycursor.execute(sql)
#     # mydb.commit()
#     results = mycursor.fetchall()
#     mycursor.close()
#     if DEBUG: 
#         print(mycursor.rowcount, "records found.")
#         for x in results:
#             print(x)

#     if DEBUG: print(json.dumps(results, indent=4, default=str))
#     print(json.dumps(results, indent=4, default=str))

# except mysql.connector.Error as err:
#     print(F"Something went wrong!:\n{err}")
#     mycursor.close()
#     print(0)
# %%
