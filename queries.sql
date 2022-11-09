-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Creato il: Nov 02, 2022 alle 16:24
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
DELIMITER $$
--
-- Procedure
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `Check_log_in` (IN `User_tag` INT(11), IN `User_nick` CHAR(32), IN `User_password_` CHAR(32))  BEGIN
SELECT user.ID, user.Comunication_key
FROM user
WHERE IDN = User_tag AND Nick = User_nick AND User_password = User_password_;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Delete_participant`(IN `User_tag` INT(11), IN `User_nick` CHAR(32), IN `Chat_id` INT(11))
BEGIN
DELETE FROM participate
WHERE Search_user_id(User_tag,User_nick) = participate.Id_user AND Id_chat = Chat_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Get_chat_founder`(IN `Chat_id` INT(11))
BEGIN
SELECT u.ID, u.IDN,u.Nick
FROM user u, chat c
WHERE c.ID = Chat_id AND u.ID = c.Founder_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Delete_chat`(IN `Chat_id` INT(11))
BEGIN
DELETE FROM chat
WHERE chat.ID = Chat_id;

DELETE FROM message
WHERE message.Id_chat = Chat_id;

DELETE FROM participate
WHERE participate.Id_chat = Chat_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Get_chat_participants`(IN `Chat_id` INT(11))
BEGIN

SELECT u.Nick,u.IDN,p.Last_message_id
FROM participate p, user u
WHERE p.Id_chat = Chat_id AND u.ID = p.Id_user;

END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Delete_user` (IN `ID_` INT(11))  BEGIN

UPDATE chat
SET chat.Founder_id = 1
WHERE ID_ = chat.Founder_id;


DELETE FROM user 
WHERE ID_ = user.ID;

END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Insert_participant`(IN `User_tag` INT(11), IN `User_nick` CHAR(32), IN `Chat_id` INT(11))
BEGIN
INSERT INTO participate(Id_user,Id_chat)
VALUES(Search_user_id(User_tag,User_nick),Chat_id);
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Messages_not_received` (IN `User_id` INT(11))  
SELECT p.Id_chat,m.Message_number,u.Nick,u.IDN,m.Timestamp,m.Body
FROM message m, participate p, user u
WHERE 	u.ID = m.Id_sender
AND	  	p.Id_user = User_id
AND		p.Id_chat = m.Id_chat
AND     m.Message_number > p.Last_message_id$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Chat_of_a_user`(IN `User_id` INT(11))
SELECT c.ID,c.Name
FROM participate p, chat c
WHERE p.Id_chat = c.ID
AND p.Id_user = User_id$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Update_chat_counter` (IN `Chat_id` INT(11))  BEGIN
UPDATE chat
SET Message_counter = Message_counter + 1
WHERE ID = Chat_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Update_Chat_Description` (IN `Id_chat` INT(11), IN `new_des` CHAR(255))  BEGIN
	UPDATE chat
    SET description = new_des
    WHERE ID = Id_chat;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Update_Chat_Name` (IN `Id_chat` INT(11), IN `New_name` CHAR(32))  BEGIN
	UPDATE chat
    SET Name = New_name
    WHERE ID = Id_chat;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Update_last_message` (IN `User_id` INT(11), IN `Chat_id` INT(11), IN `Last_idm` INT(11))  BEGIN
UPDATE participate
SET participate.Last_message_id = Last_idm
WHERE Id_user = User_id AND Id_chat = Chat_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Update_user_password` (IN `User_id` INT(11), IN `New_password` CHAR(32))  BEGIN
	UPDATE user
    SET user.User_password = New_password
    WHERE ID = user_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `Update_user_state` (IN `New_state` INT(1), IN `User_id` INT(11))  BEGIN
	UPDATE user
    SET State = New_state
    WHERE ID = User_id;
END$$

--
-- Funzioni
--
CREATE DEFINER=`root`@`localhost` FUNCTION `Create_chat` (`Chat_name` CHAR(32), `Chat_description` CHAR(255), `Chat_founder` INT(11), `Chat_photo` CHAR(32)) RETURNS INT(11) BEGIN
INSERT INTO chat(Name,Description,Founder_id,Creation_date,Photo,Message_counter)
VALUES(Chat_name,Chat_description,Chat_founder,CURRENT_DATE(),Chat_photo,0);
RETURN (SELECT MAX(ID) FROM chat);
END$$

CREATE DEFINER=`root`@`localhost` FUNCTION `create_message` (`sender_id` INT(11), `chat_id` INT(11), `body` BLOB) RETURNS INT(11) BEGIN

DECLARE counter int;
DECLARE x int DEFAULT 0;
SELECT COUNT(*) FROM participate
WHERE participate.Id_user = sender_id AND participate.Id_chat = chat_id INTO x;

IF(x is null OR x = 0)
THEN 
RETURN null;
END IF;

SELECT chat.Message_counter 
FROM chat 
WHERE chat.id = Chat_id INTO counter; 

UPDATE chat
SET chat.Message_counter = chat.Message_counter + 1
WHERE chat.ID = Chat_id;

INSERT INTO message(Id_chat,Id_sender,Body,Timestamp,Message_number)
VALUES(Chat_id,Sender_id,Body,now(),counter + 1);

RETURN (SELECT max(ID) FROM message);
END$$

CREATE DEFINER=`root`@`localhost` FUNCTION `Create_user` (`Nick_` CHAR(32), `State_` INT(1), `Comunication_key_` BLOB, `User_password_` CHAR(32)) RETURNS INT(11) BEGIN

DECLARE x int DEFAULT 0;

SELECT max(IDN)
FROM user
WHERE Nick = Nick_ INTO x;  

if (x is null) THEN
SET x = 0;
END if;

IF(x < 9999) THEN

INSERT INTO user(IDN,Nick,State,Last_log_in,Comunication_key,User_password)
VALUES(x+1,Nick_,State_,CURRENT_TIME(),Comunication_key_,User_password_);
SELECT MAX(ID) FROM user into x;
RETURN x;

ELSE
RETURN 0;
END IF;

END$$

CREATE DEFINER=`root`@`localhost` FUNCTION `Search_user_id` (`Tag` INT(11), `Nick_` CHAR(32)) RETURNS INT(11) BEGIN

RETURN (SELECT ID
       	FROM user
       	WHERE IDN = Tag AND Nick = Nick_);

END$$

DELIMITER ;