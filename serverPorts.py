import socket
import threading
import pickle
import datetime
from message import *

# Two classes:
# KeyExchanger : Binds to one port, accepts all incoming connections, used for public e2e keys sharing
# ClientSocket : Used to communicate with a client.

class KeyExchanger:
    def __init__(self, port: int = 5556, max_connections: int = 25, server: Server = None):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('127.0.0.1', port))
        self.socket.listen(max_connections)
        self.server = server
        self.public_key = server.public_key

    def run(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
    
    def _run(self):
        while True:
            client, address = self.socket.accept()
            self.server.printv("New connection from: " + str(address), level = 2)
            # Create a new thread to handle the exchange
            thread = threading.Thread(target=self._exchange, args=(client, address))
            thread.start()
    
    def _exchange(self, client, address):
        # First, we send our public key
        client.send(pickle.dumps(KeyMessage(self.public_key)))
        # Then, we wait for the client's public key
        message = client.recv(32 * 1024)
        # We unpickle the message
        message = pickle.loads(message)
        # We expect a KeyMessage
        if not isinstance(message, KeyMessage):
            self.server.printv("Invalid message received from " + str(address), level = 1)
        else:
            # We add the client to the list of clients
            self.server.key_master.add_client(address, message.key)
            # We send a message to the client to tell him what port he should connect to
            client_socket = self.server.request_port()
            # Send ciphered message
            sendCipheredMessage(PortMessage(client_socket.port), client, self.server.key_master.cipher_of(address))
            # Now that we sent the port, we can close the connection and start the client socket
            client_socket.run()
        # We close the connection
        client.close()
        return

class ClientSocket:
    def __init__(self, address: tuple, port: int = 5556, server: Server = None):
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))
        self.server = server
        self.server_key = self.server.public_key
        self.client_key = self.server.key_master.cipher_of(address)
        # If the client key is not known, we close the connection (possible DoS)
        if self.client_key is None:
            self.socket.close()
            raise Exception("Unknown client key")
        
    def run(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        # Set timeout to 15 seconds just for the login
        self.socket.settimeout(15)
        login = None
        # We check if the login is valid. We give a maximum of 3 tries.
        while not login or not login.timeout > datetime.now():
            # We wait for the client to send a login message
            message = receiveCipheredMessage(self.socket, self.client_key)
            # We expect a LoginMessage
            if not isinstance(message, LoginMessage):
                self.server.printv("Invalid message received from " + str(self.address), level = 1)
                self.socket.close()
                return
            # We check if the login is valid
            login = self.server.login(message.username, message.password)
            if login is not None:
                if login.timeout > datetime.now():
                    # We send a message to the client to tell him that he is in timeout
                    sendCipheredMessage(TimeoutMessage(login.timeout), self.socket, self.client_key)
                    login = None
                else:
                    # If it is, we send a success message
                    sendCipheredMessage(InfoMessage("logged:"+login.nick), self.socket, self.client_key)
                break
            else:
                # If not, we send a failure message
                sendCipheredMessage(InfoMessage("login failed"), self.socket, self.client_key)
        
        # If the login is still None, it means that the login failed 3 times or we are in timeout
        if login is None:
            # We close the connection
            self.socket.close()
            return
        
        # Else, we set the timeout to 60 seconds.
        self.socket.settimeout(60)
        # Now, we have two functions to absolve:
        # 1. Send messages to the client when the server puts a message in the queue
        # 2. Receive messages from the client and put them in the queue
        # We create two threads to do that. Note that if the client disconnects, the threads must stop.
        self.send_thread = threading.Thread(target=self._send, args=(login,))
        self.send_thread.start()
        self.receive_thread = threading.Thread(target=self._receive, args=(login,))
        self.receive_thread.start()
        # Return to the main thread
        return # The threads will continue to run in the background, and will stop when the client disconnects, since it will raise an exception

    def _send(self, login):
        while True:
            # We wait for a message to be put in the queue
            message = self.server.queue.of(login).get()
            # We send the message to the client
            sendCipheredMessage(message, self.socket, self.client_key)
            # We confirm that the message has been sent
            self.server.queue.of(login).task_done()
    
    def _receive(self, login):
        while True:
            # We wait for a message from the client
            message = receiveCipheredMessage(self.socket, self.client_key)
            # If message is just a keepalive, we ignore it
            if isinstance(message, KeepAliveMessage):
                continue
            # We send the message to the server
            self.server.main_queue.put((login, message))