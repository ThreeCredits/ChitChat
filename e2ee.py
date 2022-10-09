from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import platform
import os


class E2EE:
    def __init__(self, name = None) -> None:
        '''
        Generate a public/private key pair using 2048 bits key length
        :returns: None
        '''
        if name is None:
            self.keys = RSA.generate(2048) # generate a key pair
            self.dir = '.' + get_random_bytes(16).hex() # create a directory with a random name
            os.makedirs(self.dir) # create a directory with the random name
            if platform.system() == 'Windows':
                os.system(f'attrib +h {self.dir}') # hide the directory
            
            with open(f'{self.dir}/keys.pem', 'wb') as f: # export keys as PEM file
                f.write(self.keys.export_key('PEM'))
        else:
            self.dir = '.' + name
            self.keys = self.load_keys_from_file()

    
    def load_keys_from_file(self) -> RSA.RsaKey:
        '''
        Imports private and public keys to a file
        :param file_name: The name of the file
        :returns: None
        '''
        with open(f'{self.dir}/keys.pem', 'r') as f:
            keys = RSA.import_key(f.read())
        return keys

    
    def export_public_key(self, UID: str) -> None:
        '''
        Exports public key to a file
        :param UID: User's unique ID
        :returns: None
        '''
        with open(f'{self.dir}/{UID}.pub', 'wb') as f:
            f.write(self.keys.publickey().exportKey('PEM'))


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
