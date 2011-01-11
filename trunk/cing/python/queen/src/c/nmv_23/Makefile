# Makefile for nmv.c
#

#INCLUDES = /sw/include/python2.5/
INCLUDES =

#CC = gcc
CC = /opt/local/bin/gcc-mp-4.4
#CFLAGS = -fno-common -c
# result from: python-config --cflags
CFLAGS =  -c -I/opt/local/Library/Frameworks/Python.framework/Versions/2.6/include/python2.6 \
             -fno-strict-aliasing -fno-common -dynamic -pipe -O3 -DNDEBUG -g -fwrapv -Wall



nmv: nmv.o nmv_wrap.o
	$(CC) -bundle -flat_namespace -undefined suppress nmv.o nmv_wrap.o nr/nrutil.o -o _nmv.so
#	$(CC) -bundle -flat_namespace nmv.o nmv_wrap.o nr/nrutil.o -o _nmv.so
	mv _nmv.so nmv.py ../../..
	
nmv.o: nmv_wrap.c
	$(CC) $(CFLAGS) nmv.c nmv_wrap.c

nmv_wrap.c: nmv.c nmv.i 
	swig -python nmv.i

clean:
	\rm nmv.o nmv_wrap.o nmv_wrap.c

nr: 
	$(CC) -c nmv.c -Inr/ 
