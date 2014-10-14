ABOUT SHIFTX
-------------

 SHIFTX uses a hybrid predictive approach that employs pre-calculated, 
 empirically derived chemical shift hypersurfaces in combination with 
 classical or semi-classical equations (for ring current, electric field, 
 hydrogen bond and solvent effects) to calculate 1 H, 13 C and 15 N chemical
 shifts from atomic coordinates.

REFERENCE
---------

 Stephen Neal, Alex M. Nip, Haiyan Zhang, David S. Wishart (2003) "Rapid and
 accurate calculation of protein 1H, 13C and 15N chemical shifts" Journal of
 Biomolecular NMR, 26:215-240.

PROGRAMMING LANGUAGE
--------------------

 SHIFTX is written by C, requiring gcc to compile.

INSTALL SHIFTX
--------------

 1) Unix/Linux system
    a) uncompress the file shiftx.tar.gz
       >gunzip shiftx.tar.gz
       >tar -xvf shiftx.tar
    b) compile
       >cd shiftx
       >make
       a binary file "shiftx" will be generated.

RUN SHIFTX
----------

 1) Unix/Linux system
   a) Interactive mode
      >./shiftx
      Then follow the instructions.
   b) Batch mode
      >./shiftx 1[chain name] [input] [output]
      e.g.  >./shiftx 1A 2TRX.pdb 2TRX.out
	or  >./shiftx 1 3TRX.pdb 3TRX.out
   c) Input file format

      PDB data format is required.

WEB ACCESS
----------

   SHIFTX web server can be accessed at 
   http://redpoll.pharmacy.ualberta.ca/shiftx
   Notes:Web version of the shiftx is a little bit better than the code distribution

MORE INFORMATION
----------------

 If you have any questions or wish to know more information, please contact
 David Wishart (david.wishart@ualberta.ca)
