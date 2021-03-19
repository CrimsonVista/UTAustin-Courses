# Lab3: TLS Visibility

|||
|---|---|
| Assigned | 2021-03-11|
| Due: | 2021-04-01 |
| Points | 100 |

## SECURITY DISCLAIMER

In this lab, you will do many things that are BAD, BAD, BAD.
We will be setting up some simplified
security and some weak security that SHOULD NEVER BE USED. 

Here is a list of every bad decision we're making
with respect to security:

1. We are installing a trusted CA into a Firefox browser
profile. This would be a very dangerous thing to do and
you should PROTECT THE PRIVATE KEY CAREFULLY
1. We are going to disable TLS 1.3 in our Firefox Profile
1. We are going to disable OSCP stapling in our Firefox Profile\
1. We are going to enable a deprecated cipher (TLS_DHE_RSA_WITH_AES_128_CBC_SHA)

I STRONGLY RECOMMEND THAT, AFTER THE LAB IS OVER, YOU DELETE THE
FIREFOX PROFILE, OR AT LEAST RENDER IT INOPERABLE.

## Overview
To get a little exposure to cryptography and the TLS protocol,
you will, in this lab, partially implement the server-side of the 
TLS 1.2 protocol. Truthfully, most of this lab is just putting into
place cryptographic parameters as all the actual cryptographic
computations will be done by various Python libraries.

What you will create is basically a HTTPS "front end" for your
Newslister program. As we will discuss in class, the Django
test server does not provide any HTTPS security, meaning the
communications between the browser and the Newslister server
are completely readable, changeable, and forgeable by adversaries.

There is no option to "turn on" HTTPS support for the test Django
server. Instead, you will create a proxy that will provide the
HTTPS server functionality and then pass the data back and forth
to the Django application.

This lab will be a bit harder in terms of Python programming,
so make sure to debug within your study group. I have created the
lab framework to support group debugging.

## Envinronment Setup

You should be able to use your Newslister program environment out of
the box. Within that python virtual environment, you should install
the framework code as a pip "editable" module. So, perform the following
steps.

1. Make sure you have the lab3 code from the class repository
1. Copy the entire lab3 folder to your own repository working directory
1. From within this directory, call `pip install -e .`

The pip command will use the `setup.py` file to install this package into
your virtual env. This means that you will not need to be in any specific 
directory to run your code.

Also, make sure you use the `-e` option. This is "editable". It means that
the pip installed code is tied to your files in your local folder. Normally,
if you install a module, any changes you make to the module are not 
immediately reflected without *reinstalling*. But with `-e` your changes
are immediately operational.

There are two different python scripts you will run from this module. The
first is `tls_frontend.server`, which is the primary script. The second is
`tls_frontend.tls_visibility`, which will be used for debugging.

More details are provided below.

## Networking Background and Simple Python Sockets

(This section optional and not graded, but if you have no experience with
TCP and/or Sockets, you should probably walk through it)

If you don't know much about how TCP networking works, 
or you're familiar with sockets in general, but not in Python,
the following tutorial and exercises show how
to create some simple sockets and then use those sockets to send a basic data.

We won't actually be using sockets in the lab; we'll use a higher-level 
abstraction from the `asyncio` module, but going through this
Sockets exercise will help you understand how it works.

First, let's talk about Python sockets. You can find the basic documentation [here](https://docs.python.org/3/library/socket.html). It's a lot to sift through, so here's a much shorter version.

A "socket" is an abstraction around a TCP communication channel. Remember from our networking lessons that data gets to your computer via the IP protocol, but it gets to specific applications via TCP ports. It wouldn't be very useful if your web browser and your Spotify app couldn't differentiate their data. A TCP port provides what is called "demultiplexing"

Here's an ASCII art visualization.

    SPOTIFY SERVER                    ----------------------------------
         |                            |   + - port x -> web browser    |
          ==========================> | = |                            |
         |                            |   + - port y -> spotify client |
       CNN.com                        ----------------------------------

A socket represents an individual TCP channel. You can send data over this channel or receive data over this channel.

So, let's take a quick look. We'll start with an outbound initial connection. Recall that TCP is bidirectional (full-duplex). Once a socket is open, you can send data in either direction. But we say it is an outbound connection for the party that initiates the communication. It is an inbound listner/server for the party that waits to be contacted.

To open a socket in python, import the socket module, create a socket object, and call the `connect` method. It's pretty simple.

    import socket
    s = socket.socket()
    s.connect(('example.com',80))

That's it! With this three-line bit of python code, you have a TCP connection created to http://example.com. If you're not familiar with python syntax, notice that `s.connect` takes ONE argument, NOT TWO. The single argument is called a "tuple". In this case, it is a two-element tuple: `('example.com',80)`. The first element is the server's address and the second element is the server's port.

What about your own port? What is the outgoing port for your connection? Well, it's picked automatically. You can check your own hostname and port with `s.getsockname()`.

Once you're connected, you can send data using the `send()` method. We'll practice sending data to example.com in a minute. But for now, let's work on setting up the other side of a connection.

The server side of a TCP connection is a bit more complicated, partially because it has to be able to handle multiple incoming connections. The steps of the process are:

1. Bind to a specific address and port (a computer may have multiple addresses)
1. Establish a backlog for how many connections can wait to be processed
1. Wait for an incoming connection; when it arrives, spawn A NEW socket for that individual channel

Each of these steps can be a bit confusing, so we'll walk through them one at a time.

    s = socket.socket() # starts out the same!
    s.bind(('127.0.0.1', 8888))

This instructs the socket to "bind" the loopback interface (127.0.0.1) and port 8888 for the listener. By binding the interface 127.0.0.1, you are making it so the socket can ONLY receive connections from the local computer. If you want to receive connections from other computers, you must bind a public interface. Or, alternatively, if you use the empty string, the socket will bind ALL interfaces.

Now that we have a bound address, we have to "listen". This is an instruction for establishing how many incoming connections can wait in queue while a new one is being handled. For our tests, we won't have multiple connections, so even setting the value to 1 is fine:

    s.listen(1)

This means that, if a second connection was attempted while the first was being processed, their connection attempt would be immediately closed.

Now that the socket is listening, it can `accept` connections. This is a blocking call, so once you call it the program will wait (stop) until a connection is available. Once a connection is available, it will create a NEW socket. The NEW socket is a 1:1 connection between this computer and the remote computer. The OLD socket still exists and can be used to accept additional/new connections. The `listen()` limit ONLY applies to how many are waiting in queue while in the process of accepting a new connection. Once the new connection is established, the old socket can still accept new ones.

The `accept()` method returns a data pair consisting of the new socket and the addr/port of the new connection.

    new_sock, addr = s.accept()

To test this out, let's connect to ourselves on our own computers first. Do the following exercise in two separate Python interactive shells:

In shell 1, do the "server"

    >>> import socket
    >>> server_sock = socket.socket()
    >>> server_sock.bind(('127.0.0.1', 8888))
    >>> server_sock.listen(1)
    >>> client1, addr1 = server_sock.accept()

At this point, the server shell should "stop". It is blocking on `accept` while it waits for a new connection.

In shell 2, we'll connect to the server with an outbound connection.

    >>> import socket
    >>> conn1 = socket.socket()
    >>> conn1.connect(('127.0.0.1',8888))

Now, back in shell 1, you should see that `accept` returned. Print addr1 to see the connection data.

    >>> client1, addr1 = server_sock.accept()
    >>> addr1
    ('127.0.0.1', 6754)

Your port will be different of course. Before we send some data through these connections, let's get a second connection. In shell 1, call `accept` again

    >>> client2, addr2 = server_sock.accept()

Again, it stops. To proceed, in shell 2 create a second connection

    >>> conn2 = socket.socket()
    >>> conn2.connect(('',8888))

In shell 1, you should no longer be waiting. Now let's send some data. First, have the server send the clients some data like this:

    >>> client1.send(b'Hello client 1!')
    >>> client2.send(b'Hello client 2!')

To receive the data, over on shell 2, call `recv`

    >>> conn1.recv(1024)
    b'Hello client 1!'
    >>> conn2.recv(1024)
    b'Hello client 2!'

You can send data in either direction. Please note that `recv` is a blocking call if no data is available. That is, if you call `recv` on one side, but have not sent any data from the other side, it will block until data arrives.

However, although the 1024 in the argument is how much data it can accept at once, it does not have to receive 1024 bytes to proceed. Any data is fine.

Either side may close the connection with `close()` (on the socket).

    >>> conn2.close()

## TLS 1.2

Assuming that you are now comforable with the basic concepts of
sending and receiving data over a network, let's 
talk about using cryptography and the TLS protocol
to secure communications between two parties. 
The communications between the two:

1. Will be confidential; no one else can read them
2. Will be authenticated; no one else can forge them+
3. Will have integrity; no one can undetectably change them en-route

(+ Actually, only the server will be authenticated by TLS in our example)

These policies will be enforced even in the presence of a "man in the middle" (MITM). A MITM is an attacker that can intercept, drop, or even modify messages as they go between one party and another. The two parties are generally unaware of the MITM's presence.

TLS is the most common security protocol used on the Internet today. When you
see the `https` prefix, the "s" stands for secure and means that the HTTP
traffic is transmitted within a secure TLS tunnel.

TLS starts with an unencrypted, unauthenticated TCP connection.
Once the connection is established, the client and server begin the TLS handshake. In TLS 1.2:

1. Client sends a "client hello"
1. Server sends "Server Hello", "Certificate", "Key Share", and "Server Done"
1. Client sends "Key Share", "Cipher Spec Change", "Finished"
1. Server sends "Cipher Spec Change", "Finished"

This exchange creates a confidential, authenticated, and integrous channel even if there is a MITM, as there is in this case. The MITM cannot read the encrypted data sent after the handshake, even though it observed the whole handshake.

How does this work.

1. The server's certificate cannot be forged by the MITM so long as the client correctly verifies it
1. The server sends a DH public key SIGNED by its certificate that cannot be forged

The Client's DH public key could be forged (creating a fake connection between the MITM and the server), but the client is usually authenticated after the fact (e.g.,  client login).

But the Client's DH public key aside, the client and server use DH to create a secret key between them. This key agreement protocol does not reveal the derived key, even to an eavesdropper.

## Creating a Certificate

As part of this lab, you're going to have to create a certificate and sign it.
You will need openssl for this, but if you installed python Cryptography,
it should have installed openssl. If not, please ask the staff if you can't figure
out how to install it.

TLS servers typically require a certificate, signed by a trusted certificate authority to 
operate correctly. So, you're going to create TWO certificates. One that represents
the CA (Certificate Authority) and one that represents the certificate for the
dommain name `cs361s.utexas.lab2`.

First, create the CA private key:

    openssl genrsa  -out CS361S_Spring2021_CA.key 2048
    
Then, create the CA self-signed certificate:

    openssl req -x509 -new -nodes -key CS361S_Spring2021_CA.key -sha256 -days 160 -out CS361S_Spring2021_CA.pem
    
You will have to enter some information interactively, but the answers don't matter
much.

Now create a certificate signing request for `cs361s.utexas.lab2`:

    openssl req -newkey rsa:2048 -nodes -keyout lab2.key -out lab2.csr

This command will generated both the CSR (Certificate Signing Request) and the 
corresponding RSA key. It will ask some interactive questions. Most of them 
don't matter at all. The only one you really need to care about is the "Common Name".
Please set that name to be "cs361s.utexas.lab2". You may have noticed that this
doesn't look like a normal Internet address. That is on purpose and I would
prefer you didn't change it.

To sign the certificate,

    openssl x509 -req -days 360 -in lab2.csr -CA CS361S_Fall2020_CA.pem -CAkey CS361S_Spring2021_CA.key -CAcreateserial -out lab2.cert
    
This will spit out a signed certificate in the file `lab2.cert`. You will need this
for the lab.

(NOTE: I have seen problems where the timestamp for the certificate is
not adjusting for time zone. I'm not enough of an expert to know why.
If somehow you managed to complete this lab in an hour, or if you regenerate
the certificate after you get to the firefox part of this lab, you may
have firefox say the certificate is no longer valid. If you have this problem,
set your computer clock back a day or two, re-run the signing operation, and
then reset your clock)

## Faking out DNS

We are going to want to redirect the fake Internet address "cs361s.utexas.lab2"
to our local host 127.0.0.1. To do this, edit `/etc/hosts` and insert the
following line:

    127.0.0.1   cs361s.utexas.lab2

This works on Windows by editing `/Windows/System32/Drivers/etc/hosts` although
you may have to flush your DNS cache afterwards (`ipconfig /flushdns`). If you're
using WSL, you will need to edit BOTH places.

## TLS Front-End/Wrapper

The TLS front-end you have to implement is designed to provide a secure proxy for
an unsecured website. As stated previously, your Django website is NOT https and,
therefore, anyone that could tap your line could see any of the data.

The TLS front-end is designed to "wrap" the website in a protected HTTPS shell.
The idea is to first launch the unprotected server, perhaps Django, on some port (perhaps 8000). Next
run the TLS front end specifying the front-end (TLS) port, and the back-end (unprotected Djuango port), along
with the corresponding (signed) certificate and key.  Like this:

    python -m tls_frontend.server proxy 9000 8000 lab2.cert lab2.key
    
Ignore the "proxy" command for now. There is another option for students interested in 
extra credit, so most of you will only ever use "proxy".

This command-line isn't very stable. It has no `--help` option and it will break easily.
So don't expect too much from it.

Once the proxy is launched, it creates a TLS-enabled front end on port 9000 for "cs361s.utexas.lab2" and forwards
the data to the localhost unprotected port 8000.

Out of the box, 
the front-end doesn't work because the TLS methods have been stubbed. But you can start filling this in a bit at a time.
The shell file includes some instructions for stub functions/methods that you need to fill in. 
As with your previous assignment, search for `STUDENT TODO`.

This section provides a quick overview of the provided code and the stubs.

First, let's talk about the networking. You have already created some sockets in Python, so you know the most basic way of creating sockets and using them to send/receive data. If you look through this file, there's not a socket to be found. Why is that?

If you remember, sockets are typically "blocking". That is, an `accept()` call blocks until new connections arrive. Or, `recv()` blocks until data is ready. If we wrote this code using sockets in blocking mode, we would have to use threads, or an equivalent, in order to make the code no get "stuck".

Sockets can also be opened in a non-blocking mode. In this mode, `accept()` doesn't block, but even still, how do you know when to accept and not accept? For an "event loop", many programmers use something called `select`. This mechanism allows the programmer to know when data is ready. Once ready, the non-blocking calls are executed.

But whether threads or `select` is used, it's a bit complicated to write.

So instead, we will use Python3's `asyncio` module. This module uses non-blocking sockets and `select` internally, but wraps it into a very nice event-loop API.

The `asyncio` module's more recent approach to network communication is to create asynchronous streams. I'm still not as familiar with those, so I'm using the older `Protocol` approach. The basic idea is that, instead of writing a handler for a socket's read/write, you create a `Protocol` subclass that implements the following methods:

    connection_made(self, transport):

    data_received(self, data):

    connection_lost(self, reason=None):

Once the class is defined, it is passed to the Event Loop for either a Server (listening on a socket) or an Outbound Connection (on an outbound socket). Once the TCP connection is established, `connection_made` is called. When the TCP connection closes, `connection_lost` is called. In between, any time data is received, it is passed to the class through `data_received`. Outbound data can be sent using `transport.write`, where `transport` is passed as an argument to the class during `connection_made`.

All-in-all, I think it's straight-forward. You can see some more documentation (here)[https://docs.python.org/3/library/asyncio-protocol.html]. Make sure to look at the `EchoServer` and `EchoClient` examples.

You shouldn't need to create any Protocol classes in this code. We have already provided them. The classes are:

    class ProxySocket(asyncio.Protocol):

    class TLSFrontend(asyncio.Protocol):

These are the only two protocols that you'll need to deal with. `TLSFrontend` is the protocol that handles incoming requests from the client (e.g., the browser or wget). `ProxySocket` is the protocol that forwards the data to the back end server. The `ProxySocket` class, when created, keeps a back pointer to the `TLSFrontend` class that triggers it. When it receives data, it simply passes it back to `TLSFrontend`.

*NOTE*: You don't really have to do anything for ProxySocket. It is already plugged in where it needs to be. 
It is mentioned here For Your Information only.

This process can be visualized as:

    [client] -- new connection ---->  [TLSFrontend]

    [client] <--- TLS Handshake --->  [TLSFrontend][ProxySocket] -- new connection --> [Server]

    [client] <--- TLS Channel ----->  [TLSFrontEnd][ProxySocket] <- Insecure Channel -> [Server]
 

In the code, the `TLSFrontend` hands data off to `ProxySocket` like this:

    self.proxy_socket.transport.write(data)

(`proxy_socket` is set by the `ProxySocket` class in its `connection_made`).

And, `ProxySocket` passes the data back to `TLSFrontend` in its `data_received` method:

    def data_received(self, data):
        self.proxy.handle_remote_response(data)

Both classes are already defined and do not need any changes.

But the `TLSFrontend` class also has a utility class called `TLS_Visibility`. This is the class that 
enables the `TLSFrontend` to intercept the TLS handshake and subvert it. It also enables it to 

    self.tls_handler = TLS_Visibility(self.tls_cert, self.tls_key)

The `TLS_Visbility` class also handles decrypting encrypted data coming in from the client or the server and re-encrypting it to send to the other end of the connection. `TLS_Visibility` also records the data that it receives and processes the TLS state using another class called `TLSSession`. Both of these classes have the structural elements in place and only require you to fill in stub methods.

For example, here is a stub method in the `TLSSession` class:

    def set_client_random(self, time_part, random_part):
        # STUDENT TODO
        """
        1. set client_time, client_bytes
        2. calculate client_random. There is a method for this
        """
        pass

Remember, for the TLS visibility, you receive data from the client. You have to store, for example, the random number the client sends in its hello message. This method allows you to do that. The client will send both a `time_part` and a completely `random_part`. As the instructions say, you need to set three values:

    client_time
    client_bytes
    client_random

The first two should be obvious. The second one says there is "a method for this". Can you look through the methods of this class and see if there's something to help you?

On the other hand, if you look at the stub for `set_server_random`, you will see that the instructions are similar, but there are no inputs? How come there are no inputs for this one? In the client case, you are reading the data from the client. In the server case, you are generating the data. Both the time and random components can be calculated/generated within the function itself.

For some methods, however, you will need to use some methods provided by scapy's TLS library. You COULD implement these yourself, but it's error prone and not necessary. I've put hints in the code where you should use another method. A complete list of the scapy TLS methods you should know are listed in the next section.

### IMPORTANT NOTE

For debugging purposes for TLS_Visibility, anywhere you need a time stamp, you should use
the `timestamp()` function that I have provided. You should only need one of these.

Furthre, any time you need a sequence of random bytes, please use `randstring(len)`. There
is at least one of these. Perhaps a couple.

Do NOT use `time.time()` or `os.urandom()`. Doing so will make your code not repeatable for
group debugging.

## Scapy, Cryptography, and Utilities

Scapy Method list:

1. pkcs_os2ip(b) - converts bytes `b` to integer. Useful for converting DH params to integers
1. PRF.compute_master_secret(pms, cr, sr) - computes a PRF-generated master secret from `pms`, the pre-master secret, `cr`, the client random, and `sr`, the server random. Note that your PRF object is generated in the `TLSSession` constructor
1. PRF.derive_key_block(ms, sr, cr, len) - computes a `len` length PRF-generated key block from `ms`, the master secret, `sr, the server random, and `cr` the client random. Note that your PRF object is generated in the `TLSSession`constructor.
1. PRF.compute_verify_data(party, mode, msgs, ms) - computes a PRF generated verify field. For our purposes, the `party` is always the string `"server"`. Mode will b"server", mode is always the string `"read"` for processing the client's `done` message or `"write"` for creating the server's done message. `msgs` is all of the handshake messages so far and `ms` is the master secret.
1. _TLSSignature(sig_alg) - constructor for a `TLSSignature` object for signing the DH public key. For our purposes, the `sig_alg` is 0x0401
1. sig._update_sig(bytes, rsa_pri) - Update a `TLSSignature` object with bytes being signed using an RSA private key. `sig` is a `TLSSignature` object. The update is internal.
1. X509_Cert(der_bytes) - An X509 certificate object for use in Scapy TLS classes. It can be filled in from DER-encoded bytes of an existing certificate. DO NOT CONFUSE WITH x509 cryptography classes! This is from SCAPY! 
1. Cert - A Certificate object for use in Scapy TLS classes. DO NOT CONFUSE WITH x509 cryptography classes! This is from SCAPY! 
1. TLSServerHello(gmt_unix_time. random_bytes, version, cipher) - Create a TLS Server HEllo Scapy object. The version value should be `0x303`and cipher should be `TLS_DHE_RSA_WITH_AES_128_CBC_SHA.val` (don't forget the `.val`).
1. TLSCertificate(certs=\[list of certs\]) - Create a TLS Certificate Scapy object. The `certs` field should be a list of Scapy certificates (class `Cert` as shown above).
1. TLSServerKeyExchange(params, sig) - Create a TLS Server Key Exchange Scapy object. `params` should be the server's DH parameters and `sig` should be a `TLSSignature` over the parameters.
1. TLSChangeCipherSpec() - Create a Scapy TLS Change Cipher Spect message object
1. tlsSession() - A Scapy TLS Session object. DO NOT CONFUSE with your own `TLSSession` object. We rarely need this, except occasionally to set the version (`session.tls_version = 0x303`)
1. TLSFinished(vdata, tls_session) - Create a Scapy TLSFinished message. `vdata` is the verify data over handshake packets. Because Scapy screws up if the wrong version is set, you have to set the TLS version using the `tls_session`.
1. TLSFinished(plaintext_data, tls_session=f_session) - RE-create a TLS Finished message from the client transmitted bytes. Because these bytes were encrypted, they have to be decrypted first. Also, set the version
1. TLSApplicationData(plaintext) - Create a TLS Application Data object from the bytes transmitted. The Data will have to be decrypted first
1. TLS(msg) - Create a TLS Scapy message complete with the TLS record layer. `msg` is the internal TLS message type, such as TLS Server Hello
1. tls_client_key_exchange.exchkeys - Extract the exchange keys from a Scapy `TLSClientKeyExchange` method
1. ClientDiffieHellmanPublic(exchkeys) - Create a Scapy DH Public key structure from exchange keys.
1. dhp.dh_Yc - Extract the `Y` component from a Scapy DH public key structure
1. raw(pkt) - Convert any scapy packet `pkt` into bytes

Cryptography list:

1. dh.DHParameterNumbers(p,q) - generates DH parameter numbers from `p` and `q`
1. dh.DHPublicNumbers(y, pn) - generates a DH public numbers object from `y` and `pn`, where `pn`, is a DH parameter numbers object.
1. pno.public_key(default_backend()) - generate a DH public key from `pno`, a public numbers object
1. dh_pri.exchange(dh_pub) - generate a derived key from a private key/public key DH exchange. Note that your private key is already generated for you in the `TLSSession` constructor
1. hmac.HMAC(key, hash_type, default_backend()) - Create an HMAC object. The key is the MAC key. For our purposes, `hash_type` is `hashes.SHA1()`. WARNING: Because of name collisions, I recommend `from cryptography.hazmat.primitives import hmac as crypto_hmac'
1. h.update(bytes) - Update an HMAC object `h` with bytes
1. h.finalize() - Get the final HMAC from `h` over all input bytes
1. algorithms.AES(key) - Create an AES algorithm object with a key
1. modes.CBC(iv) - Create a CBC mode object with an IV
1. Cipher(alg, mode, default_backend()) - Create a Cipher object; for our purposes, alg and mode will be AES algorithms and CBC modes.
1. c.encryptor() - Create an encryptor object from `c`, a Cipher
1. c.decryptor() - Create a decryptor object from `c`, a Cipher
1. d.update(ciphertext) - Recover plaintext from ciphertext using `d`, a decryptor. 
1. d.finalize() - Finish a decryption operation for `d`, a decryptor. If the decryptor decrypts in blocks, finalize should not be called until all of the data processed is a multiple of blocklen
1. e.update(plaintext) - Create ciphertext from plaintext uing `e`, an encryptor
1. e.finalize() - Finish an encryption operation for `e`, an encryptor. If the encryptor encrypts in blocks, finalize should not be called unless a multiple of blocklen has been encrypted
1. rsa.generate_private_key(exp, ksize, default_backend()) - Generate a new RSA private key object. The `exp` values should always be  65537. `ksize` is the size of the RSA key.
1. prikey.pub_key() - For any Cryptography private key class, generate a public key
1. x509.CertificateBuilder - A Certificate Builder class. Look up documentation in the Python cryptography module
1. cert.public_bytes(encoding) - Convert a certificate object to bytes. `encoding` should be either `serialization.Encoding.PEM` or `serialization.Encoding.DER`
1. pri_key.private_bytes(encoding, format, encryption) - Get the bytes of a private key for serialization. Encoding should be `serialization.Encoding.PEM` or `serialization.Encoding.DER`. Format and encryption algorithm should be `serialization.PrivateFormat.TraditionalOpenSSL` and `serialization.NoEncryption()` respectively

Other utilities:

1. struct.pack
1. struct.unpack

## Documentation

1. [Python Cryptography](https://cryptography.io/en/latest/)
1. [Scapy TLS handshake](https://scapy.readthedocs.io/en/latest/api/scapy.layers.tls.handshake.html)

## Step One: Getting the handshake working with s_client

Openssl provides a very handy client called `s_client` that you can use to help
debug/write your TLS handshake. Here is the command with a number of
helpful options

    openssl s_client -CAfile CS361S_Fall2020_CA.pem -debug -connect cs361s.utexas.lab2:9000 -verify_return_error
    
The option "CAfile" loads a certificate that you want to treat as trusted.
Remember that your "lab2" certificate was signed by "CS361S_Fall2020_CA". So you're
telling s_client to treat the CA cert as trusted so it can verify the lab2
cert when received.

The "debug" option provides a lot of detail. You can stop using this later on.

Finally "verify_return_error" will have openssl s_client STOP when a verification error
happens. This is helpful because sometimes it will just keep going and you don't see
the error.

Note that s_client is connecting to the server on port 9000. This is assuming that
you set the front-end to run on port 9000. Change this value if you are running
it somewhere else.

## Step Two: Getting the TLS forwarding working for Firefox

I want you to use Firefox for this assignment because Firefox allows
you to install certificates into a profile. As far as I can tell, Chrome
and Microsoft browsers only install certificates globally for the computer.
I DO NOT WANT YOU TO INSTALL ANY GLOBAL CERTIFICATES. IT IS A HUGE
SECURITY RISK.

So, to do this part of the lab, you need to install Firefox and create
a separate profile. This is not a sign-in, so no need to have a new
login and password. Rather, look up the Firefox documentation for 
profile management and learn how to create a separate profile. Name
the profile something about "Dangerous" or "Experimental" or "testing only".

Once you have created the profile, and launched it, you can make changes
to this profile that will not affect the system or even other Firefox profiles.

Here are the changes you need to make.

First, go into settings and find the option to add trusted certificates.
You need to install the "CS361S_FALL2020_CA" certificate

Now, go to a URL bar and type `about:config` to bring up the advanced
config panel. Change the following settings:

1. security.ssl.enable_ocsp_must_staple to false
1. security.ssl.enable_ocsp_stapling to false
1. security.ssl3.dhe_rsa_aes_128_sha to true
1. security.tls.version.fallback-limit to 3
1. security.tls.version.max to 3

Now, once you have all of these settings in place, you should be able
to point your TLS front end to your Django app and then browse to
`https://cs361s.utexas.lab2:9000`

For grading, you will need to submit your Firefox profile (details
coming soon)

## Debugging

As aluded to, this code has been built with a powerful debugging tool. 
This tool allows you to re-run the TLS steps from a previous execution
without any networking and with exactly the same values as before. The
way this works is that, each time you run the `tls_frontend.server`, it
will save off a file called `tls_replay.bin` in your current working directory.
Armed with this file, you can re-run just the TLS part of the operations 
with the following command:

    python -m tls_frontend.tls_visibility tls_replay.bin <cert_file> <key_file>
    
Make sure to use the same cert and key as before. When you do this, the
system will re-run all TLS messages through the TLS engine, restoring the same
random numbers and timestamps from the original run (**ASSUMING YOU USED 
THE PROVIDED TIMESTAMP and RANDSTRING FUNCTIONS**).

The reason this is so important is it will allow you and a collaborator to
run through the same parts of a program and see if you're getting different
answers. So, suppose that Alice and Bob are in a group. Alice is testing her
program and having errors.

1. Alice sends tls_replay.bin, her cert, and her key to Bob
1. Bob runs the tls_visibility with these parameters
1. Bob can tell Alice where he sees differences

Please note, when you ask me for help on this lab, the first question I will ask
you is if you've had a group member try it out. If you have disfunctional groups,
please ask for reassignment. If I do need to help you debug, you will need to send
me your replay file and your key/cert.

## Grading

This is a pass/fail lab. We will use s_client to test whether or not your
system correctly processes TLS messages. We may release a test system for you
to use before the due date.

To show that you got Firefox working, include a screenshot in the root folder of your
github submission called "firefox_screenshot.png" that shows your
firefox connection to your Django webapp via https. 
