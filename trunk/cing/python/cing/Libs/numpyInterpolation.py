from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTutils import NTdebug
from matplotlib.pylab import imshow
from matplotlib.pylab import show # prone to change.
from matplotlib.pylab import subplot
from matplotlib.pylab import title
from numpy import * #@UnusedWildImport
import cing
#from matplotlib.pylab import imshow
#from matplotlib.pylab import show # prone to change.
#from matplotlib.pylab import subplot
#from matplotlib.pylab import title
#from numpy.core.fromnumeric import clip
#from numpy.core.fromnumeric import prod
#from numpy.core.ma import asarray
#from numpy.core.ma import sin
#from numpy.core.numeric import empty
#from numpy.lib.index_tricks import ndindex
#from numpy.lib.index_tricks import ogrid
#from numpy.core.fromnumeric import searchsorted

""" Absorbed from: http://www.scipy.org/PauGargallo/Interpolation
"""

def interpn_nearest( z, targetcoords, bincoords=None ):
        '''Interpolate some data, z, located at bincoords in the target locations targetcoords
        using nearest neighbor interpolation.
                z - is the data array
                targetcoords - are the coordinates where we want to evaluate the data.
                        It must have a format so that z[targetcoords] would make sense
                        if targetcoords where integers.
                        mgrid and ogrid can be used to get such a format.
                bincoords - is a list of arrays. Each array should containt.
        '''
        coords = interpn_check_data(z,targetcoords,bincoords)
        indices = [ c.round().astype('i') for c in coords ]
        return z[indices]


def interpn_linear( z, targetcoords, bincoords=None ):
        '''Interpolate some data, z, located at bincoords in the target locations targetcoords
        using linear interpolation.
                z - is the data array
                targetcoords - are the coordinates where we want to evaluate the data.
                        It must have a format so that z[targetcoords] would make sense
                        if targetcoords where integers.
                        mgrid and ogrid can be used to get such a format.
                bincoords - is a list of arrays. Each array should containt.
        '''
        coords = interpn_check_data(z,targetcoords,bincoords)

        indices = [ x.astype('i') for x in coords ]
        weights = [ x-i for x,i in zip(coords,indices) ]

        res = z[indices]*0

        for selector in ndindex( *z.ndim*(2,) ):
                weight = 1
                for w,s in zip(weights,selector):
                        if s: weight = weight*w
                        else: weight = weight*(1-w)
                value = z[ [ i+s for i,s in zip(indices,selector) ] ]
                res += weight*value

        return res



def rebin( a, newshape ):
        '''Rebin an array to a new shape, without interpolation.
        This can be usefull if the array type is not a vector space.
        '''
        assert a.ndim == len(newshape)

        slices = [ slice(0,old, float(old)/new) for old,new in zip(a.shape,newshape) ]
        coordinates = ogrid[slices]
        indices = [ c.astype('i') for c in coordinates ]
        return a[indices]



#################################
## more internal functions

def array_coordinates( targetx, binx ):
        '''Computes the coordinates in an array reference.
                targetx are the coordinates of the points that we want to get in the array reference.
                binx    are the coordinates of the array bins
        Example:
                >>> array_coordinates( [2, 10], [1, 3, 13] )
                [0.5, 1.7]
        '''
        tol = 1e-12
        binx = asarray(binx)
        nx = clip( targetx, binx.min()*(1+tol), binx.max()*(1-tol) )

        i = searchsorted( binx, nx )      # index of the biggest smaller bin

        bx = empty((len(binx)+2,), 'd')   # avoid probles at the border
        bx[0] = binx[0] - 1
        bx[1:-1] = binx
        bx[-1] = binx[-1] + 1

        return i-1 + ( nx - bx[i] )/( bx[i+1] - bx[i] )


def interpn_check_data( z, targetcoords, bincoords ):
        '''Check the validity of the input data for intepn_x functions
        and returns the target coordinates in the array reference
        '''
        dim = z.ndim
        if bincoords:
                if len(bincoords) != dim:
                        raise ValueError, 'bincoords shape mismatch.'
                for i in range(dim):
                        if prod(bincoords[i].shape) != z.shape[i]:
                                raise ValueError, 'bincoords shape mismatch.'

                coords = [ array_coordinates(targetcoords[i],bincoords[i].ravel()) for i in range(dim) ]
        else:
                coords = targetcoords
        return coords


def interp2_linear( z, tx, ty, binx=None, biny=None  ):
        '''Toy function just like interpn_linear in 2 dimensions.
        This function exists just to help the understanding and mantaining of interpn_linear.
        '''
        if not binx is None: tx = array_coordinates( tx,binx )
        if not biny is None: ty = array_coordinates( ty,biny )

        ix = tx.astype('i')
        iy = ty.astype('i')
        wx = tx-ix
        wy = ty-iy

        return    (1-wy)*(1-wx) * z[iy  ,ix  ] \
                + (1-wy)*   wx  * z[iy  ,ix+1] \
                +    wy *(1-wx) * z[iy+1,ix  ] \
                +    wy *   wx  * z[iy+1,ix+1]






###########################################
## some visual testing
##

def test():
        x,y = ogrid[ -1:1:10j, -1:1:10j ]
        z = sin( x**2 + y**2 )

        binx = (x,y)
        tx = ogrid[ -2:2:100j, -2:2:100j ]

        subplot(221)
        title('original')
        imshow(z)
        subplot(223)
        title('interpn_nearest')
        imshow( interpn_nearest( z, tx, binx ) )
        subplot(222)
        title('interpn_linear')
        imshow( interpn_linear( z, tx, binx ) )
        subplot(224)
        title('interp2_linear')
        imshow( interp2_linear( z, tx[0],tx[1], x.ravel(),y.ravel() ) )
        show()

def test_jfd():
        r,c = ogrid[ 0:10:5j, 0:1:5j ]
        # x is the row and 
        # y is the column but when printed the matrix is printed differently.
        z = r + c
#        z = sin( x - y )
        bins = (r,c)
        qr =  9.9
        qc =  0.1
        tx = ogrid[ qr:qr:1j, qc:qc:1j ]
#        tx = ( (-0.9), (-0.9) ) # single point interpolation
        interpolatedValueSection = interpn_linear( z, tx, bins )
        interpolatedValue = interpolatedValueSection[ 0,0 ] # need to use comma to separate
        # the rows and columns in numpy matrixes.
        NTdebug(" r: \n%s" % r)
        NTdebug(" c: \n%s" % c)
        NTdebug(" z: \n%s" % z)
        NTdebug(" tx: \n%s" % tx)
        NTdebug(" interpolatedValueSection: \n%s" % interpolatedValueSection)
        NTdebug(" interpolatedValue: %s" % interpolatedValue)
            
if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    test_jfd()