# test run: pytest cipher_test.py --cov=cipher --cov-report=html
import json
import sys

sys.path.append('..')
from cipher import *
from identity import *


def test_serialize() -> Any:
    id = Identity()

    dict_ = {"test2": "ciao2", "test3": ["ciao3", "ciao4"]}
    packet_item = PacketItem("test2", dict_)
    packet = Packet([packet_item])

    msg = serialize(packet)
    msg = msg.encode()
    msg = id.encrypt(msg)
    msg = serialize_(msg)
    assert json.loads(msg)


def test_deserialize() -> Packet:
    id = Identity()

    dict_ = {"test2": "ciao2", "test3": ["ciao3", "ciao4"]}
    packet_item = PacketItem("test2", dict_)
    packet = Packet([packet_item])

    msg = serialize(packet)
    msg = msg.encode()
    msg = id.encrypt(msg)
    msg = serialize_(msg)
    msg = deserialize_(msg)
    msg = id.decrypt(msg[0], msg[1], msg[2], msg[3])
    msg = deserialize(msg.decode())
    assert type(msg) is Packet
    assert msg.data[0].data['test3'][1] == "ciao4"