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
        
    
    def __str__(self):
        return str(self.number) + "," + self.author[0] + "," + str(self.author[1]) + "," + str(self.date) + "," + self.content
    

class Chat:
    def __init__(self, id: int, chat_name: str, description: str, users: List[Tuple[str, int, int]] = []):
        self.id = id
        self.chat_name = chat_name
        self.description = description
        self.users = users
        self.messages = []

    
    def __str__(self):
        res = str(self.id) + "," + self.chat_name + "," + self.description + "|"
        for u in self.users:
            res += u[0] + "," + str(u[1]) + ";"
        res += "|"
        for m in self.messages:
            res += str(m)

        
    def append_messages(self, *args: ChatMessage):
        for message in args:
            self.messages.append(message)

