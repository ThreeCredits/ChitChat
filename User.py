class User():
    """
    The user class holds the informations about a user
    """

    def __init__(self, ID: int, username: str, tag: str, password: str, public_key : bytes):
        """
        The constructor of the User class
        """
        self.username = username
        self.tag = tag
        self.password = password
        self.ID = ID
        self.public_key = public_key


    def __str__(self):
        """
        The string representation of the User class
        """
        return "User: {}#{} - Password: {}".format(self.username, self.tag, self.password)
