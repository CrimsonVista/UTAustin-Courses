import time
import http.server
import os
import sys
import urllib

cross_site_javascript_request = """
<button id="ajaxButton" type="button">Make a request</button>

<script>
(function() {
  var httpRequest;
  document.getElementById("ajaxButton").addEventListener('click', makeRequest);

  function makeRequest() {
    httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
      alert('Giving up :( Cannot create an XMLHTTP instance');
      return false;
    }
    httpRequest.onreadystatechange = alertContents;
    httpRequest.open('GET', 'http://127.0.0.1/mess');
    httpRequest.send();
  }

  function alertContents() {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      if (httpRequest.status === 200) {
        alert(httpRequest.responseText);
      } else {
        alert('There was a problem with the request: '+httpRequest.status);
      }
    }
  }
})();
</script>
"""

connections = {}

class MyHandler(http.server.BaseHTTPRequestHandler):
    def _setup(self):
        self._routes = {
            '/login':self._handle_login,
            '/cross_site_request' :self._handle_cross_site_request,
            '/csrf' : self._handle_csrf,
            '/transfer':self._handle_transfer
        }
        self._session = None
        self._cookie = None

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
    def do_GET(self):
        self._setup()
        self._method = "GET"
        self.render_page()
        
    def do_POST(self):
        print("got post")
        self._setup()
        self._method = "POST"
        self.render_page()
        
    def _handle_cross_site_request(self):
        return cross_site_javascript_request, {}
        
    def _handle_csrf(self):
        hidden_form = """
<form id="csrfForm" target="_blank" action="http://127.0.0.1/transfer" method="POST">
          <input type="hidden" name="recipient" value="evil csrf" />
        </form>
        
<script>
function onLoadDoCsrf() {
  document.getElementById('csrfForm').submit()
  alert('submitted form')
}
window.onload = onLoadDoCsrf
</script>
"""
        return hidden_form,{}
        
    def _handle_transfer(self):
        page_content, headers = "", {}
        if self._session == None:
            page_content = "<P>Cannot transfer. No session</P>"
        elif self._method == "POST":
            if "Content-Length" not in self.headers:
                page_content += "<P>Transfer Post Received, But no Content. Cannot Transfer</P>"
            else:
                content_length = int(self.headers["Content-Length"])
                form_contents = self.rfile.read(content_length)
                form_contents = urllib.parse.unquote(form_contents.decode())
                label, data = form_contents.split("=")
                page_content += "<P>Post Received: {}={}</P>".format(label, data)
                self._session["transfers"].append(data)
        else:
            page_content += """
<form action="/transfer" method="post">
<label>Send money to:</label>
<input type="text" name="recipient">
<BR>
<input type="submit" value="Submit">
</form>"""
        return page_content, headers
        
    def _handle_login(self):
        page_content = ""
        headers = {}
        if self._method == "POST":
            if "Content-Length" not in self.headers:
                page_content += "<P>Post Received, But no Content. Cannot Login</P>"
            else:
                content_length = int(self.headers["Content-Length"])
                form_contents = self.rfile.read(content_length).decode()
                label, data = form_contents.split("=")
                page_content += "<P>Post Received: {}={}</P>".format(label, data)
                self._cookie = os.urandom(16).hex()
                self._session = {"user":data,"transfers":[]}
                connections[self._cookie] = self._session
                headers["Set-Cookie"]="session="+self._cookie
        else:
            if self._session:
                page_content += ("<p><B>cannot login. Already logged in!</B></p>")
            else:
                page_content += """
<form action="/login" method="post">
<label>Login:</label>
<input type="text" name="user">
<BR>
<input type="submit" value="Submit">
</form>"""
        return page_content, headers
    
    def render_page(self):
        """Respond to a GET request."""
        if "cookie" in self.headers:
            cookiestr = self.headers["cookie"]
            cookies = {}
            if ";" in cookiestr:
                cookie_list = cookiestr.split(";")
                
            self._cookie = self.headers["cookie"].split("=")[1]
            self._session = connections.get(self._cookie, None)
            print("Render page with cookie={}".format(self._cookie))
        else:
            print("Render page with no cookie")
            
        page_content, headers = None, {}
        path_handler = self._routes.get(self.path, None)
        if path_handler:
            page_content, headers = path_handler()
            print("got page content", page_content, headers)
        user = self._session and self._session.get("user",None) or None
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        for header in headers:
            print("Sending {}={}".format(header, headers[header]))
            self.send_header(header, headers[header])
        
        self.end_headers()
        self.wfile.write("<html><head><title>Title goes here.</title></head>".encode())
        self.wfile.write("<body><p>This is a test.</p>".encode())
           
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        self.wfile.write("<p>Method: {}</p>".format(self._method).encode())
        self.wfile.write("<p>Headers: </p><UL>{}</UL>".format(
            "\n".join(
                ["<LI>{}: {}".format(k,v) for k,v in self.headers.items()]
            )).encode())
        self.wfile.write("<p>Logged in as: {}</p>".format(user).encode())
        if self._session:
            self.wfile.write("Transfers:<BR><UL>".encode())
            for recipient in self._session["transfers"]:
                self.wfile.write("<LI>{}".format(recipient).encode())
            self.wfile.write("</UL>".encode())
        self.wfile.write("<p>You accessed path: {}</p>".format(self.path).encode())
        
        if page_content: self.wfile.write(page_content.encode())
        
        self.wfile.write("</body></html>".encode())
        
if __name__ == '__main__':
    
    opts = {}
    for arg in sys.argv[1:]:
        if arg.startswith("--") and "=" in arg:
            k,v = arg.split("=")
            k = k[2:]
        else:
            k = arg[2:]
            v = True
        opts[k] = v
        
    HOST_NAME = opts.get("host",'')
    PORT_NUMBER = int(opts.get("port",80))
    httpd = http.server.HTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))