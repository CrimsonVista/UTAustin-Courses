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

from .debug import Debug
from .tls_session import TLSSession

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
        self.session.set_server_rsa_privkey(self.private_key)

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
            return self.process_tls_handshake_client_hello(tls_msg)
        if isinstance(tls_msg, TLSClientKeyExchange):
            return self.process_tls_handshake_key_exchange(tls_msg)
        if isinstance(tls_msg, TLSFinished):
            # we should never get these unencrypted
            raise Exception("Unencrypted TLSFinished message")
        if isinstance(tls_msg, Raw):
            # If we get raw data, it means we couldn't interpret it.
            # Either, an error, or it's encrypted. If encrypted, 
            # it's a finished message. 
            # Decrypt is on the "tls_pkt", not the tls_msg
            tls_finished_msg = self.decrypt_tls_handshake_finished(tls_pkt)
            return self.process_tls_handshake_finished(tls_finished_msg)
        raise Exception("Unknown packet type {}".format(type(tls_msg)))
        
    def process_tls_handshake_client_hello(self, tls_msg):
        server_hello = None
        server_cert = None
        server_key_exchange = None
        server_hello_done = None
        
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
        f_session = tlsSession()
        f_session.tls_version = 0x303
        tls_response = TLS(msg=[server_hello, server_cert, server_key_exchange, server_hello_done],
            tls_session=f_session)
        tls_response_bytes = raw(tls_response)
        Debug.print_packet(tls_response)
        return tls_response_bytes
            
    def process_tls_handshake_key_exchange(self, tls_msg):    
        Debug.print("Got key exchange")
        Debug.print_packet(tls_msg)
        
        """
        1. process the client key exchange by extracting the "exchkeys"
        2. These can be passed directly to session.set_client_dh_params
        """ 
        return b'' # (No response necessary)
            
    def process_tls_handshake_finished(self, tls_msg):    
        Debug.print("Got Client Finished")
        Debug.print_packet(tls_msg)
        
        server_change_cipher_spec = None
        server_finished_msg = None
        encrypted_finished_msg = b""
        
        f_session = tlsSession()
        f_session.tls_version = 0x303
        
        # STUDENT TODO
        """
        1. process the decrypted TLS finished message. OPTIONALLY, verify the data:
            local_verify_data = session.compute_handshake_verify("read")
            local_verify_data ?= tls_msg.vdata
        2. Create the change cipher spec
        3. create the TLSFinished message. 
            Set v_data to session.compute_handshake_verify("write")
            because of scapy weirdness, set tls_session=f_session
        4. encrypt the tls finished message (server_finished_msg). You already have a method for this.
        5. store the encrypted bytes in encrypted_finished_msg
        """
        

        self.session.handshake = False

        change_cipher_msg = TLS(msg=[server_change_cipher_spec])
        Debug.print_packet(change_cipher_msg)
        
        server_finished_msg = TLS(msg=[server_finished], tls_session=f_session)
        Debug.print_packet(server_finished_msg)
        server_finished_msg.type = 22 # This is probably not necessary any more.
        
        
        Debug.print("attempt to cast to TLS Finished")
        f_session = tlsSession()
        f_session.tls_version = 0x303
        decrypted_msg = TLSFinished(plaintext, tls_session=f_session)
        return decrypted_msg
        

    def process_tls_data(self, data):
        Debug.record("visibility", data)
        ## STUDENT TODO:
        """
        Actually, there's nothing to-do here. However, I have 
        written this code to "swallow" exceptions for stability.
        But if you're having errors, they can get lost. Although
        the system will print out the top error in server.py, 
        the stack is currently lost. Comment out the try/except
        in order to get a stack trace at the point of failure.
        """
        try:
            return self.process_tls_data_unsafe(data)
        except Exception as e:
            return ("failure", e)

    def process_tls_data_unsafe(self, data):
        output = b""
        if self.session.handshake:
            result_type = "local_response"
        else:
            result_type = "proxy"
        tls_data = TLS(data)
        Debug.print("tls data without session")
        Debug.print_packet(tls_data)
        tls_pkts = [tls_data]
        # we are getting TLS messages smushed together as payloads
        next_payload = tls_data.payload
        tls_data.remove_payload()
        while next_payload and isinstance(next_payload, TLS):
            Debug.print("got packet of type", next_payload.type)
            tls_pkts.append(next_payload)
            next_payload2 = next_payload.payload
            next_payload.remove_payload()
            next_payload = next_payload2
            Debug.print("after detach, type is", tls_pkts[-1].type)
        Debug.print("Processing {} packets".format(len(tls_pkts)))
        while tls_pkts:
            tls_pkt = tls_pkts.pop(0)
            if tls_pkt.type == 22: # handshake
                for handshake_data in tls_pkt.msg:
                    response = self.process_tls_handshake(tls_pkt, handshake_data)
                    #self.session.handshake_messages += response
                    output += response
            elif tls_pkt.type == 20:
                Debug.print("Got Change Cipher Spec")
                Debug.print_packet(tls_pkt)
            elif tls_pkt.type == 21:
                print("Got Alert")
                raise Exception("Something went wrong with TLS")
            elif tls_pkt.type == 23:
                if self.session.handshake:
                    raise Exception("Got application data while still in handshake")
                
                application_data = b""
                # STUDENT TODO
                """
                1. We've received an application data packet. It will be encrypted
                2. decrypt the packet to application_data. You should already have a method for this.
                3. store in application_data
                """
                application_pkt = TLSApplicationData(application_data)
                Debug.print("Got {} bytes of decrypted data".format(len(application_pkt.data)))
                output += application_pkt.data
            else:
                print("Got unknown tls pkt type {}".format(pkt.type))
                tls_pkt.show2()

        return (result_type, output)
        
        
        
if __name__=="__main__":
    load_layer("tls")
    replay_file, cert_file, key_file = sys.argv[1:]
    with open(cert_file, "rb") as cert_obj:
        cert = x509.load_pem_x509_certificate(cert_obj.read())
    with open(key_file, "rb") as key_obj:
        priv_key = load_pem_private_key(key_obj.read(), password=None)
        
    Debug.config_logging(True, f=sys.stdout)
    
    with open("tls_replay.bin", "rb") as replay_reader:
        Debug.config_replay(True, reader=replay_reader)
        
        visibility_engine = TLS_Visibility(cert, priv_key)
        for message in Debug.replay_tag_iterator("visibility"):
            Debug.print("Replay message: ", message)
            result_type, result = visibility_engine.process_tls_data(message)
            Debug.print("Result:")
            Debug.print(result_type, result)
