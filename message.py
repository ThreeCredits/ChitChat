from typing import *


class PacketItem:
    """
    The PacketItem class is the standard item for the Packet class.
    """

    def __init__(self, type: str, data: Any):
        self.type = type
        self.data = data

    def __str__(self):
        return self.type + ": " + str(self.data)

    def __repr__(self):
        return self.__str__()


class Packet:
    """
    The packet class is a standard container for the server-client communications
    """

    def __init__(self, data: List[PacketItem]):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self):
            # We delete the index in order not to send it to the client (as it would be just adding useless data)
            del self._index
            raise StopIteration
        else:
            self._index += 1
            return self.data[self._index - 1]
