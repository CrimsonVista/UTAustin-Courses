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

def crack_password(entry):
    s = entry.split("$")
    if s[1] != 1:
         print("Cannot brute force in time.")
    else:
        return

if __name__ == '__main__':
    if len(sys.argv) == 2:
        crack_password(sys.argv[1])
    else:
        main()
