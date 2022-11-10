import struct
from typing import Tuple, Any
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from datetime import datetime
from message import*
import base64
import json


def serialize_(obj: Any) -> Any:
    obj = list(obj)
    for i in range(len(obj)):
        obj[i] = base64.b64encode(obj[i]).decode('ascii')
    obj = tuple(obj)
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def serialize(obj: Packet) -> str:
    for i in range(obj.data.__len__()):
        if isinstance(obj.data[i].data, datetime):
            obj.data[i].data = 'datetime'+obj.data[i].data.isoformat()
        elif isinstance(obj.data[i].data, list) or isinstance(obj.data[i].data, tuple):
            for j in range(obj.data[i].data.__len__()):
                if isinstance(obj.data[i].data[j], datetime):
                    obj.data[i].data[j] = 'datetime'+obj.data[i].data[j].isoformat()
        elif isinstance(obj.data[i].data, dict):
            for key, value in obj.data[i].data.items():
                if isinstance(value, datetime):
                    obj.data[i].data[key] = 'datetime'+value.isoformat()

    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def deserialize_(obj: Any) -> Any:
    obj = json.loads(obj)
    obj = list(obj)
    for i in range(len(obj)):
        obj[i] = base64.b64decode(obj[i])
    return tuple(obj)


def deserialize(obj: str) -> Packet:
    obj_ = json.loads(obj)
    items = []
    for i in range(obj_['data'].__len__()):
        type_ = obj_['data'][i]['type']
        data = obj_['data'][i]['data']
        if isinstance(data, list) or isinstance(data, tuple):
            for i in range(data.__len__()):
                if isinstance(data[i], str):
                    if data[i].startswith('datetime'):
                        data[i] = datetime.fromisoformat(data[i][8:])
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    if value.startswith('datetime'):
                        data[key] = datetime.fromisoformat(value[8:])
        else:
            if isinstance(data, str):
                if data.startswith('datetime'):
                    data = datetime.fromisoformat(data[8:])

        items.append(PacketItem(type_, data))

    return Packet(items)


def send_ciphered_message(message: Packet, client, identity) -> None:
    message = serialize(message)
    message = message.encode()
    message = identity.encrypt(message)
    message = serialize_(message)
    # Prefix each message with a 4-byte length (network byte order)
    message = struct.pack('>I', len(message)) + message
    client.send(message)


def receive_all(client, length):
    data = bytearray()
    while len(data) < length:
        packet = client.recv(length - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def _receive_chipered_message(client):
    # Read message length and unpack it into an integer
    try:
        raw_msglen = receive_all(client, 4)
        if not raw_msglen:
            raise Exception("Missing message length header")
    except:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return receive_all(client, msglen)


def receive_ciphered_message(client, identity):
    # Receive a large message, which may have been split into multiple packets
    message = _receive_chipered_message(client)
    message = deserialize_(message)
    message = identity.decrypt(*message)
    message = message.decode()
    message = deserialize(message)
    return message


class Cipher:
    def encrypt(pub_key: RSA.RsaKey, msg: str) -> Tuple[bytes, bytes, bytes, bytes]:
        '''
        Encrypts the message using AES-256-GCM
        :param pub_key: The public key to be used for encryption
        :param msg: The message to be encrypted
        :returns: returns a the encrypted message, the encrypted session key, the authentication tag, and the nonce
        '''
        cipher_rsa = PKCS1_OAEP.new(pub_key)
        session_key = get_random_bytes(32) # encryption key for AES
        enc_session_key = cipher_rsa.encrypt(session_key) # session key encrypted with public key
        cipher_aes = AES.new(session_key, AES.MODE_GCM)
        data, tag = cipher_aes.encrypt_and_digest(msg) # encrypt the message with session key, tag is the authentication tag
        data_base64 = base64.b64encode(data) # base64 encode the encrypted message
        return data_base64, enc_session_key, tag, cipher_aes.nonce


    def decrypt(prv_key: RSA.RsaKey, msg: bytes, enc_session_key: bytes, tag: bytes, nonce: bytes) -> str:
        '''
        Decrypts the message using AES-256-GCM
        :param prv_key: The private key to be used for decryption
        :param msg: The message to be decrypted
        :param enc_session_key: The encrypted session key
        :param tag: The authentication tag
        :param nonce: The nonce
        :returns: returns the decrypted message (str)
        '''
        cipher_rsa = PKCS1_OAEP.new(prv_key)
        session_key = cipher_rsa.decrypt(enc_session_key) # session key decrypted with private key
        cipher_aes = AES.new(session_key, AES.MODE_GCM, nonce)
        data = cipher_aes.decrypt_and_verify(base64.b64decode(msg), tag) # decrypt the message with session key, tag is the authentication tag
        return data