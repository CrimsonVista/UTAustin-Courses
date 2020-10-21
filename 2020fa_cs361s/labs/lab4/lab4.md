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

# Buffer Overflow Examples

Make sure you are logged in as user and lets walk through some buffer overflow attacks.  The code for these attacks can be found in the buffer_overflow directory.

## Sploit1

[Here](https://avicoder.me/2016/02/01/smashsatck-revived/) is a reading to get familiar with Buffer Overflows to better understand this exploit.

This exploit involves target1, which simply reads in the data you give it into a variable called cmdbuf and strcopies it over to buf.  What we want to do is insert our shellcode we want to run in cmdbuf and make cmdbuf large enough so that its overflowed data holds the starting address of our shellcode that we have in cmdbuf.  When it is copied into buf, that extra data will override the return address on the stack, and cause a jump to our shellcode that resides inside cmdbuf and execute it.

We want to use gdb here to analyze what the cmdbuf address is and to analyze the contents of the address space around the stack pointer so we know how much to overflow our string.

Call `make` and `make pipes` before running `./run-target 1 2452` to prepare target 1 for sploit1.  In another terminal also run `nc -l -p 6666` to await our hack to work.

To attach gdb to your program you run `gdb -p pid` where the pid is the number you find after running `ps` in your shell and finding the run-target proccess id.  Now we want to set a breakpoint at the overflow function using `b overflow`. Now we can run `./sploit1` and hit continue in gdb with `c`.  


If you set your breakpoint (`b overflow`) Gdb will stop when it reahes the overflow function where cmdbuf is being copied over into buf.  Lets try and find the address for cmdbuf (that we will feed to the stackpointer so we ret into cmdbuf) using the gdb command `x/x cmdbuf`.  We will find that the address of cmdbuf is 0xbba72000. 
```
(gdb) x/x cmdbuf
0xbba72000:     0x31c03190
```

You can also look at the 100 bytes following cmdbuf to get a "picture" of memory.

```
(gdb) x /100 cmdbuf
0xbba72000:		0x31c03190      0x504050c9      0xb0505040      0x8980cd61
...
0xbba72180:		0x00000000	0x00000000 ...
```	

(Also useful are the gdb commands `list`, `frame`, and `where`. Try these out and see what you learn!)

If you look at sploit1 we actually feed 0xbba72001 into the overflow string because 0x00 will cause our string to terminate early.  Since we are starting at 01 now instead of 00 we will fill in a 0x90 val in our string before our shellcode to make the shellcode now start at 0xbba72001.  


After we copy in our shellcode to the string in sploit1 we need to know how long to make the rest of the string so that we properly overflow the buffer and get the stack pointer $esp to point at our return address before it returns out of the overflow function.  We can use gdb to step from where we left off with `step` until we reach line 13 or right before the overflow function ends and returns.  You can use `disas` and `stepi` to traverse the assembly instructions until you get to the exact ret instruction.


We will fill in some dummy values in our string (like nops value 0x90) and do a test run with gdb.  Now we look at $esp right before the ret instruction using `x/18x $esp - 68` to look at the 18 4-byte addresses before and including the address $esp is looking at.  We get the below output
```
(gdb) x/18x $esp -68
0xbfbf925c:     0x2f2f6851      0x2f686873      0x896e6962      0x535451e3
0xbfbf926c:     0xcd3bb050      0x90909080      0x90909090      0x90909090
0xbfbf927c:     0x90909090      0x90909090      0x90909090      0x90909090
0xbfbf928c:     0x90909090      0x90909090      0x90909090      0x90909090
0xbfbf929c:     0x90909090      0xbba72001
(gdb) x/x $esp
0xbfbf92a0:     0xbba72001
```
This output is from my already working sploit1, but we can see the amount of padding we will need in our string in order to overflow into the address that $esp will be looking at before the return call.  If you look at the rest of my sploit1, I add the right number of 0x90 and then add the address of cmdbuf we want to jump to.  We know we got it right because we see the 0xbba72001 address when we type `x/x $esp` before we hit return.  If we run run-target and sploit1 again without gdb and check our netcat connection in the other terminal, we can now use ls and other terminal commands on our victim machine.  Our shellcode basically made our victim connect to port 6666 and give us access.

Please note that, when using netcat and gdb is attached to the target, gdb may print out errors such as:

```
Program received signal SIGTRAP, Trace/breakpoint trap.
0xbbbefe30 in .rtld_start () from /usr/libexec/ld.elf_so
```

Or

```
Cannot access memory at address 0x6f732e67
Cannot access memory at address 0x6f732e63
```

This is because gdb is *confused* from your mucking around, but keep hitting "c" (continue) and you should see the output of ls in your netcat window.

## Sploit2

Read this paper on [Format String Vulnerabilities](https://cs155.stanford.edu/papers/formatstring-1.2.pdf) to better understand this exploit.

Sploit2 is a lot harder than sploit1 because our target is not using strcpy() but rather snprintf.  This makes it so we cannot overflow by just feeding the target a long string because snprintf will cut off our string if it goes over the size of buf.  Luckily there is another way to manipulate the stack using format strings.

The specific format string that lets us still change the return address of our stack is %n.  This format string takes a 4 byte address from the string and writes to that address the count of the number of bytes stored in that string up to that point %n was called.  We can get large amounts of bytes stored in our original small string of around 150 bytes using the %u format string to take a value in our string and repeat it x times where x is put in %xu (for example %165u in my sploit repeats the 4 bytes it finds in the string 165 times).  This increases the bytes in the string and allows us to manipulate the value %n will write to its given address.


To put it all together, we will write to the address the stack pointer is looking at before ret the address of cmdbuf again, except using %n 4 times to write each byte of our ret address to each byte of $esp's memory location.  
```
memcpy(bufr, "AAAdumm\xa0\x92\xbf\xbfzzzz\xa1\x92\xbf\xbfzzzz\xa2\x92\xbf\xbfzzzz\xa3\x92\xbf\xbf", 35);

  memcpy(bufr+35, shellcode, 83);
  strcpy(bufr+118, "%08x%165u%n%253u%n%135u%n%20u%n");
```


If you look at my string in sploit2, I give the program "AAA" since that input gets ignored by snprintf.  Then I give 4 dummy bytes "dumm" followed by the address byte that I want %n to copy into first (this is the  first byte of the address that $esp is looking at before calling ret), then another 4 dummy bytes "zzzz" followed by the address byte I want %n to copy into next.  I do this for all 4 address bytes.  I then drop in the shell code and the format string.  

Looking at the format string, I used %08x to look at the current address my string is on.  Then I used %165u to write 165 unsigned decimals (it uses those 4 dummy bytes as an int) into the string so I could manipulate the value that I write (165 + 8 bytes from 08x + 118 bufr bytes = 291, which has 32 or 0x23 as its lowest order byte) into the stack pointer address with %n , I do this 4 times each with different values for %u (the subsequent %n calls overwrite the higher order bytes of previous %n calls, so we only care about the lower order bytes) so that I can get %n to write each byte correctly for the return address we want (which in this case is 0xbba72023).

To verify I am writing the bytes to the correct values, I start up runtarget like last time except with 2 as the second argument instead of 1.  Attach gdb and set a breakpoint at badfmt.  We get to line 13 and now we can analyze what my code has done.
```
(gdb) x/x $esp
0xbfbf92a0:     0xbba72023
```
We can see it has written the exact address of where my shellcode begins in my attack string at the address the stackpointer is pointing to before it calls ret.  As expected since this is the same shellcode as sploit1, you should be able to connect to the victim with netcat now.

# Lab 4 ROP Exploits

## Goal

The goal of this assignment is to gain hands-on experience with exploitation of memory corruption bugs without code injection, in “code-reuse” or “return-oriented” style. You will be exploiting a vulnerable target program that is a simplified version of target1 from the buffer overflow example, but this time there is *no RWX page on which to place shellcode*. Your goal is to write three progressively more sophisticated return-oriented payloads.

As in the buffer overflow example, we will use a virtual 32-bit x86 machine running NetBSD. You can reuse the VMs the buffer overflow example.

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

The code-reuse payloads you will write will need to make system calls. On 32-bit x86, the NetBSD kernel expects programs to make system calls using as follows. To trap into the kernel, the program executes the `int 0x80` interrupt instruction. Before trapping into the kernel, it puts the system call number in the register `eax`. The actual arguments to the system call are passed on the stack, and the program needs to ensure they are there before it traps into the kernel. The first argument needs to be at location `esp+4`, the second aregument at location `esp+8`, the third at `esp+12`, and so on.

Note that no argument is passed at location `esp+0`; the four bytes there are ignored by the kernel. This is an optimization to facilitate convenient system call wrappers. It will also be very handy for you if you make your system calls using the instruction sequence `int 0x80; ret`.

## Useful Instruction Sequences

For your return-oriented payloads, you will want to use instruction sequences in libc, the standard C library. We have included a dump of instructions in NetBSD VM's libc, whether intended or unintended. This list is in the lab directiory as `gadgets-2.txt`.

Addresses in the leftmost column are offsets into libc. You will want to add the base address of libc to get an in-memory address. For the target, libc should be loaded at `0xbba73000`.

For example, the line

    0x001270e1: pop eax; ret; 

means that at offset `0×001270e1` into libc, you should find the instruction `pop eax` followed by the instruction `ret`. You can verify that from within GDB by running a command like `x/2i 0xbba73000 + 0x001270e1`.

Note that instructions here are presented in Intel notation, which in particular means that the destination operand is listed first. So, for example, the first instruction in

    0x000dfd88: mov dword ptr [eax], edx; ret; 

will store the contents of the `edx` register into the 4 bytes of memory whose address is in the `eax` register.

For completeness, we also produced dumps of all instruction sequences of lengths 3, 4, 5, and 6, but you should be able to complete the project using only instruction sequences of length 2.

You MUST NOT use Ropper or other similar tools to build your exploit payloads—doing so by hand is key to this project. If you are caught doing so, you will receive a 0 on the assignment and referral to the University for cheating. We're serious about this.

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

## Grading and Submission

Submissions are per-team. To submit:

1. Create a subdirectory in your github repository called `lab4`. This should be the same repo that you used in the previous labs.
1. Add a file called `lab4/ID.txt` that contains either one line (if you worked by yourself) or two lines (if you worked with a partner), each in the following format: ProjID EID FirstName LastName. Here ProjID is the four-digit ID that you were assigned over e-mail. If you worked with a partner, make sure the that ProjID that you used in developing your sploits is on the first line, and the other ProjID is on the second line.
1. Add the files `sploita.c`, `sploitb.c`, and `sploitc.c` which should be the only files where you change code from the class repo


Your submission will be graded with 33.3 points for each sploit.

(*Note:* We are keeping the grading even for each sploit even though some are harder than others. This way, if you are unable to complete a harder sploit, it doesn't disproportionately impact your grade).

