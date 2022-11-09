import socket
import threading
import pickle
import datetime
from server import Server
from TaggedQueue import *  
from cipher import *
from message import Packet, PacketItem
from identity import Identity
from User import User
import json
# Two classes:
# KeyExchanger : Binds to one port, accepts all incoming connections, used for public e2e keys sharing
# ClientSocket : Used to communicate with a client.

class LoginManager:
    def __init__(self, port: int = 5556, max_connections: int = 250, server: Server = None): 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('127.0.0.1', port))
        self.socket.listen(max_connections)
        self.server = server
        self.public_key = server.public_key
        self.blacklisted = {}

    def run(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
    
    def _run(self):
        while True:
            client, address = self.socket.accept()
            self.server.printv("New connection from: " + str(address), level = 2)
            # Create a new thread to handle the exchange
            thread = threading.Thread(target=self._login, args=(client, address))
            thread.start()
    
    def _login(self, client
    , address):
        # Time out after 120 seconds
        client.settimeout(120)
        server = self.server
        queue = server.queue
        user_id = None
        # Check if the client is blacklisted
        if address in self.blacklisted:
            client.send(pickle.dumps(
                Packet(
                    [
                        PacketItem("backoff", self.blacklisted[address]) # Send the backoff time
                    ]
                )
            ))
            client.close()
            return
        # First, we send our public key
        client.send(pickle.dumps(
            Packet(
                [
                    PacketItem("pub_key", self.public_key)
                ]
            )
        ))
        # Then, we wait for the client's public key
        message = client.recv(32 * 1024)
        # We unpickle the message
        message = pickle.loads(message)
        # We expect a public key
        if message[0].type != "pub_key":
            self.server.printv("Invalid message received from " + str(address), level = 1)
            # We close the connection
            client.close()
            return
        else:
            # Now that we have the client's public key, we store it in a identity 
            client_identity = Identity(pub_bytes = message.data[0].data)
            # We expect a message from the client telling us whether it wants to login or register.
            # We also will limit the number of attempts to 3, after which we will close the connection and blacklist the IP for 60 seconds.
            attempts = 0
            while attempts < 3:
                message = receive_ciphered_message(client, self.server.identity)
                if not message:
                    # We close the connection
                    client.close()
                    return
                if message[0].type == "login":
                    # Parse the rest of the message
                    username = message[0].data[0]
                    tag = message[0].data[1]
                    password = message[0].data[2]
                    # Print the request
                    self.server.printv("Login request from " + str(address) + " for user " + username + " usertag " + str(tag), level = 2)
                    # Wait for the job to finish
                    result = queue.wait_for_result(server.login(username, tag, password))
                    # If the result is None, then the login failed
                    if result is None:
                        # Send a failure message
                        send_ciphered_message( Packet(
                            [
                                PacketItem("success", False)
                            ]
                        ), client, self.server.identity)
                        attempts += 1
                    # Parse the result
                    else:
                        # Create response
                        response = Packet(
                            [
                                PacketItem("success", True)
                            ]
                        )
                        # Send response
                        send_ciphered_message(response, client, client_identity)
                        # Create user
                        user = User(result[0][0], username, tag, password, client_identity.export_public_key_bytes())
                        # Start the client handler
                        ClientHandler(client, address, client_identity, server, user).run()
                        return
                        
                elif message[0].type == "register":
                    # We expect a message with the following format:
                    # [username, password, profile_picture]
                    username = message[0].data[0]
                    user_password = message[0].data[1]
                    # print the request
                    self.server.printv("Register request from " + str(address) + " for user: " + username + " password: " + user_password, level = 2)
                    result = queue.wait_for_result(server.register(username, user_password, client_identity.export_public_key_bytes()))
                    #
                    # Result will be the user_id
                    user_id = result.result[0][0]
                    if user_id <= 0:
                        # Create response
                        response = Packet(
                            [
                                PacketItem("success", False),
                                PacketItem("error", "Not enough usertags for the username already taken")
                            ]
                        )
                        # Send response
                        send_ciphered_message(response, client, client_identity)
                    else:
                        # Get the user and tag of the new user
                        result = queue.wait_for_result(server.get_userid_info(user_id))
                        user_tag = result.result[0][0]
                        # Create response
                        response = Packet(
                            [
                                PacketItem("success", True),
                                PacketItem("tag", user_tag),
                            ]
                        )
                        # Send response
                        send_ciphered_message(response, client, client_identity)
                        # Start the client handler
                        user = User(user_id, username, user_tag, user_password, client_identity.export_public_key_bytes())
                        ClientHandler(client, address, client_identity, server, result["user"]).run()
                        
                        return
                else:
                    self.server.printv("Invalid message received from " + str(address), level = 1)
                    # We close the connection
                    client.close()
                    return
                attempts += 1
            
            # Check if the number of attempts is 3
            if attempts == 3:
                # We close the connection
                client.close()
                # We blacklist the IP for 60 seconds
                self.blacklisted[address[0]] = datetime.datetime.now() + datetime.timedelta(seconds = 60)
                return

class ClientHandler():
    def __init__(self, client, address, identity: Identity, server: Server, user: User):
        self.client = client
        self.address = address
        self.identity = identity
        self.server = server
        self.queue = server.queue
        self.user_id = user.ID
        self.user_name = user.username
        self.user_tag = user.tag
        self.user_password = user.password
        self.server_identity = server.identity
        self.user = user

    def run(self):
        self.input_thread = threading.Thread(target=self._input, daemon= True)
        self.input_thread.start()
        # Wait for the threads to finish
        self.input_thread.join()
        # Set the last seen time
        self.server.set_last_seen(self.user_id) # Don't wait for the result
        # Connection should be closed by now, but we close it again just in case
        try:
            self.client.close()
        except:
            pass


    
    def _input(self):
        self.client.settimeout(60) # since the client is already authenticated, we can set a timeout that is longer.
        while True:
            msg = receive_ciphered_message(self.client, self.server_identity)
            if not msg:
                # We close the connection
                self.client.close()
                return
            # Check if the message is a Packet, and if its data is a non empty list
            try:
                if not isinstance(msg, Packet) or len(msg.data) == 0:
                    self.server.printv("Invalid message received from " + str(self.address), level = 1)
                    # We close the connection
                    self.client.close()
                    return
            except:
                self.server.printv("Invalid message received from " + str(self.address), level = 1)
                # We close the connection
                self.client.close()
                return
            for item in msg:
                result = None
                match item.type:
                    case "ping":
                        # We send a pong message with the date of receive
                        send_ciphered_message(Packet([PacketItem("pong", item.data)]), self.client, self.identity)
                        
                    case "logout":
                        # Print the request
                        self.server.printv("Logout request from " + str(self.address) + " for user " + self.user_name + " usertag " + str(self.user_tag), level = 2)
                        # We close the connection
                        self.client.close()
                        return
    
                    case "msg_get":
                        # We get the messages
                        # result = self.queue.wait_for_result(self.server.get_messages(self.user_id, chat_id, last_message_id))
                        result = self.queue.wait_for_result(self.server.get_unread_messages(self.user_id), timeout = 60)
                        # create packet
                        packet = Packet(data = [])

                        # Check if the result is None
                        if result is None or len(result.result) == 0:
                            continue # No new messages (sadly)
                        
                        # Add the messages to the packet
                        for message in result:
                            packet.append(PacketItem("msg", message))
                            print("Sending out", message, "to", self.user_name + "#" + str(self.user_tag))
                        
                        # Send the packet
                        send_ciphered_message(packet, self.client, self.identity)

                    case "get_chats":
                        # We get the chats that the user is a part of
                        # result = self.queue.wait_for_result(self.server.get_chats(self.user_id))
                        # We send the result to the client
                        if result["success"]:
                            send_ciphered_message(Packet([PacketItem("success", True), PacketItem("chats", result["chats"])]), self.client, self.identity)
                        else:
                            send_ciphered_message(Packet([PacketItem("success", False), PacketItem("error", result["error"])]), self.client, self.identity)
                    
                    case "create_chat":
                        # We expect a message with the following format:
                        # [name, users]
                        name = item.data[0]
                        description = item.data[1]
                        users = item.data[2]
                        # We create the chat
                        result = self.queue.wait_for_result(self.server.create_chat(self.user, name, description, users))
                        if result["chat_id"] > 0:
                            # We send the result to the client
                            send_ciphered_message(Packet([
                                PacketItem("chat_create_success", (result["chat_id"], result["chat_name"], result["chat_description"], result["partecipants"])),
                            ]), self.client, self.identity)
                        else:
                            # We send the result to the client
                            send_ciphered_message( Packet( [
                                PacketItem("chat_create_fail", None)
                            ]), self.client, self.identity)
                    
                    case "msg_send":
                        # We expect a message with the following format:
                        # [chat_id, message]
                        chat_id = item.data[0]
                        message = item.data[1]
                        # We send the message, and don't wait for the result
                        result = self.queue.wait_for_result(self.server.send_message(self.user_id, chat_id, message))

                    case "set_status":
                        # We expect a message with the following format:
                        # [status]
                        user_id = self.user_id
                        # Check that the user_id is a integer
                        if not isinstance(user_id, int):
                            self.server.printv("Invalid user_id received from " + str(self.address), level = 1)
                            # We close the connection
                            self.client.close()
                            return
                        status = item.data
                        # We set the status (don't wait for the result)
                        result = self.server.set_status(user_id, status)

                    


                    case "chat_info":
                        # We expect a message with the following format:
                        # [chat_id]
                        chat_id = item.data[0]
                        # We get the chat info
                        result = self.queue.wait_for_result(self.server.get_chat_info(self.user_id, chat_id))
                        
                        # If we see that the user requested info in a illegal way, we close the connection.
                        # That is, if the user asked for a chat that the user is not a part of.
                        if not result["success"] and result["error"] == "illegal_request":
                            self.client.close()
                            # Immediately blacklist the IP, for a longer time
                            self.server.blacklisted[self.address[0]] = datetime.datetime.now() + datetime.timedelta(seconds = 300)

                        # We send the result to the client
                        if result["success"]:
                            send_ciphered_message(Packet([PacketItem("success", True), PacketItem("chat_info", result["chat_info"])]), self.client, self.identity)
                        else:
                            send_ciphered_message(Packet([PacketItem("success", False), PacketItem("error", result["error"])]), self.client, self.identity)

                    case "add_user":
                        # We expect a message with the following format:
                        # [chat_id, username, tag]
                        chat_id = item.data[0]
                        username = item.data[1]
                        tag = item.data[2]
                        # We add the user
                        # result = self.queue.wait_for_result(self.server.add_user(self.user_id, chat_id, username, tag))
                        
                        # If we see that the user was added in a illegal way, we close the connection.
                        # That is, if the user was added in a chat that the user is not a part of.
                        if not result["success"] and result["error"] == "illegal_request":
                            self.client.close()
                            # Immediately blacklist the IP, for a longer time
                            self.server.blacklisted[self.address[0]] = datetime.datetime.now() + datetime.timedelta(seconds = 300)

                        # We send the result to the client
                        if result["success"]:
                            send_ciphered_message(Packet([PacketItem("success", True)]), self.client, self.identity)
                        else:
                            send_ciphered_message(Packet([PacketItem("success", False), PacketItem("error", result["error"])]), self.client, self.identity)
                    
                    case "remove_user":
                        # We expect a message with the following format:
                        # [chat_id, user_id]
                        chat_id = item.data[0]
                        user_id = item.data[1]
                        # We remove the user
                        # result = self.queue.wait_for_result(self.server.remove_user(self.user_id, chat_id, user_id))

                        # If we see that the user was removed in a illegal way, we close the connection.
                        # That is, if the user was removed in a chat that the user is not a part of, or if the removing user is not an admin of the chat.
                        if not result["success"] and result["error"] == "illegal_request":
                            self.client.close()
                            # Immediately blacklist the IP, for a longer time
                            self.server.blacklisted[self.address[0]] = datetime.datetime.now() + datetime.timedelta(seconds = 300)
                    
                    case "user_info":
                        # We expect a message with the following format:
                        # [user_id]
                        user_id = item.data[0]
                        # We get the user info
                        result = self.queue.wait_for_result(self.server.get_user_info(self.user_id, user_id))

                        # User info is always open, so we don't need to check for illegal requests here.
                        # We send the result to the client
                        if result["success"]:
                            send_ciphered_message(Packet([PacketItem("success", True), PacketItem("user_info", result["user_info"])]), self.client, self.identity)
                        else:
                            send_ciphered_message(Packet([PacketItem("success", False), PacketItem("error", result["error"])]), self.client, self.identity)
        # We close the connection
        self.client.close()