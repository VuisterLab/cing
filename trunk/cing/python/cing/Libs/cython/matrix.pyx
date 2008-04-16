#----------------------------------------------------------------------- 
#
# matrix.pyx
# 
# Initial code to superimpose structures of ensemble.
# 
# GWV Feb 2008
# 
# Core routines mtx_superpose and superposeModels adapted from code
# by Elmar Krieger, YASARA
#
#-----------------------------------------------------------------------

#----------------------------------------------------------------------- 
#
# matrix.pxd
# GWV Apr 2008
#
#----------------------------------------------------------------------- 
#
#cdef enum:
#    MATRIX_SIZE = 4
#
#cdef class Matrix:
    #-----------------------------------------------------------------------
    #
    #   translation/rotation  MATRIX
    #   ======================
    #   1  0  0  X
    #   0  1  0  Y
    #   0  0  1  Z
    #   0  0  0  1   
    #-----------------------------------------------------------------------
#
#    cdef double mtx[MATRIX_SIZE][MATRIX_SIZE]
#
#-----------------------------------------------------------------------

from sys import stderr
from sys import stdout

from math import sqrt, fabs

# Make the Vector defs visibe within current context
from vector cimport VECTOR_SIZE, Vector
# Make the Matrix defs visible
from matrix cimport MATRIX_SIZE
    
DEF BARLENGTH = 60
DEF MTX_SUPTOLERANCE = 0.00000001
DEF MTX_SUPMAXITS  = 100000

cdef class Matrix:
    
    def __init__( self ):
        self.setunit()
    
    def __getitem__( self, indexTuple ):
        cdef int i, j, l
        
        try:
            l = len(indexTuple)
        except:
            stderr.write( "_"*BARLENGTH +"\n!!! Error Matrix: invalid indexTuple >%s<.\n" % str(indexTuple) )
            raise IndexError
            return None
        #end try
        if (l != 2):
            stderr.write( "_"*BARLENGTH +"\n!!! Error Matrix: invalid indexTuple >%s<.\n" % str(indexTuple) )
            raise IndexError
            return None
        #end if
        i = indexTuple[0]
        j = indexTuple[1]
        if (i<0 or i>=MATRIX_SIZE): 
            stderr.write( "_"*BARLENGTH +"\n!!! Error Matrix: index i (%d) out of bound.\n" % i )
            raise IndexError
        #end if
        if (j<0 or j>=MATRIX_SIZE):
            stderr.write( "_"*BARLENGTH +"\n!!! Error Matrix: index j (%d) out of bound.\n" % j )
            raise IndexError
        #end if
        return self.mtx[i][j]
    #end def
    
    def __setitem__( self, indexTuple, double value ):
        cdef int i, j, l
        
        try:
            l = len(indexTuple)
        except:
            stderr.write( "_"*BARLENGTH +"\n!!! Error Matrix: invalid indexTuple >%s<.\n" % str(indexTuple) )
            raise IndexError
        #end try
        if (l != 2):
            stderr.write( "_"*BARLENGTH +"\n!!! Error Matrix: invalid indexTuple >%s<.\n" % str(indexTuple) )
            raise IndexError
        #end if
        i = indexTuple[0]
        j = indexTuple[1]
        if (i<0 or i>=MATRIX_SIZE): 
            stderr.write( "_"*BARLENGTH +"\n!!! Error Matrix: index i (%d) out of bound.\n" % i )
            raise IndexError
        #end if
        if (j<0 or j>=MATRIX_SIZE):
            stderr.write( "_"*BARLENGTH +"\n!!! Error Matrix: index j (%d) out of bound.\n" % j )
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

    def copy( self, Matrix other not None ):
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
    
    def transformVector( self, Vector vec not None ): 
        # transform vec according to rot/trans matrix of self
        # return vec
        cdef int i, j
        cdef Vector result
        
        result = Vector( 0.0, 0.0, 0.0 )
        # rotate / translate
        for i from 0 <= i < VECTOR_SIZE:
            for j from 0 <= j < VECTOR_SIZE:
                result.e[i] = result.e[i] + self.mtx[i][j] * vec.e[j]
            #end for
        #end for
        for i from 0 <= i < VECTOR_SIZE:
            result.e[i] = result.e[i] + self.mtx[i][3]
        #end for
        
        # copy result back into vec
        result.copy( vec )
        return vec
    #end def
#end cdef

class Model( Matrix ):

    nextId = 0
    
    def __init__( self, nCoordinates ):
        Matrix.__init__( self )
        self.modelId     = Model.nextId
        Model.nextId     = Model.nextId + 1
        self.coordinates = []
        
        for i from 0<=i<nCoordinates+1: # add one to act as center coordinate
            self.coordinates.append( Vector(0.0,0.0,0.0) )
        #end for
        self.nCoordinates = nCoordinates
        self.center       = self.coordinates[nCoordinates]
        self.rmsd         = 0.0
    #end def
    
    def copy( self, other ):
        # Copy the coordinate data and matrix data to other
        cdef int i

        if (other == None):
            raise RuntimeError
        #end if

        if (self.nCoordinates != other.nCoordinates):
            raise RuntimeError
        #end if
    
        for i from 0<=i<self.nCoordinates+1:
            self.coordinates[i].copy( other.coordinates[i] )
        #end for
        
        Matrix.copy( self, other )
        other.rmsd = self.rmsd
    #end def
    
    def duplicate( self ):
        # duplicate the model
        dup = Model( self.nCoordinates )
        self.copy( dup )
        return dup
    #end def
    
    def calculateCenter( self ):
        # calculate the geometric center of model
        cdef int n, i
        cdef double tmp
        
        cdef Vector ctr, c # use temp variables to let compiler know about Vector
                           # attributes
 
        ctr = self.center
        ctr.set( 0.0, 0.0, 0.0 )
        for n from 0 <= n < self.nCoordinates:
            # we could have done:
            #    self.center += self.coordinates[i]
            # but I expect this to be slower as it involves more overhead.
            # Hence, we explicitly code it using a temp variable (see above).
            c = self.coordinates[n] 
            for i from 0<=i<VECTOR_SIZE:
                ctr.e[i] = ctr.e[i] + c.e[i]
            #end for
        #end for
        
        tmp = 1.0/self.nCoordinates
        for i from 0 <= i < VECTOR_SIZE:
            ctr.e[i] = ctr.e[i] * tmp
        #end for
    #end def
    
    def calculateRMSD( self, other ):
        # Calculate rmsd to Model other
        # store in rmsd attribute
        cdef int n, i
        cdef double rmsd, tmp
        
        cdef Vector c1, c2 # use temp variables to let compiler know about Vector
                           # attributes
                           
        if (other == None):
            raise RuntimeError
        #end if

        if (self.nCoordinates != other.nCoordinates):
            raise RuntimeError
        #end if
        
        rmsd = 0.0
        for n from 0 <= n < self.nCoordinates:
            # We explicitly code it using a temp variable.
            c1 = self.coordinates[n] 
            c2 = other.coordinates[n]
#            tmp = (c1-c2).length()
#            rmsd = rmsd + tmp*tmp
# Explicit coding saves a sqrt and multiplication operation
            for i from 0<=i<VECTOR_SIZE:
                tmp = c1.e[i]-c2.e[i]
                rmsd = rmsd + tmp*tmp # += operator not defined
            #end for
        #end for
        self.rmsd = sqrt( rmsd/self.nCoordinates )
    #end def
    
    def superpose( self, other ):
        # Superpose the coordinates of self onto other
        # Set rot/translate matrix, rot/translate coordinates and 
        # calculate rmsd to other
        # return number of iterations
        cdef int n, j, k, p, q, r
        cdef double sum, tmp
        
        cdef Vector c1, center1, c2, center2 # use temp variables to let compiler know about Vector
                                             # attributes
        cdef Matrix cmtx, smtx
        
        cdef int rotated,iterations
        cdef double sigma, gamma, dist, qk, rk
        cdef Vector tmpVec
        
        if (other == None):
            raise RuntimeError
        #end if

        if (self.nCoordinates != other.nCoordinates):
            raise RuntimeError
        #end if
        
        self.calculateCenter()
        center2 = self.center # set self to '2' to keep in-line with original C-code
        other.calculateCenter()
        center1 = other.center # set other to '1' to keep in-line with original C-code
        
        # calculate correlation matrix
        cmtx = Matrix() 
        for j from 0<=j<VECTOR_SIZE:
            for k from 0<=k<VECTOR_SIZE:
                sum = 0.0
                for n from 0 <= n < self.nCoordinates:
                    c2 = self.coordinates[n] 
                    c1 = other.coordinates[n]
                    sum = sum + (c1.e[j]-center1.e[j]) * (c2.e[k]-center2.e[k])
                #end for
                cmtx.mtx[k][j]=sum
            #end for
        #end for

        #print cmtx
        
        # calculate superposition matrix
        smtx = Matrix()
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
        tmpVec = Vector( center2.e[0], center2.e[1], center2.e[2] )
        smtx.transformVector( tmpVec )
        # and shift it to the center of model1(==other) 
        smtx.settrans( -tmpVec.e[0]+center1.e[0], -tmpVec.e[1]+center1.e[1], -tmpVec.e[2]+center1.e[2] )
        #print smtx
        
        #copy the result to self
        smtx.copy( self )
        
        # transform and calculate rmsd
        self.transform()
        self.calculateRMSD( other )
        
        return iterations
    #end def
    
    def transform( self ):
        # Transform all coordinates according to rotation/translation matrix
        for c in self.coordinates:
            self.transformVector( c )
        #end for
    #end def

    def __str__( self ):
        # generate a string representation
        s = ""
        s = s + "---------- Model %d ----------\n" % (self.modelId,)
        s = s + "coordinates (%d):\n" % (self.nCoordinates, )
        
        i = 0
        for i in range( self.nCoordinates ):
            s = s + "%-10d %s\n" % (i, str(self.coordinates[i]) )
        #end for
        s = s + "%-10s %s\n" % ("center:", str(self.center) )

        s = s + "\nmatrix:\n%s\n" % (Matrix.__str__(self), )
        s = s + "%-10s %10.3f\n" %  ("rmsd:", self.rmsd )
        return s
    #end def
#end class

def calculateAverageModel( ensemble ):
    # calculate averageModel from models in ensemble
    # return  averageModel or None on error
    cdef int i, j, n, nc, nmodels
    cdef Vector avVec, mVec
    cdef double tmp, rmsd

    if (ensemble == None or len( ensemble) == 0): 
        return None
    #end if
    
    m0 = ensemble[0]
    for m in ensemble[1:]:
        if (m.nCoordinates != m0.nCoordinates):
            return None
        #end if
    #end for
    nmodels = len(ensemble)
    tmp = 1.0/nmodels
    
    nc = ensemble[0].nCoordinates
    averageModel = Model( nc )
    for n from 0<=n<nc:
        avVec = averageModel.coordinates[n]
        for i from 0<=i<nmodels:
            mVec = ensemble[i].coordinates[n]
            for j from 0<=j<VECTOR_SIZE:
                avVec.e[j] = avVec.e[j] + mVec.e[j]
            #end for
        #end for
        for j from 0<=j<VECTOR_SIZE:
            avVec.e[j] = avVec.e[j] * tmp
        #end for
    #end for
    
    # calculate rmsd of ensemble to mean
    rmsd = 0.0
    for n from 0<=n<nc:
        avVec = averageModel.coordinates[n]
        for i from 0<=i<nmodels:
            mVec = ensemble[i].coordinates[n]
#            tmp = (mVec-avVec).length()
#            rmsd = rmsd  + tmp*tmp
# Explicit coding saves a sqrt and multiplication operation
            for j from 0<=j<VECTOR_SIZE:
                tmp = mVec.e[j]-avVec.e[j]
                rmsd = rmsd + tmp*tmp # += operator not defined
            #end for
        #end for
    #end for
    averageModel.rmsd = sqrt(rmsd/float(nmodels*nc))
    
    averageModel.calculateCenter()
    return averageModel
#end def

def superposeEnsemble( ensemble, iterations=2 ):
    # superpose the members of the ensemble
    # calculate averageModel
    #
    # iteration 0: superpose on model[0]
    # iterations 1-n: calculate average; superpose on average
    #
    # return averageModel or None on error

    if (ensemble == None or len( ensemble) == 0): 
        return None
    #end if
    
    m0 = ensemble[0]
    nmodels = len(ensemble)
    for m in ensemble[1:]:
        if (m.nCoordinates != m0.nCoordinates):
            return None
        #end if
        m.superpose( m0 )
    #end for
    
    niter = 1
    while ( niter < iterations ):
        averageModel = calculateAverageModel( ensemble )
        for m in ensemble:
            m.superpose( averageModel )
        #end for
        niter = niter + 1
    #end while
    
    return calculateAverageModel( ensemble )
#end def