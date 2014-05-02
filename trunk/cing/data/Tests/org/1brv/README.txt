The data in this directory are used to generate a CCPN project residing in:

Tests/data/ccpn/1brv_cs_pk_2mdl.tgz

252 CS were read directly from BMRB file bmr4020.str (256).
4 CS for 8 PHE HD2/HE2, and TYR HD2 and HE2 were lost due to merging.
The Asn HD21/HD22 were changed from non-stereospecific to SSA which might be a FC bug?

nb3 is original FT spectrum.
brsvg_sparky.ucsf is spectrum in UCSF SPARKY format. Can be read by FC in Analysis
En de orginele meta data staan in:
http://code.google.com/p/cing/source/browse/trunk/cing/Tests/data/org/1brv/brsvg.clu
See the end of this file.
Reading the sparky file into CCPN I see the following parameters working:

Global scale 1.0
Positive levels:		32530, 45542, 63759, 89262, 124967

SPEC         2     26   1024
  FILE nb3
  NAME nb3
  SOLV H2O
  EXPM      285.14999       4.50000
  NCHN    1024   2048
  NADR    1024   2048
  PBOX       3      3
  MBND       0
  IDIR       2      1
  IOFF       0      0
  CPLX       0      0
  FREQ      750.09998     750.09998
  SWID    10000.00000   10000.00000
  RPPM        0.00000       0.00000
  RCHN      891.59003    1784.04395
  RTOL        0.05000       0.05000
  BOXS        0.10000       0.10000
  NUCS  H H
  MAGT  N
  MIXT      100.00000
  NOED       12.00000
  CNTR       2     1    20     2    20     4.0000E+04     1.4000E+00
  ICLO       0      0
  ICHI     127    127
  SKIP       1      1
  PMLO        0.00000       0.00000
  PMHI       10.00000      10.00000
ENDSPC

The peaks were reformatted using 2D example from cing's xeasy code.

Calibration is done on peak that's top left in publication for amide-alpha of Glu 177
VAL171 became 14 so offset is 157.
GLU177 was    20.
From brsvg.pkr the peak coordinates are 9.049,3.942
In the spectrum when referenced on middle channel (water) at: 4.5 ppm the same peak is at: 8.602, 3.497
In [2]: ((9.049 - 8.602) + ( 3.942 -3.497) )/2
Out[2]: 0.44599999999999973
So instead of 4.5 for water I'll take: 4.946 and read the prot/peaks again