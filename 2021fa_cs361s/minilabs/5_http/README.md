# UT-Austin CS 361S Minilab 5 - HTTP

|||
|---|---|
| Minilab: | 5 - HTTP |
| Class Assigned: | 10/27/2021 |
| Points: | 50 |

In this lab, we will do in-class exercises where we send some HTTP traffic.
We will send some HTTP requests over a "raw" socket and we will use higher-level
libraries for some as well. We will request data from human-readable websites
as well as from web APIs.

## Setup

You only need a Python 3 shell (and optinally a command-line terminal with `curl`). 
No cryptograpny required!

## Introduction

For the next few weeks in the class we will learn some about securing
the World-Wide Web. But to do this, we need to have a least a little
familiarity with how web traffic works in general. This will help when
we talk about things like Cross-Site Scripting, Cross-Site Request Fogery,
and even how OAuth works (in your Lab 5).

## A Basic HTTP Request

We're going to use Python to do a little bit of low-level HTTP requesting.
In a python terminal import sockets. Remember this from mini-lab 2? We're going
to open a socket to `example.com` and create a very, very basic HTTP request.

The simplest HTTP request has a METHOD, a PATH, and a VERSION on the first line
followed by zero to many headers. Although no headers are technically required,
many websites (including `example.com`) require a HOST header. Lines in HTTP
requests are ended by `\r\n` control characters. A blank line ends the request.

So, to send an HTTP request to `example.com`, do the following:

    >> import socket
    >> s = socket.socket()
    >> s.connect(('example.com', 80))
    >> s.send(b"GET / HTTP/1.0\r\n")
    >> s.send(b"host: example.com\r\n")
    >> s.send(b"\r\n")
    >> s.recv(2048)
    
We will discuss in-class what the path means, why the host header is required, and answer
any questions you have. Also, note that we are using port 80. This is HTTP, not HTTPS.

Let's try HTTPS. Recall that `example.com` has HTTP and HTTPS. The default port for HTTPS
is 443. To do this, we'll need to run TLS over our socket before sending data. But don't worry,
this is provided by the Python socket library.

For this example, we will use something called "Contexts" in Python. A Context uses a
`with` statement to create a context. The context has automatic clean-up no matter how the
`with` block is exited (normally, exception, etc.). This is, for example, the recommended
way of opening files:

    with open(filename) as f:
      # do stuff with f.
      
Here is how we open a socket to `example.com` and wrap it in TLS:

    >> import socket
    >> import ssl

    >> hostname = 'example.com'
    >> context = ssl.create_default_context()

    >> with socket.create_connection((hostname, 443)) as sock:
    >>    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
    >>        ssock.send(b"GET / HTTP/1.0\r\n")
    >>        ssock.send(b"host: example.com\r\n")
    >>        ssock.send(b"\r\n")
    >>        ssock.recv(2048)
    
The `create_connection` method opens the socket and names it `sock`. The
`wrap_socket` method creates an `ssock` object that works just like a socket,
but it has already done the TLS handshake and will automatically encrypt/decrypt
the data.

NOTE: If you've sent the same requiest to example.com multiple times, it
may just send back a cache message rather than the entire HTML.

The point of this exercise is to see that an HTTP message is, at its core,
fairly simple.

One thing to notice in either example is what the HTTP response looks like.
It should have looked something like this:

    b'HTTP/1.0 200 OK\r\nAge: 526268\r\nCache-Control: max-age=604800\r\nContent-Type: text/html; charset=UTF-8\r\nDate: Wed, 27 Oct 2021 18:13:15 GMT\r\nEtag: "3147526947+ident"\r\nExpires: Wed, 03 Nov 2021 18:13:15 GMT\r\nLast-Modified: Thu, 17 Oct 2019 07:18:26 GMT\r\nServer: ECS (dab/4BAA)\r\nVary: Accept-Encoding\r\nX-Cache: HIT\r\nContent-Length: 1256\r\nConnection: close\r\n\r\n<!doctype html>\n<html>\n<head>\n    <title>Example Domain</title>\n\n    <meta charset="utf-8" />\n    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n    <meta name="viewport" content="width=device-width, initial-scale=1" />\n    <style type="text/css">\n    body {\n        background-color: #f0f0f2;\n        margin: 0;\n        padding: 0;\n        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;\n        \n    }\n    div {\n        width: 600px;\n        margin: 5em auto;\n        padding: 2em;\n        background-color: #fdfdff;\n        border-radius: 0.5em;\n        box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);\n    }\n    a:link, a:visited {\n        color: #38488f;\n        text-decoration: none;\n    }\n    @media (max-width: 700px) {\n        div {\n            margin: 0 auto;\n            width: auto;\n        }\n    }\n    </style>    \n</head>\n\n<body>\n<div>\n    <h1>Example Domain</h1>\n    <p>This domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.</p>\n    <p><a href="https://www.iana.org/domains/example">More information...</a></p>\n</div>\n</body>\n</html>\n'

Hard to follow. Let's break it up a little. The HTTP response starts with a VERSION, a CODE, and a STATUS on the
first line. Then it has a range of headers. The headers end with a blank `\r\n`. This can be followed
by data. How do you know how much data? One of the headers is `Content-Length`. Let's try and break
these out of the one above.

    b'HTTP/1.0 200 OK'
    b'Age: 526268'
    b'Cache-Control: max-age=604800'
    b'Content-Type: text/html; charset=UTF-8'
    b'Date: Wed, 27 Oct 2021 18:13:15 GMT'
    b'Etag: "3147526947+ident"'
    b'Expires: Wed, 03 Nov 2021 18:13:15 GMT'
    b'Last-Modified: Thu, 17 Oct 2019 07:18:26 GMT'
    b'Server: ECS (dab/4BAA)'
    b'Vary: Accept-Encoding'
    b'X-Cache: HIT'
    b'Content-Length: 1256'
    b'Connection: close'
    b''
    
Notice that the blank line ended this set of headers. The data that followed (with the HTML of the
website) is 1256 bytes.

Your requirements for the mini-lab so far are to take a screenshot showing that
you downloaded data from `http://example.com` and `https://example.com`. You do not
have to break out the headers as I did above. That is just for your educational benefit.

You might also try sending an HTTPS request to `google.com`. It might take more than
2048 bytes to read all of the data though. If you want to challenge yourself a little further,
try to read enough bytes to get the headers and then use `Content-Length` to calculate precisely
how many more bytes are required.

## HTTP request libraries and Curl

Nobody in their right mind uses something as basic as sockets to make HTTP requests.
Most websites have higher-level libraries that can do this for you. We'll do one
quick example. In Python 3, the `http.client` library can easily request data
from either HTTP or HTTPS websites:

    >> import urllib.request
    >> resp = urllib.request.urlopen("http://example.com")
    >> resp.getheaders()
    >> resp.read()
    
This will handle HTTPS automatically

    >> resp = urllib.request.urlopen("https://google.com")
    >> resp.getheaders()
    >> resp.read()
    
There are also commandline utilities that do this kind of thing.
`Curl` is a popular utility installed on most systems. If your
system has it, you may optionally try out:

    curl https://google.com
    
Using curl with `-v` will print out a lot of information

Take screenshots showing the use of either urllib or curl
to access these URLs.

## Web APIs

All the examples we've tried so far are for websites that
are meant for humans to use and consume. The responses are
typically HTML for rendering in a browser.

For this part of the test, we will access web API's that
are used by programs to interface with each other. In this
example, we will only be using API's that require GET.
If you were going to upload data, you would use POST, as
we did with Django. But the goal is to see the kind of responses
we get.

Using either `curl` or `urllib`, query the following URL:

    https://catfact.ninja/fact
    
You will notice the answer did not come back as HTML. The
results of APIs are usually JSON or something similar. Older
APIs used XML although that is less common/popular these days.

Here are some other web APIs to try:

    https://api.coindesk.com/v1/bpi/currentprice.json
    https://www.boredapi.com/api/activity
    
Take screenshots of your results from these API's.

These API's are free API's that require no registration.
Most API's of any value require registration. The Offeror
will usually provide an API "key" or some other kind 
of authentication method. Because API's are used by machines,
which can be automated and faster than a homan user,
even a free API might need to control access just to 
prevent itself from being overwhelmed. We will talk
more about this in class.

## Submission
Assemble the screenshots into a word document or
other such file (PDF is fine) and submit to the TA.

## Grading
This minilab, like all other minilabs, is pass fail. We are showing
you literally how to do everything. The class will be recorded. If
you missed it, please submit as soon as possible. This minilab is
designed to help you with the next lab.

    