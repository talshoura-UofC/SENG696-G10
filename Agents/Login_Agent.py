#%% Init

# python ../Project/Login_Agent.py
import time
import json
import mysql.connector
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

import Directory_Facilitators as DS
DEBUG = 1


#%% Supporting Functions

    




#%% reciever
class LoginBehav(CyclicBehaviour):
    def login_user(self, data):
        """
        This function is responsible for creating users
        It returns 1 on successful creation and
        returns 0 if an error is raised
        """

        #defining DB credintials
        mydb = mysql.connector.connect(
            host= "10.13.145.180", # "25.69.251.254", #"192.168.0.101",
            user= "username",
            password= "password",
            database= "alnasera",
        )
        if DEBUG:
            print("mydb:", mydb)

        mycursor = mydb.cursor(dictionary=True)

        sql = (
            "SELECT * FROM users_db.patients "
            "WHERE EMAIL = %(Email)s AND PASSWORD = %(Password)s"
            )

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
        if state:
            msg.set_metadata("performative", "confirm")  # Set the "confimr" FIPA performative
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
        print("\n\n\n====================================")
        print("Entering Login Behav:")
        msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
        if msg:
            print("\n________________________\n", msg, "\n________________________")
            print(F"Message received with content: {msg.body}")
            print(msg.metadata)
            print("Ontology is: ", msg.metadata["ontology"])
            request = json.loads(msg.body)
            print("Email is:", request["Email"], " and password is: ", request["Password"])
            
            response = self.login_user(request)
            print(response)
            if response:
                await self.msg_response(msg.make_reply(), True, response)
                print("User Authenticated\n\n")
            else:
                await self.msg_response(msg.make_reply(), False)
                print("User Denied\n\n")

        else:
            print("Did not received any message after 10 seconds")
            # self.kill()

    async def on_end(self):
        await self.agent.stop()

class LoginAgentComponent(Agent):
    async def setup(self):
        print("Login Agent started")

class Login_Agent:
    def loadBehaviour(self):
        self.behav = LoginBehav()

    def beginCommunications(self):
        self.loginagent = LoginAgentComponent(DS.Login["username"], DS.Login["password"])
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
    login = Login_Agent()
    login.loadBehaviour()
    login.beginCommunications()
    # loginagent = LoginAgent(DS.Login["username"], DS.Login["password"])
    # future = loginagent.start()
    # future.result()
    
    # print("Wait until user interrupts with ctrl+C")
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("Stopping...")
    
    # loginagent.stop()



#%%


# CREATE TABLE 'users_db'.'patients' (
#   'SN' INT NOT NULL AUTO_INCREMENT,
#   'FIRST_NAME' VARCHAR(45) NOT NULL,
#   'LAST_NAME' VARCHAR(45) NOT NULL,
#   'EMAIL' VARCHAR(45) NOT NULL,
#   'PHONE' CHAR(10) NOT NULL,
#   'ADDRESS' VARCHAR(100) NOT NULL,
#   'PASSWORD' CHAR(32) NOT NULL,
#   PRIMARY KEY ('SN'),
#   UNIQUE INDEX 'SN_UNIQUE' ('SN' ASC) VISIBLE,
#   UNIQUE INDEX 'EMAIL_UNIQUE' ('EMAIL' ASC) VISIBLE);




# INSERT INTO 'users_db'.'patients' ('FIRST_NAME', 'LAST_NAME', 
# 'EMAIL', 'PHONE', 'ADDRESS', 'PASSWORD') VALUES ('Tariq', 'Al Shoura', 
# 'tariq.alshoura@ucalgary.ca', '5874295432', 'Brentwood, Calgary', 'Xzibt!23');



# DELETE FROM 'users_db'.'patients' WHERE ('SN' = '1');



# CREATE TABLE `appointments_db`.`doctors` (
#   `SN` INT NOT NULL AUTO_INCREMENT,
#   `FIRST_NAME` VARCHAR(45) NOT NULL,
#   `LAST_NAME` VARCHAR(45) NOT NULL,
#   `EMAIL` VARCHAR(45) NOT NULL,
#   `PHONE` CHAR(10) NOT NULL,
#   `SPECIALIZATION` INT NOT NULL,
#   PRIMARY KEY (`SN`),
#   UNIQUE INDEX `EMAIL_UNIQUE` (`EMAIL` ASC) VISIBLE,
#   INDEX `SN_idx` (`SPECIALIZATION` ASC) VISIBLE,
#   CONSTRAINT `Specialization_FK`
#     FOREIGN KEY (`SPECIALIZATION`)
#     REFERENCES `appointments_db`.`specializations` (`SN`)
#     ON DELETE NO ACTION
#     ON UPDATE NO ACTION);



# CREATE TABLE `appointments_db`.`appointments` (
#   `SN` INT NOT NULL AUTO_INCREMENT,
#   `APPOINTMENT_DATE` DATE NOT NULL,
#   `APPOINTMENT_TIME` TIME NOT NULL,
#   `APPOINTMENT_STATUS` CHAR(1) NOT NULL,
#   `DOCTOR_ID` INT NOT NULL,
#   `PATIENT_ID` INT NOT NULL,
#   PRIMARY KEY (`SN`),
#   INDEX `Doctor_FK_idx` (`DOCTOR_ID` ASC) VISIBLE,
#   INDEX `Patients_FK_idx` (`PATIENT_ID` ASC) VISIBLE,
#   CONSTRAINT `Doctor_FK`
#     FOREIGN KEY (`DOCTOR_ID`)
#     REFERENCES `appointments_db`.`doctors` (`SN`)
#     ON DELETE NO ACTION
#     ON UPDATE NO ACTION,
#   CONSTRAINT `Patients_FK`
#     FOREIGN KEY (`PATIENT_ID`)
#     REFERENCES `users_db`.`patients` (`SN`)
#     ON DELETE NO ACTION
#     ON UPDATE NO ACTION);


# INSERT INTO `appointments_db`.`specializations` (`NAME`) VALUES ('General');
# INSERT INTO `appointments_db`.`specializations` (`NAME`) VALUES ('Addiction');
# INSERT INTO `appointments_db`.`specializations` (`NAME`) VALUES ('Neuropsychiatry');
# INSERT INTO `appointments_db`.`specializations` (`NAME`) VALUES ('Occupational');
# INSERT INTO `appointments_db`.`specializations` (`NAME`) VALUES ('Psychosomatic ');
# INSERT INTO `appointments_db`.`specializations` (`NAME`) VALUES ('Forensic ');


# INSERT INTO `appointments_db`.`doctors` (`FIRST_NAME`, `LAST_NAME`, `EMAIL`, `PHONE`, `SPECIALIZATION`) VALUES ('John', 'Brown', 'J.Brown@doma.in', '1234567890', '1');
# INSERT INTO `appointments_db`.`doctors` (`FIRST_NAME`, `LAST_NAME`, `EMAIL`, `PHONE`, `SPECIALIZATION`) VALUES ('Jasleen', 'Bernard', 'J.Bernard@doma.in', '5055176982', '1');
# INSERT INTO `appointments_db`.`doctors` (`FIRST_NAME`, `LAST_NAME`, `EMAIL`, `PHONE`, `SPECIALIZATION`) VALUES ('Jody', 'Hackett', 'J.Haigh@doma.in', '4814924475', '1');
# INSERT INTO `appointments_db`.`doctors` (`FIRST_NAME`, `LAST_NAME`, `EMAIL`, `PHONE`, `SPECIALIZATION`) VALUES ('Janelle', 'Haigh', 'A.Warren@doma.in', '2029182132', '2');
# INSERT INTO `appointments_db`.`doctors` (`FIRST_NAME`, `LAST_NAME`, `EMAIL`, `PHONE`, `SPECIALIZATION`) VALUES ('Amaya', 'Warren', 'E.Church@doma.in', '5052395965', '2');
# INSERT INTO `appointments_db`.`doctors` (`FIRST_NAME`, `LAST_NAME`, `EMAIL`, `PHONE`, `SPECIALIZATION`) VALUES ('Efe', 'Church', 'L.Shepherd@doma.in', '3182985202', '3');
# INSERT INTO `appointments_db`.`doctors` (`FIRST_NAME`, `LAST_NAME`, `EMAIL`, `PHONE`, `SPECIALIZATION`) VALUES ('Church', 'Shepherd', 'A.Estrada@doma.in', '3183402994', '4');
# INSERT INTO `appointments_db`.`doctors` (`FIRST_NAME`, `LAST_NAME`, `EMAIL`, `PHONE`, `SPECIALIZATION`) VALUES ('Matylda', 'Mccray', 'M.Mccray@doma.in', '5056622862', '5');
# INSERT INTO `appointments_db`.`doctors` (`FIRST_NAME`, `LAST_NAME`, `EMAIL`, `PHONE`, `SPECIALIZATION`) VALUES ('Manal', 'Franco', 'M.Franco@doma.in', '3189183918', '5');


# ALTER TABLE users_db.patients AUTO_INCREMENT = 1












##### OLD SQL DUMP
# sql = (
#     "INSERT INTO users_db.patients "
#     "(FIRST_NAME, LAST_NAME, EMAIL, PHONE, ADDRESS, PASSWORD) "
#     "VALUES (%s, %s, %s, %s, %s, %s)"
#     )

# val = (data["FirtName"], data["LastName"], data["Email"], data["Phone"],
# data["Address"], data["Password"])

# print("SQL:", sql)
# print("VAL:", val)
# mycursor.execute(sql, data)


