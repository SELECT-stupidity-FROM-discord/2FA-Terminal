import os
import base64
import hashlib
import hmac
from re import TEMPLATE
import sqlite3 as sqlite
import struct
import time
import pyotp
from pick import pick

from models import AESCipher

TEMPLATE = "Press Control + C to go back\nYour 2FA code is: {}"


def countdown(seconds, key):
    """
    Countdown.
    """
    template = TEMPLATE.format(get_totp_token(key))
    os.system('clear')
    while True:
        try:
            print(template + " - {}".format(seconds))
            time.sleep(1)
            print("\033[F\033[K", end="")
            print("\033[F\033[K", end="")
            if seconds == 0:
                template = TEMPLATE.format(get_totp_token(key))
                seconds = 30
                continue
            seconds -= 1
        except KeyboardInterrupt:
            break
    return


def get_totp_token(secret: str):
    pyotp_obj = pyotp.TOTP(secret)
    return pyotp_obj.now()



def make_new_entry(conn: sqlite.Connection, cipher: AESCipher):
    """
    Create a new entry in the database.
    """
    # Get the user's input.
    key = input("Enter your 2FA Key: ")
    name = input("Enter key associated name: ")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO authenticated (name, key) VALUES (?, ?)",
                   (name, cipher.encrypt(key)))
    conn.commit()


def init_db(conn: sqlite.Connection):
    """
    Initialize the database.
    """
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS authenticated (name TEXT, key TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS password (password TEXT)")
    conn.commit()


def check_for_password(conn: sqlite.Connection):
    """
    Check if the database has a password.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM password")
    return cursor.fetchone() is not None


def set_password(conn: sqlite.Connection, password: str):
    """
    Set the password.
    """
    cursor = conn.cursor()
    password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    cursor.execute("INSERT INTO password (password) VALUES (?)", (password,))
    conn.commit()


def compare_password(conn: sqlite.Connection, password: str):
    """
    Compare the password.
    """
    cursor = conn.cursor()
    password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    cursor.execute("SELECT * FROM password")
    return cursor.fetchone()[0] == password



def get_existing_entries(conn: sqlite.Connection, cipher: AESCipher):
    """
    Get the existing entries.
    """
    os.system('clear')
    cursor = conn.cursor()
    cursor.execute("SELECT name, key FROM authenticated")
    keys = cursor.fetchall()
    real_keys = [key[1] for key in keys]
    options = [key[0] for key in keys]
    if not options:
        print("No entries found.\n\nPress Enter to go back")
        input()
        return
    option, index = pick(options, "Select an entry to see its 2FA code: ", indicator="=>")
    selected = real_keys[index]
    actual_key = cipher.decrypt(selected)
    countdown(30, actual_key)


        
