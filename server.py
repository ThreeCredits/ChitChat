# We will use the reST syntax for documentation.

# The server.py file holds the main server logic.
# It is responsible for handling the connection between the client and the server.
# It will accept requests from the client and send them to the appropriate handler.
# It will also handle the connection to the internal database.

from distutils.log import info
import re
import socket           #For networking
import threading        #For multithreading
import sys              #For exiting the program
import os               #For file management
import json             #For JSON parsing and serialization
import pickle           #For pickling and unpickling
import time             #For time management
import hashlib          #For hashing (To be used in message verification)
import random           #For random number generation
import string           #For string generation
import base64           #For base64 encoding and decoding
import datetime         #For date and time management
import argparse
from tkinter import Y         #For parsing command line arguments
import yaml             #For parsing the config file

def getTimeString():
    """
    This method is responsible for generating a time string.
    """
    # Get the current time
    now = datetime.datetime.now()
    # Return the time as a string (YYYY-MM-DD HH:MM:SS::ms)
    return now.strftime("%Y-%m-%d %H:%M:%S")

def getConsoleTimeString():
    return "[" + getTimeString() + "]"

def consoleLog(msg, sender="Server"):
    """
    This method is responsible for logging messages to the console.
    """
    print("\r" + getConsoleTimeString() + " <" + sender + "> " + msg + "\n$ ", end="")

class Request():
    """
    This class is responsible for holding the request.
    """

    def __init__(self, type, data) -> None:
        # Init the request
        self.type = type
        self.data = data

    def __str__(self) -> str:
        # Return the request as a string
        return "Request: " + self.type + " " + self.data

class Response():
    """
    This class is responsible for holding the response.
    """

    def __init__(self, type, data) -> None:
        # Init the response
        self.type = type
        self.data = data

    def __str__(self) -> str:
        # Return the response as a string
        return "Response: " + self.type + " " + self.data

class ConnectionHandler():
    """
    This class is responsible for handling the connection between the client and the server.
    It will also be responsible for handling the request
    """

    def __init__(self, port, maxConnections, verbose) -> None:
        # Remember the port
        self.port = port
        # Remember the connection limit
        self.maxConnections = maxConnections
        # Init socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind to the port
        self.s.bind(('127.0.0.1', port))
        # Listen for incoming connections
        self.s.listen(maxConnections)
        # Init internal connection pool
        self.connectionPool = {} # indexed by connection id
        # Init verbose
        self.verbose = verbose
        # Init subThreads pool
        self.subThreads = []
        # Set the alive flag
        self.alive = True
        # Create the thread for waiting for connections
        self.thread = threading.Thread(target=self.waitForConnections, daemon=True)
        # Start the thread
        self.thread.start()


    def waitForConnections(self) -> None:
        """
        This method is responsible for waiting for incoming connections.
        It will create a new thread for each incoming connection.
        """
        while True:
            # Accept the connection
            conn, addr = self.s.accept()
            # If verbose, print the connection
            if self.verbose:
                consoleLog("Connection from: " + str(addr), self.thread.name)
            # Create a unique id for the connection
            connectionId = self.generateConnectionId()
            # If verbose, print the connection id
            if self.verbose:
                consoleLog("Connection id: " + connectionId, self.thread.name)
            # Add the connection to the pool
            self.connectionPool[connectionId] = (conn,addr)
            # Create a new thread for the connection
            self.subThreads.append(threading.Thread(target=self.handleConnection, args=(connectionId,), daemon=True))
            # Start the thread
            self.subThreads[-1].start()
            # If verbose, print notice
            if self.verbose:
                consoleLog("Connection accepted. Connection handler created.", self.thread.name)
    
    def generateConnectionId(self) -> str:
        """
        This method is responsible for generating a unique id for the connection.
        It will use the current time in milliseconds as the id, concatenated to 8 random nytes.
        """
        return str(int(round(time.time() * 1000))) + str(random.getrandbits(8 * 8))
    
    def handleConnection(self, connectionId) -> None:
        """
        This method is responsible for handling the connection.
        It will receive the request from the client, and send the response back.
        :param connectionId: The id of the connection
        """
        # If verbose, print notice
        if self.verbose:
            consoleLog("Connection handler started.", self.thread.name)
        # Get the connection
        conn, addr = self.connectionPool[connectionId]
        # Set the timeout to 10 minutes
        conn.settimeout(600)
        # Loop until the connection is closed
        while self.alive:
            try:
                # Receive the request
                request = self.receiveRequest(conn)
                # Process the request
                response = self.processRequest(request)
                # Send the response
                self.sendResponse(conn, response)
                # If the response is a disconnect, close the connection
                if response.type == "disconnect":
                    self.closeConnection(connectionId)
            except Exception as e:
                # If the request times out, close the connection
                if e == socket.timeout:
                    self.closeConnection(connectionId)
                    # If verbose, print notice
                    if self.verbose:
                        consoleLog("Connection " + str(connectionId) + " timed out.", self.thread.name)
                    break
                # If the host disconnected, close the connection
                else:
                    self.closeConnection(connectionId)
                    # If verbose, print notice
                    if self.verbose:
                        consoleLog("Connection " + str(connectionId) + " disconnected.", self.thread.name)
                    break
            # If verbose, print the request
            if self.verbose:
                consoleLog("Request received: " + str(request), self.thread.name)
        
    def receiveRequest(self, conn) -> dict:
        """
        This method is responsible for receiving the request from the client.
        :param conn: The connection to receive the request from
        :legacy: This method is legacy and will be removed in the future.
        """
        # Receive the request
        request = pickle.loads(conn.recv(1024))
        # Return the request
        return request
    
    def processRequest(self, request) -> dict:
        """
        This method is responsible for processing the request.
        :param request: The request to process
        :legacy: This method is legacy and will be removed in the future.
        """
        # Create a response (PLACEHOLDER)
        response = Response("msg", "You wrote " + request.data + "!")
        # Return the response
        return response
    
    def sendResponse(self, conn, response) -> None:
        """
        This method is responsible for sending the response to the client.
        :param conn: The connection to send the response to
        :param response: The response to send
        :legacy: This method is legacy and will be removed in the future.
        """
        # Send the response
        conn.send(pickle.dumps(response))
    
    def closeConnection(self, connectionId) -> None:
        """
        This method is responsible for closing the connection.
        :param connectionId: The id of the connection to close
        """
        # Get the connection
        conn, addr = self.connectionPool[connectionId]
        # Close the connection
        conn.close()
        # Remove the connection from the pool
        del self.connectionPool[connectionId]
        # If verbose, print notice
        if self.verbose:
            consoleLog("Connection " + str(connectionId) + " closed.", self.thread.name)
        # Terminate the thread
        self.subThreads.remove(threading.current_thread())
    
    def closeAllConnections(self) -> None:
        """
        This method is responsible for closing all connections.
        """
        # Loop through the connections
        for connectionId in self.connectionPool:
            # Close the connection
            self.closeConnection(connectionId)
        # If verbose, print notice
        if self.verbose:
            consoleLog("All connections closed.", self.thread.name)
    
    def close(self) -> None:
        """
        This method is responsible for closing the server.
        """
        # Close all connections
        self.closeAllConnections()
        # Close the socket
        self.s.close()
        # If verbose, print notice
        if self.verbose:
            consoleLog("Server closed.", self.thread.name)
        # Terminate the thread
        self.alive = False
        self.thread.join()                   

handlersPool = []

def commandHandler(command, args):
    """
    The commandHandler function handles the proper execution of command line commands.
    :param command: The command to parse
    :param args: The arguments to parse
    :returns int: The return code of the command
    """
    # We will support the following commands:
    #   - help : Print the help message
    #   - start <port> <maxConnections> [name] [verbose] : Add a new handler to the pool
    #   - stop <port> : Remove a handler from the pool by port
    #   - stopall : Remove all handlers from the pool
    #   - list [-noorder] : List all handlers in the pool
    #   - infoport [port] : Get information about a port
    #   - infohandler [port] : Get information about a handler
    #   - info : print the info table
    #   - generateConfigs : Generate the config files for the server with the default settings
    #   - exit : Exit the program
    # TODO: Add support for regex
    # TODO: Add following commands:
    #   - ipKick <ip> : Kick a user by ip
    #   - ipBan <ip> : Ban a user by ip
    #   - ipPardon <ip> : Unban a user by ip
    #   - userKick <user> : Kick a user by username
    #   - userBan <user> : Ban a user by username
    #   - userPardon <user> : Unban a user by username
    #   - userList : List all users

    # If the command is "help", print the help message
    if command == "help":
        print("\rAvailable commands:")
        print("  help")
        print("  start <port> <maxConnections> [verbose]")
        print("  stop <port>")
        print("  stopall")
        print("  list [-noorder]")
        print("  infoport [port]")
        print("  infohandler [port]")
        print("  info")
        return 0 # Return success

    # If the command is "start", add a new handler to the pool
    elif command == "start":
        # Check if we have the correct number of arguments
        if len(args) < 3 or len(args) > 5:
            print("\rError: Invalid number of arguments.")
            return -6 # Generic argument error return code
        # Get the port (must be an integer)
        try:
            port = int(args[0])
        except:
            print("\rError: Invalid port.")
            return -7 # Invalid argument return code
        # Get the max connections
        try:
            maxConnections = int(args[1])
        except:
            print("\rError: Invalid max connections.")
            return -7 # Invalid argument return code
        # TODO: add support for name
        # name = ""
        verbose = False
        # Get the verbose flag (must be a boolean)
        try:
            verbose = bool(args[2])
        except:
            print("\rError: Invalid verbose flag.")
            return -7 # Invalid argument return code
        try:
            handlersPool.append(ConnectionHandler(port, maxConnections, verbose))
        except:
            return -1 # Generic error return code
        return 0 # Return success

    # If the command is "stop", remove a handler from the pool by port
    elif command == "stop":
        # Check if we have the correct number of arguments
        if len(args) != 1:
            print("\rError: Invalid number of arguments.")
            return 1
        # Get the port (must be an integer)
        try:
            port = int(args[0])
        except:
            print("\rError: Invalid port.")
            return -7 # Invalid argument return code
        # Remove the handler from the pool
        try:
            # Search for the handler
            for handler in handlersPool:
                if handler.port == port:
                    # Close the handler
                    handler.close()
                    # Remove the handler from the pool
                    handlersPool.remove(handler)
                    return 0 # Return success
        except:
            return -1 # Generic error return code
        return 0
    # If the command is "stopall", remove all handlers from the pool
    elif command == "stopall":
        # Remove all handlers from the pool
        try:
            for handler in handlersPool:
                handler.close()
            handlersPool.clear()
        except:
            return -1 # Generic error return code
        return 0 # Return success
    # If the command is "list", list all handlers in the pool
    if command == "list":
        # Check if we have the correct number of arguments
        if len(args) != 1:
            print("\rError: Invalid number of arguments.")
            return -6 # Generic argument error return code
        # -noorder prints the pool
        if "-noorder" in args:
            print("Printing connection pool...")
            # Print the pool
            for handler in handlersPool:
                for connection in handler.connectionPool:
                    print("\r"+connection)
        # if no arguments are given, print the threads by handlers
        else:
            for handler in handlersPool:
                print("Handler " + str(handler.thread.name) + " id " + str(handler.thread.ident) +
                        "\t\t(" + str(len(handler.connectionPool)) + " connections)" + ":")
                for connection in handler.connectionPool:
                    print("\t" + connection)
        return 0 # Return success
    # If the command is "infoport", get information about a port
    elif command == "infoport":
        # Check if we have the correct number of arguments
        if len(args) != 1:
            print("Error: Invalid number of arguments.")
            return -6
        # Get the port (must be an integer)
        try:
            port = int(args[0])
        except:
            print("Error: Invalid port.")
            return -7
        # We will see if the port is open, occupied by a handler, or closed (denied access by the os)
        for handler in handlersPool:
            if handler.port == port:
                print("Port " + str(port) + " is occupied by handler " + str(handler.thread.name) + " id " + str(handler.thread.ident))
                return 0 # Return success
        # If we get here, the port is not occupied by one of the handlers
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("", port))
            s.close()
            print("Port " + str(port) + " is open")
            return 0 # Return success
        except:
            print("Port " + str(port) + " is unavailable")
        # If we get here, the port is not open
        print("Port is not open")
        return 0 # Return success
    # If the command is "infohandler", get information about a handler
    elif command == "infohandler":
        # Check if we have the correct number of arguments
        if len(args) != 1:
            print("Error: Invalid number of arguments.")
            return -6
        # Get the port (must be an integer)
        try:
            port = int(args[0])
        except:
            print("Error: Invalid port.")
            return -7
        # We will see if the port is open, occupied by a handler, or closed (denied access by the os)
        for handler in handlersPool:
            if handler.port == port:
                print("Handler " + str(handler.thread.name) + " id " + str(handler.thread.ident) +
                        "\t\t(" + str(len(handler.connectionPool)) + " connections)")
                return 0 # Return success
        # If we get here, the port is not occupied by one of the handlers
        print("No handler on port " + str(port) + " ( Maybe it wasn't launched because the port was closed? )")
        return 0 # Return success
    # If the command is "info", get information about the pool
    elif command == "info":
        # Print a table of the threads
        print(  "Handler".center(15)+ "|" +
                "Thread".center(15) + "|" +
                "Port".center(15)   + "|" +
                "Connections".center(15))
        print ("-"*(15) + "+" + ("-"*15) + "+" + ("-"*15) + "+" + ("-"*15))
        for handler in handlersPool:
            threadNameString = str(handler.thread.name)
            threadIdString = str(handler.thread.ident)
            threadPortString = str(handler.port)
            threadConnectionsString = str(len(handler.connectionPool)) + "/" + str(handler.maxConnections)
            # Add the indents ( default 15 characters per tab )
            threadNameString = threadNameString.center(15)
            threadIdString = threadIdString.center(15)
            threadPortString = threadPortString.center(15)
            threadConnectionsString = threadConnectionsString.center(15)
            # Print the table
            print(threadNameString+"|"+threadIdString+"|"+threadPortString+"|"+threadConnectionsString)
        return 0 # Return success
    # If the command is "generateConfigs", generate a config file with the default values
    elif command == "generateConfigs":
        configs = defaultConfigs()
        # Open the config file
        with open("configs.yaml", "w") as f:
            # Get default configs
            configs = defaultConfigs()
            # Write the configs
            for config in configs:
                f.write(config + ": " + str(configs[config]) + "\n")
            # Close the file
            f.close()
        return 0 # Return success
    # If the command is "exit", exit the program
    elif command == "exit":
        print("Exiting...")
        sys.exit(0)
    # If the command is not recognized, return an error
    else:
        print("Error: Command not recognized.")
        return -5 # Command not recognized error return code
    
def main(handlersNumber, portRange, maxConnections, verbose):
    """
    This method is responsible for starting the server.
    :param handlersNumber: The number of handlers to create.
    :param portRange: The port range to use.
    :param maxConnections: The maximum number of connections per handler.
    :param verbose: Whether to print the logs.
    """
    # Init the server
    for i in range(handlersNumber):
        # Create a new handler
        try:
            handlersPool.append(ConnectionHandler(portRange[i], maxConnections, verbose))
        except Exception as e:
            # If verbose, print the error
            if verbose:
                consoleLog("Couldn't create handler on port " + str(i) + " , skipping it...")

    # Wait for the user to exit
    while True:
        # Get input from the user
        cmd = input("$ ")
        # split the input into a command and its arguments
        split = cmd.split(" ")
        cmd = split[0]
        args = split[1:]
        # Execute the command
        exitCode = commandHandler(cmd, args)
        # If verbose, print the exit code
        if verbose:
            print("\rCommand Exit code: " + str(exitCode) + "\n")

def loadArgs():
    """
    The loadArgs function loads the arguments from the command line.
    :return args: The arguments loaded from the command line.
    """
    # Get the command line arguments
    parser = argparse.ArgumentParser(description="A server for the chat application.")
    parser.add_argument("-n", "--handlers", type=int, default=1, help="The number of handlers to create.")
    parser.add_argument("-p", "--port", type=int, default=5556, help="The first port to use.")
    parser.add_argument("-m", "--max", type=int, default=10, help="The maximum number of connections per handler.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to print the logs.")
    parser.add_argument("-y", "--yaml", type=str, default="configs.yaml", help="The path to the config file.")
    return parser.parse_args()

def defaultConfigs():
    return {
        "handlers": 1,
        "port": 5556,
        "max": 10,
        "verbose": False
    }

    
if __name__ == "__main__":

    # Load the arguments 
    args = loadArgs()
    
    # We create a dictionary of the config
    configs = {}

    # If the yaml file is provided and exists, load it
    if os.path.isfile(args.yaml):
        with open(args.yaml, "r") as f:
            # Load the file
            configsFile = yaml.load(f, Loader=yaml.FullLoader)
            # Add the configs to the configs dictionary
            for key in configsFile:
                configs[key] = configsFile[key]
            # Print the loaded configs
            print("Loaded configs:")
            for key in configs:
                print(key + ":",configs[key], type(configs[key]))
    # If the yaml file is not provided, use the default configs and warn the user
    else:
        print("No config file provided, using default configs...")
        print("To generate the config file, run the following command:")
        print("generateConfigs <path to config file>")
        # Add the default configs to the configs dictionary
        configs = defaultConfigs()
        # Print the loaded configs
        print("Loaded configs:")
        for key in configs:
            print("\t" + key + ":", configs[key])

    # Start the server
    try:
        main(
            configs["handlers"],
            [configs["port"] + i for i in range(configs["handlers"])],
            configs["max"],
            configs["verbose"]
            )
    except KeyError as e:   
        # Close the previous config file
        f.close()
        # If the config file is invalid, print the missing settings and exit
        print("Invalid config file, missing setting " + str(e))
        # Ask the user if he wants to recreate the config file
        print("Create a new config file? (y/n)")
        # Get the answer
        answer = input("$ ")
        # If the answer is yes, create the config file
        if answer == "y":
            # Ask the user for the file name
            print("Enter the file name:")
            # Get the file name
            fileName = input("$ ")
            # Create the file
            with open(fileName, "w") as f:
                # Load default config
                configs = {
                    "handlers": 1,
                    "port": 5556,
                    "max": 10,
                    "verbose": True,
                }
                # Write the config to the file
                yaml.dump(configs, f)
            # Cue the user to edit the file
            print("Edit the configuration file and run the program again.")
        # Exit the program
        sys.exit()

    
