import string
def is_secure(password):
    if len(password) < 12:
        return False
    if (any(ch in string.ascii_lowercase for ch in password) and
       any(ch in string.ascii_uppercase for ch in password) and
       any(ch.isdigit() for ch in password)):
        return True
    return False
