import asyncio, time, struct
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac as crypto_hmac # avoid name collision
from cryptography.hazmat.primitives.asymmetric import ec, rsa, dh
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from scapy.all import *
from scapy.layers.tls.keyexchange import _TLSSignature
from scapy.layers.tls.handshake import _TLSCKExchKeysField
from datetime import datetime, timedelta

from .debug import Debug
from .utils import DHParamsSerialization

randstring = Debug.replayable(Debug.random)
timestamp  = Debug.replayable(time.time)
ServerDHParams = Debug.replayable(ServerDHParams, DHParamsSerialization)

class TLSSession:
    def __init__(self):
        # manually set value
        self.tls_version = 0x303
        self.read_seq_num = 0
        self.write_seq_num = 0
        self.PRF = PRF()

        self.client_time = None
        self.client_random_bytes = None
        
        self.server_time = None
        self.server_random_bytes = None

        self.server_rsa_privkey = None
        self.client_dh_params = None

        self.mac_key_size = 20
        self.enc_key_size = 16
        #self.iv_size = 16

        self.handshake = True

        # automatically calculated
        self.client_random = None
        self.server_random = None
        self.server_dh_params = ServerDHParams()
        #self.server_dh_params.fill_missing()
        self.server_dh_privkey = self.server_dh_params.tls_session.server_kx_privkey
        self.client_dh_pubkey = None
        self.pre_master_secret = None
        self.master_secret = None
        self.read_mac = None
        self.write_mac = None
        self.read_enc = None
        self.write_enc = None
        self.read_iv = None
        self.write_iv = None
        self.key_block_len = (2*self.mac_key_size)+(2*self.enc_key_size)#+(2*self.iv_size)

        self.handshake_messages = b""

    def set_client_random(self, time_part, random_part):
        # STUDENT TODO
        """
        1. set client_time, client_bytes
        2. calculate client_random. There is a method for this
        """
        pass

    def set_server_random(self):
        # STUDENT TODO
        """
        1. set server_time, server_bytes
        2. calculate server_random. There is a method for this
        """
        pass

    def set_server_rsa_privkey(self, rsa_privkey):
        self.server_rsa_privkey = rsa_privkey

    def set_client_dh_params(self, client_params):
        self.client_dh_params = client_params  
        p = pkcs_os2ip(self.server_dh_params.dh_p)
        g = pkcs_os2ip(self.server_dh_params.dh_g)
        pn = dh.DHParameterNumbers(p,g)
        y = pkcs_os2ip(self.client_dh_params.dh_Yc)
        public_key_numbers = dh.DHPublicNumbers(y, pn)
        self.client_dh_pubkey = public_key_numbers.public_key(default_backend())
        self._derive_keys()

    def _derive_keys(self):
        # STUDENT TODO
        """
        1. calculate pre_master_secret
        2. calculate master_secret
        3. calculate a key block
        4. split the key block into read and write keys for enc and mac
        """
        pass

    def tls_sign(self, bytes):
        """
        1. Create a TLSSignature object. set sig_alg to 0x0401
        2. use this object to sign the bytes
        """
        sig = None # this should be the signature object
        return sig


    def decrypt_tls_pkt(self, tls_pkt, **kargs):
        # scapy screws up and changes the first byte if it can't decrypt it
        # from 22 to 23 (handshake to application). Check if this happens and fix
        packet_type = tls_pkt.type
        tls_pkt_bytes = raw(tls_pkt)
        tls_pkt_bytes = struct.pack("!B",packet_type)+tls_pkt_bytes[1:]
        
        # STUDENT TODO
        """
        1. The beginning of this function, already provided, extracts the data from scapy
        2. Do the TLS decryption process on tls_pkt_bytes
        3. Technically, you don't have to do the hmac. wget will do it right
        4. But if you check the hmac, you'll know your implementation is correct!
        5. return ONLY the decrypted plaintext data
        6. NOTE: When you do the HMAC, don't forget to re-create the header with the plaintext len!
        """
        plaintext = b''
        return plaintext

    def encrypt_tls_pkt(self, tls_pkt, test_iv=None):
        pkt_type = tls_pkt.type
        tls_pkt_bytes = raw(tls_pkt)

        # scapy can make some mistakes changing the first bytes on handshakes
        if tls_pkt_bytes[0] != pkt_type:
            Debug.print(tls_pkt_bytes[0], pkt_type)
            tls_pkt_bytes = struct.pack("!B",pkt_type)+tls_pkt_bytes[1:]
        
        # no matter what, should only have one msg
        plaintext_msg = tls_pkt.msg[0]
        plaintext_bytes = raw(plaintext_msg)
        
        # STUDENT TODO
        """
        1. the beginning of this function, already provided, extracts the data from scapy
        2. Do the TLS encryption process on the plaintext_bytes
        3. You have to do hmac. This is the write mac key
        4. You have to compute a pad
        5. You can use os.urandom(16) to create an explicit IV
        6. return the iv + encrypted data
        """
        
        ciphertext = b""
        
        return ciphertext

    def record_handshake_message(self, m):
        self.handshake_messages += m

    def compute_handshake_verify(self, mode):
        # STUDENT TODO
        """
        1. use PRF.compute_verify_data to compute the handshake verify data
            arg_1: the string "server"
            arg_2: mode
            arg_3: all the handshake messages so far
            arg_4: the master secret
        """
        verify_data = b""
        
        return verify_data

    def time_and_random(self, time_part, random_part=None):
        if random_part is None:
            random_part = randstring(28)
        return struct.pack("!I",time_part) + random_part

        
        
