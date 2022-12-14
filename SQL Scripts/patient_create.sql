
CREATE TABLE `patients` (
  `SN` int NOT NULL AUTO_INCREMENT,
  `FIRST_NAME` varchar(45) NOT NULL,
  `LAST_NAME` varchar(45) NOT NULL,
  `EMAIL` varchar(45) NOT NULL,
  `PHONE` char(11) NOT NULL,
  `ADDRESS` varchar(100) NOT NULL,
  `PASSWORD` char(32) NOT NULL,
  PRIMARY KEY (`SN`),
  UNIQUE KEY `SN_UNIQUE` (`SN`),
  UNIQUE KEY `EMAIL_UNIQUE` (`EMAIL`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

