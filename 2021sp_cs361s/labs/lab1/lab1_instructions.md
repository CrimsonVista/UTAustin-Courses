# Lab1: Network Basics and Visualization #

|||
|---|---|
| Assigned | 2021-02-03 |
| TA: | 2021-02-10 |
| Points | 100 |

In this lab, we will do in-class exercises to send data over networks and visualize
it with Wireshark. Although we won't learn too much about TLS yet, we will see
that TLS makes it impossible to read the data without a key

## Virtual Network Classroom

The Virtual Network Classroom is a tool designed to help students learn together about network traffic even when they're physically remote.

The Virtual Network Classroom has two major components:

1. A Hub
2. Spokes

The Hub will normally be run by the professor. Each student will run a spoke. The Hub and Spokes enable students to setup servers on their local machines for remote peers to access, and also enables other students to _tap_ those servers. Students tapping a server can watch a pseudo-reconstruction of the traffic between the two endpoints on wireshark.

## Setup

Because you will be permitting others to access your machine over the Internet, you are REQUIRED to run this in a virtual machine. This should prevent any (hopefully accidental) "breaches" from gaining any access to your "real" machine.

The setup is as follows:

1. [Download Ubuntu](https://ubuntu.com/download/desktop)
1. Install in virtualbox (or a VM of your choice)
1. Install Ubuntu in your VM
1. Launch Ubuntu. The software will probably update
1. sudo apt install gcc make perl
1. install vbox add ons for screen resizing, drag and drop
1. sudo apt install git
1. use git/ssh/drag and drop to get files onto system
1. sudo apt install python3-pip
1. sudo apt install openssh-server, wget
1. pip install cryptography, scapy

In addition, you need to install the following components:

1. sudo apt install wireshark
1. sudo apt install net-tools (optional, but HIGHLY recommended)

To setup the Spoke, you will need the Python code and a TLS certificate. The Python code can be found in github under `2021sp_361s/network_classroom` and the certificate can be found in `2021sp_361s/certs`. The certificate is currently named `2021sp_utcs361s_root.pem.cert`.

For getting data out of wireshark, you need to create a named pipe in your Virtual Ubuntu:

    mkfifo /tmp/dump1.pcap

## Getting Connected

To connect to the class Hub, change directories to `network_classroom/src/`. I don't currently have an installer, so you'll just have to run it from this directory. Or, if you feel so inclined, you can set your PYTHONPATH or something. The certificate needs to be in the current working dir and MUST be named `cert.pem`, so copy the cert from `certs` into this directory and rename or symlink it.

To run the Spoke:

    python3 -m network_classroom.spoke crimsonvista.net

The domain `crimsonvista.net` is owned and maintained by the professor. You will need the provided certificate in order to complete the network connection.

## Registration

Each time you run Spoke you will enter a username and password. But the first time you connect you can register. As part of registration, you choose your username and password. You may enter *any* username you wish, but it would be helpful if you could pick a name that the professor and classmates will recognize. 

Here is how it works:

    $ python3 -m network_classroom.spoke crimsonvista.net
    user: my_user_name
    password: <invisible password>

    >>>

Unfortunately, because this is still in heavy alpha stage, it will probably spew some debug information as well. Just hit enter and you should get a clean `>>>` prompt. Then register:

    >>> register <code>

The `code` will be provided by the instructor during a registration period only, after which it will be disabled. Check slack for the registration code

## Logging in subsequently

Should you need to disconnect from the hub and reconnect, enter your registered username and password as when you registered. But instead of typing `register`, type `login` when you see the `>>>` prompt.

## Starting a server

Using Spoke, you can enable students to send data to a server running in your VM. To set this up, from the Spoke command prompt:

    >>> listen port <alias>

You do not have to have a server running when you execute this command. It simply advertises the server port to others. You will need to have a server running in order for your classmates to connect to it though.

Classmates can reach your servers using your username and port (`<username>:<port>`). But, because it's much easier to just use an alias, you can create a global alias when setting up your server.

*NOTE:* This function will probably change somewhat in the future. I would like to be able to proxy connections to servers off your machine (e.g., google.com). Stay tuned for changes.

## Connecting to somebody else's server

You can forward traffic from your local machine to someone else's server with the `forward` command

    >>> forward <local_port> <server_id>

This means that servers on your machine that connect to `127.0.0.1:<local_port>` will have their traffic forwarded to the identified server. The server is identified by `<username>:<port>` or by its alias.

## Listing Users and Listing Servers

You can see who else is connected with `list_users` and what servers are currently listening with `list_servers`.

## Tapping a Server

To tap communications to and from a server,

    >>> tap <server_id>

Again, the server_id is a `<username>:<port>` or the alias. Data that is tapped is sent to `/tmp/dump1.pcap`. If you didn't make your fifo, it will just create a regular file and dump the data there. But a pipe will be better for our wireshark stuff.

## Wireshark

If you have correctly created a fifo pipe, you can pipe the data from your Spoke tap to Wireshark. To launch wireshark listening to the fifo pipe:

    $ wireshark -k -i /tmp/dump1.pcap

Wireshark will show you the tap traffic as it arrives. Please note that this is a pseudo-reconstruction. We don't actually have the real IP addresses that were used. Instead, Spoke is creating a fake IP address for each user and creating fake IP packets with these IP addresses as the source and dest addresses. It also uses the real destination port as TCP's dport, but an artificial connection ID as TCP's sport. The sequence numbers are also made up, but should be approximately correct. The TCP handshake is not re-created.

You can see the username to IP mapping by export a "hosts" file from spoke.

    >>> export_user_ips <filename>

The exported file will have IP's followed by usernames:

    192.168.137.35 user1

You can actually have Wireshark automatically convert the ip addresses to usernames by copying this file into `~/.config/wireshark/`. When Wireshark relaunches, select the `network name resolution` option.

## Run some simple tests

You can, of course, connect a client on your machine to a server on your machine *through* your Spoke. Try the following.

First, setup a very basic webserver using python.

    $ python -m http.server 54321

Now, advertise this server on your Spoke and setup a forwarding from some other port like 65432 (the following assumes you are already logged in)

    >>> listen 54321 test1
    >>> forward 65432 test1

Again, this instructed the hub that your spoke will accept traffic destined for port 54321 (under the alias test1), and it will forward traffic from your local 65432 port to the server identified by the alias test1. NOTE! Aliases are GLOBAL! You should probably pick a more unique name than `test1`. If your classmate is trying out this exercise at the same time, and uses `test1`, you will not be able to!

Now, using wget, connect to the web sever

   $ wget 127.0.0.1:65432

If all went well, you should download a file as `index.html`.

What happened was:

1. Your wget utility connected to the spoke on 65432 and sent an HTTP request
1. The spoke sent this to the hub and indicated that it was for `test1`
1. The Hub determined that `test1` is on your computer at 54321
1. The Spoke received the data and forwarded it to 54321.
1. The webserver listening on54321 responded 
1. The response went in the reverse direction

You can also tap your own server:

    >>> tap test1

And then watch the traffic on wireshark!

## Warnings

Look, this project was put together in a few weekends. The code is weak, there are debug statements all over the place, and the functionality isn't even finished.

1. If you get stuck, just quit and try again
1. Sometimes it hangs on connect. Just ctrl-c and try again
1. If debug data has filled your screen, hit enter to get a clear `>>>` prompt
1. There is no command yet to STOP serving or STOP connecting. Unfortunately, you just have to quit
1. Still in development so watch for changes

## Visualization

For those that like images, here is an ASCII-art representation of what's going on here. Here is a depiction of the initial connections between the hub and spokes. Can you see why they're called "hub" and "spoke"?

    --------------------------                                       ---------------------------
    | Student A VM           |                                       | Student B VM            |
    |                        |                                       |                         |
    |       spoke            |                                       |          spoke          |
    --------------------------                                       ---------------------------
              |                                                                   |
              |                                                                   |
              |                                                                   |
              |                  ----------------------------------               |
              |                  | crimsonvista.net               |               |
              |                  |                                |               |
              |----------------->|   hub (crimsonvista.net:34150) |<--------------|
                                 ----------------------------------

Student B set's up a web server on 8888. Student B tells the spoke to "listen 8888 b_webserver". This instructs the spoke to be willing to forward information to local port 8888 (on the VM) but also instructs the hub to advertise this (including the helpful name 'b_webserver').


    --------------------------                                       ---------------------------
    | Student A VM           |                                       | Student B VM            |
    |                        |                                       |    +-->webserver (:8888)|
    |       spoke            |                                       |  spoke                  |
    --------------------------                                       ---------------------------
              |                                                                   |
              |                                                                   |
              |                                                                   |
              |                  ----------------------------------               |
              |                  | crimsonvista.net               |               |
              |                  |                                |               |
              |----------------->|   hub (crimsonvista.net:34150) |<--------------|
                                 | SERVERS:                       |
                                 | * Student B: 8888 (b_webserver)|
                                 ----------------------------------

Now, Student A, after learning about this server, creates a connection to the webserver. She does this by picking a random port, 9876, and then instructing the spoke to "forward 9876 b_webserver", which tells it to forward traffic sent to localhost port 9876 to b_webserver. Next, she uses some client program, such as wget, to connect to localhost:9876. The spoke forwards the requests from wget through the hub to the webserver hosted by Student B.

    --------------------------                                       ---------------------------
    | Student A VM           |                                       | Student B VM            |
    |   wget (localhost:9876 |                                       |    +-->webserver (:8888)|
    |    +---> spoke (:9876) |                                       |  spoke <...             |
    ------------:-------------                                       ------------:--------------
              | :                                                                :|
              | :                                                                :|
              | :                                                                :|
              | :                ----------------------------------              :|
              | :                | crimsonvista.net               |              :|
              | :...............>|                                |..............:|
              |----------------->|   hub (crimsonvista.net:34150) |<--------------|
                                 | SERVERS:                       |
                                 | * Student B: 8888 (b_webserver)|
                                 ----------------------------------



## Setting up a SOCKS proxy

A SOCKS proxy is used by a Browser when it needs to go through an outbound
proxy device.  We're going to setup a SOCKS proxy on the "server" side of our
Hub and Spoke and forward traffic over the Hub and Spoke to the proxy. The 
reason for this is to "tap" traffic and to look at it with Wireshark.

To setup a SOCKS proxy, you simply need ssh. Figure out some port that you want
to use for the proxy. 12345, for example, would be fine. To start a SOCKS
proxy on your machine with SSH, you can run SSH like this:

    ssh -N -D 12345 yourusername@localhost
    
You can test this by launching Firefox and configuring this as your proxy. If
you go to Preferences and search for Proxy, you will find settings that include
configuring a SOCKS proxy. Leave any other proxy information blank but put in
your proxy address as 127.0.0.1 and your port as the port chosen for the SSH 
command above (12345 in the above example).

If everything has worked, you should still be able to browse the Internet
normally.

If everything has worked out so far, you can now forward your socks proxy to
your group mates over the hub and spoke. To do this, create a new server in the 
spoke application with a command like this `listen <port> <servername>`. For port,
you should put int whatever your proxy port was for SSH (12345 in the above example).
For servername, put it something that will be unique across the class, such as
`<username>_socks1`. Putting it altogether in a concrete example:

    >>> listen 12345 professor_socks1
    
Now any body in the class can use your socks proxy by forwarding one of their
own ports to your named server. If, for example, they planned to use port 11223,
the command in Spoke is:

    >>>> forward 11223 professor_socks1
    
On the forwarding computer, the browser (e.g., Firefox) needs to set `127.0.0.1` as
the SOCKS proxy, still, but the port as the forwarding port (e.g., 11223 in the
example above).  Once this is setup, here is the crazy route from a browser
to a given website, such as google.com

    | browser |                    | SSH SOCKS Proxy on port 12345 | --> google.com
        |                                        |
        |                                        |
    | Spoke port 11223 |           | Spoke server professor_socks1 |
        |                                        |
        |                                        |
        |-----------------> | HUB | -------------|
        
Please be warned, this will be slower than normal browsing especially if 
the rest of the class is doing this at the same time.

## Warning About The Hub ##

The Crimsonvista.net ISP slows down incoming connections, probably to 
prevent DDOS or something. You may have trouble connecting to the Hub
when everyone else is. If you have trouble, wait a minute and try again.
If you can connect before class, please do. I will post the registration 
code early.

## The Labwork

In class, you need to complete the following exercises with one or more members of your group:

1. From a python shell, open sockets to each other through the hub-and-spoke system and send some basic messages back and forth ('hello world' in both directions is fine)
1. Host the python basic webserver to share a directory of files over the hub and spoke system
1. Use a browser to browse a group member's web server
1. Setup a proxy to google.com (or another https website) through hub and spoke
1. Connect to google.com (or another https website) through a group member's proxy on hub and spoke
1. Tap the communications of a group member's for all of the communications in this lab
1. Capture traffic for off the communications in this lab using Wireshark

You will submit a series of screenshots for all of these steps. The final submission should include:

1. A screenshot of a python shell wherein you sent and received messages over a socket to your group member
1. A screenshot of browsing your own webserver locally (not via hub and spoke)
1. A screenshot of browsing your group member's webserver over hub and spoke
1. A screenshot of browsing google.com through hub and spoke
1. A screenshot for tapped communications for a group member's python shell communications
1. A screenshot for tapped communications for a group member's webserver browsing communications
1. A screenshot for tapped communications for a group member's google browsing communications
1. A screenshot of wireshark visualizations of a group member's python shell communications
1. A screenshot of wireshark visualizations of a group member's webbrowsing communications
1. A screenshot of wireshark visualization of a group member's google browsing communications

There is more data than will fit in any one screenshot. Please find something that is representative. You should consider annotating the screenshot to point out/emphasize what you captured.
