"""
Adds export/import to NIH files
Adds Talos+ related methods
"""
import cing
from cing import constants
from cing.core import sml
from cing.core import validation
from cing.Libs import io

from cing.Libs.Adict import Adict
from cing.Libs.AwkLike import AwkLike
from cing.Libs.AwkLike import AwkLikeS
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import DihedralRestraint
from cing.core.classes import jsonTools as jsonTools
from cing.constants import * #@UnusedWildImport
from cing.definitions import cingPaths
from cing.definitions import cingDefinitions
from cing.definitions import directories

# versions < 0.95 not logged with version number
# cing versions >1.0 first ones to include this
__version__ = cingDefinitions.version



NIHheaderDefinitionString = """
/***/
/* fdatap.h: defines the NMRPipe data header array FDATA, and
/*           outlines some data format details.
/***/

/***/
/* The NMRPipe parameter array FDATA currently consists of 512 4-byte
/* floating-point values which describe the spectral data.  While all numerical
/* values in this array are floating point, many represent parameters
/* (such as size in points) which are integers.  Some parts of the
/* header contain packed ascii text.
/*
/* There are currently three variations of spectral data in the NMRPipe
/* format:
/*
/*   1. Single-File (1D and 2D): the data are stored in a single
/*      binary file consiting of the header followed by the
/*      spectral intensities, stored in sequential order as
/*      4-byte floats.
/*
/*   2. Multi-File (3D and 4D): the data are stored as a series
/*      of 2D file planes, each with its own complete header
/*      followed by the spectral intensities in sequential order.
/*
/*   3. Data Stream (1D-4D): the data are in the form of a pipeline
/*      stream, with a single header at the beginning followed by
/*      all of the spectral intensities in sequential order.
/*
/* The header values can be manipulated directly, but this is not
/* recommended.  Instead, the functions getParm() and setParm() can
/* be used to extract or set header values according to parameter
/* codes and the dimension of interest (if any).  See the source
/* code distribution for examples of these functions.
/*
/* The NMRPipe format was created to be compatible with an older format
/* which pre-dates phase-sensitive NMR and multidimensional NMR.
/* So, for historical reasons, there are some potentially confusing
/* aspects regarding definition of dimension sizes, data types,
/* and interleaving of real and imaginary data.
/*
/* In the NMRPipe nomenclature, the dimensions are called the X-Axis,
/* Y-Axis, Z-Axis, and A-Axis.  Some rules of thumb about the data format
/* follow:
/*
/*  1. Complex data in the X-Axis is stored as separated 1D vectors
/*     of real and imaginary points (see below).
/*
/*  2. Complex data in the Y-Axis, Z-Axis, and A-Axis is stored as
/*     interleaved real and imaginary points.
/*
/*  3. The X-Axis size is recorded as complex points.
/*
/*  4. The Z-Axis and A-Axis sizes are recorded as total points real+imag.
/*
/*  5. If both the X-Axis and Y-Axis are complex, the Y-Axis size
/*     is reported as total points real+imag.
/*
/*  6. If the X-Axis is not complex but the Y-Axis is complex,
/*     the Y-axis size is reported as complex points.
/*
/*  7. TPPI data, and Bruker QSEQ mode data are treated as real data.
/***/

/***/
/* 1D Real Format:
/*  (512-point FDATA)
/*  (N real points...)
/*
/* 1D Complex Format:
/*  (512-point FDATA)
/*  (N real points...)
/*  (N imag points...)
/*
/* 2D Hypercomplex Format;
/* (direct dimension = t2, indirect dimension = t1):
/*
/*  (512-point FDATA)
/*  (N t2=real points... for t1=1 Real)
/*  (N t2=imag points... for t1=1 Real)
/*  (N t2=real points... for t1=1 Imag)
/*  (N t2=imag points... for t1=1 Imag)
/*  (N t2=real points... for t1=2 Real)
/*  (N t2=imag points... for t1=2 Real)
/*  (N t2=real points... for t1=2 Imag)
/*  (N t2=imag points... for t1=2 Imag)
/*  ... etc ...
/*  (N t2=real points... for t1=M Real)
/*  (N t2=imag points... for t1=M Real)
/*  (N t2=real points... for t1=M Imag)
/*  (N t2=imag points... for t1=M Imag)
/*
/* 3D Hypercomplex format: consists of a series of 2D hypercomplex
/* planes above, which are alternating real and imaginary in the third
/* dimension.
/*
/* 4D Hypercomplex format: consists of a series of 3D hypercomplex
/* spectra above, which are alternating real and imaginary in the
/* fourth dimension.
/***/

/***/
/* Some useful constant definitions:
/***/

#define FDATASIZE          512   /* Length of header in 4-byte float values. */

##define FDIEEECONS   0xeeeeeeee  /* Indicates IEEE floating point format.    */
##define FDVAXCONS    0x11111111  /* Indicates DEC VAX floating point format. */
##define FDORDERCONS       2.345  /* Constant used to determine byte-order.   */
##define FDFMTCONS    FDIEEECONS  /* Floating point format on this computer.  */
##define ZERO_EQUIV       -666.0  /* Might be used as equivalent for zero.    */

/***/
/* General Parameter locations:
/***/

#define FDMAGIC        0 /* Should be zero in valid NMRPipe data.            */
#define FDFLTFORMAT    1 /* Constant defining floating point format.         */
#define FDFLTORDER     2 /* Constant defining byte order.                    */

#define FDSIZE        99 /* Number of points in current dim R|I.             */
#define FDREALSIZE    97 /* Number of valid time-domain pts (obsolete).      */
#define FDSPECNUM    219 /* Number of complex 1D slices in file.             */
#define FDQUADFLAG   106 /* See Data Type codes below.                       */
#define FD2DPHASE    256 /* See 2D Plane Type codes below.                   */

/***/
/* Parameters defining number of dimensions and their order in the data;
/* a newly-converted FID has dimension order (2 1 3 4). These dimension
/* codes are a hold-over from the oldest 2D NMR definitions, where the
/* directly-acquired dimension was always t2, and the indirect dimension
/* was t1.
/***/

#define FDTRANSPOSED 221 /* 1=Transposed, 0=Not Transposed.                  */
#define FDDIMCOUNT     9 /* Number of dimensions in complete data.           */
#define FDDIMORDER    24 /* Array describing dimension order.                */

#define FDDIMORDER1   24 /* Dimension stored in X-Axis.                      */
#define FDDIMORDER2   25 /* Dimension stored in Y-Axis.                      */
#define FDDIMORDER3   26 /* Dimension stored in Z-Axis.                      */
#define FDDIMORDER4   27 /* Dimension stored in A-Axis.                      */

/***/
/* The following parameters describe the data when it is
/* in a multidimensional data stream format (FDPIPEFLAG != 0):
/***/

#define FDPIPEFLAG    57 /* Dimension code of data stream.    Non-standard.  */
#define FDPIPECOUNT   75 /* Number of functions in pipeline.  Non-standard.  */
#define FDSLICECOUNT 443 /* Number of 1D slices in stream.    Non-standard.  */
#define FDFILECOUNT  442 /* Number of files in complete data.                */

/***/
/* The following definitions are used for data streams which are
/* subsets of the complete data, as for parallel processing:
/***/

#define FDFIRSTPLANE  77 /* First Z-Plane in subset.            Non-standard. */
#define FDLASTPLANE   78 /* Last Z-Plane in subset.             Non-standard. */
#define FDPARTITION   65 /* Slice count for client-server mode. Non-standard. */

#define FDPLANELOC    14 /* Location of this plane; currently unused.         */

/***/
/* The following define max and min data values, previously used
/* for contour level setting:
/***/

#define FDMAX        247 /* Max value in real part of data.                  */
#define FDMIN        248 /* Min value in real part of data.                  */
#define FDSCALEFLAG  250 /* 1 if FDMAX and FDMIN are valid.                  */
#define FDDISPMAX    251 /* Max value, used for display generation.          */
#define FDDISPMIN    252 /* Min value, used for display generation.          */

/***/
/* Locations reserved for User customization:
/***/

#define FDUSER1       70
#define FDUSER2       71
#define FDUSER3       72
#define FDUSER4       73
#define FDUSER5       74

/***/
/* Defines location of "footer" information appended to spectral
/* data; currently unused for NMRPipe format:
/***/

#define FDLASTBLOCK  359
#define FDCONTBLOCK  360
#define FDBASEBLOCK  361
#define FDPEAKBLOCK  362
#define FDBMAPBLOCK  363
#define FDHISTBLOCK  364
#define FD1DBLOCK    365

/***/
/* Defines data and time data was converted:
/***/

#define FDMONTH      294
#define FDDAY        295
#define FDYEAR       296
#define FDHOURS      283
#define FDMINS       284
#define FDSECS       285

/***/
/* Miscellaneous Parameters:
/***/

#define FDMCFLAG      135 /* Magnitude Calculation performed.               */
#define FDNOISE       153 /* Used to contain an RMS noise estimate.         */
#define FDRANK        180 /* Estimate of matrix rank; Non-standard.         */
#define FDTEMPERATURE 157 /* Temperature, degrees C.                        */
#define FD2DVIRGIN    399 /* 0=Data never accessed, header never adjusted.  */
#define FDTAU         199 /* A Tau value (for spectral series).             */

#define FDSRCNAME    286  /* char srcFile[16]  286-289 */
#define FDUSERNAME   290  /* char uName[16]    290-293 */
#define FDOPERNAME   464  /* char oName[32]    464-471 */
#define FDTITLE      297  /* char title[60]    297-311 */
#define FDCOMMENT    312  /* char comment[160] 312-351 */

/***/
/* For meanings of these dimension-specific parameters,
/* see the corresponding ND parameters below.
/***/

#define FDF2LABEL     16
#define FDF2APOD      95
#define FDF2SW       100
#define FDF2OBS      119
#define FDF2ORIG     101
#define FDF2UNITS    152
#define FDF2QUADFLAG  56 /* Non-standard. */
#define FDF2FTFLAG   220
#define FDF2AQSIGN    64 /* Non-standard. */
#define FDF2LB       111
#define FDF2CAR       66 /* Non-standard. */
#define FDF2CENTER    79 /* Non-standard. */
#define FDF2OFFPPM   480 /* Non-standard. */
#define FDF2P0       109
#define FDF2P1       110
#define FDF2APODCODE 413
#define FDF2APODQ1   415
#define FDF2APODQ2   416
#define FDF2APODQ3   417
#define FDF2C1       418
#define FDF2ZF       108
#define FDF2X1       257 /* Non-standard. */
#define FDF2XN       258 /* Non-standard. */
#define FDF2FTSIZE    96 /* Non-standard. */
#define FDF2TDSIZE   386 /* Non-standard. */

#define FDF1LABEL     18
#define FDF1APOD     428
#define FDF1SW       229
#define FDF1OBS      218
#define FDF1ORIG     249
#define FDF1UNITS    234
#define FDF1FTFLAG   222
#define FDF1AQSIGN   475 /* Non-standard. */
#define FDF1LB       243
#define FDF1QUADFLAG  55 /* Non-standard. */
#define FDF1CAR       67 /* Non-standard. */
#define FDF1CENTER    80 /* Non-standard. */
#define FDF1OFFPPM   481 /* Non-standard. */
#define FDF1P0       245
#define FDF1P1       246
#define FDF1APODCODE 414
#define FDF1APODQ1   420
#define FDF1APODQ2   421
#define FDF1APODQ3   422
#define FDF1C1       423
#define FDF1ZF       437
#define FDF1X1       259 /* Non-standard. */
#define FDF1XN       260 /* Non-standard. */
#define FDF1FTSIZE    98 /* Non-standard. */
#define FDF1TDSIZE   387 /* Non-standard. */

#define FDF3LABEL     20
#define FDF3APOD      50 /* Non-standard. */
#define FDF3OBS       10
#define FDF3SW        11
#define FDF3ORIG      12
#define FDF3FTFLAG    13
#define FDF3AQSIGN   476 /* Non-standard. */
#define FDF3SIZE      15
#define FDF3QUADFLAG  51 /* Non-standard. */
#define FDF3UNITS     58 /* Non-standard. */
#define FDF3P0        60 /* Non-standard. */
#define FDF3P1        61 /* Non-standard. */
#define FDF3CAR       68 /* Non-standard. */
#define FDF3CENTER    81 /* Non-standard. */
#define FDF3OFFPPM   482 /* Non-standard. */
#define FDF3APODCODE 400 /* Non-standard. */
#define FDF3APODQ1   401 /* Non-standard. */
#define FDF3APODQ2   402 /* Non-standard. */
#define FDF3APODQ3   403 /* Non-standard. */
#define FDF3C1       404 /* Non-standard. */
#define FDF3ZF       438 /* Non-standard. */
#define FDF3X1       261 /* Non-standard. */
#define FDF3XN       262 /* Non-standard. */
#define FDF3FTSIZE   200 /* Non-standard. */
#define FDF3TDSIZE   388 /* Non-standard. */

#define FDF4LABEL     22
#define FDF4APOD      53 /* Non-standard. */
#define FDF4OBS       28
#define FDF4SW        29
#define FDF4ORIG      30
#define FDF4FTFLAG    31
#define FDF4AQSIGN   477 /* Non-standard. */
#define FDF4SIZE      32
#define FDF4QUADFLAG  54 /* Non-standard. */
#define FDF4UNITS     59 /* Non-standard. */
#define FDF4P0        62 /* Non-standard. */
#define FDF4P1        63 /* Non-standard. */
#define FDF4CAR       69 /* Non-standard. */
#define FDF4CENTER    82 /* Non-standard. */
#define FDF4OFFPPM   483 /* Non-standard. */
#define FDF4APODCODE 405 /* Non-standard. */
#define FDF4APODQ1   406 /* Non-standard. */
#define FDF4APODQ2   407 /* Non-standard. */
#define FDF4APODQ3   408 /* Non-standard. */
#define FDF4C1       409 /* Non-standard. */
#define FDF4ZF       439 /* Non-standard. */
#define FDF4X1       263 /* Non-standard. */
#define FDF4XN       264 /* Non-standard. */
#define FDF4FTSIZE   201 /* Non-standard. */
#define FDF4TDSIZE   389 /* Non-standard. */

/***/
/* Header locations in use for packed text:
/***/

/* 286 287 288 289                                                     */
/* 290 291 292 293                                                     */
/* 464 465 466 467  468 469 470 471                                    */
/* 297 298 299 300  301 302 303 304  305 306 307 308  309 310 311      */
/* 312 313 314 315  316 317 318 319  320 321 322 323  324 325 326 327  */
/* 328 329 330 331  332 333 334 335  336 337 338 339  340 341 342 343  */
/* 344 345 346 347  348 349 350 351                                    */

#define SIZE_NDLABEL    8
#define SIZE_F2LABEL    8
#define SIZE_F1LABEL    8
#define SIZE_F3LABEL    8
#define SIZE_F4LABEL    8

#define SIZE_SRCNAME   16
#define SIZE_USERNAME  16
#define SIZE_OPERNAME  32
#define SIZE_COMMENT  160
#define SIZE_TITLE     60

/***/
/* The following are definitions for generalized ND parameters:
/***/

##define NDPARM      1000

##define BAD_DIM     -666
##define NULL_DIM       0
##define CUR_XDIM       1
##define CUR_YDIM       2
##define CUR_ZDIM       3
##define CUR_ADIM       4

##define ABS_XDIM      -1
##define ABS_YDIM      -2
##define ABS_ZDIM      -3
##define ABS_ADIM      -4

##define CUR_HDIM       9
##define CUR_VDIM      10

##define NDSIZE        (1+NDPARM)  /* Number of points in dimension.          */
##define NDAPOD        (2+NDPARM)  /* Current valid time-domain size.         */
##define NDSW          (3+NDPARM)  /* Sweep Width Hz.                         */
##define NDORIG        (4+NDPARM)  /* Axis Origin (Last Point), Hz.           */
##define NDOBS         (5+NDPARM)  /* Obs Freq MHz.                           */
##define NDFTFLAG      (6+NDPARM)  /* 1=Freq Domain 0=Time Domain.            */
##define NDQUADFLAG    (7+NDPARM)  /* Data Type Code (See Below).             */
##define NDUNITS       (8+NDPARM)  /* Axis Units Code (See Below).            */
##define NDLABEL       (9+NDPARM)  /* 8-char Axis Label.                      */
##define NDLABEL1      (9+NDPARM)  /* Subset of 8-char Axis Label.            */
##define NDLABEL2     (10+NDPARM)  /* Subset of 8-char Axis Label.            */
##define NDP0         (11+NDPARM)  /* Zero Order Phase, Degrees.              */
##define NDP1         (12+NDPARM)  /* First Order Phase, Degrees.             */
##define NDCAR        (13+NDPARM)  /* Carrier Position, PPM.                  */
##define NDCENTER     (14+NDPARM)  /* Point Location of Zero Freq.            */
##define NDAQSIGN     (15+NDPARM)  /* Sign adjustment needed for FT.          */
##define NDAPODCODE   (16+NDPARM)  /* Window function used.                   */
##define NDAPODQ1     (17+NDPARM)  /* Window parameter 1.                     */
##define NDAPODQ2     (18+NDPARM)  /* Window parameter 2.                     */
##define NDAPODQ3     (19+NDPARM)  /* Window parameter 3.                     */
##define NDC1         (20+NDPARM)  /* Add 1.0 to get First Point Scale.       */
##define NDZF         (21+NDPARM)  /* Negative of Zero Fill Size.             */
##define NDX1         (22+NDPARM)  /* Extract region origin, if any, pts.     */
##define NDXN         (23+NDPARM)  /* Extract region endpoint, if any, pts.   */
##define NDOFFPPM     (24+NDPARM)  /* Additional PPM offset (for alignment).  */
##define NDFTSIZE     (25+NDPARM)  /* Size of data when FT performed.         */
##define NDTDSIZE     (26+NDPARM)  /* Original valid time-domain size.        */
##define MAX_NDPARM   (27)

/***/
/* Axis Units, for NDUNITS:
/***/

#define FD_SEC       1
#define FD_HZ        2
#define FD_PPM       3
#define FD_PTS       4

/***/
/* 2D Plane Type, for FD2DPHASE:
/***/

#define FD_MAGNITUDE 0
#define FD_TPPI      1
#define FD_STATES    2
#define FD_IMAGE     3

/***/
/* Data Type (FDQUADFLAG and NDQUADFLAG)
/***/

#define FD_QUAD       0
#define FD_COMPLEX    0
#define FD_SINGLATURE 1
#define FD_REAL       1
#define FD_PSEUDOQUAD 2

/***/
/* Sign adjustment needed for FT (NDAQSIGN):
/***/

#define ALT_NONE            0 /* No sign alternation required.                */
#define ALT_SEQUENTIAL      1 /* Sequential data needing sign alternation.    */
#define ALT_STATES          2 /* Complex data needing sign alternation.       */
#define ALT_NONE_NEG       16 /* As above, with negation of imaginaries.      */
#define ALT_SEQUENTIAL_NEG 17 /* As above, with negation of imaginaries.      */
#define ALT_STATES_NEG     18 /* As above, with negation of imaginaries.      */

#define FOLD_INVERT        -1 /* Folding requires sign inversion.             */
#define FOLD_BAD            0 /* Folding can't be performed (extracted data). */
#define FOLD_ORDINARY       1 /* Ordinary folding, no sign inversion.         */
"""


# Parse and create NIH header definitions
NIHheaderDefs = NTdict()
for l in AwkLikeS( NIHheaderDefinitionString, minNF = 3 ):
    if l.dollar[1] == '#define':
        #print '>>', l.dollar[0]
        if l.NF > 5:
            comment = ' '.join(l.dollar[5:l.NF])
        else: comment = None
        NIHheaderDefs[l.dollar[2]] = int(l.dollar[3])   # store value
#        NIHheaderDefs['_'+l.dollar[2]] = (l.dollar[2],int(l.dollar[3]), comment) #store definition as _NAME
    #end if
#end for
NIHheaderDefs.keysformat() #define a format string for 'pretty' output

class NMRPipeFile( NTfile ):
    """
    Class to Read (Write?) NMRPipe file
    Reads header on opening
    """

    def __init__( self, path, dimcount=2):
        NTfile.__init__( self, path )
        self.header = parseNMRPipeHeader( self.readHeader() )
    #end def

    def readHeader( self ):
        self.rewind()
        return self.binaryRead( typecode='f', size=NIHheaderDefs.FDATASIZE )
    #end def
#end class

def parseNMRPipeHeader( data ):
    """parse an NMRPipe header
       Return an NTdict structure or None on error
    """

    # convert the data also to char format
    charData = array.array('b')
    charData.fromstring( array.array('f',data).tostring())

    # Parse and interpret the header data
    header = NTdict()

    #dimensions and dimension order; bloody pipe format
    for name in ['DIMCOUNT','SIZE','SPECNUM','TRANSPOSED']:
        n = NIHheaderDefs['FD'+name]
        header[name.lower()] = int( data[n] )
    #end for

    n1 = NIHheaderDefs.FDDIMORDER
    n2 = n1+header.dimcount
    header.dimorder = map(int, data[n1:n2])

    # dimension parameters
    for d in range(1,5):

        dim = NTdict()
        header['axis_'+str(d)] = dim
        dim.axisIndex = d

        root = 'FDF'+str(d)

        # Char's
        #define FDF4LABEL     22
        #define SIZE_F4LABEL    8
        n1 = NIHheaderDefs[root+'LABEL']*4  # 4 Bytes per float
        n2 = n1 + NIHheaderDefs['SIZE_F'+str(d)+'LABEL'] # given in Bytes
        dim.label = charData[n1:n2].tostring()

        # Int's
        #define FDF4APOD      53 /* Non-standard. */
        #define FDF4FTFLAG    31
        #define FDF4AQSIGN   477 /* Non-standard. */
        #define FDF4SIZE      32
        #define FDF4CENTER    82 /* Non-standard. */
        #define FDF4QUADFLAG  54 /* Non-standard. */
        #define FDF4UNITS     59 /* Non-standard. */
        #define FDF4APODCODE 405 /* Non-standard. */
        #define FDF4ZF       439 /* Non-standard. */
        #define FDF4X1       263 /* Non-standard. */
        #define FDF4XN       264 /* Non-standard. */
        #define FDF4FTSIZE   201 /* Non-standard. */
        #define FDF4TDSIZE   389 /* Non-standard. */
        for name in ['APOD','FTFLAG','AQSIGN','CENTER','QUADFLAG','UNITS',
                     'APODCODE','ZF','X1','XN','FTSIZE','TDSIZE'
                    ]:
            n = NIHheaderDefs[root+name]
            dim[name.lower()] = int( data[n] )
        #end for

        # float's
        #define FDF4OBS       28
        #define FDF4SW        29
        #define FDF4ORIG      30
        #define FDF4P0        62 /* Non-standard. */
        #define FDF4P1        63 /* Non-standard. */
        #define FDF4CAR       69 /* Non-standard. */
        #define FDF4OFFPPM   483 /* Non-standard. */
        #define FDF4APODQ1   406 /* Non-standard. */
        #define FDF4APODQ2   407 /* Non-standard. */
        #define FDF4APODQ3   408 /* Non-standard. */
        #define FDF4C1       409 /* Non-standard. */
        for name in ['OBS','SW','ORIG','P0','P1','CAR','OFFPPM',
                     'APODQ1','APODQ2','APODQ3','C1'
                    ]:
            n = NIHheaderDefs[root+name]
            dim[name.lower()] = data[n]
        #end for

    #end for

    # Do the mapping of axis_1 _2 _3 _4 on X, Y, Z, A using dimorder
    for xyza,axis in zip( ['X','Y','Z','A'], header.dimorder ):
        header[xyza] = header['axis_'+str(axis)]
    #end for

    # Now get sizes right; just write out all posibilities
    # BLOODY !@#$ Pipe (see definitions above)
    if (header.X.quadflag == 0):
        header.X.size      = header.size
        header.X.totalsize = header.size*2
        header.X.dataType  = 'sComplex'   # size Real, size Imag points
    else:
        header.X.size      = header.size
        header.X.totalsize = header.size
        header.X.dataType  = 'Real'
    #end if

    if (header.Y.quadflag == 0):
        if (header.X.quadflag == 0):
            header.Y.size      = header.specnum/2
            header.Y.totalsize = header.specnum
            header.Y.dataType  = 'Complex'   # Interleaved Real,Imag
        else:
            header.Y.size      = header.specnum
            header.Y.totalsize = header.specnum*2
            header.Y.dataType  = 'Complex'   # Interleaved Real,Imag
        #end if
    else:
        header.Y.size      = header.specnum
        header.Y.totalsize = header.specnum
        header.Y.dataType  = 'Real'
    #end if

    for i in ['3','4']:
        dim = header['axis_'+i]
        dim.totalsize = int( data[NIHheaderDefs['FDF'+i+'SIZE']] )
        if (dim.quadflag == 0):
            dim.size = dim.totalsize/2
            dim.dataType = 'Complex'    # Interleaved Real,Imag
        else:
            dim.size = dim.totalsize
            dim.dataType = 'Real'
        #endif
    #end for


    # Processing
    #define FDPIPEFLAG    57 /* Dimension code of data stream.    Non-standard.  */
    #define FDPIPECOUNT   75 /* Number of functions in pipeline.  Non-standard.  */
    #define FDSLICECOUNT 443 /* Number of 1D slices in stream.    Non-standard.  */
    #define FDFILECOUNT  442 /* Number of files in complete data.                */
    for name in ['PIPEFLAG','PIPECOUNT','SLICECOUNT','FILECOUNT']:
        n = NIHheaderDefs['FD'+name]
        header[name.lower()] = int( data[n] )
    #end for

    # others
    for name in ['MONTH','DAY','YEAR','HOURS','MINS','SECS',
                 'SCALEFLAG','MCFLAG'
                ]:
        n = NIHheaderDefs['FD'+name]
        header[name.lower()] = int( data[n] )
    #end for
    # others

    for name in ['NOISE','TEMPERATURE','TAU',
                 'USER1','USER2','USER3','USER4','USER5',
                 'MAX','MIN','DISPMAX', 'DISPMIN'
                ]:
        n = NIHheaderDefs['FD'+name]
        header[name.lower()] = data[n]
    #end for

    for name,i in [('SRCNAME',16),('USERNAME',16),('OPERNAME',32),
                   ('TITLE',60),('COMMENT',160)
                  ]:
        n = NIHheaderDefs['FD'+name]*4
        header[name.lower()] = charData[n:n+i].tostring()
    #end for


    # set the output formats
    for xyza in ['X','Y','Z','A'][0:header.dimcount]:
        header[xyza].keysformat()
    #end for
    header.keysformat()
    return header
#end def


# Python Tablefile implementation
# Formerly in Talos/NmrPipeTable.py
class NmrPipeTabRow( NTdict ):
    """
    Class defining a row in a nmrTable file
    """

    def __init__( self, table, id, **kwds ):
        NTdict.__init__( self, __CLASS__  = 'NmrPipeTabRow',
                                 table      = table,
                                 id         = id,
                                 name       = 'row'+str(id),
                                 __FORMAT__ = '%(name)s',
                                 **kwds
                          )
        # set defaults to None
        for c in self.keys():
            self.setdefault( c, None )
        #end for
    #end def

    def keys( self ):
        """overide keys method to define collums as 'active' items"""
        keys = []
        for c in self.table.columnDefs:
            keys.append( c.name )
        return keys
    #end def

    def __iter__( self ):
        for v in self.values():
            yield v
        #end for
    #end def

    def __str__( self ):
        r = ''
        for col in self.table.columnDefs:
            if not col.hide:
                if self[col.name] == None:
                    dot=col.fmt.find('.')
                    if dot < 0:
                        fmt = col.fmt[:-1] + 's'
                    else:
                        fmt = col.fmt[0:dot] + 's'
                    #endif

                    r = r + fmt % (self.table.noneIndicator) + ' '
                else:
                    r = r + sprintf(col.fmt, self[ col.name ] ) + ' '
                #end if
            #end if
        #end for
        return r
    #end def
#end class

class NmrPipeTable( NTdict ):
    """
    NmrPipeTable class
    implemented as NTdict of NTdict's, i.e.

    element (row-0, INDEX) indexed as
        tab[0].INDEX   or tab[0]['INDEX']

    tab = NmrPipeTable()                # Empty table
    tab = NmrPipeTable( 'tabFile' )     # table from tabFile

    METHODS:

    addColumn( name, fmt = "%s", default=None ):
        Add column 'name' to table; set values to 'default'

    hideColumn( *cNames )
        Hide column(s) cNames

    showColumn( *cNames )
        Show columns cNames

    addRow( **kwds ):
        Add row to table, optional kwds can be used to set values

    readFile( tabFile  ):
        Read table from tabFile

    write( stream=sys.stdout ):
        Write table to stream

    writeFile( tabFile)   :
        Open tabFile, write table and close tabFile

    """

    def __init__( self, tabFile=None, **kwds ):
        NTdict.__init__( self, __CLASS__ = 'nmrPipeTab', **kwds )

        self.setdefault('noneIndicator', '-') # character to identify the None value

        self.columnDefs = NTlist()          # list of column definitions, implemented
                                            # as NTdict
        self.rows       = NTlist()
        self.nrows      = 0
        self.remarks    = NTlist()
        self.data       = NTdict()
        self.tabFile    = tabFile

        if tabFile:
            self.readFile( tabFile  )
        #end if
    #end def

    def format(self): # pylint: disable=W0221
        return sprintf(
'''=== NmrPipeTable "%s" ===
columns:  %s
nrows:    %d''', self.tabFile, self.columnDefs.zap('name'), self.nrows
        )


    def addRow( self, **kwds ):
        """
        Add row to table, optional kwds can be used to set values
        """
        row = NmrPipeTabRow( table=self, id=self.nrows, **kwds )
        self[ self.nrows ] = row
        self.rows.append( row )
        self.nrows += 1
        return row
    #end def

    def addColumn( self, name, fmt = "%s", default=None ):
        """
        Add column 'name' to table; set values to 'default'
        return columnDef, or None on error
        """
        if name in self:
            nTerror('NmrPipeTable.addColumn: column "%s" already exists\n', name )
            return None
        #end if

        col = NTdict( name=name,
                        fmt=fmt,
                        id=len(self.columnDefs),
                        hide=False,
                        __FORMAT__ = '%(name)s'
                      )
        self.columnDefs.append( col )
        self[name] = col
        for row in self:
            row[name] = default
        #end for

        return col
    #end def

    def column( self, cName ):
        """Return list of values of column cName or None on error
        """
        if cName not in self:
            return None

        col = NTlist()
        for row in self:
            col.append( row[cName] )
        #end for
        return col
    #end def

    def hideColumn( self, *cNames ):
        """
        Hide column(s) cNames
        """
        for c in cNames:
            if not c in self:
                nTerror('NmrPipeTable.hideColumn: column "%s" not defined\n', c)
            else:
                self[c].hide = True
            #end if
        #end for
    #end def

    def showColumn( self, *cNames ):
        """
        Show column(s) cNames
        """
        for c in cNames:
            if not c in self:
                nTerror('NmrPipeTable.showColumn: column "%s" not defined\n', c)
            else:
                self[c].hide = False
            #end if
        #end for
    #end def

    def readFile( self, tabFile  ):
        """
        Read table from tabFile
        """
#        nTmessage('Reading nmrPipe table file %s', tabFile )

        #end if

        for line in AwkLike( tabFile, minNF = 1, commentString = '#' ):
            if ( line.dollar[1] == 'REMARK' and line.NF > 1 ):
                self.remarks.append( line.dollar[2:] )

            elif ( line.dollar[1] == 'VARS' ):
                for v in line.dollar[2:]:
                    self.addColumn( name=v )
                #end for
            elif ( line.dollar[1] == 'FORMAT' ):
                i = 0
                for f in line.dollar[2:]:
                    self.columnDefs[i].fmt=f
                    i += 1
                #end for
            elif ( line.dollar[1] == 'DATA' and line.NF > 3 ):
                self.data[line.dollar[2]] = line.dollar[3:]

            elif ( line.NF == len( self.columnDefs ) ):
                row = self.addRow()
                for i in range( 0, line.NF ):
                    col = self.columnDefs[i]

                    if (line.dollar[i+1] == self.noneIndicator):
                        row[col.name] = None
                    else:
                        # derive conversion function from fmt field
                        if (col.fmt[-1:] in ['f','e','E','g','G']):
                            func = float
                        elif (col.fmt[-1:] in ['d','o','x','X']):
                            func = int
                        else:
                            func = str
                        #end if
                        row[ col.name ] = func( line.dollar[i+1] )
                    #endif
                #end for
            else:
                pass
            #end if
        #end for
        self.tabFile = tabFile
    #end def

    def write( self, stream=sys.stdout):
        """
        Write tab to stream
        """
        for r in self.remarks:
            fprintf( stream, 'REMARK %s\n', r )
        #end for
        fprintf( stream, '\n' )

        for d,v in self.data.iteritems():
            fprintf( stream, 'DATA %s %s\n', d, v ) # Note: only ONE space between DATA and identifier!!!
        #end for
        fprintf( stream, '\n' )

        fprintf(     stream, 'VARS    ' )
        for c in self.columnDefs:
            if not c.hide:
                fprintf( stream, '%s ', c.name )
        #end for
        fprintf( stream, '\n' )

        fprintf(     stream, 'FORMAT  ' )
        for c in self.columnDefs:
            if not c.hide:
                fprintf( stream, '%s ', c.fmt )
        #end for
        fprintf( stream, '\n' )

        fprintf( stream, '\n' )
        for row in self:
            fprintf( stream, '%s\n', row )
        #end for

    #end def

    def writeFile( self, tabFile)   :
        """
        Write table to tabFile.
        Return True on error
        """
        fp = open( tabFile, 'w' )
        if fp is None:
            nTerror('NmrPipeTable.writeFile: error opening "%s"', tabFile)
            return True
        self.write( fp )
        fp.close()
#        nTdebug('==> Written nmrPipe table file "%s"', tabFile )
        return False
    #end def

    #iteration overrides: loop over row indices or rows
    def keys( self ):
        return range( 0, self.nrows )
    #end def

    def __iter__( self ):
        for row in self.rows:
            yield row
        #end for
    #end def
#end def


#-----------------------------------------------------------------------------
# NIH routines
#-----------------------------------------------------------------------------
def exportShifts2TalosPlus( project, fileName=None):
    """Export shifts to TalosPlus format

    Return True on error including situation where no shifts were added to the file.

---------------------------------------------------

An example of the required shift table format is shown below. Complete examples can be found in the talos/shifts and talos/test directories. Specifically:

In the current version of TALOS/TALOS+, residue numbering must begin at 1.
The protein sequence should be given as shown, using one or more "DATA SEQUENCE" lines. Space characters in the sequence will be ignored. Use "c" for oxidized CYS (CB ~ 42.5 ppm) and "C" for reduced CYS (CB ~ 28 ppm) in both the sequence header and the shift table.
The table must include columns for residue ID, one-character residue name, atom name, and chemical shift.
The table must include a "VARS" line which labels the corresponding columns of the table.
The table must include a "FORMAT" line which defines the data type of the corresponding columns of the table.
Atom names are always given exactly as:
    HA       for H-alpha of all residues except glycine
    HA2      for the first H-alpha of glycine residues
    HA3      for the second H-alpha
    C        for C' (CO)
    CA       for C-alpha
    CB       for C-beta
    N        for N-amide
    HN       for H-amide
As noted, there is an exception for naming glycine assignments, which should use HA2 and HA3 instead of HA. In the case of glycine HA2/HA3 assignments, TALOS/TALOS+ will use the average value of the two, so that it is not necessary to have these assigned stereo specifically ; for use of TALOS/TALOS+, the assignment can be arbitrary. Note however that the assignment must be given exactly as either "HA2" or "HA3" rather than "HA2|HA3" etc.
Other types of assignments may be present in the shift table; they will be ignored.

Example shift table (excerpts):

   REMARK Ubiquitin input for TALOS, HA2/HA3 assignments arbitrary.

   DATA SEQUENCE MQIFVKTLTG KTITLEVEPS DTIENVKAKI QDKEGIPPDQ QRLIFAGKQL
   DATA SEQUENCE EDGRTLSDYN IQKESTLHLV LRLRGG

   VARS   RESID RESNAME ATOMNAME SHIFT
   FORMAT %4d   %1s     %4s      %8.3f

     1 M           HA                  4.23
     1 M           C                 170.54
     1 M           CA                 54.45
     1 M           CB                 33.27
     2 Q           N                 123.22
     2 Q           HA                  5.25
     2 Q           C                 175.92
     2 Q           CA                 55.08
     2 Q           CB                 30.76
---------------------------------------------------

From talos+ randcoil.tab file:

REMARK Talos Random Coil Table 2005.032.16.15
REMARK Cornilescu, Delaglio and Bax
REMARK CA/CB from Spera, Bax, JACS 91.
REMARK Others from Wishart et al. J. Biomol. NMR, 5(1995), 67-81
REMARK Pro N shift is the current database average (7 residues).
REMARK HIS = Wishart's val - 0.5*(diff between prot./non-prot. Howarth&Lilley)

DATA RESNAMES  A C c D E F G H I K L M N P Q R S T V W Y
DATA ATOMNAMES HA CA CB C N HN

#
# Values for C are CYS-reduced.
# Values for c are CYS-oxidized.
# Values for H are HIS-unprotonated.
# Values for h are for HIS-protonated.
# Values for D and E are for protonated forms.
---------------------------------------------------

    """

    if not project:
        return True
    #end if

    if not project.molecule:
        nTerror('exportShifts2TalosPlus: no molecule defined')
        return True
    molecule = project.molecule
    residues = molecule.residuesWithProperties('protein')
    if not residues:
        nTerror('exportShifts2TalosPlus: no amino acid defined')
        return True

    table = NmrPipeTable()
    table.remarks.append( sprintf('shifts from %s', molecule.name ) )
    residueOffset = residues[0].resNum-1 # residue numbering has to start from 1
    table.remarks.append( sprintf('residue numbering offset  %d', residueOffset ) )

#   generate a one-letter sequence string; map 'all chains to one sequence'
    seqString = ''
    for res in residues:
#        seqString = seqString + res.db.shortName JFD mod; wrong, look at format def above!
        if res.translate(INTERNAL_0) == 'CYSS':
            seqString = seqString + 'c' # oxidized
        else:
            seqString = seqString + res.db.shortName
    #end for

#   data
    table.data.SEQUENCE = seqString

#   add collun entries
    table.addColumn('RESID',    '%-4d')
    table.addColumn('RESNAME',  '%-4s')
    table.addColumn('ATOMNAME', '%-4s')
    table.addColumn('SHIFT',    '%8.3f')

    # defines IUPAC to talos mapping and nuclei used
    talosDict = dict(
                 N  = 'N',
                 H  = 'HN',
                 CA = 'CA',
                 HA = 'HA',
                 HA2= 'HA2',
                 HA3= 'HA3',
                 QA = 'HA2,HA3', # QA will be translsate into real atoms
                 CB = 'CB',
                 C  = 'C'
                 )
    talosNuclei = talosDict.keys()

    atmCount = 0
    for resId,res in enumerate(residues):
        for ac in res.allAtoms():
            atomName = ac.translate(IUPAC)
            if (ac.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY) and ( atomName in talosNuclei)):
                shift = ac.shift(resonanceListIdx=RESONANCE_LIST_IDX_ANY) # save the shift, because Gly QA pseudo atom does get expanded
                for ra in ac.realAtoms():
                    atomName = ra.translate(IUPAC)
                    # Translate to TalosPlus
                    if talosDict.has_key(atomName):
                        atomName = talosDict[atomName]
                    else:
                        nTerror('exportShifts2TalosPlus: strange, we should not be here (ra=%s)', ra)
                        continue
                    #end if

                    #print '>', seqString[resId:resId+1]
                    table.addRow( RESID=resId+1, RESNAME=seqString[resId:resId+1], ATOMNAME=atomName, SHIFT=shift)
                    atmCount += 1
                #end for
            #end if
        #end for
    #end for

    # save the table
    if not fileName:
        fileName = molecule.name + '.tab'
    if not table.writeFile(fileName):
        nTmessage( '==> exportShifts2TalosPlus:  %-4d shifts   written to "%s"', atmCount, fileName )
    if atmCount == 0:
        return True
#end def

def _importTableFile( tabFile, molecule ):
    """import a tabFile, match to residue instances of molecule

    Return the NmrPipeTable instance or None on error
    """

    if not os.path.exists( tabFile ):
        nTerror('_importTableFile: table file "%s" not found', tabFile)
        return None

    if molecule==None:
        nTerror('_importTableFile: no molecule defined')
        return None

    # residues for which we will analyze; same as used in export2talosPlus
    residues = molecule.residuesWithProperties('protein')
    if not residues:
        nTerror('_importTableFile: no amino acid defined')
        return None

    table = NmrPipeTable()
    table.readFile(tabFile)

    for row in table:
        # find the residue
        row.residue = None

        if row.RESID > len(residues):
            nTerror('_importTableFile: invalid RESID %d',  row.RESID)
            continue

        # map back onto CING
        res = residues[row.RESID-1] # RESID started at 1
        if res.db.shortName != row.RESNAME.upper(): # also allow for the 'c'
            nTerror('_importTableFile: invalid RESNAME %s and CING %s',  row.RESNAME, res)
            continue

        row.residue = res
        #print res, row
    #end for
    return table
#end def


class TalosPlusResult( validation.ValidationResult ):
    """Class to store Talos+ results
Reference: Shen et al., 2009, J. Biomol. NMR 44, 213-223
Reference: Predicted order parameter (S2) from backbone chemical shifts for talosPlus.tab
           from David Wishart's RCI method, JACS, 127(43), 14970-14971
    """
    KEY            = constants.TALOSPLUS_KEY
    PHI            = 'phi'
    PSI            = 'psi'
    COUNT          = 'count'
    CLASSIFICATION = 'classification'
    S2             = 'S2'
    SS_CLASS       = 'ss_class'
    SS_CONFIDENCE  = 'ss_confidence'
    Q_H            = 'Q_H'
    Q_E            = 'Q_E'
    Q_L            = 'Q_L'

    def __init__(self, *args, **kwds):

        validation.ValidationResult.__init__( self, *args, **kwds)
        self.setdefault(TalosPlusResult.PHI, None)
        self.setdefault(TalosPlusResult.PSI, None)
        self.setdefault(TalosPlusResult.COUNT, 0)
        self.setdefault(TalosPlusResult.CLASSIFICATION, None)
        self.setdefault(TalosPlusResult.S2, NaN)
        self.setdefault(TalosPlusResult.SS_CLASS, None)
        self.setdefault(TalosPlusResult.SS_CONFIDENCE, None)
        self.setdefault(TalosPlusResult.Q_E, NaN)
        self.setdefault(TalosPlusResult.Q_H, NaN)
        self.setdefault(TalosPlusResult.Q_L, NaN)
        self.setdefault(TalosPlusResult.OBJECT_KEY, None)
        self.setdefault('residue', None) #LEGACY:
    #end def

    def format(self, fmt=None):
        if fmt is None:
            fmt = '%(residue)-18s  phi= %(phi)-15s  psi= %(psi)-15s  (%(count)2s predictions, classified as ' +\
                  '"%(classification)-4s")  S2= %(S2)4.2f   Sec.Struct.: %(ss_class)-8s ' +\
                  '(confidence: %(ss_confidence)4.2f)'
            return fmt % self
        else:
            return fmt.format(**self)
    #end if
#end class


class TalosPlusResultJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the TalosPlusResult class
    """
    namespace = cing.constants.TALOSPLUS_KEY
    cls = TalosPlusResult
    encodedKeys = [cing.constants.OBJECT_KEY,'residue']

    def restore(self, data):
        a = TalosPlusResult()
        self._restore(data, a)
        #print('TalosPlusJsonHandler.restore>', a.format(), self.context.referenceObject)
        return a
#end class
TalosPlusResultJsonHandler.handles(TalosPlusResult)


def _importTalosPlus( project, predFile, ssFile=None ):
    """
    Helper code: Import TalosPlus results from pred.tab and pred.ss.tab
    """

    if not project:
        return True
    #end if

    nTdebug('_importTalosPlus: files %s and %s', predFile, ssFile)

    if not project.molecule:
        nTerror('importTalosPlus: no molecule defined')
        return True
    molecule = project.molecule

    table = _importTableFile( predFile, molecule )

    for row in table:

        #print '>', row, row.residue
        talosPlus = TalosPlusResult()
        talosPlus.residue = row.residue
        talosPlus.phi = NTvalue( row.PHI, row.DPHI, '%6.1f +- %4.1f')
        talosPlus.psi = NTvalue( row.PSI, row.DPSI, '%6.1f +- %4.1f')
        talosPlus.S2  = row.S2
        talosPlus.count = row.COUNT
        talosPlus.classification = row.CLASS

        if talosPlus.classification == 'None' or \
           talosPlus.phi.value == 9999.00 or \
           talosPlus.psi.value == 9999.00:
            talosPlus.phi.value = NaN
            talosPlus.phi.error = NaN
            talosPlus.psi.value = NaN
            talosPlus.psi.error = NaN
            talosPlus.S2 = NaN # pylint: disable=C0103
        #end if

        validation.setValidationResult(row.residue, constants.TALOSPLUS_KEY, talosPlus)
        #LEGACY:
        row.residue.talosPlus = talosPlus
    #end for

    # do the second ss file
    ssdict = dict( H = 'Helix', E='Extended', L='Coil' ) # X is translated to None
    if ssFile:
        table = _importTableFile( ssFile, molecule )
        #print '>>', table
        for row in table:
            #print '>>', row

            if ('residue' in row):
                tPlus = validation.getValidationResult(row.residue, constants.TALOSPLUS_KEY)
                if tPlus is not None:
                    tPlus.Q_H = row.Q_H    # Helix
                    tPlus.Q_E = row.Q_E    # Extended
                    tPlus.Q_L = row.Q_L    # Loop
                    if row.SS_CLASS in ssdict:
                        tPlus.ss_class = ssdict[row.SS_CLASS]
                    else:
                        tPlus.ss_class = None
                    tPlus.ss_confidence = row.CONFIDENCE
                else:
                    nTerror('_importTalosPlus: %s: row: %s', ssFile, row)
                #end if
            #end if
        #end for
    #end if
#end def

def _resetTalosPlus(talosDefs, molecule):
    """Reset the talosPlus references in the data
    """
    for res in molecule.allResidues():
        #LEGACY:
        res.talosPlus = None
        validation.setValidationResult(res, constants.TALOSPLUS_KEY, None)
    #end for
    talosDefs.present = False
#end def


talosDefaults= dict(
    directory    = constants.TALOSPLUS_KEY,
    tableFile    = 'talosPlus.tab', # file generated by CING
    predFile     = 'pred.tab',      # file with predictions returned by Talos(+)
    predSSFile   = 'predSS.tab',    # file with sec struct returned by Talos(+): pred.ss.tab also encountered
    molecule     = None,
    completed    = False,
    parsed       = False
)


def _findTalosOutputFiles( path, talosDefs ):
    """ Check for existence of the output files; return True on error
    """
    # pred.tab file; curently only one name encountered
    talosDefs.predFile = None
    for tFile in 'pred.tab'.split():
        pFile = path / tFile
        if pFile.exists():
            #print '>found>', pFile
            talosDefs.predFile = tFile # only store local part of name
            break
    #end for
    if talosDefs.predFile == None:
        nTerror("_findTalosOutputFiles: Failed to find pred.tab file")
        return True
    #end if
    # Multiple predSS names found
    talosDefs.predSSFile = None
    for tFile in 'predSS.tab pred.ss.tab'.split():
        pFile = path / tFile
        if pFile.exists():
            #print '>found>', pFile
            talosDefs.predSSFile = tFile # only store local part of name
            break
    #end for
    if talosDefs.predSSFile == None:
        nTerror("_findTalosOutputFiles: Failed to find predSS.tab or pred.ss.tab file")
        return True
    #end if
    return False
#end def


def runTalosPlus(project, tmp=None, parseOnly=False):
    """Perform a talos+ analysis; parses the results; put into new CING dihedral restraint list; and
    saves the results.

    Returns True on error.
    Returns False when talos is absent or when all is fine.
    """
    #LEGACY:
    if parseOnly:
        return parseTalosPlus(project)

    if project is None:
        nTerror("runTalosPlus: No project defined")
        return True

    if cingPaths.talos is None:
        nTmessage('runTalosPlus: no talosPlus executable, skipping')
        return False # Gracefully return

    if project.molecule is None:
        nTmessage("runTalosPlus: No molecule defined")
        return True

    residues = project.molecule.residuesWithProperties('protein')
    if not residues:
        nTmessage('runTalosPlus: no amino acid defined')
        return False

    if len( project.molecule.resonanceSources ) == 0:
        nTmessage("==> runTalosPlus: No resonances defined so no sense in running.")
        # JFD: This doesn't catch all cases.
        return False

    talosDefs = project.getStatusDict(constants.TALOSPLUS_KEY, **talosDefaults)

    talosDefs.molecule = project.molecule.asPid()
    talosDefs.directory = constants.TALOSPLUS_KEY

    path = project.validationPath( talosDefs.directory )
    if not path:
        return True
    if path.exists():
        nTdebug('runTalosPlus: removing %s with prior data', path)
        path.rmdir()
    path.makedirs()

    startTime = io.now()

    talosDefs.completed = False
    talosDefs.parsed = False
    _resetTalosPlus(talosDefs, project.molecule)
    talosDefs.saved = False

    # Exporting the shifts
    fileName = os.path.join(path, talosDefs.tableFile )
    if exportShifts2TalosPlus(  project, fileName=fileName ):
        nTwarning("runTalosPlus: Failed to exportShifts2TalosPlus; this is normal for empty CS list.")
        return False

    # running TalosPlus
    talosProgram = ExecuteProgram(cingPaths.talos, rootPath=path,
                                  redirectOutput=True
                                 )
    nTmessageNoEOL('==> Running talos+ ... ')
    talosProgram( '-in ' + talosDefs.tableFile + ' -sum ' + talosDefs.predFile )
    nTmessage('Done!')

    if _findTalosOutputFiles(path, talosDefs):
        return True

    talosDefs.date = io.now()
    talosDefs.completed=True
    talosDefs.version = __version__
    talosDefs.molecule = project.molecule.asPid()
    talosDefs.remark = 'TalosPlus on %s completed in %.1f seconds on %s; data in %s' % \
                       (project.molecule, talosDefs.date-startTime, talosDefs.date, path)

    # Importing the results
    if parseTalosPlus(project):
        nTerror("runTalosPlus: Failed parseTalosPlus")
        return True

    project.history(talosDefs.remark)
    nTmessage('==> %s', talosDefs.remark)
    return False
#end def


def parseTalosPlus( project, tmp=None ):
    """Import talosPlus results.
    Return True on error.
    """
    if project is None:
        io.warning("parseTalosPlus: No project defined\n")
        return False

    if project.molecule is None:
        io.warning("parseTalosPlus: No molecule defined\n")
        return False

    talosDefs = project.getStatusDict(constants.TALOSPLUS_KEY, **talosDefaults)

    if not talosDefs.completed:
        io.warning("parseTalosPlus: No talos+ was run\n")
        return False

    path = project.validationPath(talosDefs.directory)
    if not path:
        io.error('parseTalosPlus: directory "{0}" with talosPlus data not found\n', path)
        return True

    if _findTalosOutputFiles(path, talosDefs):
        return True

    predFile = path / talosDefs.predFile
    if not predFile.exists() or predFile.isdir():
        io.error('parseTalosPlus: file "{0}" with talosPlus predictions not found\n', predFile)
        return True

    predSSFile = path / talosDefs.predSSFile
    if not predSSFile.exists() or predSSFile.isdir():
        io.error('parseTalosPlus: file "{0}" with talosPlus SS predictions not found\n', predSSFile)
        return True

    _resetTalosPlus(talosDefs, project.molecule)
    if _importTalosPlus(project, predFile, predSSFile):
        return True

    talosDefs.parsed = True

    if talosPlus2restraints(project):
        io.error("parseTalosPlus: Failed talosPlus2restraints\n")
        return True

    return False
#end def


def saveTalosPlus(project, tmp=None):
    """
    Save talos+ results to sml file
    Returns True on error.
    Returns None on success.
    """
    if project is None:
        nTmessage("saveTalosPlus: No project defined")
        return True

    if project.molecule is None:
        nTmessage("saveTalosPlus: No molecule defined")
        return True
    # save the data
    return project._savePluginData(constants.TALOSPLUS_KEY, saved=True, saveVersion=__version__)
#end def


# pylint: disable=C0102
def restoreTalosPlus(project, tmp=None):
    """
    Restore talos+ results from sml file.
    Return True on error
    """
    if project == None:
        nTmessage("restoreTalosPlus: No project defined")
        return True

    if project.molecule == None:
        return False # Gracefully returns

    # Reset the data
    talosDefs = project.getStatusDict(constants.TALOSPLUS_KEY, **talosDefaults)
    _resetTalosPlus(talosDefs, project.molecule)
    #restore the data
    return project._restorePluginData(constants.TALOSPLUS_KEY, present=True)
#end def


def talosPlus2restraints( project, name=TALOSPLUS_LIST_STR, status='noRefine', errorFactor=2.0 ):
    """
    Convert talos+ results to a CING dihedral restraint list
    """
    if project == None:
        nTmessage("talosPlus2restraints: No project defined")
        return True

    if project.molecule == None:
        nTmessage("talosPlus2restraints: No project defined")
        return True

    if not project.status.has_key('talosPlus') or not project.status.talosPlus.completed:
        nTmessage("talosPlus2restraints: No talos+ data")
        return True

    if name in project.dihedrals.names():
        project.dihedrals.delete(name)

    dhl = project.dihedrals.new(name=name, status=status)
    for res in project.molecule.allResidues():
        if res.talosPlus and res.talosPlus.classification=='Good':
            lower = res.talosPlus.phi.value-errorFactor*res.talosPlus.phi.error
            upper = res.talosPlus.phi.value+errorFactor*res.talosPlus.phi.error
            atoms = getDeepByKeysOrAttributes( res, PHI_STR, ATOMS_STR )
            if atoms:
                d = DihedralRestraint(atoms, lower, upper)
                dhl.append(d)

            lower = res.talosPlus.psi.value-errorFactor*res.talosPlus.psi.error
            upper = res.talosPlus.psi.value+errorFactor*res.talosPlus.psi.error
            atoms = getDeepByKeysOrAttributes( res, PSI_STR, ATOMS_STR )
            if atoms:
                d = DihedralRestraint(atoms, lower, upper)
                dhl.append(d)
        #end if
    #end for
    nTmessage('==> Created %s', dhl)
#end def


def export2nih( project, tmp=None ):
    """
    Export resonances to NIH (talos) format
    """

    talosDefs = project.getStatusDict(constants.TALOSPLUS_KEY, **talosDefaults)
    for mol in project.molecules:
        fileName = project.path( project.directories.nih, mol.name+'.'+talosDefs.tableFile )
        exportShifts2TalosPlus(  project, fileName=fileName )
    #end for
#end def

#-----------------------------------------------------------------------------

# register the functions
methods  = [(runTalosPlus,None),
            (parseTalosPlus,None),
            (talosPlus2restraints,None)
           ]
saves    = []
restores = []
exports  = [(export2nih, None)]


#-----------------------------------------------------------------------------
# Testing from here-on
#-----------------------------------------------------------------------------
#
if __name__ == '__main__':
    pass


