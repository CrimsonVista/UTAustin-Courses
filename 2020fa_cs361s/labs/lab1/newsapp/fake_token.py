from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import sys, time

def FakeToken(seed, refresh=30, salt=b"", info=b"fake-rsa-token"):
    while True:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=3,
            salt=salt,
            info=info,
        )
        token_time = time.time()
        cur_epoch = int(token_time/refresh)
        next_time = (cur_epoch+1)*refresh
        yield (next_time-int(token_time), int.from_bytes(hkdf.derive(seed + cur_epoch.to_bytes(4,"big")), "big"))
        
if __name__=="__main__":
    seed = sys.argv[1]
    seed = seed.encode()
    for time_left, next_num in FakeToken(seed):
        print(time_left, next_num)
        time.sleep(time_left)