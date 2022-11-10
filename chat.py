import datetime, time
from typing import Tuple, Any, List

class Chat:
    pass

class ChatMessage:
    pass

class ChatMessage:
    def __init__(self, number:int, author: Tuple[str, int, int], date: datetime.datetime, content: Any) -> None:
        self.number: int = number
        self.author: List[Tuple[str, int, int]] = author
        self.date: datetime.datetime = date
        self.content: Any = content
        

class Chat:
    def __init__(self, id: int, chat_name: str, description: str, creation_date: datetime.datetime, users: List[Tuple[str, int, int]] = [])-> None:
        self.id: int = id
        self.chat_name: str = chat_name
        self.description: str = description
        self.users: List[Tuple[str, int, int]] = users
        self.messages: List[ChatMessage] = []

    
    def update(self, chat_name: str, description: str, users: List[Tuple[str, int, int]]):
        self.chat_name = chat_name
        self.description = description
        self.users = users


    def _append_message(self, msg_number: int) -> int:
        i = 0
        while i < len(self.messages) and msg_number >= self.messages[i].number:
            i = i + 1
        return i


    def append_message(self, msg: ChatMessage) -> None: #TODO
        self.messages.insert(self._append_message(msg.number), msg)

