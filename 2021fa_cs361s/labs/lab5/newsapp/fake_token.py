import os
import time
import sys
from cryptography.hazmat.primitives.twofactor.totp import TOTP
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def FakeToken(seed, salt=b'', refresh=30, info=b"fake-rsa-token"):
    kdf = PBKDF2HMAC(
     algorithm=SHA256(),
     length=32,
     salt=salt,
     iterations=100000,
    )
    key = kdf.derive(seed)
    totp = TOTP(key, 8, SHA256(), refresh)
    while True:
        token_time = time.time()
        cur_epoch = int(token_time/refresh)
        next_time = (cur_epoch+1)*refresh
        yield (next_time-int(token_time), totp.generate(token_time))
        
if __name__=="__main__":
    seed = sys.argv[1]
    seed = seed.encode()
    for time_left, next_num in FakeToken(seed):
        print(time_left, next_num)
        time.sleep(time_left)