# Makefile for nmv.c
#

INCLUDES = /usr/include/python2.2/

CC = gcc
CFLAGS = -c


nmv: nmv.o
	gcc -shared nmv.o nmv_wrap.o nr/nrutil.o -o _nmv.so

nmv.o: nmv_wrap.c $(INCLUDES)
	$(CC) $(CFLAGS) nmv.c nmv_wrap.c -I$(INCLUDES)

nmv_wrap.c: nmv.c nmv.i 
	swig -python nmv.i

clean:
	\rm nmv.o nmv_wrap.o _nmv.so nmv_wrap.c nmv.py

nr: 
	gcc -c nmv.c -Inr/ 
