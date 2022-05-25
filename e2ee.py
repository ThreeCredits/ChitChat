from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import os


class E2EE:
    def __init__(self) -> None:
        '''
        Generate a public/private key pair using 2048 bits key length
        :returns: None
        '''
        self.key = RSA.generate(2048) # generate a key pair
        self.dir = '.' + get_random_bytes(16).hex() # create a directory with a random name
        os.makedirs(self.dir) # create a directory with the random name
        self.export_keys('keys') # export the keys as files
    

    def export_keys(self, file_name: str) -> None:
        '''
        Exports the private and public keys to a file
        :param file_name: The name of the file
        :returns: None
        '''
        with open(f'{self.dir}/{file_name}', 'wb') as f:
            f.write(self.key.exportKey('PEM'))

        with open(f'{self.dir}/{file_name}.pub', 'wb') as f:
            f.write(self.key.publickey().exportKey('PEM'))


    def get_private_key(self) -> RSA.RsaKey:
        ''' 
        Returns the private key
        :returns: Rsakey object
        '''
        with open(f'{self.dir}/keys', 'rb') as f:
            key = RSA.import_key(f.read())
        return key


    def get_public_key(self) -> RSA.RsaKey:
        '''
        Returns the public key
        :returns: Rsakey object
        '''
        with open(f'{self.dir}/keys.pub', 'rb') as f:
            key = RSA.import_key(f.read())
        return key


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
