from cing.Libs.NTutils import NTerror
from numpy.core.fromnumeric import clip, searchsorted, prod
from numpy.core.numeric import asarray, empty
from numpy.lib.index_tricks import ndindex
from numpy.lib.index_tricks import ogrid
import numpy

""" Absorbed from: http://www.scipy.org/PauGargallo/Interpolation
"""

def interpn_nearest(z, targetcoords, bincoords=None):
        '''Interpolate some data, z, located at bincoords in the target locations targetcoords
        using nearest neighbor interpolation.
                z - is the data array
                targetcoords - are the coordinates where we want to evaluate the data.
                        It must have a format so that z[targetcoords] would make sense
                        if targetcoords where integers.
                        mgrid and ogrid can be used to get such a format.
                bincoords - is a list of arrays. Each array should containt.
        '''
        coords = interpn_check_data(z, targetcoords, bincoords)
        indices = [ c.round().astype('i') for c in coords ]
        return z[indices]


def interpn_linear(z, targetcoords, bincoords=None):
        '''Interpolate some data, z, located at bincoords in the target locations targetcoords
        using linear interpolation.
                z - is the data array
                targetcoords - are the coordinates where we want to evaluate the data.
                        It must have a format so that z[targetcoords] would make sense
                        if targetcoords where integers.
                        mgrid and ogrid can be used to get such a format.
                bincoords - is a list of arrays. Each array should containt.

        JFD NB consider checking out interp2_linear to see what this function is actually doing.
        '''
        coords = interpn_check_data(z, targetcoords, bincoords)

        indices = [ x.astype('i') for x in coords ]
        weights = [ x - i for x, i in zip(coords, indices) ]

        res = z[indices] * 0

        for selector in ndindex(*z.ndim * (2,)):
                weight = 1
                for w, s in zip(weights, selector):
                        if s: weight = weight * w
                        else: weight = weight * (1 - w)
                value = z[ [ i + s for i, s in zip(indices, selector) ] ]
                res += weight * value

        return res



def rebin(a, newshape):
        '''Rebin an array to a new shape, without interpolation.
        This can be usefull if the array type is not a vector space.
        '''
        assert a.ndim == len(newshape)

        slices = [ slice(0, old, float(old) / new) for old, new in zip(a.shape, newshape) ]
        coordinates = ogrid[slices]
        indices = [ c.astype('i') for c in coordinates ]
        return a[indices]



#################################
## more internal functions

def array_coordinates(targetx, binx):
        '''Computes the coordinates in an array reference.
                targetx are the coordinates of the points that we want to get in the array reference.
                binx    are the coordinates of the array bins
        Example:
                >>> array_coordinates( [2, 10], [1, 3, 13] )
                [0.5, 1.7]
        '''
        tol = 1e-12
        binx = asarray(binx)
        nx = clip(targetx, binx.min()*(1 + tol), binx.max()*(1 - tol))

        i = searchsorted(binx, nx)      # index of the biggest smaller bin

        bx = empty((len(binx) + 2,), 'd')   # avoid probles at the border
        bx[0] = binx[0] - 1
        bx[1:-1] = binx
        bx[-1] = binx[-1] + 1

        return i - 1 + (nx - bx[i]) / (bx[i + 1] - bx[i])


def interpn_check_data(z, targetcoords, bincoords):
        '''Check the validity of the input data for intepn_x functions
        and returns the target coordinates in the array reference
        '''
        dim = z.ndim
        if bincoords:
                if len(bincoords) != dim:
                        raise ValueError, 'bincoords shape mismatch (A).'
                for i in range(dim):
                        if prod(bincoords[i].shape) != z.shape[i]:
                                raise ValueError, 'bincoords shape mismatch (B).'

                coords = [ array_coordinates(targetcoords[i], bincoords[i].ravel()) for i in range(dim) ]
        else:
                coords = targetcoords
#        print coords
        return coords


def interp2_linear(z, tx, ty, binx=None, biny=None):
        '''Toy function just like interpn_linear in 2 dimensions.
        This function exists just to help the understanding and maintaining of interpn_linear.
        '''
        if not binx is None: tx = array_coordinates(tx, binx)
        if not biny is None: ty = array_coordinates(ty, biny)

        ix = tx.astype('i')
        iy = ty.astype('i')
        wx = tx - ix
        wy = ty - iy

        return    (1 - wy) * (1 - wx) * z[iy  , ix  ] \
                + (1 - wy) * wx * z[iy  , ix + 1] \
                + wy * (1 - wx) * z[iy + 1, ix  ] \
                + wy * wx * z[iy + 1, ix + 1]

def circularlizeMatrix(p):
    """Adds 2 rows and columns with circular values.
    Returns None on error.
    See unit test case
    """

    if p == None:
        NTerror("Got None for hist in circularlizeMatrix")
        return

    if not isinstance(p,numpy.ndarray):
        NTerror("Got hist that is not an instance of ndarray but a: [%s]" % `p.__class__`)
        return


    binCount = p.shape[0]
#    NTdebug("binCounts p: %s" % `p.shape`)
#    NTdebug(`p`)
    binCountP = binCount + 2
    binCountM = binCount - 1
    binCountPM = binCountP - 1
    q = numpy.zeros(binCountP * binCountP).reshape(binCountP, binCountP)
#    NTdebug("binCounts q: %s" % `q.shape`)
    # Corners
    q[0,0] = 0.0 # for debugging.
#    v = p[binCountM][binCountM]
    v = p[binCountM,binCountM]
    q[0,0] = v
    q[0,binCountPM] = p[binCountM,0]
    q[binCountPM,0] = p[0,binCountM]
    q[binCountPM,binCountM] = p[0,0]
    # Edges
    for i in range(binCount):
         iP = i + 1
         q[iP,0] = p[i,binCountM]        # old right
         q[iP,binCountPM] = p[i,0]       # old left
         q[binCountPM,iP] = p[0,i]       # old top
         q[0,iP] = p[binCountM,i]        # old bottom
         # Inside
         for j in range(binCount):
             q[iP,j + 1] = p[i,j]
#    NTdebug(`q`)
    return q

