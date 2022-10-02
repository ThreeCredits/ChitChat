from cipher import *
import pickle

def sendCipheredMessage(message, client, cipher):
    message = pickle.dumps(message)
    message = cipher.encrypt(message)
    message = pickle.dumps(message)
    client.send(message)

def receiveCipheredMessage(message, client, cipher):
    message = client.recv(32 * 1024)
    message = pickle.loads(message)
    message = cipher.decrypt(*message)
    message = pickle.loads(message)
    return message

class Message():
    '''
    The message class is the carrier of all data between the client and the server.
    It is always sent in clear text.
    '''
    def __init__(self, data):
        self.data = data

class KeyMessage():
    '''
    The KeyMessage class is a message that is sent to/by the server to share a public key.
    '''
    def __init__(self, key):
        self.key = key

class PortMessage():
    '''
    The PortMessage class is a message that is sent by the server to indicate which port the client should connect to.
    '''
    def __init__(self, port):
        self.port = port

class LoginMessage():
    '''
    The LoginMessage class is a message that is sent by the client to the server to login.
    '''
    def __init__(self, username, password):
        self.username = username
        self.password = password

class TimeoutMessage():
    '''
    The TimeoutMessage class is a message that is sent by the server to the client to indicate that the user is timed out.
    '''
    def __init__(self, datetime):
        self.datetime = datetime

class InfoMessage():
    '''
    The InfoMessage class is a message that is sent by/to the server to/from the client to send information.
    '''
    def __init__(self, info):
        self.info = info

class KeepAliveMessage():
    '''
    The KeepAliveMessage class is a message that is sent by the client to the server to indicate that the client is still connected.
    '''
    def __init__(self):
        pass