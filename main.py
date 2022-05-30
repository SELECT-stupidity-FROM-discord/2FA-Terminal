
import os
from getpass import getpass
from pick import pick
import sqlite3 as sqlite

from functions import check_for_password, init_db, make_new_entry, set_password, compare_password, get_existing_entries
from models import AESCipher

POSSIBLES = {
    0: make_new_entry,
    1: get_existing_entries
}


def main():
    """
    Main function.
    """
    authenticated = False
    title = "What do you wish to do: "
    options = ["1. Enter a new authentication", "2. Look in existing entries.", "3. Exit"]


    with sqlite.connect('./database/encrypted.db', check_same_thread=False) as conn:
        init_db(conn)
        if not check_for_password(conn):
            print("You don't have a password set, please enter one right now. (For security purpose, it won't be visible)")
            var = "a"
            password = "b"
            while var != password:
                password = getpass("=> ")
                var = getpass(" Enter Again\n=> ")
            set_password(conn, password)
            authenticated = True
        else:
            print("You have a password set, please enter it now.")
            while True:
                password = getpass("=> ")
                if not compare_password(conn, password):
                    print("Wrong password, please try again.")
                else:
                    authenticated = True
                    break
        if not authenticated:
            return
        my_cipher = AESCipher(password)
        while True:
            option, index = pick(options, title, indicator="=>", default_index=0)
            if index == 2:
                break
            else:
                if index in POSSIBLES:
                    function = POSSIBLES[index]
                    function(conn, my_cipher)
                else:
                    print("Invalid option")
        os.system('clear')

        


try:
    main()
except KeyboardInterrupt:
    os.system('clear')