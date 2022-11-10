import string
import tkinter as tk


def is_secure(password):
    if len(password) < 12:
        return False
    if (any(ch in string.ascii_lowercase for ch in password) and
       any(ch in string.ascii_uppercase for ch in password) and
       any(ch.isdigit() for ch in password)):
        return True
    return False


def get_all_children(w):
    if not w.winfo_children(): return []
    res = []
    for c in w.winfo_children():
        res.append(c)
        res.extend(get_all_children(c))
    return res

