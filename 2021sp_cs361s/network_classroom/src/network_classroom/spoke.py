import asyncio, getpass, sys, os, random, hashlib, ssl
from .marshall import marshall, unmarshall
from scapy.all import *

from .shell.clishell import *

_ip_to_user = {}
_user_to_ip = {}

def user_to_ip(name):
    if name in _user_to_ip:
        return _user_to_ip[name]
    hash = hashlib.sha1(name.encode()).digest()
    a,b = 0, 0
    for i in range(10):
        a += hash[i]
        b += hash[10+i]
    ipaddr = "192.168.{}.{}".format(a%256, b%256)
    if ipaddr in _ip_to_user and _ip_to_user[ipaddr] != name:
        return _user_to_ip("_"+name)
    _ip_to_user[ipaddr] = name
    _user_to_ip[name] = ipaddr
    return ipaddr

class ProxyDataProtocol(asyncio.Protocol):
    def __init__(self, spoke, conn_user, conn_id, server):
        self.spoke = spoke
        self.conn_user = conn_user
        self.conn_id = conn_id
        if conn_id == None:
            # this is a client proxy. 
            self.inbound_direction = "s2c"
            self.outbound_direction = "c2s"
        else:
            self.inbound_direction = "c2s"
            self.outbound_direction = "s2c"
        self.server = server
        self.transport = None
        self.backlog = b""
        
    def connection_made(self, transport):
        print("connection made to {}".format(transport.get_extra_info("peername")))
        self.transport = transport
        if self.conn_id == None:
            t = asyncio.ensure_future(self.create_new_connection())
            t.add_done_callback(self.handle_new_connection)
        
    async def create_new_connection(self):
            conn_id = random.randint(1024,2**32)
            conn_hdr = {
                "command":"PROXY_CONNECTION",
                "conn_id":conn_id,
                "server":self.server
                }
            result = await self.spoke.await_send_request(conn_hdr, b"")
            self.conn_id = conn_id
            # proxy conns stores inbound directions
            self.spoke.proxy_conns[(self.conn_user, self.conn_id, self.inbound_direction)] = self
            
    def handle_new_connection(self, f):
        if f.exception() or self.conn_id is None:
            print("Proxy connection failed.", f.exception(), self.conn_id)
            self.transport.close()
            if (self.conn_user, self.conn_id, "client") in self.spoke.proxy_conns:
                del self.spoke.proxy_conns[(self.conn_user, self.conn_id)]
        else:
            self.data_received(b"")
        
    def data_received(self, data):
        if self.conn_id is None:
            self.backlog += data
            return
        if self.backlog:
            data = self.backlog + data
            self.backlog = b""
        if not data: return
        proxy_data_hdr = {
            "command":"PROXY_DATA",
            "conn_user":self.conn_user,
            "conn_id":self.conn_id,
            "direction":self.outbound_direction
        }
        asyncio.ensure_future(self.spoke.await_send_request(proxy_data_hdr, data))
        
    def connection_lost(self, reason=None):
        self.transport = None
        if self.conn_id is not None: 
        
            close_conn_hdr = {
                "command":"CLOSE_CONNECTION",
                "conn_user":self.conn_user,
                "conn_id":self.conn_id,
            }
            asyncio.ensure_future(self.spoke.await_send_request(close_conn_hdr, b""))

class NetworkClassroomSpoke(asyncio.Protocol):
    def __init__(self):
        self.sent_requests = {}
        self.proxy_conns = {}
        self.username = None
        self.tap_sink = None
        self.tcp_seq = {}
        self.buffer = b""

    def connection_made(self, transport):
        self.transport = transport
        
    async def login(self, username, password, reg_code=None):
        login_hdr = {
            "command":"LOGIN_USER",
            "username":username,
            "password":password
        }
        self.username = username
        if reg_code is not None:
            login_hdr["registration_code"] = reg_code
        return await self.await_send_request(login_hdr)
        
    async def list_users(self):
        list_hdr = {
            "command":"LIST_USERS"
            }
        return await self.await_send_request(list_hdr)

    async def list_servers(self):
        list_hdr = {
           "command":"LIST_SERVERS"
        }
        return await self.await_send_request(list_hdr)
        
    async def create_proxy_server(self, port, server_alias=""):
        proxy_hdr = {
            "command":"PROXY_SERVER",
            "port":port,
            "server_alias":server_alias}
        return await self.await_send_request(proxy_hdr)
        
    async def stop_proxy_server(self, port):
        proxy_hdr = {
            "command":"PROXY_SERVER_STOP",
            "port":port}
        return await self.await_send_request(proxy_hdr)
        
    async def create_proxy_connection(self, local_port, server):
        await asyncio.get_event_loop().create_server(lambda: ProxyDataProtocol(self, self.username, None, server), port=local_port)
        
    async def connect_to_server(self, conn_user, conn_id, port):
        #self.proxy_conns[(conn_user, conn_id, "server")] = None
        transport, protocol = await asyncio.get_event_loop().create_connection(lambda: ProxyDataProtocol(self, conn_user, conn_id, None), port=port)
        # store inbound direction
        self.proxy_conns[(conn_user, conn_id, protocol.inbound_direction)] = protocol
        
    def handle_connect_to_server(self, f, push_id):
        response = {
            "request_id":0,
            "command":"push_response",
            "push_id":push_id
        }
        if f.exception():
            response["result"] = "failed"
            response["error"] = str(f.exception())
        else:
            response["result"] = "success"
        self.transport.write(
            marshall(
                response,
                b""
            )
        )
        
    async def tap_server(self, server_id):
        tap_hdr = {
            "command":"TAP_SERVER",
            "server":server_id
            }
        return await self.await_send_request(tap_hdr)
        
    async def stop_tap_server(self, server_id):
        tap_hdr = {
            "command":"STOP_TAP_SERVER",
            "server":server_id
            }
        return await self.await_send_request(tap_hdr)
            
    def send_request(self, hdr, payload=b""):
        hdr["request_id"] = os.urandom(4).hex()
        self.sent_requests[hdr["request_id"]] = hdr
        request = marshall(hdr, payload)
        #print("Send request", request)
        self.transport.write(request)
        return hdr["request_id"]
        
    async def await_send_request(self, hdr, payload=b""):
        request_id = self.send_request(hdr, payload)
        self.sent_requests[request_id]["__future__"] = asyncio.get_event_loop().create_future()
        return await self.await_response(request_id)
        
    async def await_response(self, request_id):
        if request_id in self.sent_requests and "__future__" in self.sent_requests[request_id]:
            result =  await self.sent_requests[request_id]["__future__"]
            del self.sent_requests[request_id]
            return result
        return None
            
    def data_received(self, data):
        try:
            self.data_received_unsafe(data)
        except Exception as e:
            print("Failure:",e)
            # any untrapped exception should trigger all current futures
            for request_id in self.sent_requests:
                if "__future__" in self.sent_requests[request_id]:
                    self.sent_requests[request_id]["__future__"].set_exception(e)
                    
    def handle_push(self, header, payload):
        h = header
        if h["command"] == "connect":
            f = asyncio.ensure_future(self.connect_to_server(h["conn_user"], h["conn_id"], h["port"]))
            f.add_done_callback(lambda f: self.handle_connect_to_server(f, h["push_id"]))
        elif h["command"] == "data":
            conn_user, conn_id, direction = h["conn_user"], h["conn_id"], h["direction"]
            push_response = {
                "command":"push_response",
                "request_id":0,
                "push_id":h["push_id"]
            }
            proxy_key = (conn_user, conn_id, direction)
            if proxy_key not in self.proxy_conns or self.proxy_conns[proxy_key].transport is None:
                push_response["result"] = "failed"
                push_response["error"] = "No such connection"
            else:
                push_response["result"] = "success"
                print("Spoke transmitting {} bytes to proxy".format(len(payload)))
                self.proxy_conns[proxy_key].transport.write(payload)
            self.transport.write(
                marshall(
                    push_response,
                    b""
                )
            )
        elif h["command"] == "tap_data":
            # build a fake set of packets to represent the user to user communication
            # IP address will be 192.168.A.B where A.B are assigned per username
            # source port will be conn_id, dest port will be the actual port
            #print("got tap data. Sink={}".format(repr(self.tap_sink)))
            if self.tap_sink == None:
                return
            server_user, server_port = h["server_id"].split(":")
            if h["direction"] == "c2s":
                src_ip = user_to_ip(h["conn_user"])
                dst_ip = user_to_ip(server_user)
                src_port = h["conn_id"]
                dst_port = int(server_port)
            else:
                src_ip = user_to_ip(server_user)
                dst_ip = user_to_ip(h["conn_user"])
                src_port = int(server_port)
                dst_port = h["conn_id"]
            tcp_key = (src_ip, src_port, dst_ip, dst_port)
            seq = self.tcp_seq.get(tcp_key, 0)
            self.tcp_seq[tcp_key] = seq + len(payload)
            #print(tcp_key, seq, self.tcp_seq[tcp_key])
            pkt = Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=src_port, dport=dst_port, seq=seq, flags='')/payload
            #pcap_name = self.tap_sink
            #if os.path.exists(pcap_name) and not os.path.isfile(pcap_name):
            #    # assume that non-file, existing paths are pipes. Open object in non-blocking mode
            #    pcap_name = os.fdopen(os.open(self.tap_sink, os.O_RDWR), "wb")
            #wrpcap(pcap_name, [pkt], sync=True)
            self.tap_sink.write(pkt)
            self.tap_sink.flush()
        elif h["command"] == "close_connect":
            conn_user, conn_id = h["conn_user"], h["conn_id"]
            for direction in ["c2s", "s2c"]:
                proxy_key = (conn_user, conn_id, direction)
                if proxy_key in self.proxy_conns:
                    if self.proxy_conns[proxy_key].transport is not None:
                        self.proxy_conns[proxy_key].transport.close()
                    del self.proxy_conns[proxy_key]
        else:
            raise Exception("Unknown push type {}".format(h["command"]))
    
    def data_received_unsafe(self, data):
        #print("Data received", data)
        data = self.buffer + data
        self.buffer = b""
        while data:
            h, payload, data = unmarshall(data)
            if h == None:
                self.buffer += data
                return
            print(h)
            response_id = h.get("response_id", None)
            if response_id in self.sent_requests and "__future__" in self.sent_requests[response_id]:
                response_future = self.sent_requests[response_id]["__future__"]
            else:
                response_future = None
            
            if h.get("error",None):
                print("Server Error: {}".format(h["error"])) 
                #self.transport.close()
                #raise Exception("Server error: {}".format(h["error"]))
                
            if response_id == "push":
                self.handle_push(h, payload)
                        
            elif response_future == None:
                # error reporting?
                self.transport.close()
                raise Exception("Internal error. Unexpected response {}".format(response_id))
            
            if response_future:            
                req = self.sent_requests[h["response_id"]]
                response_future.set_result(h)
                
    def connection_lost(self, reason):
        print("Connection lost. shutdown", reason)
        self.stop()

    def stop(self):
        if self.tap_sink:
            self.tap_sink.close()
            self.tap_sink = None
        asyncio.get_event_loop().stop()
                
class NetworkClassroomSpokeController:
    def __init__(self, spoke, username, password):
        self.spoke = spoke
        self.user = username
        self.password = password
        
    async def login(self, writer):
        result = await self.spoke.login(self.user, self.password)
        writer("Logged in.\n")
        
    async def register(self, writer, reg_code):
        reg_code = int(reg_code)
        writer("Registering user with code {}\n".format(reg_code))
        result = await self.spoke.login(self.user, self.password, reg_code)
        writer("Registered and logged in.\n")
        
    async def list_users(self, writer):
        result = await self.spoke.list_users()
        writer("Users logged in to the Network Hub:\n")
        for username in result["users"]:
            user_to_ip(username)
            writer("\t{}\n".format(username))

    async def list_servers(self, writer):
        result = await self.spoke.list_servers()
        writer("Current servers in the Network Hub:\n")
        for port, alias in result["servers"]:
            writer("\t{} (alias: {})\n".format(port, alias))
            
    async def start_server(self, writer, port, alias=""):
        result = await self.spoke.create_proxy_server(int(port), alias)
        writer("Now accepting proxy data on port {}\n".format(port))
        
    async def stop_server(self, writer, port, alias=""):
        result = await self.spoke.stop_proxy_server(int(port))
        if "error" in result and result["error"]:
            writer("Stop listening failed: {}".format(result["error"]))
        else:
            writer(result["result"])
        
    async def connect(self, writer, port, server_id):
        result = await self.spoke.create_proxy_connection(port, server_id)
        writer("Port {} forwarded to server {}\n".format(port, server_id))

    def set_tap_sink(self, filename):
        if os.path.exists(filename) and not os.path.isfile(filename):
            # assume pipe
            fd = os.open(filename, os.O_RDWR)
            f = os.fdopen(fd, "wb")
            self.spoke.tap_sink = PcapWriter(f)
        else:
            self.spoke.tap_sink = PcapWriter(filename)

    async def export_user_hosts(self, writer, filename):
        with open(filename, "w+") as f:
            for ipaddr in _ip_to_user:
                f.write("{} {}\n".format(ipaddr, _ip_to_user[ipaddr]))
         
def configure_ui(shell, spoke):  
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    spoke_controller = NetworkClassroomSpokeController(spoke, username, password)
    
    login = CLICommand("login", "Log in to the system. Must already be registered", 
        lambda writer, *args: asyncio.ensure_future(spoke_controller.login(writer)))
    register = CLICommand("register", "Register and log into the system.",
        lambda writer, reg_code, *args: asyncio.ensure_future(spoke_controller.register(writer, reg_code)))
    list_users=CLICommand("list_users", "List users currently connected",
        lambda writer, *args: asyncio.ensure_future(spoke_controller.list_users(writer)))
    list_servers=CLICommand("list_servers", "List servers currently available",
        lambda writer, *args: asyncio.ensure_future(spoke_controller.list_servers(writer)))
        
    start_server=CLICommand("listen", "Accept data to forward to local servers",
        mode=CLICommand.STANDARD_MODE)
    start_server.configure(
        numArgs=2, 
        usage="<port> <alias>", 
        helpTxt="Permit proxy to connect to local <port>. Provide a proxy-wide <alias>",
        cmdHandler=lambda writer, *args: asyncio.ensure_future(spoke_controller.start_server(writer, *args)))
    start_server.configure(
        numArgs=1, 
        usage="<port>", 
        helpTxt="Permit proxy to connect to local <port>.",
        cmdHandler=lambda writer, *args: asyncio.ensure_future(spoke_controller.start_server(writer, *args)))
    
    stop_server=CLICommand("stoplisten", "Stop listening on a port", mode=CLICommand.STANDARD_MODE)
    stop_server.configure(
        numArgs=1,
        usage="<port>",
        helpTxt="Stop listening on port <port> for proxying.",
        cmdHandler=lambda writer, *args: asyncio.ensure_future(spoke_controller.stop_server(writer, *args)))
    
    connect=CLICommand("forward", "Forward connections from a local port to a proxy server. ", mode=CLICommand.STANDARD_MODE)
    connect.configure(
        numArgs=2, 
        usage="<port> <server_id>",
        helpTxt="Start forwarding from <port> to <server_id>. <server_id> must either be a known alias or <username>:<server port>",
        cmdHandler=lambda writer, *args: asyncio.ensure_future(spoke_controller.connect(writer, *args)))
        
    tap=CLICommand("tap", "Tap all communications to/from a server",
        lambda writer, *args: asyncio.ensure_future(spoke.tap_server(*args)))
    untap=CLICommand("stop_tap", "Stop an existing server tap",
        lambda writer, *args: asyncio.ensure_future(spoke.stop_tap_server(*args)))
        
    tap_sink=CLICommand("set_tap_sink", "Set the sink file or pipe for tap data",
        lambda writer, *args: spoke_controller.set_tap_sink(*args))
    spoke_controller.set_tap_sink("/tmp/dump1.pcap")
    
    export_hosts=CLICommand("export_user_ips", "Export a hosts file mapping ip to user. This helps wireshark resolve the made-up ip addresses into the user names", lambda writer, *args: asyncio.ensure_future(spoke_controller.export_user_hosts(writer, *args)))

    shell.registerCommand(login)
    shell.registerCommand(register)
    shell.registerCommand(list_users)
    shell.registerCommand(list_servers)
    shell.registerCommand(start_server)
    shell.registerCommand(stop_server)
    shell.registerCommand(connect)
    shell.registerCommand(tap)
    shell.registerCommand(untap)
    shell.registerCommand(tap_sink)
    shell.registerCommand(export_hosts)
    shell.registerExitListener(lambda *args: spoke.stop())
    
def build_ui(spoke):
    shell = CLIShell()
    configure_ui(shell, spoke)
    a = AdvancedStdio(shell)
                
registration_code = None
addr = sys.argv[1]
if "--port" in sys.argv:
    port = int(sys.argv[sys.argv.index("--port")+1])
else:
    port = 34150
if "--no-tls" in sys.argv:
    ssl_context = None
else:
    ssl_context = ssl.create_default_context()
    if addr == "127.0.0.1":
        ssl_context.check_hostname = False
    ssl_context.load_verify_locations(cafile="cert.pem")

loop = asyncio.get_event_loop()
loop.set_debug(True)
spoke = NetworkClassroomSpoke()

coro = loop.create_connection(lambda: spoke, addr, port, ssl=ssl_context)
print("create connection to {}:{}".format(addr, port))
loop.run_until_complete(coro)
print("Connection created. Create UI")
loop.call_soon(lambda: build_ui(spoke))
loop.run_forever()
print("Connection closed")
