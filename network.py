import socket
from typing import Any, Tuple
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import base64

class Cipher:
    def __init__(self, pub_key: None, prv_key: None) -> None:
        '''
        pub_key and prv_key are RSA.RsaKey objects
        :returns: None
        '''
        self.pub_key = pub_key
        self.prv_key = prv_key


    def encrypt(self, msg: str) -> Tuple[bytes, bytes, bytes, bytes]:
        '''
        Encrypts the message using AES-256-GCM
        :param msg: The message to be encrypted
        :returns: returns a the encrypted message, the encrypted session key, the authentication tag, and the nonce
        '''
        cipher_rsa = PKCS1_OAEP.new(self.pub_key)
        session_key = get_random_bytes(32) # encryption key for AES
        enc_session_key = cipher_rsa.encrypt(session_key) # session key encrypted with public key
        cipher_aes = AES.new(session_key, AES.MODE_GCM)
        data, tag = cipher_aes.encrypt_and_digest(str(msg).encode('utf-8')) # encrypt the message with session key, tag is the authentication tag
        data_base64 = base64.b64encode(data) # base64 encode the encrypted message
        return data_base64, enc_session_key, tag, cipher_aes.nonce


    def decrypt(self, msg: bytes, enc_session_key: bytes, tag: bytes, nonce: bytes) -> str:
        '''
        Decrypts the message using AES-256-GCM
        :param msg: The message to be decrypted
        :param enc_session_key: The encrypted session key
        :param tag: The authentication tag
        :param nonce: The nonce
        :returns: returns the decrypted message (str)
        '''
        cipher_rsa = PKCS1_OAEP.new(self.prv_key)
        session_key = cipher_rsa.decrypt(enc_session_key) # session key decrypted with private key
        cipher_aes = AES.new(session_key, AES.MODE_GCM, nonce)
        data = cipher_aes.decrypt_and_verify(base64.b64decode(msg), tag) # decrypt the message with session key, tag is the authentication tag
        return data.decode('utf-8')


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


    def encrypt(self, msg: str, key: RSA.RsaKey) -> bytes:
        '''
        Encrypts the message using AES-256-GCM
        :param msg: The message to be encrypted
        :param key: The key to encrypt the message with (public key)
        :returns: returns the encrypted message, the encrypted session key, the authentication tag, and the nonce
        '''
        cipher = Cipher(key, None)
        return cipher.encrypt(msg)


    def decrypt(self, msg: bytes, key: RSA.RsaKey, enc_session_key: bytes, tag: bytes, nonce: bytes) -> str:
        '''
        Decrypts the message using AES-256-GCM
        :param msg: The message to be decrypted
        :param key: The key to decrypt the message with (private key)
        :param enc_session_key: The encrypted session key
        :param tag: The authentication tag
        :param nonce: The nonce
        :returns: returns the decrypted message (str)
        '''
        cipher = Cipher(None, key)
        return cipher.decrypt(msg, enc_session_key, tag, nonce)


    def sendWithResponse(self, data, buffer_size: int = 2048*16) -> bytes:
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
    

    def sendEEResponse(self, data: Any, key: RSA.RsaKey, buffer_size: int = 2048*16) -> bytes:
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


    def sendEE(self, data: Any, key: RSA.RsaKey) -> None:
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


    def receiveEE(self, key: RSA.RsaKey, buffer_size: int = 2048*16) -> str:
        '''
        Returns the decrypted data received from the server
        :param key: The key to decrypt the data with (private key)
        :param buffer_size: The buffer size
        :returns: returns the decrypted data received from the server
        '''
        return self.decrypt(self.client.recv(buffer_size), key)