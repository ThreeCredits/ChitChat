from typing import Tuple
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
        data, tag = cipher_aes.encrypt_and_digest(msg) # encrypt the message with session key, tag is the authentication tag
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
        return data