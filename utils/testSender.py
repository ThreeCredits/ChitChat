#This simple script asks for a port, connects to it, and sends a message.
import socket
import sys
import os
import json
import pickle


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

def main():
    # Ask for a port
    port = input("Please enter a port: ")
    # Create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the port
    s.connect(('127.0.0.1', int(port)))
    msg = ""
    while msg != "exit":
        # Ask for a message
        msg = input("Please enter a message: ")
        # Send the message
        s.send(pickle.dumps(Request("message", msg)))
        # Receive the response
        # response = pickle.loads(s.recv(1024))
        # Print the response
        # print(response.data)

if __name__ == "__main__":
    main()

