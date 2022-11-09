"""
The server.py file is the main file of the server.
It contains the Server class, The DBMS class, as well as other classes and methods useful for the server.
"""
### IMPORTS ###
import threading                # For the threads
import socket                   # For the sockets
import os                       # For navigating in the file system
import sys
from urllib import response     # For the exit function
import yaml                     # For the configuration file
import time                     # For the sleep function
import random                   # For the random number generation 
import datetime                 # For easy date and time management
import argparse                 # For the command line arguments
import copy                     # For the deepcopy function
from identity import Identity   # For the Identity class (see identity.py)
import mysql.connector          # For the database connection
from typing import *            # For the type hints
from TaggedQueue import *       # For the TaggedQueue class (see TaggedQueue.py)
from User import *              # For the User class (see User.py)
from serverPorts import *       # For the server ports (see serverPorts.py)

### CONSTANTS ###
# Note: for now the constants are arbitrary, but they will be changed later
MAX_DB_CONNECTION_ATTEMPTS = 5              # The maximum number of attempts to connect to the database
DB_CONNECTION_DELAY = 1                     # The delay between two attempts to connect to the database (in seconds)
WORKER_THREAD_QUEUE_CHECK_DELAY = 0.05      # The delay between two checks of the queue (in seconds)
WATCHDOG_CHECK_DELAY = 5                    # The delay between two checks of the watchdog (in seconds)
QUEUE_RESPONSE_TIMEOUT = 15                 # The maximum time to wait for a response from the queue (in seconds)
QUEUE_CHECK_DELAY = 0.01                    # The delay between two checks of the queue (in seconds)
WATCHDOG_CHECK_DELAY = 0.5                  # The delay between two checks of the watchdog (in seconds)

### Utility functions ###
def clear_screen(ansi: bool = True):
    """
    Clears the screen
    """
    if ansi:
        print("\033[H\033[2J")
    else:
        os.system("cls")

def _print_verbose(verbose: int, level: int, *args: Any):
    """
    Prints the arguments if the verbose level is low enough
    """
    if level <= verbose:
        print(*args)

### CLASSES ###

class DBMS():
    """
    The DBMS class handles the communication between the server and the database.
    """
    def __init__(self, config: dict):
        """
        The constructor of the DBMS class
        """
        # We store the configuration
        self.config = config

    def query(self, results_queue: TaggedQueue, job_tag: int, query: str, args: TypedDict = None, procedure: bool = False, fetch: bool = True):
        """
        Executes a query on the database
        The query method is designed to be used by multiple threads, so it is thread-safe
        TODO: try to reconnect to the database if the connection is lost (to prevent soft crashes)
        TODO: notify watchdow of how many queries are running (avoid overloading the database)
        TODO: keep count of number of reconnections (detect bad connection)
        """
        # We try to connect to the database
        attempts = 0
        while attempts < MAX_DB_CONNECTION_ATTEMPTS:
            try:
                connection = mysql.connector.connect(
                    host=self.config["host"],
                    user=self.config["user"],
                    password=self.config["password"],
                    database=self.config["database"]
                )
                # We store the cursor
                cursor = connection.cursor()
                break
            except mysql.connector.Error as err:
                # If we have too many attempts, we exit
                if attempts > MAX_DB_CONNECTION_ATTEMPTS:
                    print("Too many attempts to connect to the database. Exiting...")
                    sys.exit(1)
                # Else, we print the error and we wait a bit
                print("Failed to connect to the database. Error: {}".format(err))
                print("Trying again in {} seconds...".format(DB_CONNECTION_DELAY))
                time.sleep(DB_CONNECTION_DELAY)
                # We increment the number of attempts
                attempts += 1
                # We try again
                continue
        if attempts >= MAX_DB_CONNECTION_ATTEMPTS:
            raise Exception("DB not responding: Too many attempts to connect to the database")
        # We execute the query

        if procedure:
            # We execute the procedure
            cursor.callproc(query, args)
            if not fetch:
                # We commit the changes
                connection.commit()
                # And we close the connection
                connection.close()
                return
            # Get the results
            results = cursor.stored_results()
            # Store the results in a list with all the results of every stored procedure, not divided by procedure
            results_list = []
            for result in results:
                for row in result.fetchall():
                    results_list.append(row)
            results = results_list
        else:
            # We execute the query
            cursor.execute(query, args)
            if not fetch:
                # We commit the changes
                connection.commit()
                # And we close the connection
                connection.close()
                return
            # We get the results
            results = cursor.fetchall()
        
        # We commit the changes
        connection.commit()
        # And we close the connection
        connection.close()
        # Wrap them into the DBMSResult class
        results = DBMSResult(job_tag, query, args, results)
        # We put the results in the queue
        results_queue.put_response(job_tag, results)
    
class DBMSResult(Response):
    """
    The DBMSResult class is used to store the results of a query
    """
    def __init__(self, job_tag: int, query: str, args: tuple, result: list):
        """
        The constructor of the DBMSResult class
        """
        self.job_tag = job_tag
        self.query = query
        self.args = args
        self.result = result
    
    def get(self, index: int):
        """
        Returns the result at the specified index
        """
        return self.result[index]

    def __str__(self):
        """
        The string representation of the DBMSResult class
        """
        return "DBMS Result: Job#{} - Query: {} {}".format(self.job_tag, self.query, self.args)

class Server():

    def printv(self, *args: Any, level: int = 0):
        """
        Prints the arguments if the verbose level is high enough
        """
        _print_verbose(self.verbose, level, *args)

    """
    The Server class is the main class of the server.
    """
    def __init__(
        self,
        host: str = "localhost",
        dbhost: str = "localhost",
        dbuser: str = "root",
        dbpassword: str = "",
        dbname: str = "ChitChat",

        key_port: int = 5556,
        max_key_connections: int = 250,

        com_port_base: int = 5557,
        com_port_number: int = 250,
        max_port_communications: int = 250,

        worker_threads_count = 10,

        verbose = 3,
        ansi = True
        ):

        # Init the attributes
        self.host = host
        self.dbhost = dbhost
        self.dbuser = dbuser
        self.dbpassword = dbpassword
        self.dbname = dbname
        self.key_port = key_port
        self.max_key_connections = max_key_connections
        self.com_port_base = com_port_base
        self.com_port_number = com_port_number
        self.max_port_communications = max_port_communications
        self.worker_threads_count = worker_threads_count
        self.verbose = verbose
        self.ansi = ansi
        self.blacklisted = {} # IP : end_of_blacklist_time

        # Running threads and signal flags
        self.watchdog_thread = None
        self.watchdog_signal = -1 # -1 not running, 0 running, >0 error
        self.worker_threads = []
        self.worker_signals = []

        # Setup the queue
        self.queue = TaggedQueue()

        # Print startup message
        self.printv("Starting server...", level = 0)

        # Connect to DBMS
        self.printv("Connecting to DBMS...", level = 1)

        # We store the configuration of the database
        self.db_config = {
            "host": self.dbhost,
            "user": self.dbuser,
            "password": self.dbpassword,
            "database": self.dbname
        }

        # We also want the database to be thread-safe
        self.db_config["pool_name"] = "pool"
        self.db_config["pool_size"] = self.worker_threads_count + 1 + 1 # We add one for the KeyMaster and one to avoid deadlocks 
    
        # We create the DBMS object
        self.dbms = DBMS(self.db_config)

        # Print success message
        self.printv("Connected to DBMS", level = 1)

        # Create the server 
        self.printv("Creating identity...", level = 2)
        self.identity = Identity()
            
        # Store the public key for ease of access
        self.public_key = self.identity.export_public_key_bytes()

        # Print the public key
        self.printv("Public key: {}".format(self.public_key), level = 3)

        # Init the login manager
        self.printv("Initializing LoginManager...", level = 2)
        self.login_manager = LoginManager(
            5556,
            550,
            self
        )

        self.printv("Initialized KeyMaster", level = 2)

        # Initialize worker threads pool
        self.printv("Initializing worker threads pool...", level = 2)
        
        # Init the worker threads
        for i in range(self.worker_threads_count):
            self.worker_signals.append(0) # ready to run
            self.worker_threads.append(
                threading.Thread(
                    target=self._worker_thread,
                    daemon=True,
                    args=(i,)
                )
            )

        # Init the watchdog thread
        self.watchdog_signal = 0 # ready to run
        self.watchdog_thread = threading.Thread(
            target=self._watchdog,
            daemon=True
        )

        # Start the worker threads (we will start them in a asymmetric fashion, so that they don't all start at the same time)
        for thread in self.worker_threads:
            thread.start()
            time.sleep(random.random() * 0.1)

        # Start the watchdog
        self.watchdog_thread.start()

        # Start the login manager
        self.printv("Starting LoginManager...", level = 2)
        self.login_manager.run()

        # TODO: rest
        # ...
    
    def _watchdog(self):
        # The watchdog is responsible for checking the status of the server
        # In particular, it will check periodically if the connection to the DBMS is still alive,
        # as well as if any worker thread is stuck.
        # If the connection to the DBMS is lost, it will try to reconnect.
        # If a worker thread is stuck, it will be killed and restarted
        self.watchdog_signal = 0 # Signal that the watchdog is now running
        while self.watchdog_signal == 0:
            # Check
            time.sleep(WATCHDOG_CHECK_DELAY) # To not overload the CPU
        # Check the exit signal, and log accordingly
        match self.watchdog_signal:
            case 5:
                self.printv("[Watchdog] Free error code. Shouldn't trigger before assigning it.", level = 0)
            case 4:
                self.printv("[Watchdog] Free error code. Shouldn't trigger before assigning it.", level = 0)
            case 3:
                self.printv("[Watchdog] DBMS connection stopped. Couldn't reconnect. Exiting program...", level = 1)
                self.shutdown()
            case 2:
                self.printv("[Watchdog] Free error code. Shouldn't trigger before assigning it.", level = 0)
            case 1:
                self.printv("[Watchdog] Received kill message. Exiting...", level = 2)
                self.shutdown() 

        # Restore free slot for any future watchdog execution
        self.watchdog_signal = -1
        return
    
    def _worker_thread(self, id):
        # The _worker_thread function is the execution body of a thread.
        # It will:
        # Check for active jobs in the queue
        # Communicate with the database
        # Resolve the job, by outputting a response
        while self.worker_signals[id] == 0:
            # ... do stuff
            # To not overload the CPU
            job = self.queue.next()
            if job:
                # TODO: instead of match-case, we call the function _"job_type" with job as argument
                match job.type:
                    case "get":
                        # Get the data from the database
                        pass # TODO
                    case "register":
                        # Ask to register a new user
                        self._register(job)
                    case "get_userid_info":
                        # Get the info of a user
                        self._get_userid_info(job)
                    case "login":
                        # Login a user
                        self._login(job)
                    case "set_last_seen":
                        # Set the last seen time of a user
                        self._set_last_seen(job)
                    case "create_chat":
                        # Create a new chat
                        self._create_chat(job)
                    case "send_message":
                        # Send a message to a chat
                        self._send_message(job)
                    case "get_unread_messages":
                        # Get the unread messages of a chat
                        self._get_unread_messages(job)

                pass
            time.sleep(WORKER_THREAD_QUEUE_CHECK_DELAY)
        # Restore free slot for any future worker thread allocated
        self.worker_signals[id] = -1
        return
    
    def login(self, username, user_tag, password):
        # This function will create a new job for the queue, and return the job_tag
        # The job will be resolved by the worker threads, which will then put the response in the queue
        job = Job(
            type = "login",
            args = {
                "user_nick": username,
                "user_tag": user_tag,
                "user_password": password
            }
        )
        job_tag = self.queue.put_request(job)
        return job_tag
    
    def _login(self, job : Job):
        """
        The _login method is the actual code executed by workers to resolve a login request.
        It will be called by the _worker_thread function.
        """
        query = "Check_Log_In"
        response = self.dbms.query(self.queue, job.job_tag, query, (
            job.args["user_tag"],
            job.args["user_nick"],
            job.args["user_password"]
        ), procedure=True)
        return job.job_tag
    
    def register(self, username, password, key):
        # This function will create a new job for the queue, and return the job_tag
        # The job will be resolved by the worker threads, which will then put the response in the queue
        job = Job(
            type = "register",
            args = {
                "username": username,
                "password": password,
                "state" : 0, # TODO: use constants in other branch
                "key" : key
            }
        )
        job_tag = self.queue.put_request(job)
        return job_tag
    
    def _register(self, job):
        """
        The _register method is the regiasteactual code executed by workers to resolve a register request.
        It will be called by the _worker_thread function.
        """
        query = "Select create_user (%(username)s, %(state)s, %(key)s, %(password)s)" # TODO: to be replaced by query from dbms developement branch
        response = self.dbms.query(self.queue, job.job_tag, query, 
            {
             "username" : job.args["username"],
             "password" : job.args["password"],
             "state" : job.args["state"],
             "key" : job.args["key"]
            }
        )

        return job.job_tag
    
    def set_last_seen(self, user_id):
        # This function will create a new job for the queue, and return the job_tag
        # The job will be resolved by the worker threads, which will then put the response in the queue
        job = Job(
            type = "set_last_seen",
            args = {
                "user_id": str(user_id)
            }
        )
        job_tag = self.queue.put_request(job)
        return job_tag
    
    def _set_last_seen(self, job):
        """
        The _set_last_seen method is the actual code executed by workers to resolve a set_last_seen request.
        It will be called by the _worker_thread function.
        """
        query = "Update User Set last_log_in = now() Where id = %(user_id)s"
        response = self.dbms.query(self.queue, job.job_tag, query, {
            "user_id" : job.args["user_id"]
        }, fetch=False)
        return job.job_tag
    
    def get_chat_info(self, user, chat):
        # This function will create a new job for the queue, and return the job_tag
        # The job will be resolved by the worker threads, which will then put the response in the queue
        job = Job(
            type = "get_chat_info",
            args = {
                "user": user,
                "chat": chat
            }
        )
        job_tag = self.queue.put_request(job)
        return job_tag
    
    def _get_chat_info(self, job):
        """
        The _get_chat_info method will query the db, making sure that the user is actually in the chat.
        It will be called by the _worker_thread function.
        """
        # query = "Select * from chat where chatid = %(chatid)s and userid = %(userid)s"
        pass
    
    def get_userid_info(self, user):
        # This function will create a new job for the queue, and return the job_tag
        # The job will be resolved by the worker threads, which will then put the response in the queue
        job = Job(
            type = "get_userid_info",
            args = {
                "user": str(user)
            }
        )
        job_tag = self.queue.put_request(job)
        return job_tag
    
    def _get_userid_info(self, job):
        """
        The _get_userid_info method will query the db, making sure that the user exists.
        It will be called by the _worker_thread function.
        """
        query = "Select IDN from user where ID = %(userid)s"
        response = self.dbms.query(self.queue, job.job_tag, query, {
            "userid": job.args["user"]
        })
        return job.job_tag
    
    def create_chat(self, creator, name, description, partecipants):
        # This function will create a new job for the queue, and return the job_tag
        # The job will be resolved by the worker threads, which will then put the response in the queue
        job = Job(
            type = "create_chat",
            args = {
                "creator": creator,
                "name": name,
                "description": description,
                "partecipants": partecipants,
                "photo" : "photos/default.png"
            }
        )
        job_tag = self.queue.put_request(job)
        return job_tag
    
    def _create_chat(self, job):
        """
        The _create_chat method will query the db, creating a new chat.
        It will be called by the _worker_thread function.
        """
        query = "SELECT create_chat(%(chat_name)s, %(chat_description)s, %(chat_creator)s, %(chat_photo)s)"
        response = self.dbms.query(self.queue, str(job.job_tag)+"-1", query, {
            "chat_creator": job.args["creator"].ID,
            "chat_name": job.args["name"],
            "chat_description": job.args["description"],
            "chat_photo": job.args["photo"]
        })
        # Wait for the chat to be created   
        creation = self.queue.wait_for_result(str(job.job_tag)+"-1")
        chat_id = creation[0][0]
        # Add creator as partecipant
        query = "Insert_participant"
        response = self.dbms.query(self.queue, str(job.job_tag)+"-2", query, (
            job.args["creator"].tag,
            job.args["creator"].username,
            chat_id
        ), procedure=True)
        # Wait for the partecipant to be added
        self.queue.wait_for_result(str(job.job_tag)+"-2")
        # Add the partecipants
        for partecipant in job.args["partecipants"]:
            query = "Insert_participant"
            response = self.dbms.query(self.queue, str(job.job_tag)+"-3", query, (
                partecipant[1],
                partecipant[0],
                chat_id
            ), procedure=True)
            # Wait for the partecipant to be added
            self.queue.wait_for_result(str(job.job_tag)+"-3")
        # Get the chat partecipants
        query = "GET_CHAT_PARTICIPANTS"
        response = self.dbms.query(self.queue, str(job.job_tag)+"-4", query, (
            chat_id,
        ), procedure=True)
        # Wait for the partecipants to be retrieved
        partecipants = self.queue.wait_for_result(str(job.job_tag)+"-4")
        # Create the response
        response = Response(
            job_tag = job.job_tag,
            result = {
                "chat_id" : chat_id,
                "chat_name" : job.args["name"],
                "chat_description" : job.args["description"],
                "partecipants" : partecipants.result
            }
        )
        # Put the response in the queue
        self.queue.put_response(job.job_tag, response)
        return job.job_tag

    def send_message(self, user_id, chat_id, message):
        # This function will create a new job for the queue, and return the job_tag
        # The job will be resolved by the worker threads, which will then put the response in the queue
        job = Job(
            type = "send_message",
            args = {
                "user_id": user_id,
                "chat_id": chat_id,
                "message": message
            }
        )
        job_tag = self.queue.put_request(job)
        return job_tag
    
    def _send_message(self, job):
        """
        The _send_message method will query the db, creating a new message.
        It will be called by the _worker_thread function.
        """
        query = "Select create_message(%(sender_id)s, %(chat_id)s, %(message)s)"
        response = self.dbms.query(self.queue, job.job_tag, query, {
            "sender_id": job.args["user_id"],
            "chat_id": job.args["chat_id"],
            "message": job.args["message"]
        })
        return job.job_tag
    
    def get_unread_messages(self, user_id):
        # This function will create a new job for the queue, and return the job_tag
        # The job will be resolved by the worker threads, which will then put the response in the queue
        job = Job(
            type = "get_unread_messages",
            args = {
                "user_id": user_id
            }
        )
        job_tag = self.queue.put_request(job)
        return job_tag
    
    def _get_unread_messages(self, job):
        """
        The _get_unread_messages method will query the db, retrieving the unread messages.
        It will be called by the _worker_thread function.
        """
        query = "messages_not_received"
        response = self.dbms.query(self.queue, str(job.job_tag) + "-1", query, (
            job.args["user_id"],
        ), procedure=True)
        result = self.queue.wait_for_result(str(job.job_tag) + "-1")
  
        # Find the highest relative message id for each chat (second element in the tuple)
        highest_ids = {}
        for message in result.result:
            if message[0] in highest_ids:
                if message[1] > highest_ids[message[0]]:
                    highest_ids[message[0]] = message[1]
            else:
                highest_ids[message[0]] = message[1]
        # Update the last message id for each chat
        for chat_id in highest_ids:
            query = "update_last_message"
            response = self.dbms.query(self.queue, str(job.job_tag) + "-2", query, (
                job.args["user_id"],
                chat_id,
                highest_ids[chat_id]
            ), procedure=True)
            self.queue.wait_for_result(str(job.job_tag) + "-2")
        # Create the response
        response = Response(
            job_tag = job.job_tag,
            result = result.result
        )
        # Put the response in the queue
        self.queue.put_response(job.job_tag, response)
        return job.job_tag

    def shutdown(self):
        # Shutdown the server
        # Kill the watchdog
        self.watchdog_signal = 1
        # Kill the worker threads
        for i in range(len(self.worker_signals)):
            self.worker_signals[i] = 1
        # Exit
        sys.exit(0)
        return

if __name__ == "__main__":
    # We create the server object
    server = Server()
    
    # Wait for user input
    while True:
        try:
            command = input(">>> ")
        except KeyboardInterrupt:
            server.shutdown()
        if command == "shutdown":
            server.shutdown()
        elif command == "register":
            username = input("Username: ")
            password = input("Password: ")
            job_tag = server.register(username, password)
            response = server.queue.wait_for_result(job_tag)
            print(response)
            print("ID of created user is", response.get(0)[0])
    # Shutdown the server
    server.shutdown()



