import sys
sys.path.append("../ChitChat")
import utils
import random, string

from pytest_mock import MockerFixture

def password_should_be_secure() -> None:
    lower_case = random.randint(1,10)
    upper_case = random.randint(1, 12 - lower_case - 1)
    digits = 12 - (lower_case + upper_case)

    password = ""
    for i in range(lower_case):
        password += random.choice(string.ascii_letters).lower()
    for i in range(upper_case):
        password += random.choice(string.ascii_letters).upper()
    for i in range(digits):
        password += str(random.randint(0,9))
    
    assert utils.is_secure(password)


def password_should_not_be_secure() -> None:
    lower_case = random.randint(1,9)
    upper_case = random.randint(1, 11 - lower_case - 1)
    digits = 11 - (lower_case + upper_case)

    password = ""
    for i in range(lower_case):
        password += random.choice(string.ascii_letters).lower()
    for i in range(upper_case):
        password += random.choice(string.ascii_letters).upper()
    for i in range(digits):
        password += str(random.randint(0,9))
    
    assert not utils.is_secure(password)


def password_should_not_be_secure2() -> None:
    lower_case = random.randint(1,11)
    digits = 12 - lower_case

    password = ""
    for i in range(lower_case):
        password += random.choice(string.ascii_letters).lower()
    for i in range(digits):
        password += str(random.randint(0,9))
    assert not utils.is_secure(password)


def password_should_not_be_secure3() -> None:
    lower_case = random.randint(1,11)
    upper_case = 12 - lower_case

    password = ""
    for i in range(lower_case):
        password += random.choice(string.ascii_letters).lower()
    for i in range(upper_case):
        password += random.choice(string.ascii_letters).upper()
    
    assert not utils.is_secure(password)


def password_should_not_be_secure4() -> None:
    upper_case = random.randint(1,11)
    digits = 12 - upper_case

    password = ""
    for i in range(upper_case):
        password += random.choice(string.ascii_letters).upper()
    for i in range(digits):
        password += str(random.randint(0,9))
    assert not utils.is_secure(password)
