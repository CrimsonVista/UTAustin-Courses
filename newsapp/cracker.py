import sqlite3
import base64
import sys
from cryptography.hazmat.primitives import hashes as h
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def main():
    # Make common_pwords list
    common_pwords = ["123456",
    "123456789",
    "qwerty",
    "password",
    "1234567",
    "12345678",
    "12345",
    "iloveyou",
    "111111",
    "123123",
    "abc123",
    "qwerty123",
    "1q2w3e4r",
    "admin",
    "qwertyuiop",
    "654321",
    "555555",
    "lovely",
    "7777777",
    "welcome",
    "888888",
    "princess",
    "dragon",
    "password1",
    "123qwe"]    

    # Connect to database
    con = sqlite3.connect('db.sqlite3')
    cursor = con.cursor()
    cursor.execute("SELECT * FROM auth_user;")

    # Retrieve all entries
    user_info = cursor.fetchall()

    # Loop through entries and extract hashes
    hashes = []
    for i in user_info:
        info = i[1]
        s = info.split("$")
        s.pop(0)
        s.append(i[4])
        # Store iterations, salt, and hash
        hashes.append(s)

    # Loop through all common passwords and hash using iterations and salt
    for pw in hashes:
        # Loop through each common password
        for common in common_pwords:
            # Recreate PBKDF2 instance each use
            kdf = PBKDF2HMAC(algorithm=h.SHA256(),
                length=32,
                salt= bytes(pw[1], 'utf-8'),
                iterations= int(pw[0])
                )
            # Take out newline
            s = common.split()
            # Derive key
            key = kdf.derive(bytes(s[0], "utf-8"))
            # Print common password if it appears in the Django database
            if base64.b64encode(key) == bytes(pw[2], 'utf-8'):
                print(pw[3], ",", s[0])

def crack_password(entry) -> bool:
    s = entry.split("$")
    iterations = int(s[1])
    salt = s[2]
    hash = s[3]
    if iterations != 1:
         print("Cannot brute force in time.")
         return True
    else:
        for char in range(97, 123):
            s1 = ""+chr(char)
            if try_guess(salt, hash, s1):
                return True
            for char in range(97, 123):
                s2 = s1+chr(char)
                if try_guess(salt, hash, s2):
                    return True
                for char in range(97, 123):
                    s3 = s2+chr(char)
                    if try_guess(salt, hash, s3):
                        return True
                    for char in range(97, 123):
                        s4 = s3+chr(char)
                        if try_guess(salt, hash, s4):
                            return True
        return False



def try_guess(salt, hash, guess)-> bool:
    kdf = PBKDF2HMAC(algorithm=h.SHA256(),
        length=32,
        salt= bytes(salt, 'utf-8'),
        iterations= 1
        )
    key = kdf.derive(bytes(guess, "utf-8"))
    if base64.b64encode(key) == bytes(hash, 'utf-8'):
        print("Password cracked:", guess)
        return True
    return False
if __name__ == '__main__':
    if len(sys.argv) == 2:
        if not crack_password(sys.argv[1]):
            print("Password not cracked")
    else:
        main()
