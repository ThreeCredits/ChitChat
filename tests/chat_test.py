import sys
sys.path.append("../ChitChat")
import chat, datetime
import random

def message_should_be_first():
    c = chat.Chat(1, "test chat", "...", datetime.datetime.now(), users = [("test user", 0, 0)])
    c.messages = [
        chat.ChatMessage(2, ("test user", 0, 0), datetime.datetime.now(), "hello"),
        chat.ChatMessage(3, ("test user", 0, 0), datetime.datetime.now(), "hello"),
        chat.ChatMessage(4, ("test user", 0, 0), datetime.datetime.now(), "hello")
    ]

    c.append_message(chat.ChatMessage(1, ("test user", 0, 0), datetime.datetime.now(), "hello"))
    
    assert c.messages[0].number == 1


def message_should_be_last():
    c = chat.Chat(1, "test chat", "...", datetime.datetime.now(), users = [("test user", 0, 0)])
    c.messages = [
        chat.ChatMessage(1, ("test user", 0, 0), datetime.datetime.now(), "hello"),
        chat.ChatMessage(2, ("test user", 0, 0), datetime.datetime.now(), "hello"),
        chat.ChatMessage(3, ("test user", 0, 0), datetime.datetime.now(), "hello")
    ]

    c.append_message(chat.ChatMessage(4, ("test user", 0, 0), datetime.datetime.now(), "hello"))
    
    assert c.messages[3].number == 4
    

def messages_should_be_in_order():
    c = chat.Chat(1, "test chat", "...", datetime.datetime.now(), users = [("test user", 0, 0)])

    message_ids_to_append = list(range(1,11))
    for i in range(10):
        msg_id = random.choice(message_ids_to_append)
        message_ids_to_append.remove(msg_id)
        c.append_message(chat.ChatMessage(msg_id, ("test user", 0, 0), datetime.datetime.now(), "hello"))
    
    #check order
    for i in range(9):
        assert c.messages[i].number < c.messages[i + 1].number
    

def Chat_constructor_test():
    date = datetime.datetime.now()
    c = chat.Chat(1, "test chat", "...", date, users = [("test user", 0, 0)])

    assert c.id == 1
    assert c.chat_name == "test chat"
    assert c.description == "..."
    assert c.creation_date == date
    assert c.users[0] == ("test user", 0, 0)


def Chat_update_test():
    date = datetime.datetime(1, 1, 1)
    c = chat.Chat(1, "test chat", "...", date, users = [("test user", 0, 0)])
    c.update("test chat updated", "...!", users = [("test user2", 0, 0)])

    assert c.chat_name == "test chat updated"
    assert c.description == "...!"
    assert c.users == [("test user2", 0, 0)]


def ChatMessage_constructor_test():
    date = datetime.datetime.now()
    msg = chat.ChatMessage(1, ("test user", 0, 0), date, "hello")

    assert msg.number == 1
    assert msg.author == ("test user", 0, 0)
    assert msg.date == date
    assert msg.content == "hello"
