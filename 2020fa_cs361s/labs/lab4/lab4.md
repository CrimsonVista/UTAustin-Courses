## VM Setup

Download the lab4vm.ova file from canvas and import it into Virtualbox.  Once done go to its settings and travel to the network section.  Click on advanced and find the button labeled port forwarding.  Create a new rule titled SSH using the TCP protocol.  Set the host port to 2222 (or any port that is open on your device) and set the guest port to 22.  This will allow you to ssh into your vm at localhost port 2222.  Now launch your vm and access it using the corresponding ssh call for your host machine.  For example in windows powershell, use the command

```
ssh user@localhost -p 2222
```

Now you can login into the machine using "user" as the username and password.  You will be doing most of your lab as "user", however before you start you should sign in as root (password is also root) and install netcat with

```
pkgin install netcat
```

*NOTE:* The command for netcat is `nc`, not `netcat`. If you type `netcat` you will still get the error message about the command not being found.

You may also want to install bash, if you're more comfortable with the shell, and git if you'd like to move your data on/off the machine via your repo.  These can both be installed with pkgin. If you do install git, you will also need the mozilla rootcerts for HTTPS to work.  This is done with the following commands as root.

```
pkgin install mozilla-rootcerts
mozilla-rootcerts intsall
```

If you don't want to use git to move data, you can also use scp or other network copying tools.

# Lab 4 ROP Exploits

## Goal

The goal of this assignment is to gain hands-on experience with exploitation of memory corruption bugs without code injection, in “code-reuse” or “return-oriented” style. You will be exploiting a vulnerable target program that is a simplified version of target1 from the buffer overflow example, but this time there is *no RWX page on which to place shellcode*. Your goal is to write three progressively more sophisticated return-oriented payloads.

As in the buffer overflow example, we will use a virtual 32-bit x86 machine running Linux. You can reuse the VMs the buffer overflow example.

In addition to the ROP reading for class, you may wish to google additional explanations and papers.

In the class github, you are given the source code for one exploitable program, `target.c`. Your goal is to write three exploit programs (`sploita.c`, `sploitb.c`, and `sploitc.c`), all exploiting the same target, but to different ends.

The exploit behavior gets increasingly complicated from A to B to C. Accordingly, while not required, you should AIM to have the exploits for A and B done after the first week, leaving all of week 2 to work on C. You are responsible for having good time management.

## Setting up the Environment

You will use the same VM as in the buffer overflow example. The class github has the code for getting started under `labs/lab4`.

## The Target

The provided code includes a Makefile that specifies how to build the target.

The Makefile also provides a "make pipes" command that will create the named pipe /tmp/targetpipe. (Note that we have changed the name since the buffer overflow example.) *As before, you may need to rerun make pipes each time you restart the x86 virtual machine*.

You should not run the target directly. Instead, run it through the run-target wrapper. The run-target wrapper will ask for two arguments. The first is the number of file descriptors to allocate before executing the target. You should leave this at 0 for sploits A and B, and increase it only when you are ready to test sploit C. The second argument is the last 4 digits of your UTEID. Make sure always to use the same, correct ID; this will ensure that addresses for stack variables remain consistent each time you examine your target, making your exploits reliable and repeatable. If you work with a partner, you may use either of your two four-digit IDs. (You don't have to work with the same partner for project 2 as you did for project 1, and even if you do, you don't have to pick the same out of your two IDs. But you must work with the same partner and use the same ID for all three sploits in this project.)

*NOTE:* Because the target in this lab calls readcmd inside overflow, the buffer overflow example strategy of attaching GDB to the target and setting a breakpoint at the beginning of overflow will not work. You will instead want to set the breakpoint in overflow after readcmd returns.

## Executing System Calls

The code-reuse payloads you will write will need to make system calls. On 32-bit x86, the Linux kernel expects programs to make system calls using as follows. To trap into the kernel, the program executes the `int 0x80` interrupt instruction. Before trapping into the kernel, it puts the system call number in the register `eax`. The actual arguments to the system call are in corresponding registers, and the program needs to ensure they are there before it traps into the kernel. The first argument needs to be in `ebx`, the second argument in `ecx`, the third in `edx`, and so on.

## Useful Instruction Sequences

For your return-oriented payloads, you will want to use instruction sequences in libc, the standard C library. We have included a dump of instructions in NetBSD VM's libc, whether intended or unintended. This list is in the lab directory as `gadgets-2.txt`.

Addresses in the leftmost column are offsets into libc. You will want to add the base address of libc to get an in-memory address. For the target, libc should be loaded at `0xbba73000`.

For example, the line

    0x001270e1: pop eax; ret; 

means that at offset `0×001270e1` into libc, you should find the instruction `pop eax` followed by the instruction `ret`. You can verify that from within GDB by running a command like `x/2i 0xbba73000 + 0x001270e1`.

Note that instructions here are presented in Intel notation, which in particular means that the destination operand is listed first. So, for example, the first instruction in

    0x000dfd88: mov dword ptr [eax], edx; ret; 

will store the contents of the `edx` register into the 4 bytes of memory whose address is in the `eax` register.

For completeness, we also produced dumps of all instruction sequences of lengths 3, 4, 5, and 6, but you should be able to complete the project using only instruction sequences of length 2.

You MUST NOT use Ropper or other similar tools to build your exploit payloads—doing so by hand is key to this project. If you are caught doing so, you will receive a 0 on the assignment and referral to the University for cheating. We're serious about this.

## The Vulnerability
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

## The Exploits

The assignment tarball also contains skeleton source for the exploits which you are to write, along with a Makefile for building them. Unlike project 1, you will not inject shellcode into the target; instead, you will reuse instruction sequences in the target libc to induce desired behavior. All three exploits will attack the same target, but they will induce increasingly sophisticated behavior, as follows.

### Sploit A

Sploit A should cause the target to `execve` a shell on its own terminal, without making a network connection first. That is, you will want to induce behavior like:

1. Write to memory location x the NUL-terminated string `"/bin/sh"`.
1. Write to the 8 bytes at memory starting at location y first the four-byte address x and then the four-byte value zero.
1. Put on the stack the three arguments that `execve` expects: the value x; the value y; and either the value y+4 or the value 0.
1. Put in register `eax` the value 59, for `execve`.
1. Execute `int 0x80` to trap into the kernel.

### Sploit B

Sploit B will make a network connection to localhost (IP address `127.0.0.1`, port `12345`), arrange for process standard input, standard output, and standard error to be redirected to the resulting network connection, and then spawn a shell. It can assume that the return value from the socket system call, which returns a file descriptor for the new socket, is always 3 (the first free descriptor after `stdin`, `stdout`, `stderr` aka 0, 1, 2), and hardcode this value later on in the payload. You will want to induce behavior like:

1. Put on the stack the three arguments that the `__socket30` system call expects: the four-byte value 2 (`AF_INET`); the four-byte value 1 (`SOCK_STREAM`); and the four-byte value 0.
1. Put in register `eax` the value 394, for `__socket30`.
1. Execute `int 0x80` to trap into the kernel.
1. After the system call, the file descriptor of the newly allocated socket will be in the `eax` register, but you may assume for the purposes of sploit B that this register holds the value 3.
1. Let x be the address of 16 contiguous bytes in memory, to store a `struct sockaddr_in`. Byte 0 and bytes 8—15 of this structure do not matter, but the others do. Byte 1 should be 2 (`AF_INET`); bytes 2 and 3 should be the port number `12345`, stored big endian (`0×3039`); bytes 4 through 7 should be the IP address `127.0.0.1`, stored big endian (`0×7f000001`).
1. Put on the stack the three arguments that the connect system call expects: the four-byte value 3, the hardcoded file descriptor we assume the socket system call returned; the value x; and the four-byte value 16.
1. Put in register `eax` the value 98, for connect.
1. Execute `int 0x80` to trap into the kernel again.
1. Next we call `dup2` three times, to duplicate the socket descriptor onto each of descriptors 0, 1, and 2. For all three calls, make sure that register `eax` holds the value 90, for `dup2`.
1. In the first call to `dup2`, put the following two arguments on the stack: the four-byte value 3, the hardcoded file descriptor we assume the socket system call returned; and the four-byte value 0. Execute `int 0x80` to trap into the kernel.
1. In the second call to dup2, put the following two arguments on the stack: the four-byte value 3, the hardcoded file descriptor we assume the socket system call returned; and the four-byte value 1. Execute `int 0x80` to trap into the kernel.
1. In the third call to dup2, put the following two arguments on the stack: the four-byte value 3, the hardcoded file descriptor we assume the socket system call returned; and the four-byte value 2. Execute `int 0x80` to trap into the kernel.
1. Finally spawn a shell using the same behavior as in sploit A above.

### Sploit C

Sploit C will behave the same as sploit B, but it will not make the assumption that `socket()` returns descriptor 3. Instead, having made the `socket()` system call, before returning, it stores the value in `eax` somewhere convenient in memory. Then it loads that value back and puts it on the stack in the appropriate location before the connect system call and before each of the `dup2` system calls.


### Secret
We declare the secret array as a static global char pointer.
```c
static char *secret;
```
It means `secret` will be allocated in `data` section instead of `stack` or `heap`. Therefore we can find where `secret` is by examining the `target` binary.
One way to do that is using `objdump`
```shell
$ objdump -t target | grep secret
08139ea8 l     O .bss  00000004 secret
```
The first column is the address allocated to our `secret`, and the value stored in that address is the pointer to the secret value.

## Grading and Submission

Submissions are per-team. To submit:

1. Create a subdirectory in your github repository called `lab4`. This should be the same repo that you used in the previous labs.
1. Add a file called `lab4/ID.txt` that contains either one line (if you worked by yourself) or two lines (if you worked with a partner), each in the following format: ProjID EID FirstName LastName. Here ProjID is the four-digit ID that you were assigned over e-mail. If you worked with a partner, make sure the that ProjID that you used in developing your sploits is on the first line, and the other ProjID is on the second line.
1. Add the files `sploita.c`, `sploitb.c`, and `sploitc.c` which should be the only files where you change code from the class repo


Your submission will be graded with 33.3 points for each sploit.

(*Note:* We are keeping the grading even for each sploit even though some are harder than others. This way, if you are unable to complete a harder sploit, it doesn't disproportionately impact your grade).

