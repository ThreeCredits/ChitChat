from Crypto.PublicKey import RSA


class E2EE:
    def __init__(self) -> None:
        '''
        Generate a public/private key pair using 2048 bits key length
        :returns: None
        '''
        self.key = RSA.generate(2048)


    def get_private_key(self) -> RSA.RsaKey:
        ''' 
        Returns the private key
        :returns: Rsakey object
        '''
        key = RSA.import_key(self.key.exportKey('PEM'))
        return key


    def get_public_key(self) -> RSA.RsaKey:
        '''
        Returns the public key
        :returns: Rsakey object
        '''
        key = RSA.import_key(self.key.publickey().exportKey('PEM'))
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