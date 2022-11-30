

INSERT INTO `users_db`.`patients`
(`SN`,
`FIRST_NAME`,
`LAST_NAME`,
`EMAIL`,
`PHONE`,
`ADDRESS`,
`PASSWORD`)
VALUES
(<{SN: }>,
<{FIRST_NAME: }>,
<{LAST_NAME: }>,
<{EMAIL: }>,
<{PHONE: }>,
<{ADDRESS: }>,
<{PASSWORD: }>);

#################################################
SET @SN_to_select = <{row_id}>;
SELECT patients.*
    FROM patients
    WHERE patients.SN = @SN_to_select;

