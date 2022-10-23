import datetime
from typing import Tuple, Any, List
import string

class Chat:
    pass

class ChatMessage:
    def __init__(self, chat: Chat, author: int, date: datetime.datetime, content: Any):
        self.chat = chat
        self.author = author
        self.content = content
        self.date = date

class Chat:
    def __init__(self, chat_name: string, image_name: string, users: List[str] = []):
        self.chat_name = chat_name
        self.image_name = image_name
        self.users = users
        self.messages = []

        
    def append_messages(self, *args: ChatMessage):
        for message in args:
            self.messages.append(message)

