##############################################################################
#   WARNING: If you change how the targets are compiled in any way, your     #
#            exploits may not work when we test them. So don't do that!      #
##############################################################################

# tools
CC := gcc

# flags
CFLAGS := -g -fvar-tracking -fvar-tracking-assignments -fno-stack-protector -O0 -Wall

all: sploit1 pipes

# targets

util32.o: util.c util.h
	$(CC) -m32 $(CFLAGS) -c util.c -o util32.o

target1.o: target1.c util.h
	$(CC) -m32 $(CFLAGS) -c target1.c -o target1.o

target2.o: target2.c util.h
	$(CC) -m32 $(CFLAGS) -c target2.c -o target2.o

target1: target1.o util32.o
	$(CC) -m32 $(CFLAGS) target1.o util32.o -o target1

target2: target2.o util32.o
	$(CC) -m32 $(CFLAGS) target2.o util32.o -o target2


# sploits

sploit1: sploit1.o util.o
	$(CC) sploit1.o util.o -o sploit1

sploit2: sploit2.o util.o
	$(CC) sploit2.o util.o -o sploit2

pipes:
	rm -f /tmp/t1pipe /tmp/t2pipe
	mkfifo /tmp/t1pipe /tmp/t2pipe

clean:
	rm -f *.o
	rm -f target1 target2 sploit1 sploit2
	rm -f /tmp/t1pipe /tmp/t2pipe
