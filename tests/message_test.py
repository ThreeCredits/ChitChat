import sys
sys.path.append("..")
from message import Packet, PacketItem

# Unit test for the PacketItem class
def packet_item():
    item = PacketItem("test", 1)
    assert item.type == "test"
    assert item.data == 1
    assert str(item) == "test: 1"
    assert repr(item) == "test: 1"

    item = PacketItem("packet", "testdatatest")
    assert item.type == "packet"
    assert item.data == "testdatatest"
    assert str(item) == "packet: testdatatest"
    assert repr(item) == "packet: testdatatest"

    item = PacketItem("test", [1, 2, 3, 4, 5])
    assert item.type == "test"
    assert item.data == [1, 2, 3, 4, 5]
    assert str(item) == "test: [1, 2, 3, 4, 5]"
    assert repr(item) == "test: [1, 2, 3, 4, 5]"
    
    item = PacketItem("test", {"test": 1, "test2": 2})
    assert item.type == "test"
    assert item.data == {"test": 1, "test2": 2}
    assert str(item) == "test: {'test': 1, 'test2': 2}"
    assert repr(item) == "test: {'test': 1, 'test2': 2}"

# Unit test for the Packet class
def packet():
    packet = Packet()
    assert len(packet) == 0
    packet.append(PacketItem("test", 1))
    assert len(packet) == 1
    packet.clear()
    assert len(packet) == 0

    packet = Packet([PacketItem("test", 1), PacketItem("test2", 2)])
    assert len(packet) == 2
    assert packet[0].type == "test"
    assert packet[0].data == 1
    assert packet[1].type == "test2"
    assert packet[1].data == 2
    for item in packet:
        assert isinstance(item, PacketItem)
    packet.append(PacketItem("test3", 3))
    assert len(packet) == 3
    packet.clear()
    assert len(packet) == 0
    
    packet = Packet([PacketItem("test", {"test": 1, "test2": 2}), PacketItem("test2", [1, 2, 3, 4, 5])])
    assert len(packet) == 2
    assert packet[0].type == "test"
    assert packet[0].data == {"test": 1, "test2": 2}
    assert packet[1].type == "test2"
    assert packet[1].data == [1, 2, 3, 4, 5]
    for item in packet:
        assert isinstance(item, PacketItem)
    packet.append(PacketItem("test3", 3))
    assert len(packet) == 3
    packet.clear()
    assert len(packet) == 0
    

