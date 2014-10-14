#
# Makefile for psa version 1.1 - A System for Chemical Shift Prediction
# (integrated, enhanced and multi-platform version)
#
# Author:   Alexander Nip
# E-Mail:   anip@redpoll.pharmacy.ualberta.ca
#
#CC=gcc -Xcpluscomm -cckr
CC=/usr/bin/gcc
CFLAGS=-O3
SYSLIB=
INCLUDES=-I/usr/include
LIBS=$(SYSLIB) -lm 
INSTALL_DIR=/usr/local/sbin
INSTALL_LIB=/usr/local/lib
OBJS=Main.o Nn.o Ssbond.o Residue.o Hetatm.o Vector.o Torison.o Cs.o Phipsi.o \
     Cspline.o Hydrogens.o Rings.o Es.o Proline.o Hbond.o Optimize.o \
     Display.o Dss.o 

# Rules to create .o files from .c files
.c.o:
	$(CC) -c $(CFLAGS) $(INCLUDES) $*.c

# Targets
all: shiftx

shiftx:	$(OBJS)
	$(CC) $(OBJS) $(CFLAGS) $(LIBS) -o $@

Main.o:		Main.c main.h states.h nn.h ssbond.h residue.h hetatm.h cs.h \
                phipsi.h torison.h hydrogens.h rings.h es.h proline.h hbond.h \
                optimize.h display.h

Nn.o:		Nn.c main.h residue.h nn.h vector.h cs.h

Ssbond.o:	Ssbond.c vector.h cs.h ssbond.h

Residue.o:	Residue.c main.h hetatm.h

Hetatm.o:	Hetatm.c hetatm.h

Vector.o:	Vector.c vector.h main.h

Torison.o:	Torison.c main.h vector.h residue.h

Cs.o:		Cs.c cs.h

Phipsi.o:	Phipsi.c phipsi.h cs.h main.h matrices.h rc.h cspline.h residue.h

Cspline.o:	Cspline.c

Hydrogens.o:	Hydrogens.c vector.h residue.h atomnametable.h

Rings.o:	Rings.c main.h rings.h residue.h vector.h cs.h nn.h

Es.o:		Es.c main.h cs.h vector.h

Proline.o:	Proline.c main.h nn.h cs.h

Hbond.o:	Hbond.c main.h nn.h hetatm.h cs.h hbond.h

Optimize.o:	Optimize.c cs.h residue.h

Display.o:	Display.c main.h display.h cs.h nn.h optimize.h

Dss.o:		Dss.c main.h psa.h

clean:
	rm -f *.o shiftx
