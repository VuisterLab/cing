#-----------------------------------------------------------------------
# superpose.pyx
#-----------------------------------------------------------------------
#
#
# Initial code to superimpose structures of ensemble.
#
# GWV Feb 2008
#
# Core routines mtx_superpose and superposeModels adapted from code
# by Elmar Krieger, YASARA
#
#-----------------------------------------------------------------------
from math   import sqrt
from math   import sin
from math   import cos
from math   import tan
from math   import asin
from math   import acos
from math   import atan2
from math   import pi
from math   import fabs
from math   import pow

from sys import stderr
from sys import stdout


cdef class NTcVector:

    def __init__( NTcVector self,  double x,  double y,  double z ):
        self.iterCount = -1
        self.set( x, y, z)
    #end def

    property x:
        def __get__( NTcVector self ):
            return self.e[0]
        def __set__( NTcVector self, double value ):
            self.e[0] = value
    property y:
        def __get__( NTcVector self ):
            return self.e[1]
        def __set__( NTcVector self, double value ):
            self.e[1] = value
    property z:
        def __get__( NTcVector self ):
            return self.e[2]
        def __set__( NTcVector self, double value ):
            self.e[2] = value

    def __getitem__( NTcVector self, int i ):
        if (i<0 or i>=VECTOR_SIZE):
            raise IndexError
        return self.e[i]
    #end def

    def __setitem__( NTcVector self, int i, double value ):
        if (i<0 or i>=VECTOR_SIZE):
            raise IndexError
        self.e[i] = value
    #end def

    def set( NTcVector self, double x, double y, double z ):
        self.e[0] = x
        self.e[1] = y
        self.e[2] = z
    #end def

    def get( NTcVector self ):
        return ( self.e[0] , self.e[1] , self.e[2] )
    #end def

    def copy( NTcVector self, NTcVector toVector not None ):
        cdef int i
        for i from 0 <= i < VECTOR_SIZE:
            toVector.e[i] = self.e[i]
        #end for
    #end def

    def duplicate( NTcVector self ):
        # Return a copy of self
        cdef NTcVector dup
        dup = NTcVector( self.e[0] , self.e[1] , self.e[2] )
        return dup
    #end def

    def __iter__( NTcVector self ):
        self.iterCount = 0
        return self
    #end def

    def __next__( NTcVector self ):
        if (self.iterCount < 0 or self.iterCount == VECTOR_SIZE):
            raise StopIteration
        #end if
        self.iterCount = self.iterCount+1
        return self.e[self.iterCount-1]
    #end def

    def __len__( NTcVector self ):
        return int(VECTOR_SIZE)
    #end def

    def __str__( NTcVector self ):
        return '(%+.3f,%+.3f,%+.3f)' % self.get()
    #end def

    def __repr__(NTcVector self):
        return 'NTcVector(%f,%f,%f)' % self.get()
    #end def

    def length( NTcVector self ):
        # return length of self
        cdef double l
        cdef int i
        l = 0.0
        for i from 0 <= i < VECTOR_SIZE:
            l = l+(self.e[i]*self.e[i])
        #end for
        return sqrt(l)
    #end def

    def norm( NTcVector self ):
        # Return a normalized vector
        cdef double l
        l = 1.0/self.length()
        return NTcVector( self.e[0]*l, self.e[1]*l, self.e[2]*l )
    #end def

    def sqsum( NTcVector self ):
        # return squared sum of elements of self
        cdef double l
        cdef int i
        l = 0.0
        for i from 0 <= i < VECTOR_SIZE:
            l = l+(self.e[i]*self.e[i])
        #end for
        return l
    #end def

# arithmic; special methods cannot use the C exposed variables
# Page xxx Pyrec documentation
    def __add__( NTcVector self, NTcVector other not None ):
        cdef NTcVector result
        result = NTcVector( self[0] + other[0], self[1] + other[1], self[2] + other[2] )
        return result
    #end def

    def __iadd__( NTcVector self, NTcVector other not None ):
        self[0] = self[0] + other[0]
        self[1] = self[1] + other[1]
        self[2] = self[2] + other[2]
        return self
    #end def

    def __mul__( NTcVector self, double factor ):
        cdef NTcVector result
        result = NTcVector( self[0] * factor, self[1]  * factor, self[2] * factor )
        return result
    #end def

    def __div__( NTcVector self, double factor ):
        cdef NTcVector result
        result = NTcVector( self[0] / factor, self[1]  / factor, self[2] / factor )
        return result
    #end def


    def __sub__( NTcVector self, NTcVector other not None ):
        cdef NTcVector result
        result = NTcVector( self[0] - other[0], self[1] - other[1], self[2] - other[2] )
        return result
    #end def

    def __isub__( NTcVector self, NTcVector other not None ):
        self[0] = self[0] - other[0]
        self[1] = self[1] - other[1]
        self[2] = self[2] - other[2]
        return self
    #end def

    def __neg__( NTcVector self ):
        cdef NTcVector result
        result = NTcVector( -self[0], -self[1], -self[2] )
        return result
    #end def

    def __pos__( NTcVector self ):
        cdef NTcVector result
        result = NTcVector( self[0], self[1], self[2] )
        return result
    #end def

    def toPolar( NTcVector self, radians = False ):
        """
        return triple of polar coordinates (r,u,v)
        with:
          -pi<=u<=pi
          -pi/2<=v<=pi/2

          x = rcos(v)cos(u)
          y = rcos(v)sin(u)
          z = rsin(v)
        """
        cdef double fac
        fac = 1.0
        if not radians: fac = 180.0/pi

        r = self.length()
        u = atan2( self.e[1], self.e[0] )
        v = asin( self.e[2]/r )
        return (r, u*fac, v*fac)
    #end def

    def fromPolar( NTcVector self, polarCoordinates, radians = False ):
        """
        set vector using polarCoordinates (r,u,v)
        with:
          0<=u<=2pi
          -pi/2<=v<=pi/2

          x = rcos(v)cos(u)
          y = rcos(v)sin(u)
          z = rsin(v)
        """
        fac = 1.0
        if not radians: fac =pi/180.0

        r,u,v = polarCoordinates
        self.e[0] = r*cos(v*fac)*cos(u*fac)
        self.e[1] = r*cos(v*fac)*sin(u*fac)
        self.e[2] = r*sin(v*fac)
    #end def

    def dot( NTcVector self, NTcVector other ):
        """
        Return inner product of self and other
        """
        return (self.e[0]*other.e[0]+self.e[1]*other.e[1]+self.e[2]*other.e[2])
    #end def

    def cross( NTcVector self, NTcVector other ):
        """
        return cross vector spanned by self and other

          result = self x other

        Definitions from Kreyszig, Advanced Enginering Mathematics, 4th edition, Wiley and Sons, p273

        """

        return NTcVector( self.e[1]*other.e[2] - self.e[2]*other.e[1], # x-coordinate
                          self.e[2]*other.e[0] - self.e[0]*other.e[2], # y-coordinate
                          self.e[0]*other.e[1] - self.e[1]*other.e[0]  # z-coordinate
                        )
    #end def

    def triple( NTcVector self, NTcVector b, NTcVector c):
        """
        return triple product of self,b,c
        """
        return (  self.e[0] * (b.e[1]*c.e[2]-b.e[2]*c.e[1] )
                - self.e[1] * (b.e[0]*c.e[2]-b.e[2]*c.e[0] )
                + self.e[2] * (b.e[0]*c.e[1]-b.e[1]*c.e[0] )
               )
    #end def

    def angle( NTcVector self, NTcVector other, radians = False ):
        """
        return angle spanned by self and other
        range = [0, pi]
        """
        cdef double fac, c

        fac = 1.0
        if not radians: fac = 180.0/pi

        c = self.dot(other) /(self.length()*other.length())
        if (c > 1.0): c = 1.0
        if (c < -1.0): c = -1.0
        return acos( c ) * fac
    #end def

    def distance( NTcVector self, NTcVector other ):
        """
        return distance between self and other
        """
        return (self-other).length()
    #end def

#end cdef NTcVector

def Rm6dist( NTcVector v1, NTcVector v2 ):
    """
    Return R-6 distance of vector v1 and v2
    """
    cdef double d, tmp
    cdef int i
    d = 0.0
    for i from 0 <= i < VECTOR_SIZE:
        tmp = v1.e[i]-v2.e[i]
        d = d+tmp*tmp
    #end for
    # no need to take sqrt first and then pow
    # R = sqrt(d) = l**0.5
    # R**-6 = 1/R**6 = 1/(d**0.5)**6 = 1/d**3=d**-3
    if d>0.0:
        return pow(d, -3)
    else:
        return 0.0
#end def


def isNTcVector(x):
    """
    Determines if the argument is a NTcVector class object.
    """
    # Convert 1/0 from C's hasattr fie to Python's True/False
    if (hasattr(x,'__class__') and x.__class__ is NTcVector):
        return True
    else:
        return False
#end def



DEF BARLENGTH = 60

cdef class NTcMatrix:

    def __init__( self ):
        self.setunit()

    def __getitem__( self, indexTuple ):
        cdef int i, j, l

        try:
            l = len(indexTuple)
        except:
            stderr.write( "_"*BARLENGTH +"\n!!! Error NTcMatrix: invalid indexTuple >%s<.\n" % str(indexTuple) )
            raise IndexError
        #end try
        if (l != 2):
            stderr.write( "_"*BARLENGTH +"\n!!! Error NTcMatrix: invalid indexTuple >%s<.\n" % str(indexTuple) )
            raise IndexError
        #end if
        i = indexTuple[0]
        j = indexTuple[1]
        if (i<0 or i>=MATRIX_SIZE):
            stderr.write( "_"*BARLENGTH +"\n!!! Error NTcMatrix: index i (%d) out of bound.\n" % i )
            raise IndexError
        #end if
        if (j<0 or j>=MATRIX_SIZE):
            stderr.write( "_"*BARLENGTH +"\n!!! Error NTcMatrix: index j (%d) out of bound.\n" % j )
            raise IndexError
        #end if
        return self.mtx[i][j]
    #end def

    def __setitem__( self, indexTuple, double value ):
        cdef int i, j, l

        try:
            l = len(indexTuple)
        except:
            stderr.write( "_"*BARLENGTH +"\n!!! Error NTcMatrix: invalid indexTuple >%s<.\n" % str(indexTuple) )
            raise IndexError
        #end try
        if (l != 2):
            stderr.write( "_"*BARLENGTH +"\n!!! Error NTcMatrix: invalid indexTuple >%s<.\n" % str(indexTuple) )
            raise IndexError
        #end if
        i = indexTuple[0]
        j = indexTuple[1]
        if (i<0 or i>=MATRIX_SIZE):
            stderr.write( "_"*BARLENGTH +"\n!!! Error NTcMatrix: index i (%d) out of bound.\n" % i )
            raise IndexError
        #end if
        if (j<0 or j>=MATRIX_SIZE):
            stderr.write( "_"*BARLENGTH +"\n!!! Error NTcMatrix: index j (%d) out of bound.\n" % j )
            raise IndexError
        #end if
        self.mtx[i][j] = value
    #end def

    def setunit( self ):
        cdef int i, j
        for i from 0 <= i < MATRIX_SIZE:
            for j from 0 <= j < MATRIX_SIZE: self.mtx[i][j] = 0.0
            self.mtx[i][i] = 1.0;
        #end for
    #end cdef

    def copy( self, NTcMatrix other not None ):
        cdef int i, j
        for i from 0 <= i < MATRIX_SIZE:
            for j from 0 <= j < MATRIX_SIZE: other.mtx[i][j] = self.mtx[i][j]
        #end for
    #end cdef

    def settrans( self, double x, double y, double z ):
        # set vector part mtx
        self.mtx[0][3] = x
        self.mtx[1][3] = y
        self.mtx[2][3] = z
    #end cdef

    def addtrans( self, double x, double y, double z ):
        # add to vector part mtx
        self.mtx[0][3] = self.mtx[0][3] + x
        self.mtx[1][3] = self.mtx[1][3] + y
        self.mtx[2][3] = self.mtx[2][3] + z
    #end cdef

    def __str__( self ):
        cdef int i,j
        result = ""
        for i from 0 <= i < MATRIX_SIZE:
            for j from 0 <= j < MATRIX_SIZE:  result = result + '%10.3f' % self.mtx[i][j]
            result = result + "\n"
        #end for
        return result
    #end def

    def transformVector( self, NTcVector vec not None ):
        # transform vec according to rot/trans matrix of self
        # return vec
        cdef int i, j
        cdef NTcVector result

        # translate
        result = NTcVector( self.mtx[0][3], self.mtx[1][3], self.mtx[2][3] )
        # rotate
        for i from 0 <= i < VECTOR_SIZE:
            for j from 0 <= j < VECTOR_SIZE:
                result.e[i] = result.e[i] + self.mtx[i][j] * vec.e[j]
            #end for
        #end for

        # copy result back into vec
        result.copy( vec )
        return vec
    #end def
#end cdef

cdef NTcVector calculateCenter( vectors ):
    # calculate the geometric center of vectors
    # Return NTcVector instance
    cdef int n, nv, i
    cdef double tmp

    cdef NTcVector ctr, c # use temp variables to let compiler know about NTcVector
                          # attributes

    ctr = NTcVector( 0.0, 0.0, 0.0 )
    nv = len(vectors)
    for n from 0 <= n < nv:
        # we could have done:
        #    ctr += vectors[i]
        # but I expect this to be slower as it involves more overhead.
        # Hence, we explicitly code it using a temp variable (see above).
        c = vectors[n]
        for i from 0<=i<VECTOR_SIZE:
            ctr.e[i] = ctr.e[i] + c.e[i]
        #end for
    #end for

    tmp = 1.0/nv
    for i from 0 <= i < VECTOR_SIZE:
        ctr.e[i] = ctr.e[i] * tmp
    #end for

    return ctr
#end def


def calculateRMSD( vectorList1, vectorList2 ):
    # Calculate rmsd of vectorList1 and vectorList2
    # return rmsd
    cdef int n, nv, i
    cdef double rmsd, tmp

    cdef NTcVector c1, c2 # use temp variables to let compiler know about NTcVector
                          # attributes

    if (vectorList1 == None or vectorList2 == None):
        stderr.write("Error calculateRMSD: undefined vectorList(s)\n")
        raise RuntimeError
    #end if

    nv = len( vectorList1 )
    if nv==0:
        return 0.0
    #end if
    if len(vectorList2) != nv:
        stderr.write("Error calculateRMSD: unequal vectorLists\n")
        raise RuntimeError
    #end if

    rmsd = 0.0
    for n from 0 <= n < nv:
        # We explicitly code it using a temp variable.
        c1 = vectorList1[n]
        c2 = vectorList2[n]
#       tmp = (c1-c2).length()
#       rmsd = rmsd + tmp*tmp
#       Explicit coding saves a sqrt and multiplication operation
        for i from 0<=i<VECTOR_SIZE:
            tmp = c1.e[i]-c2.e[i]
            rmsd = rmsd + tmp*tmp # += operator not defined
        #end for
    #end for
    return sqrt( rmsd/nv )
#end def


DEF MTX_SUPTOLERANCE = 0.00000001
DEF MTX_SUPMAXITS  = 100000

def superposeVectors( sourceVectors, otherVectors ):
    # Calculate rot/translate matrix to superpose the sourceVectors onto otherVectors
    # return matrix
    cdef int n, j, k, p, q, r, nv
    cdef double sum, tmp

    cdef NTcVector c1, center1              # use temp variables to let compiler know about NTcVector
    cdef NTcVector c2, center2              # attributes
    cdef NTcMatrix cmtx, smtx

    cdef int rotated,iterations
    cdef double sigma, gamma, dist, qk, rk
    cdef NTcVector tmpVec

    if (sourceVectors == None):
        raise RuntimeError
    #end if

    if (otherVectors == None):
        raise RuntimeError
    #end if

    if len(otherVectors) != len( sourceVectors):
        raise RuntimeError
    #end if

    center2 = calculateCenter( sourceVectors ) # set souce to '2' to keep in-line with original C-code
    center1 = calculateCenter( otherVectors ) # set other to '1' to keep in-line with original C-code

    #print sourceVectors, otherVectors, center1, center2

    nv = len( sourceVectors )
    # calculate correlation matrix
    cmtx = NTcMatrix()
    for j from 0<=j<VECTOR_SIZE:
        for k from 0<=k<VECTOR_SIZE:
            sum = 0.0
            for n from 0 <= n < nv:
                c2 = sourceVectors[n]
                c1 = otherVectors[n]
                sum = sum + (c1.e[j]-center1.e[j]) * (c2.e[k]-center2.e[k])
            #end for
            cmtx.mtx[k][j]=sum
        #end for
    #end for

    #print cmtx

    # calculate superposition matrix
    smtx = NTcMatrix()
    # Iterate
    iterations = 0
    rotated = 1
    while (rotated and iterations < MTX_SUPMAXITS):
        # CALCULATE THE ROTATION NEEDED ABOUT EACH AXIS */
        rotated=0;
        for p from 0<=p<3:
            if (p+1<=2): q=p+1
            else: q=0 # q=(p+1<=2)?p+1:0;
            if (q+1<=2): r=q+1
            else: r=0 # r=(q+1<=2)?q+1:0;

            # CALCULATE THE ROTATION NEEDED, ANGLE = ARCTAN(SIGMA/GAMMA) */
            sigma=cmtx.mtx[r][q]-cmtx.mtx[q][r]
            gamma=cmtx.mtx[q][q]+cmtx.mtx[r][r]

            # IF THE ANGLE IS NOT TOO SMALL, UPDATE THE TWO MATRICES */
            # printf(">> Iteration %d: %g %g %d\n",iterations,sigma,gamma,fabs(sigma/gamma)>MTX_SUPTOLERANCE); */

            # IF TWO POINTS ARE PLACED ALONG ONE MAJOR AXIS BUT IN REVERSED DIRECTION,
            # fabs(sigma/gamma)<MTX_SUPTOLERANCE, BUT STILL THEY ARE NOT SUPERPOSED.
            # THE CHECK FOR gamma<0 FIXES THAT PROBLEM. */
            if (gamma!=0.0 and (gamma<0.0 or fabs(sigma/gamma)>MTX_SUPTOLERANCE)):
                dist=sqrt(gamma*gamma+sigma*sigma)
                if (dist!=0.0):
                    for k from 0<=k<3:
                        # THE SUPERPOSITION MATRIX */
                        qk=smtx.mtx[q][k]
                        rk=smtx.mtx[r][k]
                        smtx.mtx[q][k]=(gamma*qk+sigma*rk)/dist
                        smtx.mtx[r][k]=(-sigma*qk+gamma*rk)/dist
                        # AND THE CORRELATION MATRIX */
                        qk=cmtx.mtx[q][k]
                        rk=cmtx.mtx[r][k]
                        cmtx.mtx[q][k]=(gamma*qk+sigma*rk)/dist
                        cmtx.mtx[r][k]=(-sigma*qk+gamma*rk)/dist
                    #end for
                #end if
                rotated=1
            #end if
        #end for
        iterations = iterations + 1
    #end while  # rotated&&iterations++<MTX_SUPMAXITS);

    # CREATE FINAL TRANSFORMATION MATRIX */
    # to calculate the translation we have to rotate the geometric center of model2(==Self)
    tmpVec = NTcVector( center2.e[0], center2.e[1], center2.e[2] )
    smtx.transformVector( tmpVec )
    # and shift it to the center of model1(==other)
    smtx.settrans( -tmpVec.e[0]+center1.e[0], -tmpVec.e[1]+center1.e[1], -tmpVec.e[2]+center1.e[2] )
    #print 'iterations>', iterations, 'smtx>', smtx

    return smtx
#end def

##############################################################################
# OLD STUFF #
##############################################################################
# class Model( NTcMatrix ):
#     """
#     Model class
#
#     nCoordinates > 0 initializes fitting coordinate vectors
#     nOtherCoordinates > 0 initializes other coordinate vectors
#     """
#     nextId = 0
#
#     def __init__( self, nCoordinates = 0, nOtherCoordinates = 0 ):
#         cdef int i
#
#         NTcMatrix.__init__( self )
#         self.modelId           = Model.nextId
#         Model.nextId           = Model.nextId + 1
#         self.coordinates       = []  # coordinates used for fitting
#         self.nCoordinates      = 0
#         self.otherCoordinates  = []  # coordinates not used for fitting
#         self.nOtherCoordinates = 0
#         self.rmsd              = 0.0
#
#         for i from 0<=i<nCoordinates:
#             self.appendFitCoordinate( NTcVector(0.0, 0.0, 0.0) )
#         #end for
#         for i from 0<=i<nOtherCoordinates:
#             self.appendOtherCoordinate( NTcVector(0.0, 0.0, 0.0) )
#         #end for
#     #end def
#
#     def appendFitCoordinate( self, coordinate ):
#         self.coordinates.append( coordinate )
#         self.nCoordinates = self.nCoordinates + 1
#     #end def
#
#     def appendOtherCoordinate( self, coordinate ):
#         self.otherCoordinates.append( coordinate )
#         self.nOtherCoordinates = self.nOtherCoordinates + 1
#     #end def
#
#     def copy( self, other ):
#         # Copy the coordinate data and matrix data to other
#         cdef int i
#
#         if (other == None):
#             raise RuntimeError
#         #end if
#
#         if (self.nCoordinates != other.nCoordinates):
#             raise RuntimeError
#         #end if
#
#         if (self.nOtherCoordinates != other.nOtherCoordinates):
#             raise RuntimeError
#         #end if
#
#         for i from 0<=i<self.nCoordinates:
#             self.coordinates[i].copy( other.coordinates[i] )
#         #end for
#
#         for i from 0<=i<self.nOtherCoordinates:
#             self.otherCoordinates[i].copy( other.otherCoordinates[i] )
#         #end for
#
#
#         NTcMatrix.copy( self, other )
#         other.rmsd = self.rmsd
#     #end def
#
#     def duplicate( self ):
#         # duplicate the model
#         dup = Model( self.nCoordinates, self.nOtherCoordinates )
#         self.copy( dup )
#         return dup
#     #end def
#
#     def superpose( self, other ):
#         smtx = superposeVectors( self.coordinates, other.coordinates )
#         #copy the result to source
#         smtx.copy( self )
#
#         # transform and calculate rmsd
#         self.transform()
#         self.calculateRMSD( other )
#     #end def
#
#     def calculateRMSD( self, other ):
#         # Calculate rmsd to Model other
#         # store in rmsd attribute
#         self.rmsd = calculateRMSD( self.coordinates, other.coordinates )
#     #end def
#
#     def transform( self ):
#         # Transform all coordinates according to rotation/translation matrix
#         for c in self.coordinates + self.otherCoordinates:
#             self.transformVector( c )
#         #end for
# #        self.transformVector( self.center )
#     #end def
#
#     def __str__( self ):
#         # generate a string representation
#         s = ""
#         s = s + "---------- Model %d ----------\n" % (self.modelId,)
#         s = s + "coordinates (%d):\n" % (self.nCoordinates, )
#
#         i = 0
#         for i in range( self.nCoordinates ):
#             s = s + "%-10d %s\n" % (i, str(self.coordinates[i]) )
#         #end for
# #        s = s + "%-10s %s\n" % ("center:", str(self.center) )
#
#         s = s + "\nmatrix:\n%s\n" % (NTcMatrix.__str__(self), )
#         s = s + "%-10s %10.3f\n" %  ("rmsd:", self.rmsd )
#         return s
#     #end def
# #end class
#
# def calculateAverageModel( ensemble ):
#     # calculate averageModel from models in ensemble
#     # return  averageModel or None on error
#     cdef int i, j, n, nc, nmodels
#     cdef NTcVector avVec, mVec
#     cdef double tmp, rmsd
#
#     if (ensemble == None or len( ensemble) == 0):
#         return None
#     #end if
#
#     m0 = ensemble[0]
#     for m in ensemble[1:]:
#         if (m.nCoordinates != m0.nCoordinates):
#             return None
#         #end if
#     #end for
#     nmodels = len(ensemble)
#     tmp = 1.0/nmodels
#
#     nc = ensemble[0].nCoordinates
#     nc2 = ensemble[0].nOtherCoordinates
#     averageModel = Model( nc, nc2 )
#     for n from 0<=n<nc:
#         avVec = averageModel.coordinates[n]
#         for i from 0<=i<nmodels:
#             mVec = ensemble[i].coordinates[n]
#             for j from 0<=j<VECTOR_SIZE:
#                 avVec.e[j] = avVec.e[j] + mVec.e[j]
#             #end for
#         #end for
#         for j from 0<=j<VECTOR_SIZE:
#             avVec.e[j] = avVec.e[j] * tmp
#         #end for
#     #end for
#
#     for n from 0<=n<nc2:
#         avVec = averageModel.otherCoordinates[n]
#         for i from 0<=i<nmodels:
#             mVec = ensemble[i].otherCoordinates[n]
#             for j from 0<=j<VECTOR_SIZE:
#                 avVec.e[j] = avVec.e[j] + mVec.e[j]
#             #end for
#         #end for
#         for j from 0<=j<VECTOR_SIZE:
#             avVec.e[j] = avVec.e[j] * tmp
#         #end for
#     #end for
#
#     # calculate rmsd of ensemble to mean
#     rmsd = 0.0
#     for n from 0<=n<nc:
#         avVec = averageModel.coordinates[n]
#         for i from 0<=i<nmodels:
#             mVec = ensemble[i].coordinates[n]
# #            tmp = (mVec-avVec).length()
# #            rmsd = rmsd  + tmp*tmp
# # Explicit coding saves a sqrt and multiplication operation
#             for j from 0<=j<VECTOR_SIZE:
#                 tmp = mVec.e[j]-avVec.e[j]
#                 rmsd = rmsd + tmp*tmp # += operator not defined
#             #end for
#         #end for
#     #end for
#     averageModel.rmsd = sqrt(rmsd/float(nmodels*nc))
#
#     return averageModel
# #end def
#
#
#
# def superposeEnsemble( ensemble, iterations=2 ):
#     # superpose the members of the ensemble
#     # calculate averageModel
#     #
#     # iteration 0: superpose on model[0]
#     # iterations 1-n: calculate average; superpose on average
#     #
#     # return averageModel or None on error
#
#     if (ensemble == None or len( ensemble) == 0):
#         return None
#     #end if
#
#     m0 = ensemble[0]
#     nmodels = len(ensemble)
#     for m in ensemble[1:]:
#         if (m.nCoordinates != m0.nCoordinates):
#             return None
#         #end if
#         m.superpose( m0 )
#     #end for
#
#     niter = 1
#     while ( niter < iterations ):
#         averageModel = calculateAverageModel( ensemble )
#         for m in ensemble:
#             m.superpose( averageModel )
#         #end for
#         niter = niter + 1
#     #end while
#
#     return calculateAverageModel( ensemble )
# #end def