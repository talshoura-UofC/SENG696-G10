
INSERT INTO `appointments_db`.`doctors`
(`SN`,
`FIRST_NAME`,
`LAST_NAME`,
`EMAIL`,
`PHONE`,
`SPECIALIZATION`)
VALUES
(<{SN: }>,
<{FIRST_NAME: }>,
<{LAST_NAME: }>,
<{EMAIL: }>,
<{PHONE: }>,
<{SPECIALIZATION: }>);

########################################
SELECT `doctors`.`SN`,
    `doctors`.`FIRST_NAME`,
    `doctors`.`LAST_NAME`,
    `doctors`.`EMAIL`,
    `doctors`.`PHONE`,
    `doctors`.`SPECIALIZATION`
FROM `appointments_db`.`doctors`;

