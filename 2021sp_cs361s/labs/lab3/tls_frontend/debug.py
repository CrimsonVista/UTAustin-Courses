import json

"""
Debug is a singleton that controls the debugging of the TLS Frontend.
""" 
class DataRecorder:
    def __init__(self, writer):
        self._writer = writer
        
    def record(self, tag, data):
        if type(data) == bytes:
            record = {
                'tag': tag,
                'len': len(data)
            }
            b = data
        else:
            record = {
                'tag': tag,
                'value': data
                }
            b = None
        j = json.dumps(record)
        self._writer.write(struct.pack("b", len(j)))
        self._writer.write(j.encode())
        if b:
            self._writer.write(b)

class NoMoreReplayTags(Exception):
    pass

class DataReplayer:
    def __init__(self, reader):
        self._reader = reader
        self._tag_buffer = {}
        self._can_read = True
        
    def _pop_record(self):
        if not self._can_read:
            return None, None
            
        rec_len_bytes = self._reader.read(1)
        if not rec_len_bytes: 
            self._can_read = False
            return None, None
        rec_len = struct.unpack("b", rec_len_bytes)[0]
        rec_bytes = self._reader.read(rec_len)
        rec = json.loads(rec_bytes.decode())
        if 'value' in rec: return rec['tag'], rec['value']
        b = self._reader.read(rec['len'])
        return rec['tag'], b
        
    def replay(self, tag):
        if tag in self._tag_buffer:
            next_value = self._tag_buffer[tag].pop(0)
            if len(self._tag_buffer[tag]) == 0:
                del self._tag_buffer[tag]
            return next_value
            
        next_tag, next_value = self._pop_record()
        while next_tag is not None and next_tag != tag:
            if next_tag not in self._tag_buffer:
                self._tag_buffer[next_tag] = []
            self._tag_buffer[next_tag].append(next_value)
            next_tag, next_value = self._pop_record()
        if next_tag is None or next_tag != tag:
            raise NoMoreReplayTags("No next tag {} found.".format(tag))
        return next_value   
            
class PopBytes:
    def __init__(self, b):
        self.bytestr = b
        
    def pop(self, l):
        popped, self.bytestr = self.bytestr[:l], self.bytestr[l:]
        return popped
            
class Debug:
    Enabled = {
        "logging":False,
        "random":False,
        "record":False,
        "replay":False,
    }
    Config = {
    }       
    @classmethod
    def config_logging(cls, enable, **opts):
        if not enable:
            cls.Enabled["logging"] = False
        else:
            cls.Enabled["logging"] = True
            if "f" not in opts or opts["f"] == None:
                f = sys.stdout
            else:
                f = opts["f"]
            cls.Config["logging"] = lambda *args, **kargs: f.write(" ".join([str(a) for a in args])+kargs.get('ending','\n'))
    
    @classmethod
    def config_record(cls, enable, **opts):
        if not enable:
            cls.Enabled["record"] = False
        else:
            cls.Enabled["record"] = True
            if "writer" not in opts:
                raise Exception("Record requires a writer")
            cls.Config["record"] = DataRecorder(opts["writer"])
    
    @classmethod
    def config_replay(cls, enable, **opts):
        if not enable:
            cls.Enabled["replay"] = False
        else:
            cls.Enabled["replay"] = True
            if "reader" not in opts:
                raise Exception("Replay requires a reader")
            cls.Config["replay"] = DataReplayer(opts["reader"])
            
    @classmethod
    def config_random(cls, enable, **opts):
        if not enable:
            cls.Enabled["random"] = False
        else:
            cls.Enabled["random"] = True
            if "seed" in opts:
                r_seed = int(opts["seed"])
                r = random.Random(r_seed)
                cls.Config["random"] = {
                    "type":"seed",
                    "generator": lambda len: bytes([r.getrandbits(8) for i in range(len)])
                }
            elif "generator" in opts:
                # generator is for replay where the number of bytes are ignored
                generator = opts["generator"]
                cls.Config["random"] = {
                    "type":"generator",
                    "generator": lambda len: next(generator)}
            elif "preload" in opts:
                popper = PopBytes(opts["preload"])
                cls.Config["random"] = {
                    "type":"preload",
                    "generator": lambda len: popper.pop(len)}
            else:
                raise Exception("Unknown configuration for debug random generator")
                
    
    @classmethod
    def print(cls, *args, **kargs):
        if not cls.Enabled["logging"]: return
        cls.Config["logging"](*args, **kargs)
        
    @classmethod
    def print_packet(cls, pkt, recalculate=False):
        if not cls.Enabled["logging"]: return
        if recalculate:
            data = pkt.show2(dump=True)
        else:
            data = pkt.show(dump=True)
        cls.Config["logging"](data)
        
    @classmethod
    def random(cls, len):
        if not cls.Enabled["random"]: return os.urandom(len)
        return cls.Config["random"]["generator"](len)
        
    @classmethod
    def replayable(cls, f, v_converter=None):
        def replayable_f(*args, **kargs):
            if cls.Enabled["replay"]:
                v = cls.replay(f.__name__)
                if v_converter:
                    v = v_converter("load", v)
                return v
            v = f(*args, **kargs)
            if cls.Enabled["record"]:
                v_record = v
                if v_converter:
                    v_record = v_converter("store", v_record)
                cls.record(f.__name__, v_record)
            return v
        return replayable_f
        
    @classmethod
    def record(cls, tag, data):
        if not cls.Enabled["record"]: return
        cls.Config["record"].record(tag, data)
        
    @classmethod
    def replay(cls, tag, default=None):
        if not cls.Enabled["replay"]: return default
        return cls.Config["replay"].replay(tag)
            
    @classmethod
    def replay_tag_iterator(cls, tag):
        if not cls.Enabled["replay"]: return None
        while True:
            try:
                next_value = cls.replay(tag)
            except NoMoreReplayTags:
                return
            yield next_value

            
        
