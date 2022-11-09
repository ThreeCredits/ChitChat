-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Creato il: Nov 02, 2022 alle 16:31
-- Versione del server: 10.4.21-MariaDB
-- Versione PHP: 8.0.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `chit chat 2.0`
--

-- --------------------------------------------------------
--
-- Struttura della tabella `user`
--

CREATE TABLE `user` (
  `ID` int(11) NOT NULL,
  `IDN` int(11) NOT NULL,
  `Nick` char(32) NOT NULL,
  `State` int(11) NOT NULL,
  `Photo` char(32) NOT NULL,
  `Last_log_in` datetime DEFAULT NULL,
  `Comunication_key` blob NOT NULL,
  `User_password` char(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dump dei dati per la tabella `user`
--

INSERT INTO `user` (`ID`, `IDN`, `Nick`, `State`, `Photo`, `Last_log_in`, `Comunication_key`, `User_password`) VALUES
(1, 1, 'Deleted_user', 0, '', NULL, '', 'apache1234');
--
-- Struttura della tabella `chat`
--

CREATE TABLE `chat` (
  `ID` int(11) NOT NULL,
  `Name` char(32) NOT NULL,
  `Photo` char(32) NOT NULL,
  `Description` char(255) DEFAULT NULL,
  `Creation_date` date NOT NULL,
  `Founder_id` int(11) NOT NULL,
  `Message_counter` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dump dei dati per la tabella `chat`
--


-- --------------------------------------------------------

--
-- Struttura della tabella `message`
--

CREATE TABLE `message` (
  `ID` int(11) NOT NULL,
  `Id_chat` int(11) NOT NULL,
  `Id_sender` int(11) NOT NULL,
  `Body` blob NOT NULL,
  `Timestamp` datetime NOT NULL,
  `Message_number` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dump dei dati per la tabella `message`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `participate`
--

CREATE TABLE `participate` (
  `Id_user` int(11) NOT NULL,
  `Id_chat` int(11) NOT NULL,
  `Last_message_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dump dei dati per la tabella `participate`
--


--
-- Trigger `participate`
--
DELIMITER $$
CREATE TRIGGER `Clean_up_chat` AFTER DELETE ON `participate` FOR EACH ROW BEGIN

DECLARE x int DEFAULT 0;

SELECT COUNT(*) FROM participate
WHERE old.Id_chat = participate.Id_chat INTO x;

IF(x = 0 or x is null)
THEN
DELETE FROM chat
WHERE old.Id_chat = chat.ID;
END IF;

END
$$
DELIMITER ;

-- --------------------------------------------------------


--
-- Trigger `user`
--
DELIMITER $$
CREATE TRIGGER `Clean_up_user` AFTER DELETE ON `user` FOR EACH ROW DELETE FROM participate
WHERE participate.Id_user = old.ID
$$
DELIMITER ;

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `chat`
--
ALTER TABLE `chat`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `Founder_id` (`Founder_id`);

--
-- Indici per le tabelle `message`
--
ALTER TABLE `message`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `Foreign_key_sender_id` (`Id_sender`),
  ADD KEY `Id_chat` (`Id_chat`);

--
-- Indici per le tabelle `participate`
--
ALTER TABLE `participate`
  ADD PRIMARY KEY (`Id_user`,`Id_chat`);

--
-- Indici per le tabelle `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `chat`
--
ALTER TABLE `chat`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT per la tabella `message`
--
ALTER TABLE `message`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT per la tabella `user`
--
ALTER TABLE `user`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- Limiti per le tabelle scaricate
--

--
-- Limiti per la tabella `chat`
--
ALTER TABLE `chat`
  ADD CONSTRAINT `chat_ibfk_1` FOREIGN KEY (`Founder_id`) REFERENCES `user` (`ID`);

--
-- Limiti per la tabella `message`
--
/*ALTER TABLE `message`
  ADD CONSTRAINT `Foreign_key_sender_id` FOREIGN KEY (`Id_sender`) REFERENCES `user` (`ID`) ON DELETE CASCADE,
  ADD CONSTRAINT `message_ibfk_1` FOREIGN KEY (`Id_chat`) REFERENCES `chat` (`ID`);*/
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
