# UT-Austin CS 361S Minilab

|||
|---|---|
| Minilab: | 1 - Buffer Overflow |
| Class Assigned: | 8/30/2021 |
| Points: | 50 |

## Introduction

This mini-lab is to remind you of how a buffer overflow works and
how to examine it in memory as it happens. You should have already
done a lab like this in your computer architecture class. However,
I have repeatedly seen students not remember details, so we will work
through it together.

## What you need to bring to class

To do this minilab in class you need:

EITHER:

I. Have your own setup

1. Bring your computer
2. On the computer have access to a typical nix-style environment
3. gcc
4. gdb
5. Make
6. git
7. screenshot tools

Please note, you can build everything if you have a 32 bit OS
(e.g., 32-bit linux in a virtual machine)

II. OR just use CS lab machines

1. If you're at home, you will need to have remote access via ssh
2. Make sure you still have screenshot capabilities

## What we will do in class

In class, we will walk through a buffer overflow. You will need
to do this on your own machine (or CS lab machine) and provide
some values on the screen as well as a screenshot of memory showing
key elements.

1. Clone the course repo: git clone https://github.com/CrimsonVista/UTAustin-Courses
2. within the repo, navigate to: 2021fa_cs361s/minilabs/1_bufferoverflow
3. Make the "sploit1" binary by running "Make" in this path. Do NOT run
`Make target1` as this will overwrite the preprovisioned binary

NOTE 1: The Makefile creates a pair of pipes in the `/tmp` directory.
If you are using the same machine as another student, you may run into conflicts.
Please use your own device if possible or coordinate during class by making
comments on Zoom as to which device you are using. It would be best to have
members of a group use the same machine, taking turns with the resources

NOTE 2: If you are on your own machine, you can build target1 yourself for
fun. To do this, you need to either build on a 32 bit OS (e.g., using virtualbox)
or you can build it on your 64-bit system so long as gcc multiarch is installed.

4. OPTIONAL BUT RECOMMENDED ON LAB MACHINES. Use a terminal emulator
such as `screen`. This enables you to use multiple screens in the same terminal
window and, more importantly, allows you to return to your work if you
get disconnected. If you're not familiar with `screen` (or `tmux`), please
google it.

5. In one terminal (or virtual screen), launch target1 using gdb: gdb ./target1
6. Set a breakpoint on the function overflow (look at the C code first if needed): b overflow
7. Tell gdb to start running the program: run 
8. In separate terminal (or virtual window): ./sploit1
9. in gdb, you will have stopped at the breakpoint
10. in gdb: info frame
11. in gdb: print $ebp
12. in gdb: print $esp
13. in gdb: print buf
14. in gdb: x /32x $esp
15. in gdb: n (until after strcpy)
16. in gdb: x /32x $esp

FOR THE LAB: 
* Identify the values of EBP, ESP, buf
* Take screenshot annotated with EBP, buf, return address, return EBP

17. Modify target1.c to send more than 127 bytes (maybe 150?)
    Use recognizable patterns, especially after 127
18. Rerun: make
19. Rerun the operations above again

FOR THE LAB:
* redo the screenshot showing the changes

20. Use calculations or brute force to find where to
put the overwrite address into the buffer. Insert
shellcode from `shellcode.h` at the beginning of the buffer, 0x90 until
the address which should overwrite the return address.
20. Rerun: make
21. Rerun the operations above again
21. After strcpy, 'ni' (next instruction) until return address reached

FOR THE LAB:
* screenshot showing the overflow succeeded (print $eip)

## Submission
Assemble the information and screenshots into a word document or
other such file (PDF is fine) and submit to the TA.

## Grading
This minilab, like all other minilabs, is pass fail. We are showing
you literally how to do everything. The class will be recorded. If
you missed it, please submit as soon as possible. This minilab is
designed to help you with the next lab.