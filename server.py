# We will use the reST syntax for documentation.

# The server.py file holds the main server logic.
# It is responsible for handling the connection between the client and the server.
# It will accept requests from the client and send them to the appropriate handler.
# It will also handle the connection to the internal database.

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
import argparse         #For parsing command line arguments

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
        """
        # If verbose, print notice
        if self.verbose:
            consoleLog("Connection handler started.", self.thread.name)
        # Get the connection
        conn, addr = self.connectionPool[connectionId]
        # Set the timeout to 10 minutes
        conn.settimeout(600)
        # Loop until the connection is closed
        while True:
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
        """
        # Receive the request
        request = pickle.loads(conn.recv(1024))
        # Return the request
        return request
    
    def processRequest(self, request) -> dict:
        """
        This method is responsible for processing the request.
        """
        # Create a response (PLACEHOLDER)
        response = Response("msg", "You wrote " + request.data + "!")
        # Return the response
        return response
    
    def sendResponse(self, conn, response) -> None:
        """
        This method is responsible for sending the response to the client.
        """
        # Send the response
        conn.send(pickle.dumps(response))
    
    def closeConnection(self, connectionId) -> None:
        """
        This method is responsible for closing the connection.
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

handlersPool = []

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
        # If the user wants to exit, exit the program
        if cmd == "exit":
            consoleLog("Exiting...")
            # Exit the program (threads are daemon threads, so they will automatically exit)
            sys.exit()
        # If the user wants to print the list of connections, print it
        elif cmd[0:4] == "list":
            # -noorder prints the pool
            if "-noorder" in cmd:
                print("Printing connection pool...")
                # Print the pool
                for handler in handlersPool:
                    for connection in handler.connectionPool:
                        print("\r"+connection)
            # if no arguments are given, print the threads by handlers
            else:
                for handler in handlersPool:
                    print("Handler " + str(handler.thread.name) + " id " + str(handler.thread.ident) + "\t\t(" + str(len(handler.connectionPool)) + " connections)" + ":")
                    for connection in handler.connectionPool:
                        print("\t" + connection)
        elif cmd[0:4] == "info":
            # Print a table of the threads
            print(  "Handler".center(15)+ "|" +
                    "Thread".center(15) + "|" +
                    "Port".center(15)   + "|" +
                    "Connections".center(15))
            print ("-"*(63))
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
    

    
if __name__ == "__main__":
    # Get the command line arguments
    parser = argparse.ArgumentParser(description="A server for the chat application.")
    parser.add_argument("-n", "--handlers", type=int, default=1, help="The number of handlers to create.")
    parser.add_argument("-p", "--port", type=int, default=5556, help="The first port to use.")
    parser.add_argument("-m", "--max", type=int, default=10, help="The maximum number of connections per handler.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to print the logs.")
    args = parser.parse_args()
    # Start the server
    main(args.handlers, [args.port + i for i in range(args.handlers)], args.max, args.verbose)
    
