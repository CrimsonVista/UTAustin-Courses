##############################################################################
#   WARNING: If you change how the targets are compiled in any way, your     #
#            exploits may not work when we test them. So don't do that!      #
##############################################################################

# tools
CC := gcc

# flags
CFLAGS := -g -fvar-tracking -fvar-tracking-assignments -O0 -Wall

all: run-target target1 target2 sploit1 sploit2

# targets

run-target: run-target.o util.o
	$(CC) run-target.o util.o -o run-target

target1: target1.o util.o
	$(CC) target1.o util.o -o target1

target2: target2.o util.o
	$(CC) target2.o util.o -o target2


# sploits

sploit1: sploit1.o util.o
	$(CC) sploit1.o util.o -o sploit1

sploit2: sploit2.o util.o
	$(CC) sploit2.o util.o -o sploit2

pipes:
	mkfifo /tmp/t1pipe /tmp/t2pipe
