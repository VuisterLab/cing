# Makefile for mpiext.c
#

INCLUDES = /usr/include/python2.2/

CC = mpicc
CFLAGS = -c

mpiext.so: mpiext.o
	$(CC) -shared mpiext.o -o mpiext.so

mpiext.o: mpiext.c $(INCLUDES)
	$(CC) $(CFLAGS) mpiext.c -I$(INCLUDES)

clean:
	\rm mpiext.o mpiext.so *.pyc

