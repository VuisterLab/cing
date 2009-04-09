# Makefile for nmv.c
#

INCLUDES = /sw/include/python2.5/

CC = gcc
#CFLAGS = -fno-common -c
CFLAGS =  -c


nmv: nmv.o
	$(CC) -bundle -flat_namespace -undefined suppress nmv.o nmv_wrap.o nr/nrutil.o -o _nmv.so
#	$(CC) -bundle -flat_namespace nmv.o nmv_wrap.o nr/nrutil.o -o _nmv.so

nmv.o: nmv_wrap.c $(INCLUDES)
	$(CC) $(CFLAGS) nmv.c nmv_wrap.c -I$(INCLUDES)

nmv_wrap.c: nmv.c nmv.i 
	swig -python nmv.i

clean:
	\rm nmv.o nmv_wrap.o _nmv.so nmv_wrap.c nmv.py

nr: 
	$(CC) -c nmv.c -Inr/ 
