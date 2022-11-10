from User import User
from typing import List, Dict
import random
import string

# Unit test for the User class

# Constructor test
def test_constructor():
    user = User(1, "test", "1234", "password", b"public_key")
    assert user.ID == 1
    assert user.username == "test"
    assert user.tag == "1234"
    assert user.password == "password"
    assert user.public_key == b"public_key"

    random_data = (
        random.randint,
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    )

    user = User(*random_data)
    assert user.ID == random_data[0]
    assert user.username == random_data[1]
    assert user.tag == random_data[2]
    assert user.password == random_data[3]
    assert user.public_key == random_data[4]

# String representation test
def string_representation():
    user = User(1, "test", "1234", "password", b"public_key")
    assert str(user) == "User: test#1234 - Password: password"
    user = User(2, "user", "5678", "admin", b"even_more_public_key")
    assert str(user) == "User: user#5678 - Password: admin"