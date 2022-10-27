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
        # We store the connection to the database
        self.connection = None
        # We store the cursor
        self.cursor = None
        # We store the number of attempts to connect to the database
        self.attempts = 0
        # We try to connect to the database
        self.connect()

    def connect(self):
        """
        Connects to the database
        """
        # We try to connect to the database
        try:
            self.connection = mysql.connector.connect(
                host=self.config["host"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["database"]
            )
            # We store the cursor
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as err:
            # If we have too many attempts, we exit
            if self.attempts > MAX_DB_CONNECTION_ATTEMPTS:
                print("Too many attempts to connect to the database. Exiting...")
                sys.exit(1)
            # Else, we print the error and we wait a bit
            print("Failed to connect to the database. Error: {}".format(err))
            print("Trying again in {} seconds...".format(DB_CONNECTION_DELAY))
            time.sleep(DB_CONNECTION_DELAY)
            # We increment the number of attempts
            self.attempts += 1
            # We try again
            self.connect()

    def query(self, results_queue: TaggedQueue, job_tag: int, query: str, args: TypedDict = None ):
        """
        Executes a query on the database
        The query method is designed to be used by multiple threads, so it is thread-safe
        TODO: try to reconnect to the database if the connection is lost (to prevent soft crashes)
        TODO: notify watchdow of how many queries are running (avoid overloading the database)
        TODO: keep count of number of reconnections (detect bad connection)
        """
        # We execute the query
        self.cursor.execute(query, args)
        # We get the results
        results = self.cursor.fetchall()
        # We commit the changes
        self.connection.commit()
        # Wrap them into the DBMSResult class
        results = DBMSResult(job_tag, query, args, results)
        # We put the results in the queue
        results_queue.put_response(job_tag, results)
    
    def close(self):
        """
        Closes the connection to the database
        """
        self.connection.close()

    def __del__(self):
        """
        The destructor of the DBMS class
        """
        # We close the connection to the database
        self.close()
    
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

class KeyMaster():
    """
    The key master class is used to mediate the access to public keys.
    """
    def __init__(self, server_identity: Identity, dbms: DBMS):
        """
        The constructor of the KeyMaster class
        """
        self.server_identity = server_identity
        self.dbms = dbms
        # In order to avoid querying the database too much, we store the keys in a dictionary
        self.keys = {} 
        # In order to not overload the normal query queue, we use a separate queue for the key queries
        self.key_query_queue = TaggedQueue()
    
    def get_key(self, user: User, results_queue: Any, job_tag: int):
        """
        Gets the public key of an identity
        """
        # If we already have the key, we return it
        if user in self.keys:
            return self.keys[user]
        # Else, we query the database (TODO: query from the database development branch)
        
        # self.dbms.query(results_queue, job_tag, GET_KEY_QUERY, user.get_name(), user.get_tag(), user.get_password())
        key = results_queue.wait_for_result(job_tag)
        # We store the key
        self.keys[user] = key
        return key

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
        ansi = True,
        key_name = None):

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
        self.key_name = key_name

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
        if self.key_name:
            self.identity = Identity(name = self.key_name)
            # Warn the user that using already existing keys is not recommended
            self.printv("Using existing identity. This is not recommended.", level = 2)
        else:
            self.identity = Identity()
            self.printv("Created identity.", level = 2)
        
        # Store the public key for ease of access
        self.public_key = self.identity.get_public_key()

        # Print the public key
        self.printv("Public key: {}".format(self.public_key), level = 3)

        # Initialize the KeyMaster
        self.printv("Initializing KeyMaster...", level = 2)
        self.keymaster = KeyMaster(
            self.identity,
            self.dbms
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
                self.printv("[Watchdog] Received kill message. Exiting watchdog...", level = 2)

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
                match job.type:
                    case "get":
                        # Get the data from the database
                        pass # TODO
                    case "register":
                        # Ask to register a new user
                        self._register(job)
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
                "username": username,
                "user_tag": user_tag,
                "password": password
            }
        )
        job_tag = self.queue.put_request(job)
        return job_tag
    
    def _login(self, job):
        """
        The _login method is the actual code executed by workers to resolve a login request.
        It will be called by the _worker_thread function.
        """
        query = None
        # query = LOGIN_QUERY # TODO: query from dbms developement branch
        response = self.dbms.query(self.queue, job.job_tag, query, (
            job.args["username"],
            job.args["user_tag"],
            job.args["password"]
        ))
        return job.tag
    
    def register(self, username, password):
        # This function will create a new job for the queue, and return the job_tag
        # The job will be resolved by the worker threads, which will then put the response in the queue
        job = Job(
            type = "register",
            args = {
                "username": username,
                "password": password
            }
        )
        job_tag = self.queue.put_request(job)
        return job_tag
    
    def _register(self, job):
        """
        The _register method is the regiasteactual code executed by workers to resolve a register request.
        It will be called by the _worker_thread function.
        """
        query = "Select createuser (%(username)s, %(password)s)" # TODO: to be replaced by query from dbms developement branch
        response = self.dbms.query(self.queue, job.job_tag, query, 
            {
             "username" : job.args["username"],
             "password" : job.args["password"]
            }
        )

        return job.job_tag

    def shutdown(self):
        # Shutdown the server
        # Kill the watchdog
        self.watchdog_signal = 1
        # Kill the worker threads
        for i in range(len(self.worker_signals)):
            self.worker_signals[i] = 1
        # Kill the DBMS connection
        self.dbms.close()
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



