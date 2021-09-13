import asyncio, hashlib, sys, ssl, shelve, random
from .marshall import marshall, unmarshall
from .shell.clishell import *

def SHA256(data):
    return hashlib.sha256(data.encode()).hexdigest()

class NetworkClassroomHub:
    """
    commands:
        LIST USERS
        LIST SERVERS
        LIST CONNECTIONS [server_name/USER:port]
        PROXY SERVER name ON port
        PROXY CONNECT server_name/USER:port ON client_port
        CLOSE server_port
        TAP output=file/named_pipe [client=USER:port] [server=server_name/USER:port] [user=USER[:port]]
    """
    def __init__(self, auth):
        self.registration_code = None
        self.users = {}
        self.auth = auth
        self.server_aliases = {}
        self.pushes = {}
        self.debug_handler = lambda *args: args
        
    def set_debug_handler(self, handler):
        self.debug_handler = handler
    
    def build(self):
        return NetworkClassroomHubSession(self)
        
    def close_connection(self, conn_user, conn_id, msg=""):            
        conn_obj, conn_servers, conn_conns = self.users.get(conn_user, (None, None, None))
        if conn_obj == None:
            return
        conn_obj.send_close_connection(conn_user, conn_id, msg)
        if conn_id in conn_conns:
            server_user, port = conn_conns[conn_id]
            del conn_conns[conn_id]
            if server_user not in self.users: return
            
            server_obj, server_servers, server_conns = self.users[server_user]
            if port  not in server_servers: return
            
            server_alias, server_inbound_conns, server_taps = server_servers[port]
            if (conn_user, conn_id) not in server_inbound_conns: return
            server_inbound_conns.remove((conn_user, conn_id))
            server_obj.send_close_connection(conn_user, conn_id, msg)
            
    def close_server(self, server_user, port, msg=""):
        server_obj, server_servers, server_conns = self.users.get(server_user, (None, None, None))
        if server_obj == None:
            return
        if port not in server_servers:
            return
        server_alias, server_conns, server_taps = server_servers[port]
        while server_conns:
            conn_user, conn_id = next(iter(server_conns))
            self.close_connection(conn_user, conn_id, msg)
            if (conn_user, conn_id) in server_conns:
                server_conns.remove((conn_user, conn_id))
        for tap_user in server_taps:
            tap_obj, t_s, t_c = self.users.get(tap_user, (None, None, None))
            if not tap_obj: continue
            server_id = server_alias
            if not server_id:
                server_id = "{}:{}".format(server_user, port)
            #TODO: tap_obj.send_close_tap(server_id)
        server_taps.clear()
        del server_servers[port]
        if server_alias and server_alias in self.server_aliases:
            del self.server_aliases[server_alias]
        
class NetworkClassroomHubSession(asyncio.Protocol):
    def __init__(self, hub):
        self.hub = hub
        self.users = self.hub.users
        self.auth = self.hub.auth
        self.server_aliases = self.hub.server_aliases
        self.connected_user = None
        self.pushes = self.hub.pushes
        self.buffer = b""
        
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        try:
            self.data_received_unsafe(data)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.hub.debug_handler("Error in data received.")
            self.hub.debug_handler("\n".join(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
            self.transport.write(
                marshall({
                    "response_id":"",
                    "error":str(e)}
                )
            )
            
    def data_received_unsafe(self, data):
        data = self.buffer + data
        self.buffer = b""
        while data:
            h, payload, data = unmarshall(data)
            if h == None:
                self.buffer += data
                return
            response = {
                    "response_id":h["request_id"]
            }
            response_payload = b""
            
            if h["command"] == "push_response":
                push_id = h["push_id"]
                if push_id not in self.pushes:
                    raise Exception("Unknown push response {}".format(push_id))
                push, arg = self.pushes[push_id]
                if push["command"] == "connect":
                    connecting_user, connecting_response = arg
                    connecting_obj, connecting_servers, connecting_connections = self.users.get(connecting_user, (None, None, None))
                    
                    if connecting_obj is None:
                        # no need to try globally. Not in global data structure.
                        self.send_close_connection(connecting_user, h["conn_id"])
                    elif push["conn_id"] not in connecting_connections or (None, push_id) != connecting_connections[push["conn_id"]]:
                        connecting_response["result"] = "failed"
                        connecting_response["error"] = "Peer misconfigured."
                        # global misconfig. Try global close
                        self.hub.close_connection(connecting_user, push["conn_id"], "Invalid connection data")
                    elif h["result"] == "success":
                        self.hub.debug_handler("Success opening connection.")
                        # the server responded to the push. Add the connection for this port
                        connected_user_servers = self.users[self.connected_user][1]
                        server_inbound_conns = connected_user_servers[push["port"]][1]
                        server_inbound_conns.add((connecting_user, push["conn_id"]))
                        connecting_connections[push["conn_id"]] = (self.connected_user, push["port"])
                        connecting_response["result"] = "success"
                    else:
                        connecting_response["result"] = "failed",
                        connecting_response["error"] = h["error"]
                        
                    if connecting_obj: connecting_obj.transport.write(
                        marshall(
                            connecting_response,
                            b""
                            )
                        )
                elif push["command"] == "data":
                    if h["result"] == "failed":
                        # attempt to globally close this connection
                        self.hub.close_connection(push["conn_user"], push["conn_id"])
                        
                # push commands are different. Move on
                continue
            
            if h["command"] == "LOGIN_USER":
                username = h["username"]
                if self.connected_user:
                    response["error"] = "Cannot connect multiple users per session"
                elif "registration_code" in h:
                    if username in self.auth:
                        response["error"] = "User {} already registered".format(username)
                    elif h["registration_code"] != self.hub.registration_code:
                        response["error"] = "Invalid registration code"
                    else:
                        response["result"] = "Logged in"
                        self.auth[username] = SHA256(h["password"])
                        self.connected_user = username
                        self.users[h["username"]] = [self, {}, {}]
                elif self.auth.get(username,None) != SHA256(h["password"]):
                    response["error"] = "Invalid username or password"
                else:
                    response["result"] = "Logged in"
                    self.connected_user = username
                    self.users[h["username"]] = [self, {}, {}]
            else:
                this_conn, user_servers, user_connections = self.users.get(self.connected_user, (None, None, None))
                if this_conn != self:
                    response["error"] = "Not logged in"
                elif h["command"] == "LIST_USERS":
                    response["users"] = list(self.users.keys())
                elif h["command"] == "LIST_SERVERS":
                    s_list = []
                    for user in self.users:
                        servers = self.users[user][1]
                        for port in servers:
                            s_list.append(("{}:{}".format(user, port), servers[port][0]))
                    response["servers"] = s_list
                elif h["command"] == "PROXY_SERVER":
                    port = h["port"]
                    server_alias = h["server_alias"]
                    if port in user_servers:
                        response["error"] = "Port already in use"
                    elif type(port) != int or port < 0:
                        response["error"] = "Port must be a positive integer"
                    elif server_alias and server_alias in self.server_aliases:
                        response["error"] = "Alias already in use"
                    elif ":" in server_alias:
                        response["error"] = "Server alias cannot use ':'"
                    else:
                        if server_alias:
                            self.server_aliases[server_alias] = "{}:{}".format(self.connected_user, port)
                        user_servers[port] = (server_alias, set([]), set([]))
                        response["result"] = "Proxy Server Port Open"
                elif h["command"] == "PROXY_SERVER_STOP":
                    port = h["port"]
                    if port  not in user_servers:
                        response["error"] = "Port not in use"
                    elif type(port) != int or port < 0:
                        response["error"] = "Port must be positive integer"
                    else:
                        server_alias = user_servers[port][0]
                        if server_alias in self.server_aliases:
                            del self.server_aliases[server_alias]
                        del user_servers[port]
                        response["result"] = "Proxy Server Port {} Closed".format(port)
                elif h["command"] == "CLOSE_SERVER":
                    port = h["proxy_port"]
                    if port  not in user_servers:
                        response["error"] = "No server open on port {}".format(port)
                    else:
                        self.hub.close_server(self.connected_user, port)
                        for alias in self.server_aliases:
                            if self.server_aliases[alias] == "{}:{}".format(self.connected_user, port):
                                del self.server_aliases[alias]
                                break
                        
                elif h["command"] == "PROXY_CONNECTION":
                    server = h["server"]
                    user_port = self.server_aliases.get(server, server)
                    conn_id = h["conn_id"]
                    if conn_id in user_connections:
                        response["error"] = "Connectin ID already in use."
                    elif ":" not in server and ":" not in user_port:
                        # it was an alias (no ":") but didn't resolve
                        response["error"] = "No such server {}".format(server)
                    elif ":" not in user_port:
                        response["error"] = "Invalid format or other error"
                    else:
                        server_user, port = user_port.split(":")
                        port = int(port)
                        server_obj, server_ports, server_connects = self.users.get(server_user, (None, None, None))
                        if server_obj is None:
                            response["error"] = "No user {} logged in.".format(server_user)
                        elif port not in server_ports:
                            response["error"] = "No server for user {} on port {}".format(server_user, port)
                        else:
                            push_connect = {
                                "response_id":"push",
                                "push_id":os.urandom(4).hex(),
                                "command":"connect",
                                "port":port,
                                "conn_user":self.connected_user,
                                "conn_id":conn_id
                            }
                            # TODO: Do I need to remove this? Or add error handling?
                            user_connections[conn_id] = (None, push_connect["push_id"])
                            server_obj.transport.write(marshall(push_connect, b""))
                            self.pushes[push_connect["push_id"]] = (push_connect, (self.connected_user, response))
                            response = None
                elif h["command"] == "PROXY_DATA":
                    conn_user = h["conn_user"]
                    conn_id = h["conn_id"]
                    direction = h["direction"]
                    self.hub.debug_handler("Proxy Data.", conn_user, conn_id, direction)
                    
                    conn_obj, conn_servers, conn_conns = self.users.get(conn_user, (None, None, None))
                    if conn_obj is None or conn_id not in conn_conns:
                        response["error"] = "Unknown connection {}".format((conn_user, conn_id, direction))
                        # no global info. Send local close
                        self.send_close_connection(conn_user, conn_id, "Unknown connection")
                    else:
                        server_user, server_port = conn_conns[conn_id]
                        server_obj, server_servers, server_conns = self.users.get(server_user, (None, None, None))
                        
                        if direction == "c2s":
                            dest_user = server_user
                            dest_obj = server_obj
                        elif direction == "s2c":
                            # the dest is just the client itself
                            dest_user = conn_user
                            dest_obj = conn_obj
                            
                        if not server_servers or server_port not in server_servers:
                            response["error"] = "Unknown connection or server closed"
                            self.hub.close_connection(conn_user, conn_id, "Unknown connection or server closed")
                        elif dest_obj is None or dest_obj.transport is None:
                            response["error"] = "Unknown connection or connection closed"
                            # global. Try global shutdown.
                            self.hub.close_connection(conn_user, conn_id, "Unknown connection or connection closed")
                        else:
                            response["result"] = "success"
                            push_data = {
                                "response_id":"push",
                                "push_id":os.urandom(4).hex(),
                                "command":"data",
                                "conn_user":h["conn_user"],
                                "conn_id":h["conn_id"],
                                "direction":h["direction"]
                            }
                            self.pushes[push_data["push_id"]] = (push_data, None)
                            dest_obj.transport.write(
                                marshall(
                                    push_data,
                                    payload
                                )
                            )
                            server_alias, server_inbound_conns, tap_conns = server_servers[server_port]
                            server_id = "{}:{}".format(server_user, server_port)
                            # push id 0. DO NOT RESPOND
                            push_data["push_id"] = 0
                            push_data["server_id"] = server_id
                            push_data["command"] = "tap_data"
                            removed = []
                            tap_data = marshall(
                                push_data,
                                payload
                            )
                            for tap_user in tap_conns:
                                tap_user_obj, ts, tc = self.users.get(tap_user, (None, None, None))
                                if not tap_user_obj or tap_user_obj.transport is None:
                                    removed.append(tap_user)
                                else:
                                    tap_user_obj.transport.write(tap_data)
                            for removed_tap_user in removed:
                                tap_conns.remove(removed_tap_user)
                            
                elif h["command"] == "CLOSE_CONNECTION":
                    conn_user = h["conn_user"]
                    conn_id = h["conn_id"]
                    
                    self.hub.close_connection(conn_user, conn_id)
                elif h["command"] == "TAP_SERVER" or h["command"] == "STOP_TAP_SERVER":
                    server = h["server"]
                    user_port = self.server_aliases.get(server, server)
                    if ":" not in server and ":" not in user_port:
                        # it was an alias (no ":") but didn't resolve
                        response["error"] = "No such server {}".format(server)
                    elif ":" not in user_port:
                        response["error"] = "Invalid format or other error"
                    else:
                        server_user, port = user_port.split(":")
                        port = int(port)
                        server_obj, server_servers, server_conns = self.users.get(server_user, (None, None, None))
                        if server_user not in self.users:
                            response["error"] = "No such user {}".format(server_user)
                        elif port not in server_servers:
                            response["error"] = "No such server {}:{} ({})".format(server_user, port, server)
                        else:
                            server_alias, server_inbound_conns, tap_conns = server_servers[port]
                            if h["command"] == "TAP_SERVER":
                                tap_conns.add(self.connected_user)
                                response["result"] = "success"
                            elif self.connected_user in tap_conns:
                                tap_conns.remove(self.connected_user)
                                response["result"] = "success"
                            else:
                                response["error"] = "Server not tapped"
                else:
                    response["error"] = "Unknown Command {}".format(h["command"])
            if response:
                self.transport.write(marshall(response, response_payload))
            
    def send_close_connection(self, conn_user, conn_id, msg=""):
        if not self.transport:
            return 
        # Best effort. No response required (push_id 0)
        push_close = {
            "response_id":"push",
            "push_id":0,
            "command":"close_connect",
            "conn_user":conn_user,
            "conn_id":conn_id,
            "message":msg}
        self.transport.write(
            marshall(
                push_close,
                b"")
        )
                
    def connection_lost(self, reason):
        if self.connected_user and self.connected_user in self.users:
            conn_obj, servers, conns = self.users[self.connected_user]
            while servers:
                port = next(iter(servers))
                self.hub.close_server(self.connected_user, port)
                if port in servers:
                    del servers[port]
            while conns:
                conn_id = next(iter(conns))
                self.hub.close_connection(self.connected_user, conn_id, "connection lost")
                if conn_id in conns:
                    del conns[conn_id]
            del self.users[self.connected_user]

class NetworkClassroomHubController:
    def __init__(self, hub):
        self.hub = hub
        
    def change_registration(self, writer, reg="random"):
        if reg == "random":
            reg = random.randint(1,9999999)
        elif reg == "None":
            reg = None
        else: reg = int(reg)
        self.hub.registration_code = reg
        writer("Registration changed to {}.\n".format(reg))
        
    def list_user_data(self, writer):
        for username in self.hub.users:
            writer("* {}\n".format(username))
            userobj, servers, conns = self.hub.users[username]
            for port in servers:
                alias, server_conns, tap_conns = servers[port]
                writer("\t- port {} (Alias={}): {} connections]\n".format(port, alias, len(server_conns)))
            for conn_id in conns:
                remote_user, remote_port = conns[(user_obj, conn_id)]
                if remote_user in self.hub.users and remote_port in self.hub.users[remote_user][1]:
                    alias = self.hub.users[remote_user][1][0]
                else:
                    alias = "<Broken Connection?>"
                writer("\t- outbound conn {} to {}:{} (alias: {})\n".format(conn_id, remote_user, remote_port, alias))
        writer("\n")
        
def quit(shell, writer, *args):
    shell.quit()
    asyncio.get_event_loop().stop()
         
def configure_ui(shell, hub):         
    hub_controller = NetworkClassroomHubController(hub)
    hub.set_debug_handler(lambda *args: print("DEBUG:", *args))
    
    setRegistration = CLICommand("set_register", "Set registration", mode=CLICommand.STANDARD_MODE,
        defaultCb=hub_controller.change_registration)
    setRegistration.configure(
        numArgs=1, 
        cmdHandler=hub_controller.change_registration, 
        usage="[code]",
        helpTxt="Sets the registration code. If code is not specified, pick a random value.")
        
    list_connections = CLICommand("user_data", "List users, their servers and connections",
        hub_controller.list_user_data)
    
    shell.registerCommand(setRegistration)
    shell.registerCommand(list_connections)
    shell.registerExitListener(lambda *args: asyncio.get_event_loop().stop())
    
def build_ui(hub):
    shell = CLIShell()
    configure_ui(shell, hub)
    a = AdvancedStdio(shell)

if "--port" in sys.argv:
    port = int(sys.argv[sys.argv.index("--port")+1])
else:
    port = 34150
print("Starting hub on port {}".format(port))
                
loop = asyncio.get_event_loop()
loop.set_debug(True)
auth = shelve.open("hub.auth")
hub = NetworkClassroomHub(auth)
if os.path.exists("key.pem"):
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain("cert.pem", "key.pem")
else:
    choice = input("No server key/cert. Start without ssl [yes/no]? ")
    if choice.lower()[0] != 'y':
        sys.exit("Not starting unprotected hub")
    ssl_context=None
coro = loop.create_server(hub.build, port=port, ssl=ssl_context)
server = loop.run_until_complete(coro)
loop.call_soon(lambda: build_ui(hub))

# Serve requests until Ctrl+C is pressed
#print('Network Hub on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
auth.close()
loop.run_until_complete(server.wait_closed())
loop.close()
