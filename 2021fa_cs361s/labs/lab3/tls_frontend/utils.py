from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, load_pem_private_key
from scapy.all import *
import time

from .debug import Debug

load_layer("tls")
    
def DHParamsSerialization(mode, data):
    if mode == "load":
        raw_param_len_bytes, data = data[:4], data[4:]
        raw_param_len = struct.unpack('!L', raw_param_len_bytes)[0]
        raw_params, raw_dh_priv_key = data[:raw_param_len], data[raw_param_len:]
        params = ServerDHParams(raw_params, tls_session=tlsSession())
        dh_priv_key = load_pem_private_key(raw_dh_priv_key, password=None)
        params.tls_session.server_kx_privkey = dh_priv_key
        params.fill_missing()
        return params
    elif mode == "store":
        params = data
        params.fill_missing()
        raw_params = raw(params)
        dh_priv_key = params.tls_session.server_kx_privkey
        raw_dh_priv_key = dh_priv_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        return struct.pack("!L", len(raw_params)) + raw_params + raw_dh_priv_key
    else:
        raise Exception("Unknown mode {}".format(mode))
   