import sqlite3
import base64
import sys
from cryptography.hazmat.primitives import hashes as h
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def main():
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
        print(info)
        s = info.split("$")
        s.pop(0)
        # Store iterations, salt, and hash
        hashes.append(s)

    # Loop through all common passwords and hash using iterations and salt
    for pw in hashes:
        # Loop through each common password
        file = open("most_common_pwords.txt", "r")
        for common in file:
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
                print(s[0])

        file.close()

def crack_password(entry) -> bool:
    s = entry.split("$")
    iterations = int(s[1])
    salt = s[2]
    hash = s[3]
    if iterations != 1:
         print("Cannot brute force in time.")
         return true
    else:
        for char in range(97, 123):
            s1 = ""+chr(char)
            if try_guess(salt, hash, s1):
                return true
            for char in range(97, 123):
                s2 = s1+chr(char)
                if try_guess(salt, hash, s2):
                    return true
                for char in range(97, 123):
                    s3 = s2+chr(char)
                    if try_guess(salt, hash, s3):
                        return true
                    for char in range(97, 123):
                        s4 = s3+chr(char)
                        if try_guess(salt, hash, s4):
                            return true
        return false;



def try_guess(salt, hash, guess)-> bool:
    kdf = PBKDF2HMAC(algorithm=h.SHA256(),
        length=32,
        salt= bytes(salt, 'utf-8'),
        iterations= 1
        )
    key = kdf.derive(bytes(guess, "utf-8"))
    if base64.b64encode(key) == bytes(hash, 'utf-8'):
        print("Password cracked:", guess)
        return true
    return false
if __name__ == '__main__':
    if len(sys.argv) == 2:
        if not crack_password(sys.argv[1]):
            print("Password not cracked")
    else:
        main()
