#%%
import time
import json
import mysql.connector
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
import Directory_Facilitators as DS

DEBUG = 1

query_data = {
    "Doctor_ID": 3
}

allocate_data = {
    "Appointment_ID": 2,
    "User_ID": 59
}


#%%
class QueryDBBehav(CyclicBehaviour):
    def fetch_appointments(self, data):
        if DEBUG: print(data)

        #defining DB credintials
        mydb = mysql.connector.connect(
            host= "10.13.145.180", #"25.69.251.254", #"192.168.0.101",
            user= "username",
            password= "password",
            database= "alnasera",
        )
        if DEBUG: print("mydb:", mydb)

        mycursor = mydb.cursor(dictionary=True)

        sql = (
            "SELECT "
            "   appointments_db.appointments.SN, "
            "   appointments_db.appointments.APPOINTMENT_DATE, "
            "   appointments_db.appointments.APPOINTMENT_TIME, "
            "   appointments_db.appointments.APPOINTMENT_STATUS, "
            "   appointments_db.appointments.DOCTOR_ID, "
            "   appointments_db.doctors.FIRST_NAME, "
            "   appointments_db.doctors.LAST_NAME, "
            # "   appointments_db.appointments.PATIENT_ID, "
            "   appointments_db.specializations.NAME as field "
            "FROM appointments_db.appointments, appointments_db.doctors, appointments_db.specializations "
            "WHERE appointments_db.appointments.DOCTOR_ID = appointments_db.doctors.SN "
            "AND appointments_db.doctors.SPECIALIZATION = appointments_db.specializations.SN "
            "AND appointments_db.appointments.APPOINTMENT_STATUS = 'A' "
            # "AND appointments_db.specializations.NAME = %(Specialization)s "
            "AND appointments_db.appointments.DOCTOR_ID = %(Doctor_ID)s "
            # "AND Timestamp(appointments_db.appointments.APPOINTMENT_DATE, appointments_db.appointments.APPOINTMENT_TIME) > now()"
            )

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
        if state:
            msg.set_metadata("performative", "confirm")  # Set the "confimr" FIPA performative
        else:
            msg.set_metadata("performative", "failure")
        
        print("\n_______RESPONSE:_______\n",msg, "\n______________")
        await self.send(msg)
        print("Response sent!")

    async def run(self):
        print("\n\n\n====================================")
        print("QueryDB Behav running")
        msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
        if msg:
            print("\n________________________\n", msg, "\n________________________")
            print(F"Message received with content: {msg.body}")
            print(msg.metadata)
            print("Ontology is: ", msg.metadata["ontology"])
            request = json.loads(msg.body)
            print("Doctor ID is:", request["Doctor_ID"])

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
            # self.kill()
    
    async def on_end(self):
        await self.agent.stop()



#%%
class AllocateDBBehav(CyclicBehaviour):
    def fetch_appointment_details(self, data):
        if DEBUG: print(data)

        #defining DB credintials
        mydb = mysql.connector.connect(
            host= "10.13.145.180", #"25.69.251.254",
            user= "username",
            password= "password",
            database= "alnasera",
        )
        if DEBUG: print("mydb:", mydb)

        mycursor = mydb.cursor(dictionary=True)

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
            msg.set_metadata("performative", "inform")  # Set the "propose" FIPA performative
            msg.set_metadata("ontology", "SENG696-G10-Ontology")  # Set the ontology of the message content
            msg.set_metadata("thread", "SENG696-G10-Project")  # Set the thread of the message content
            msg.set_metadata("language", "JSON")       # Set the language of the message content
            
            msg.body = json.dumps(notificationData, default=str)
            if DEBUG: print("\n\nREQUESTING NOTIFICATION\n", msg)
            await self.send(msg)
            return 1

        else:
            print("Something went wrong")
            return 0



    def allocate_appointment(self, data):
        if DEBUG: print(data)

        #defining DB credintials
        mydb = mysql.connector.connect(
            host= "10.13.145.180", #"25.69.251.254", #"192.168.0.101",
            user= "username",
            password= "password",
            database= "alnasera",
        )
        if DEBUG: print("mydb:", mydb)

        mycursor = mydb.cursor(dictionary=True)

        sql = (
            "UPDATE appointments_db.appointments "
            # " SET APPOINTMENT_STATUS = 'B', PATIENT_ID =%(User_ID)s "
            "SET APPOINTMENT_STATUS = if(PATIENT_ID IS NULL, 'B', APPOINTMENT_STATUS), "
            "PATIENT_ID = if(PATIENT_ID IS NULL, %(User_ID)s, PATIENT_ID) "
            "WHERE (SN = %(Appointment_ID)s)"
        )

        try:
            mycursor.execute(sql, data)
            mydb.commit()
            results = mycursor.fetchall()
            mycursor.close()
            if DEBUG:
                print(mycursor.rowcount, "records updated.") #TODO CHECK IF len < 1
                for x in results:
                    print(x)

            print("\n\nEffected Resutls!!:", type(mycursor.rowcount), mycursor.rowcount, "\n\n")
            if(int(mycursor.rowcount) > 0):
                if DEBUG: print("returning 1")
                return 1
            else:
                if DEBUG: print("no records available")
                return 2

        except mysql.connector.Error as err:
            if DEBUG: print(F"Something in connection went wrong!:\n{err}")
            mycursor.close()
            return 3

    async def msg_response(self, msg, state):
        if state:
            msg.set_metadata("performative", "confirm")  # Set the "confimr" FIPA performative
        else:
            msg.set_metadata("performative", "failure")

        print("\n_______RESPONSE:_______\n",msg, "\n______________")
        await self.send(msg)
        print("Response sent!")

    async def run(self):
        print("\n\n\n====================================")
        print("AllocateDB Behav running")
        msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
        if msg:
            print("\n________________________\n", msg, "\n________________________")
            print(F"Message received with content: {msg.body}")
            print(msg.metadata)
            print("Ontology is: ", msg.metadata["ontology"])
            request = json.loads(msg.body)
            print("Patient ID is:", request["User_ID"], ",\t\tAppointment ID is:", request["Appointment_ID"])

            response = self.allocate_appointment(request)
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
            # self.kill()
    
    async def on_end(self):
        await self.agent.stop()

class SchedulingAgentComponent(Agent):
    async def setup(self):
        print("Starting Scheduling Agent")

class Scheduling_Agent():
    def loadBehaviour(self):
        self.Qbehav = QueryDBBehav()
        self.Q_template = Template()
        self.Q_template.set_metadata("performative", "query")
        
        self.Abehav = AllocateDBBehav()
        self.A_template = Template()
        self.A_template.set_metadata("performative", "propose")
        
        

    def beginCommunications(self):
        self.schedulingagent = SchedulingAgentComponent(DS.Scheduling["username"], DS.Scheduling["password"])
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
    sch = Scheduling_Agent()
    sch.loadBehaviour()
    sch.beginCommunications()
    
    # fetch_appointments(query_data)
    # allocate_appointment(allocate_data)
    # a = SchedulingAgent(DS.Scheduling["username"], DS.Scheduling["password"])
    # future = a.start()
    # future.result()
    # print("Wait until user interrupts with ctrl+C")
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("Stopping...")
    
    # a.stop()













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
