import datetime, time
from typing import Tuple, Any, List

class Chat:
    pass

class ChatMessage:
    pass

class ChatMessage:
    def __init__(self, number:int, author: Tuple[str, int, int], date: datetime.datetime, content: Any) -> None:
        self.number = number
        self.author = author
        self.date = date
        self.content = content
        

class Chat:
    def __init__(self, id: int, chat_name: str, description: str, creation_date: datetime.datetime, users: List[Tuple[str, int, int]] = [])-> None:
        self.id = id
        self.chat_name = chat_name
        self.description = description
        self.users = users
        self.messages = []

    
    def update(self, chat_name: str, description: str, users: List[Tuple[str, int, int]]):
        self.chat_name = chat_name
        self.description = description
        self.users = users


    def _append_message(self, msg_number: int , l: int, r: int) -> int:
        if l == r:
            return l
        p = (l + r)//2
        if msg_number > self.messages[p].number:
            return self._append_message(msg_number, p + 1, r)
        else:
            return self._append_message(msg_number, l, p)


    def append_message(self, msg: ChatMessage) -> None: #TODO
        self.messages.append(msg)
        return
        self.messages.insert(self._append_message(msg.number, 0, len(self.messages - 1)), msg)

