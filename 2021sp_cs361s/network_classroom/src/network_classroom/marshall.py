import json

"""
Messages:
  <header len> <payload len>\n
  json
  binary
"""

def marshall(d, payload=b""):
    json_str = json.dumps(d)
    b = "{} {}\n{}".format(len(json_str), len(payload), json_str)
    return b.encode() + payload
    
def unmarshall(data):
    orig_data = data
    lens, data = data.split(b"\n", maxsplit=1)
    hlen, plen = [int(l.strip()) for l in lens.split(b" ")]
    if len(data) <  hlen+plen:
        return None, None, orig_data
    json_bytes, data = data[:hlen], data[hlen:]
    payload, r = data[:plen], data[plen:]
    return json.loads(json_bytes.decode()), payload, r