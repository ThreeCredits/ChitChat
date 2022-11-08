from ast import Bytes
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from cipher import Cipher
import platform
import os


class Identity:
    def __init__(self, pub_bytes : bytes = None) -> None:
        '''
        Generate a public/private key pair using 2048 bits key length
        :returns: None
        '''
        # If pub_bytes is None, then we are creating / loading a complete identity (with private key)
        if pub_bytes is None:
            # Check if a key already exists in .keys/self.pem
            if os.path.isfile(f'.keys/self.pem'):
                # Load
                self.keys = self.load_keys_from_file()
            else:
                # Create
                self.keys = RSA.generate(2048)
                # Write to '.keys/self.pem'
                # Check if the directory exists
                if not os.path.isdir('.keys'):
                    os.mkdir('.keys')
                    # Hide the directory on Windows
                    if platform.system() == 'Windows':
                        os.system('attrib +H .keys')
                # Write the key
                self.export_private_key()

        else:
            self.keys = RSA.import_key(pub_bytes)
    
    def has_private(self) -> bool:
        '''
        Checks if the key is complete
        :returns: bool
        '''
        return self.keys.has_private()

    def load_keys_from_file(self, UID : str = "self") -> RSA.RsaKey:
        '''
        Imports private and public keys to a file
        :param file_name: The name of the file
        :returns: RSA.RsaKey
        '''
        with open(f'.keys/{UID}.pem', 'r') as f:
            keys = RSA.import_key(f.read())
        return keys

    def load_pub_key_from_bytes(self, keystr: bytes) -> None:
        '''
        Imports private and public keys from bytes
        :param keystr: The bytes to be imported
        :returns: None
        '''
        self.pub_key = RSA.import_key(keystr)

    def export_private_key(self, UID: str = "self") -> None:
        '''
        Exports private key to a file
        :param UID: User's unique ID
        :returns: None
        '''
        with open(f'.keys/{UID}.pem', 'wb') as f:
            f.write(self.keys.exportKey('PEM'))

    def export_public_key(self, UID: str = "self") -> None:
        '''
        Exports public key to a file
        :param UID: User's unique ID
        :returns: None
        '''
        with open(f'.keys/{UID}.pub', 'wb') as f:
            f.write(self.keys.publickey().exportKey('PEM'))
    
    def export_public_key_bytes(self) -> bytes:
        '''
        Returns the public key as bytes
        :returns: bytes
        '''
        return self.get_public_key().export_key('PEM')

    def get_private_key(self) -> RSA.RsaKey:
        ''' 
        Returns the private key
        :returns: Rsakey object
        '''
        return self.keys

    def get_public_key(self) -> RSA.RsaKey:
        '''
        Returns the public key
        :returns: Rsakey object
        '''
        return self.keys.publickey()

    def get_keys(self) -> dict:
        '''
        Returns a dictionary with the private and public keys
        :returns: dict object
        '''
        private_key, public_key = self.get_private_key(), self.get_public_key()
        keys = {
            "private_key": private_key,
            "public_key": public_key
        }
        return dict(keys)

    def encrypt(self, msg: str) -> bytes:
        '''
        Encrypts the message using AES-256-GCM
        :param msg: The message to be encrypted
        :returns: returns the encrypted message, the encrypted session key, the authentication tag, and the nonce
        :legacy: to be removed
        '''
        return Cipher.encrypt(self.get_public_key(), msg)

    def decrypt(self, msg: bytes, enc_session_key: bytes, tag: bytes, nonce: bytes) -> str:
        '''
        Decrypts the message using AES-256-GCM
        :param msg: The message to be decrypted
        :param enc_session_key: The encrypted session key
        :param tag: The authentication tag
        :param nonce: The nonce
        :returns: returns the decrypted message (str)
        :legacy: to be removed
        '''
        if self.has_private():
            return Cipher.decrypt(self.get_private_key(), msg, enc_session_key, tag, nonce)
        else:
            raise Exception('Trying to decrypt with a public key')
