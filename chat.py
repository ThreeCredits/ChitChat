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
        self.content = content
        self.date = date
    

class Chat:
    def __init__(self, id: int, chat_name: str, description: str, users: List[Tuple[str, int, int]] = []):
        self.id = id
        self.chat_name = chat_name
        self.description = description
        self.users = users
        self.messages = []

        
    def append_messages(self, *args: ChatMessage):
        for message in args:
            self.messages.append(message)

