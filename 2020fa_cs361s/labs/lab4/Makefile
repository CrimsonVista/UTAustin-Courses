##############################################################################
#   WARNING: If you change how the targets are compiled in any way, your     #
#            exploits may not work when we test them. So don't do that!      #
##############################################################################

# tools
CC := gcc

# flags
CFLAGS := -g -fvar-tracking -fvar-tracking-assignments -O0 -Wall

all: run-target target sploita sploitb sploitc

# targets

run-target: run-target.o util.o
	$(CC) run-target.o util.o -o run-target

target: target.o util.o
	$(CC) target.o util.o -o target


# sploits

sploita: sploita.o util.o
	$(CC) sploita.o util.o -o sploita

sploitb: sploitb.o util.o
	$(CC) sploitb.o util.o -o sploitb

sploitc: sploitc.o util.o
	$(CC) sploitc.o util.o -o sploitc

pipes:
	mkfifo /tmp/targetpipe
