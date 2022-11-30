
INSERT INTO `appointments_db`.`appointments`
(`SN`,
`APPOINTMENT_DATE`,
`APPOINTMENT_TIME`,
`APPOINTMENT_STATUS`,
`DOCTOR_ID`,
`PATIENT_ID`)
VALUES
(<{SN: }>,
<{APPOINTMENT_DATE: }>,
<{APPOINTMENT_TIME: }>,
<{APPOINTMENT_STATUS: }>,
<{DOCTOR_ID: }>,
<{PATIENT_ID: }>);

###############################################
SET @SN_to_select = <{row_id}>;
SELECT appointments.*
    FROM appointments
    WHERE appointments.SN = @SN_to_select;
    
SELECT `appointments`.`SN`,
    `appointments`.`APPOINTMENT_DATE`,
    `appointments`.`APPOINTMENT_TIME`,
    `appointments`.`APPOINTMENT_STATUS`,
    `appointments`.`DOCTOR_ID`,
    `appointments`.`PATIENT_ID`
FROM `appointments_db`.`appointments`;


#############################################
UPDATE `appointments_db`.`appointments`
SET
`SN` = <{SN: }>,
`APPOINTMENT_DATE` = <{APPOINTMENT_DATE: }>,
`APPOINTMENT_TIME` = <{APPOINTMENT_TIME: }>,
`APPOINTMENT_STATUS` = <{APPOINTMENT_STATUS: }>,
`DOCTOR_ID` = <{DOCTOR_ID: }>,
`PATIENT_ID` = <{PATIENT_ID: }>
WHERE `SN` = <{expr}>;






