#----------------------------------------------------------------------- 
#
# vecmat.pxd
# GWV Apr 2008
#
#----------------------------------------------------------------------- 
cdef enum:
    VECTOR_SIZE = 3
    MATRIX_SIZE = 4

cdef class NTcVector:
    #-----------------------------------------------------------------------
    #    
    # mapped onto vec.e[0], vec.e[1], vec.e[2] (for C-part only)
    # mapped onto vec.x,    vec.y,    vec.z    (C-part and Python)
    # mapped onto vec[0],   vec[1],   vec[2]   (C-part and Python)

    cdef double e[VECTOR_SIZE]
    cdef int iterCount
    #-----------------------------------------------------------------------

cdef class NTcMatrix:
    #-----------------------------------------------------------------------
    #
    #   translation/rotation  MATRIX
    #   ======================
    #   1  0  0  X
    #   0  1  0  Y
    #   0  0  1  Z
    #   0  0  0  1   
    #-----------------------------------------------------------------------

    cdef double mtx[MATRIX_SIZE][MATRIX_SIZE]

#-----------------------------------------------------------------------
