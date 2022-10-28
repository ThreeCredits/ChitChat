class User():
    """
    The user class holds the informations about a user
    """

    def __init__(self, name: str, tag: str, password: str):
        """
        The constructor of the User class
        """
        self.name = name
        self.tag = tag
        self.password = password

    def get_name(self):
        """
        Returns the name of the user
        """
        return self.name

    def get_tag(self):
        """
        Returns the tag of the user
        """
        return self.tag

    def get_password(self):
        """
        Returns the password of the user
        """
        return self.password

    def __str__(self):
        """
        The string representation of the User class
        """
        return "User: {}#{} - Password: {}".format(self.name, self.tag, self.password)
