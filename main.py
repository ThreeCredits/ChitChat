from e2ee import E2EE
from network import Network


def get_keys(obj: E2EE):
    private_key, public_key = obj.get_private_key(), obj.get_public_key()
    keys = {
        "private_key": private_key, 
        "public_key": public_key
    }
    return dict(keys)


user1 = E2EE()
user2 = E2EE()

net = Network()

user1Keys = user1.get_keys()
user2Keys = user2.get_keys()

print(f'user1 keys:\n {user1Keys}\n\nuser2 keys:\n {user2Keys}')

msg = "no way it works! am not a virus, am a dolphin"

encmsg, enc_session_key, tag, nonce = net.encrypt(msg, user2Keys["public_key"])
print("\necnmsg: \n{}\n".format(encmsg))

decmsg = net.decrypt(encmsg, user2Keys["private_key"], enc_session_key, tag, nonce)

print("decmsg: \n{}\n".format(decmsg))