# CONSIDER REMOVING THIS FILE
import socket
from typing import Any
from Crypto.PublicKey import RSA
from cipher import Cipher


class Network:
    def __init__(self, server: str = "127.0.0.1", port: int = 5556) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket
        self.server = server # address of server
        self.port = port # port of server
        self.addr = (self.server, self.port)
        self.connect() # connect to server

    
    def connect(self) -> None:
        '''
        Creates a connection to the server
        :returns: None
        '''
        self.client.connect(self.addr) # starts new connection


    def send_with_response(self, data, buffer_size: int = 2048*16) -> bytes:
        '''
        Sends the data to the server and returns the response
        :param data: The data to be sent
        :param buffer_size: The buffer size
        :returns: returns the response of the server
        '''
        try:
            self.client.send(data)
            return self.client.recv(buffer_size)
        except socket.error as e:
            print("ERROR IN SEND",e)


    def send(self, data: Any) -> None:
        '''
        Sends the data to the server without returning a response
        :param data: The data to be sent
        :returns: None
        '''
        try:
            self.client.send(data)
        except: pass
    

    def send_EE_response(self, data: Any, key: RSA.RsaKey, buffer_size: int = 2048*16) -> bytes:
        '''
        Sends the encrypted data to the server and returns the response
        :param data: The data to be sent
        :param key: The key to encrypt the data with (public key)
        :param buffer_size: The buffer size
        :returns: returns the response of the server
        '''
        try:
            self.client.send(self.encrypt(data, key))
            return self.client.recv(buffer_size)
        except socket.error as e:
            print("ERROR IN SEND",e)


    def send_EE(self, data: Any, key: RSA.RsaKey) -> None:
        '''
        Sends the encrypted data to the server without returning a response
        :param data: The data to be sent
        :param key: The key to encrypt the data with (public key)
        :returns: None
        '''
        try:
            self.client.send(self.encrypt(data, key))
        except: pass
    

    def receive(self, buffer_size: int = 2048*16) -> bytes:
        '''
        Returns the data received from the server
        :param buffer_size: The buffer size
        :returns: returns the data received from the server
        '''
        return self.client.recv(buffer_size)


    def receive_EE(self, key: RSA.RsaKey, buffer_size: int = 2048*16) -> str:
        '''
        Returns the decrypted data received from the server
        :param key: The key to decrypt the data with (private key)
        :param buffer_size: The buffer size
        :returns: returns the decrypted data received from the server
        '''
        return self.decrypt(self.client.recv(buffer_size), key)