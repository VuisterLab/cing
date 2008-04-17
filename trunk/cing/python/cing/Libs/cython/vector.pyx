#----------------------------------------------------------------------- 
#
# vector.pyx
# GWV Feb 2008
#
#-----------------------------------------------------------------------

#----------------------------------------------------------------------- 
#
# vector.pxd
# GWV Feb 2008
#
#----------------------------------------------------------------------- 
#
#cdef enum:
#    VECTOR_SIZE = 3
#
#cdef class Vector:
#    
     # mapped onto vec.e[0], vec.e[1], vec.e[2] (for C-part only)
     # mapped onto vec.x,    vec.y,    vec.z    (C-part and Python)
     # mapped onto vec[0],   vec[1],   vec[2]   (C-part and Python)
#
#    cdef double e[VECTOR_SIZE]
#    cdef int iterCount
#-----------------------------------------------------------------------

from vector cimport VECTOR_SIZE
from math   import sqrt, sin, cos, tan, asin, acos, atan2, pi

cdef class Vector:
    
    def __init__( self,  double x,  double y,  double z ):
        self.iterCount = -1
        self.set( x, y, z)
    #end def
    
    property x:
        def __get__( self ):
            return self.e[0]
        def __set__( self, double value ):
            self.e[0] = value
    property y:
        def __get__( self ):
            return self.e[1]
        def __set__( self, double value ):
            self.e[1] = value
    property z:
        def __get__( self ):
            return self.e[2]
        def __set__( self, double value ):
            self.e[2] = value

    def __getitem__( self, int i ):
        if (i<0 or i>=VECTOR_SIZE):
            raise IndexError
        return self.e[i]
    #end def

    def __setitem__( self, int i, double value ):
        if (i<0 or i>=VECTOR_SIZE):
            raise IndexError
        self.e[i] = value
    #end def

    def set( self, double x, double y, double z ):
        self.e[0] = x
        self.e[1] = y
        self.e[2] = z
    #end def

    def get( self ):
        return ( self.e[0] , self.e[1] , self.e[2] )
    #end def

    def copy( self, Vector toVector not None ):
        cdef int i
        for i from 0 <= i < VECTOR_SIZE:
            toVector.e[i] = self.e[i]
        #end for
    #end def

    def duplicate( self ):
        # Return a copy of self
        cdef Vector dup
        dup = Vector( self.e[0] , self.e[1] , self.e[2] )
        return dup
    #end def

    def __iter__( self ):
        self.iterCount = 0
        return self
    #end def

    def __next__( self ):
        if (self.iterCount < 0 or self.iterCount == VECTOR_SIZE):
            raise StopIteration
            return None
        #end if
        self.iterCount = self.iterCount+1
        return self.e[self.iterCount-1]
    #end def
    
    def __len__( self ):
        return int(VECTOR_SIZE)
    #end def

    def __str__( self ):
        return '(%+.3f,%+.3f,%+.3f)' % self.get()
    #end def

    def __repr__(self):
        return 'Vector(%f,%f,%f)' % self.get()
    #end def

    def length( self ):
        # return length of self
        cdef double l
        cdef int i
        l = 0.0
        for i from 0 <= i < VECTOR_SIZE:
            l = l+(self.e[i]*self.e[i])
        #end for
        return sqrt(l)
    #end def

    def norm( self ):
        # Return a normalized vector   
        cdef double l
        l = 1.0/self.length()
        return Vector( self.e[0]*l, self.e[1]*l, self.e[2]*l )
    #end def

# arithmic; special methods cannot use the C exposed variables
# Page xxx Pyrec documentation
    def __add__( self, Vector other not None ):
        cdef Vector result 
        result = Vector( self[0] + other[0], self[1] + other[1], self[2] + other[2] )
        return result
    #end def 
    
    def __iadd__( self, Vector other not None ):
        self[0] = self[0] + other[0]
        self[1] = self[1] + other[1]
        self[2] = self[2] + other[2]
        return self
    #end def 
    
    def __sub__( self, Vector other not None ):
        cdef Vector result 
        result = Vector( self[0] - other[0], self[1] - other[1], self[2] - other[2] )
        return result
    #end def 
    
    def __isub__( self, Vector other not None ):
        self[0] = self[0] - other[0]
        self[1] = self[1] - other[1]
        self[2] = self[2] - other[2]
        return self
    #end def 
    
    def __neg__( self ):
        cdef Vector result 
        result = Vector( -self[0], -self[1], -self[2] )
        return result
    #end def 
    
    def __pos__( self ):
        cdef Vector result 
        result = Vector( self[0], self[1], self[2] )
        return result
    #end def 
    
    def toPolar( self, radians = False ):
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
    
    def fromPolar( self, polarCoordinates, radians = False ):
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

    def dot( self, Vector other ):
        """
        Return inner product of self and other
        """
        return (self.e[0]*other.e[0]+self.e[1]*other.e[1]+self.e[2]*other.e[2])
    #end def    

    def cross( self, Vector other ):
        """
        return cross vector spanned by self and other

          result = self x other
          
        Definitions from Kreyszig, Advanced Enginering Mathematics, 4th edition, Wiley and Sons, p273
        
        """

        return Vector( self.e[1]*other.e[2] - self.e[2]*other.e[1], # x-coordinate
                       self.e[2]*other.e[0] - self.e[0]*other.e[2], # y-coordinate
                       self.e[0]*other.e[1] - self.e[1]*other.e[0]  # z-coordinate
                     )
    #end def

    def triple( self, Vector b, Vector c):
        """
        return triple product of self,b,c
        """        
        return (  self.e[0] * (b.e[1]*c.e[2]-b.e[2]*c.e[1] )
                - self.e[1] * (b.e[0]*c.e[2]-b.e[2]*c.e[0] )
                + self.e[2] * (b.e[0]*c.e[1]-b.e[1]*c.e[0] )
               )
    #end def

    def angle( self, Vector other, radians = False ):
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

    def distance( self, Vector other ):
        """
        return distance between self and other
        """        
        return (self-other).length()    
    #end def

#end cdef Vector
                  
def isVector(x):
    """
    Determines if the argument is a vector class object.
    """
    # Convert 1/0 from C's hasattr fie to Python's True/False
    if (hasattr(x,'__class__') and x.__class__ is Vector):
        return True
    else:
        return False
#end def

