#----------------------------------------------------------------------- 
#
# vector.pxd
# GWV Feb 2008
#
#----------------------------------------------------------------------- 
#
cdef enum:
    VECTOR_SIZE = 3

cdef class Vector:
    
    # mapped onto vec.e[0], vec.e[1], vec.e[2] (for C-part)
    # mapped onto vec.x, vec.y, vec.z (C and Python)
    # mapped onto vec[0], vec[1], vec[2] (Python)

    cdef double e[VECTOR_SIZE]
    cdef int iterCount
#-----------------------------------------------------------------------


