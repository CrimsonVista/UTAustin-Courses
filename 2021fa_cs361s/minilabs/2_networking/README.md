# UT-Austin CS 361S Minilab 2 - Networking

|||
|---|---|
| Minilab: | 2 - Networking |
| Class Assigned: | 9/13/2021 |
| Points: | 50 |

In this lab, we will do in-class exercises to send data over networks and visualize
it with Wireshark. Although we won't learn too much about TLS yet, we will see
that TLS makes it impossible to read the data without a key

## Setup

The only setup for this lab is installing wireshark. This should be straightforward for
most users. For Mac M1 users, I believe you have to install rosetta. Please search Google
for the appropriate instructions.


## Wireshark

When you install Wireshark in some POSIX environments, it will ask you if you want to install non-root user support. Specifically, 
it will want to know if you'd like anyone in group "wireshark" to be able to run the pcap stuff. You
should say "yes". If you find that you did this wrong, you can reconfigure the 
system by the command `sudo dpkg-reconfigure wireshark-common`.

Afterward, you will need to add your user to the group by this command:

    adduser <your username here> wireshark
	
After adding yourself to the group, you will need to restart. At least, for me, logging out and logging
back in wasn't enough, even though it's supposed to be. After a restart, if you type `groups` with no
arguments, it should list all the groups for the current user and it should include `wireshark`.


## Examining the OSI layers with Wireshark

Along with the rest of the class, we will visit "http://example.com" in a web browser. PLEASE MAKE SURE
TO TYPE HTTP! We want this test to NOT be encrypted.

First, launch Wireshark and pick an appropriate adapter monitoring traffic. Wireshark should show
you which adapters have traffic on them by graphing the rates. Once you start Wireshark, it will
start collecting every packet and will overwhelm you with data. Don't worry about that yet.

Now, in your browser, go to "http://example.com". Once the page has loaded, go back to wireshark
and press the "stop" button.

Somewhere among all of the many thousands of collected packets are the ones we are looking for. How
to find them? Wireshark has a filter bar at the top. Typing in "http" will tell wireshark to only show
packets with HTTP traffic. You should be able to see some traffic to this website. BE WARNED, however,
that Wireshark can sometimes have a hard time resolving the IP address to the name "example.com" because
multiple domains use the same address and Wireshark can get confused. If it's not showing up, look
for the IP address 93.184.216.34. If you still can't find it, ask for help.

As part of the mini lab, take a screenshot showing you found transfers relating to example.com in
wireshark. You just need to show a single capture event with the correct domain name or ip address
in the source or destination.

Once you've found one of these capture events, click on it. In the window below, you should see all
of the networking detail. You should see multiple "layers" starting with Frame, followed by Ethernet (or 
maybe WiFi), Internet Protocol, Transmission Control Protocol, and HyperText Transfer Protocol. Each
of these layers has an arrow to the left indicating that it can be expanded. Expand all the different layers
to see the data that is in each one.

In the Internet Protocol layer, you should see  both a Source Address and a Destination Address. Take a 
screenshot of this.

The IP layer is where all the global addressing happens. Every packet that reaches an Internet host
somewhere in the world is using this data. 

Also take a look at the HTTP protocol. You should see some kind of HTTP request or HTTP response.
If it is an HTTP request, it probably starts with "GET". If it is a response, it probalby starts
with a number like 200. Take a screenshot of this as well.

Now, using the filter bar, change the filtering from "http" to "ip.host==example.com". If Wireshark
did not display "example.com", you will need to use the IP address instead. This should still show you
communications between your computer and example.com but additional communications besides the 
HTTP transfer for the webpage. We will talk in class about what all of these mean. For now, 
take a screenshot of the top window showing the various communications between your computer
and example.com.

Finally, restart your wireshark capture by pressing the shark icon. Be warned, this will get rid
of everything you're currently looking at so make sure you've taken your screenshots first.

Once packets are being captured again, go back to your browser and browse to "https://example.com".
Note that this is https and not http. Once the page has loaded, pause the capture.

If you are still filtering on "ip.host==example.com" you will still see data, but you will no longer
see HTTP data. Why is that? We will talk about this in class but please take a screenshot of the top
window from Wireshark. This should include references to the TLS protocol.


## Sending data between computers using "Sockets"
Although we won't be using sockets directly in class, sockets are a simple building block for
sending data over a TCP connection. For this next part of the lab, you need to use a CS lab machine.
If you do not have an account, please just watch and talk to me after class. The following test
needs to be done between pairs of students so find a partner (preferably in your group).

Student 1 needs to set up a "server". Launch the Python interactive shell and execute
the following:

* import socket
* s = socket.socket()
* s.bind(('',<n>))
* s.listen(1)
* conn, addr = s.accept()

Note that "<n>" is any number between 1025 and 64000+, so pick something random (e.g., 15293, 2998, etc).

Student 2 needs to setup a "client". Launch the Python interactive shell and execute
the following:

* import socket
* conn = socket.socket()
* conn.connect((<host>, <n>))

Note that "<host>" is the name of the machine of your partner (e.g., "Aries"), and "<n>
is whatever number they picked for part 1.

The student running the server should note that the "s.accept" command "hangs" until after
student 2 does the connect. when it returns, examine the addr and conn variable.

At this point, either student can send data to the other by typing `conn.send(b"something")`
and the student can receive it by typing `conn.recv(1024)`.

Take a screen shot of sending a message or two.
## Submission
Assemble the screenshots into a word document or
other such file (PDF is fine) and submit to the TA.

## Grading
This minilab, like all other minilabs, is pass fail. We are showing
you literally how to do everything. The class will be recorded. If
you missed it, please submit as soon as possible. This minilab is
designed to help you with the next lab.