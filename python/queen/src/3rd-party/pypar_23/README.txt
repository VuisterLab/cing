------------------------------------------------
PyPAR - Parallel Python, efficient and scalable 
parallelism using the message passing interface (MPI).

Author:  Ole Nielsen (2001, 2002, 2003)
Email:   Ole.Nielsen@anu.edu.au
Version: 1.6.4
Date:    10 January 2003

Major contributions by 
  Gian Paolo Ciceri (gp.ciceri@acm.org)
  Prabhu Ramachandran (prabhu@aero.iitm.ernet.in) 
------------------------------------------------

The python module pypar.py and the C-extension mpi.c 
implements scalable parallelism on distributed and shared 
memory architectures using an important subset of 
the Message Passing Interface (MPI) standard.

FEATURES

- Python interpreter is not modified: 
  Parallel python programs need only import the pypar module.

- Easy installation: This is essentially about compiling and linking 
  the C-extension with the local MPI installation. A distutils setup file
  is included.

- Flexibility: Pypar allows communication of general Python objects 
  of any type.  
  
- Intuitive API: 
  The user need only specify what to send and to which processor.
  Pypar takes care of details about 
  data types and MPI specifics such as tags, communicators and buffers.
  Receiving is analogous.
 
- Efficiency:
  Full bandwidth of C-MPI programs is achieved for consecutive Numerical 
  arrays. Latency is less than twice that of pure C-MPI programs. 
  Test programs to verify this are included (pytiming, ctiming.c)
  
  See the DOC file for instructions on how to program with pypar.
  
PRE-REQUISITES

  Python 2.0 or later 
  Numeric Python (incl RandomArray) 
  Native MPI C library must be installed. 
  Native C compiler must be installed
  Pypar has been tested on the following platforms
    MPI on DEC Alpha
    LAM/MPI (6.5.6) on Linux 
    MPICH on Solaris (Sun Enterprise)
    MPICH on Linux (This was the hardest part)
    MPICH on Windows (NT/2000).
   
  
INSTALL

  UNIX PLATFORMS	
    Type
      python setup.py install 
 
    This should install pypar and its extension in the default
    site-packages directory on your system.
    
    If you wish to install it in your home directory use
  
      python setup.py install --prefix=~    	 
      
  WINDOWS (NT/2000, MPICH)
    To build, you need:
      1) MPICH (http://www-unix.mcs.anl.gov/mpi/mpich/)
      2) MinGW (http://www.mingw.org). Tested with GCC v 2.95-3.6.
      3) Set MPICH_DIR to the appropriate directory
      4) Build using 'python setup.py build --compiler=mingw32'
      5) Install using 'python setup.py install'.

  ---
  If you encountered any installation problems, read on.
  Do not worry about messages about unresolved symbols. This is normal 
  for shared libraries on some machines.
    
  To compile C-extension mpi.c requires either a mpi-aware c compiler
  such as mpicc or a standard c compiler with mpi libraries linked in.
  See local MPI installation for details, possibly edit Makefile and 
  type make.   
  See installation notes below about compiling under mpi. 

  
TESTING
  Pypar comes with a number of tests and demos available in the 
  examples directory - please try these to verify the installation.
  

RUNNING PYTHON MPI JOBS 
 
  Pypar runs in exactly the same way as MPI programs written in 
  C or Fortran. 
  
  E.g. to run the enclosed demo script (demo.py) on 4 processors, 
  enter a command similar to
   
    mpirun -np 4 python demo.py
 
  Consult your MPI distribution for exact syntax of mpirun. 
  Sometimes it is called prun and often parallel jobs will be
  submitted in batch mode.
  
  You can also execute demo.py as a stand-alone executable python script 
  
    mpirun -np 4 demo.py
  
  
  Enclosed is a script to estimate the communication speed of your system.
  Execute  
  
    mpirun -np 4 pytiming
  
  Care has been taken in pypar to achieve the same bandwidth and almost as 
  good communication latency as corresponding C/MPI programs.
  Please compile and run ctiming.c to see the reference values:
  
    make ctiming
    mpirun -np 4 ctiming       
    
  Note that timings might fluctuate from run to run due to variable 
  system load.   

  An example of a master-slave program using pypar is available in demo2.py.  
  
  
INSTALLATION NOTES (If all else fails)

Most MPI implementations provide a script or an executable called 
"mpicc" which compiles C programs using MPI and does 
not require any explicitly mentioned libraries. 
If such a script exists, but with a different name, change
the name in the beginning of compile.py. If no such script exists, put
the name of your C compiler in that place and add all required linking
options yourself.

For example, on an Alpha server it would look something like

 cc -c mpi.c -I/opt/Python-2.1/include/python2.1/
 cc -shared mpi.o -o mpi.so -lmpi -lelan
 
 or using the wrapper
 
 mpicc -c mpi.c -I/opt/Python-2.1/include/python2.1/
 mpicc -shared mpi.o -o mpi.so

On Linux (using LAM-MPI) it is 

 mpicc -c mpi.c -I/opt/Python-2.1/include/python2.1/
 mpicc -shared mpi.o -o mpi.so

 Start processors using
 lamboot -v lamhosts  

DOCUMENTATION

  See the file DOC for an introduction to pypar.
  See also examples demo.py and pytiming
  as well as documentation in pypar.py. 

  
HISTORY
version 1.6.4 10 Jan 2003
  Comments and review of installation
version 1.6.3 10 Jan 2003
  Minor issues and clean-up
version 1.6.2 29 Oct 2002
  Added Windows platform to installation as contributed by 
  Simon Frost
version 1.6.0 18 Oct 2002
  Changed installation to distutils as contributed by
  Prabhu Ramachandran
version 1.5, 30 April 2002
  Got pypar to work with MPICH/Linux and cleaned up initialisation
version 1.4, 4 March 2002
  Fixed-up and ran testpypar on 22 processors on Sun
version 1.3, 21 February 2002                                      
  Added gather and reduce fixed up testpypar.py
version 1.2.2, 1.2.3, 17 February 2002                                      
  Minor fixes in distribution
version 1.2.1, 16 February 2002                                      
  Status block, MPI_ANY_TAG, MPI_ANY_SOURCE exported                 
Version 1.2, 15 February 2002                                       	   
  Scatter added by Gian Paolo Ciceri                                   
Version 1.1, 14 February 2002                                       	   
  Bcast added by Gian Paolo Ciceri                                   
Version 1.0.2, 10 February 2002                                          
  Modified by Gian Paulo Ciceri to allow pypar run under Python 2.2  
Version 1.0.1, 8 February 2002                                       
  Modified to install on SUN enterprise systems under Mpich          
Version 1.0, 7 February 2002                                         
  First public release for Python 2.1 (OMN)                          
  
  
  
LICENSE
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License (http://www.gnu.org/copyleft/gpl.html)
    for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307


 Contact address: Ole.Nielsen@anu.edu.au

 =============================================================================
   
ACKNOWLEDGEMENTS  
  This work was supported by School of Mathematical Sciences at 
  the Australian National University and funded by Australian 
  Partnership for Advanced Computing (APAC).
  Many thanks go to 
  
    Gian Paolo Ciceri (gp.ciceri@acm.org) 
        for fixing pypar to run under Python 2.2 and for adding all the 
        collective communication stuff from version 1.1 and onwards.
    Prabhu Ramachandran (prabhu@aero.iitm.ernet.in)
        for making a proper distutils installation procedure
    Simon D. W. Frost (sdfrost@ucsd.edu)
        for testing pypar under Windows and adding installation procedure 
    Jakob Schiotz (schiotz@fysik.dtu.dk) and Steven Farcy (steven@artabel.net) 
        for pointing out initial problems with pypar and MPICH.
    Markus Hegland (Markus.Hegland@anu.edu.au)
        for supporting the work.


  
     









