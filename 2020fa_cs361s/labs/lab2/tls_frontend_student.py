#BKCTL# begin_output: http_proxy.py
import asyncio, time, struct
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac as crypto_hmac # avoid name collision
from cryptography.hazmat.primitives.asymmetric import ec, rsa, dh
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509.oid import NameOID
from scapy.all import *
from scapy.layers.tls.keyexchange import _TLSSignature
from scapy.layers.tls.handshake import _TLSCKExchKeysField
from datetime import datetime, timedelta
from urllib.parse import urlparse

load_layer("tls")

class Debug:
    def __init__(self):
        self.enabled = False
    def print(self, *args, **kargs):
        if not self.enabled: return
        print(*args, **kargs)
    def scapy_show(self, pkt):
        if not self.enabled: return
        pkt.show2()
debug = Debug()

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
        self.server_dh_params.fill_missing()
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
        # sig_alg 0x0401 = sha256+rsa as per our certificate
        # STUDENT TODO
        """
        1. Create a TLSSignature object. set sig_alg to 0x0401
        2. use this object to sign the bytes
        """
        return None # return signature object

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
        return b""

    def encrypt_tls_pkt(self, tls_pkt):
        pkt_type = tls_pkt.type
        tls_pkt_bytes = raw(tls_pkt)

        # scapy can make some mistakes changing the first bytes on handshakes
        if tls_pkt_bytes[0] != pkt_type:
            tls_pkt_bytes = struct.pack("!B",pkt_type)+tls_pkt_bytes[1:]
            
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
        return b""

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
        return b""

    def time_and_random(self, time_part, random_part=None):
        if random_part is None:
            random_part = randstring(28)
        return struct.pack("!I",time_part) + random_part
        
class TLS_Visibility:
    def __init__(self, tls_cert, priv_key):
        self.session = TLSSession()
        self.load_crypto(tls_cert, priv_key)

    def load_crypto(self, cryptography_cert, cryptography_private_key):
        cert_der_bytes = cryptography_cert.public_bytes(serialization.Encoding.DER)
        self.cert = Cert(X509_Cert(cert_der_bytes))
        privatekey_pem_bytes = cryptography_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption())
        self.private_key = PrivKey(privatekey_pem_bytes)

    def encrypt_data(self, data):
        # STUDENT TODO
        """
        Actually, we did this one for you because it was pretty
        simple. But we want you to see that you take data, 
        put it into a TLS application packet, and then 
        encrypt the packet.
        """
        application_part = TLSApplicationData(data=data)
        application_pkt = TLS(msg=[application_part])
        application_pkt.type = 23
        return self.session.encrypt_tls_pkt(application_pkt)

    def process_tls_handshake(self, tls_pkt, tls_msg):
        if isinstance(tls_msg, TLSClientHello):
            debug.print("Got client hello")
            debug.scapy_show(tls_msg)
 
            self.session.set_server_rsa_privkey(self.private_key)
            # STUDENT TODO
            """ 
            Instructions:
            1. process client hello. set the session client random appropriately
            2. create the server hello. Set cipher=TLS_DHE_RSA_WITH_AES_128_CBC_SHA.val
            3. create the server cert message. Set certs=[self.cert]
            4. create server key exchange.
                params = self.session.server_dh_params
                sig = <signature you calculate>
            5. create server hello done
            6. store in the provided server_hello, server_cert, server_key_exchange,
                and server_hello_done variables
            """
            server_hello = None
            server_cert = None
            server_key_exchange = None
            server_hello_done = None
            f_session = tlsSession()
            f_session.tls_version = 0x303
            tls_response = TLS(msg=[server_hello, server_cert, server_key_exchange, server_hello_done],
                tls_session=f_session)
            tls_response_bytes = raw(tls_response)
            debug.scapy_show(tls_response)
            return tls_response_bytes
        elif isinstance(tls_msg, TLSClientKeyExchange):
            debug.print("Got key exchange")
            debug.scapy_show(tls_msg)
            # STUDENT TODO
            """
            1. process the client key exchange by extracting the "exchkeys"
            2. These can be passed directly to session.set_client_dh_params
            """ 
                
            
        elif isinstance(tls_msg, TLSFinished):
            debug.print("Got Client Finished")
            debug.scapy_show(tls_msg)
            # STUDENT TODO
            """
            1. process the decrypted TLS finished message. OPTIONALLY, verify the data:
                local_verify_data = session.compute_handshake_verify("read")
                local_verify_data ?= tls_msg.vdata
            2. Create the change cipher spec
            3. store in server_change_cipher_spec
            """
            server_change_cipher_spec = None
            msg1 = TLS(msg=[server_change_cipher_spec])
            output = raw(msg1)

            # STUDENT TODO
            """
            1. create the TLSFinished message. 
                Set v_data to session.compute_handshake_verify("write")
                because of scapy weirdness, set tls_session=f_session
            2. store in server_finished
            """
            f_session = tlsSession()
            f_session.tls_version = 0x303
            server_finished = None
            
            msg2 = TLS(msg=[server_finished], tls_session=f_session)
            
            # STUDENT TODO
            """
            1. encrypt the tls finished message (msg2). You already have a method for this.
            2. store in encrypted_finished
            """
            encrypted_finished = b""
            
            self.session.handshake = False
            return output+encrypted_finished
        elif isinstance(tls_msg, Raw):
            # STUDENT TODO
            """
            1. This was a HANDSHAKE message scapy couldn't process. It's because it's encrypted
            2. decrypt the packet to plaintext_data. You should already have a method for this
            3. store in plaintext_data
            4. The provided code already re-creates the TLSFinished from your decrypted data
            """
            plaintext_data = None

            # We re-create the TLS message with the decrypted handshake
            # Then we call `process_tls_handshake` again with this new message
            f_session = tlsSession()
            f_session.tls_version = 0x303
            decrypted_msg = TLSFinished(plaintext_data, tls_session=f_session)
            return self.process_tls_handshake(None, decrypted_msg)
            
        return b""

    def process_tls_data(self, data):
        # STUDENT TODO (kind of)
        """
        Sometimes Asyncio can swallow
        exceptions. If that's happening, you can
        try uncommenting this try except block
        """
        #try:
            return self.process_tls_data_unsafe(data)
        #except Exception as e:
        #    return ("failure", e)

    def process_tls_data_unsafe(self, data):
        output = b""
        if self.session.handshake:
            result_type = "local_response"
        else:
            result_type = "proxy"
        tls_data = TLS(data)
        debug.print("tls data without session")
        debug.scapy_show(tls_data)
        tls_pkts = [tls_data]
        # we are getting TLS messages smushed together as payloads
        next_payload = tls_data.payload
        tls_data.remove_payload()
        while next_payload and isinstance(next_payload, TLS):
            debug.print("got packet of type", next_payload.type)
            tls_pkts.append(next_payload)
            next_payload2 = next_payload.payload
            next_payload.remove_payload()
            next_payload = next_payload2
            debug.print("after detach, type is", tls_pkts[-1].type)
        debug.print("Processing {} packets".format(len(tls_pkts)))
        while tls_pkts:
            tls_pkt = tls_pkts.pop(0)
            if tls_pkt.type == 22: # handshake
                for handshake_data in tls_pkt.msg:
                    response = self.process_tls_handshake(tls_pkt, handshake_data)
                    #self.session.handshake_messages += response
                    output += response
            elif tls_pkt.type == 20:
                debug.print("Got Change Cipher Spec")
                debug.scapy_show(tls_pkt)
            elif tls_pkt.type == 21:
                print("Got Alert")
                raise Exception("Something went wrong with TLS")
            elif tls_pkt.type == 23:
                if self.session.handshake:
                    raise Exception("Got application data while still in handshake")
                # STUDENT TODO
                """
                1. We've received an application data packet. It will be encrypted
                2. decrypt the packet to application_data. You should already have a method for this.
                3. store in application_data
                """
                application_data = None
                application_pkt = TLSApplicationData(application_data)
                output += application_pkt.data
            else:
                print("Got unknown tls pkt type {}".format(pkt.type))
                tls_pkt.show2()

        return (result_type, output)

class ProxySocket(asyncio.Protocol):

    def __init__(self, proxy):
        self.proxy = proxy

    def connection_made(self, transport):
        self.transport = transport
        self.proxy.proxy_socket = self

    def data_received(self, data):
        debug.print("PROXY RECV:", data)
        self.proxy.handle_remote_response(data)

    def connection_lost(self, exc):
        self.proxy.transport.close()


class TLSFrontend(asyncio.Protocol):
    def __init__(self, tls_cert, tls_key, proxy_port):
        super().__init__()
        self.tls_cert = tls_cert
        self.tls_key  = tls_key
        self.proxy_port = proxy_port
        self.backlog = b""
        
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        self.proxy_socket = None
        self.tls_handler = TLS_Visibility(self.tls_cert, self.tls_key)
        coro = asyncio.get_event_loop().create_connection(lambda: ProxySocket(self), "127.0.0.1", self.proxy_port, ssl=False)
        t = asyncio.get_event_loop().create_task(coro)
        t.add_done_callback(self.proxy_connected)
        
    def proxy_connected(self, task):
        if not self.proxy_socket:
            raise Exception("Unable to connect to backend server")
        if self.backlog:
            print("Writing backlog to proxy")
            self.proxy_socket.transport.write(self.backlog)
            self.backlog = b""

    def handle_remote_response(self, data):
        data = self.tls_handler.encrypt_data(data)   
        self.transport.write(data)

    def data_received(self, data):
            
        debug.print("PROXY SEND:", data)

        # Responding with our own TLS response
        result_type, result = self.tls_handler.process_tls_data(data)
        if result_type == "local_response":
            if result: self.transport.write(result)
        elif result_type == "failure":
            self.transport.close()
        elif result_type == "proxy":
            debug.print("Sending decrypted data to server")
            debug.print(result)
            if result: 
                if not self.proxy_socket:
                    self.backlog += result
                else:
                    self.proxy_socket.transport.write(result)

    def connection_lost(self, exc):
        if not self.proxy_socket: return
        self.proxy_socket.transport.close()
        self.proxy_socket = None
        
def main(args): 
    # uncomment the next line to turn on debug
    # debug.enabled = True
    frontend_port, backend_port, tls_cert, tls_key = args
    with open(tls_cert, "rb") as cert_obj:
        cert = x509.load_pem_x509_certificate(cert_obj.read())
    with open(tls_key, "rb") as key_obj:
        priv_key = load_pem_private_key(key_obj.read(), password=None)
    
    loop = asyncio.get_event_loop()
    coro = loop.create_server(lambda: TLSFrontend(cert, priv_key, backend_port), '127.0.0.1', frontend_port)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('TLS front-end to {} running on {}'.format(backend_port, frontend_port))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__=="__main__":
    main(sys.argv[1:])