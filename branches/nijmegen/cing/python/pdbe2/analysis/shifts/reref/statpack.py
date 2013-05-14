#@PydevCodeAnalysisIgnore # pylint: disable-all
## Automatically adapted for numpy.oldnumeric Dec 01, 2009 by 

#
# Code from Wolfgang!
#

#from Numeric import *
#from numpy.oldnumeric.mlab import median
from matplotlib.pylab import * #@UnusedWildImport
from numpy.numarray.numerictypes import Float
from numpy.numarray.numerictypes import Float32
from numpy.oldnumeric.compat import NewAxis #@UnresolvedImport
from numpy.oldnumeric.linear_algebra import * #@UnusedWildImport
import numpy.oldnumeric as Numeric
#from LinearAlgebra import *

def histogram(data, nbins, range = None):
    """
    Comes from Konrad Hinsen: Scientific Python
    """
    
    data = Numeric.array(data, Numeric.Float)
    
    if range is None:
        min = Numeric.minimum.reduce(data)
        max = Numeric.maximum.reduce(data)
    else:
        min, max = range
        data = Numeric.repeat(data,
                  Numeric.logical_and(Numeric.less_equal(data, max),
                          Numeric.greater_equal(data,
                                    min)))
    # end if
    bin_width = (max-min)/nbins
    
    data = Numeric.floor((data - min)/bin_width).astype(Numeric.Int)
    histo = Numeric.add.reduce(Numeric.equal(
    Numeric.arange(nbins)[:,Numeric.NewAxis], data), -1)
    histo[-1] = histo[-1] + Numeric.add.reduce(Numeric.equal(nbins, data))
    bins = min + bin_width*(Numeric.arange(nbins)+0.5)
    return Numeric.transpose(Numeric.array([bins, histo]))
    
def correlation(x1, x2):
    x1 = (x1 - average(x1)) / standardDeviation(x1)
    x2 = (x2 - average(x2)) / standardDeviation(x2)

    return dot(x1,x2) / (len(x1) - 1.)

def average(x, return_sd = 0):

    av = Numeric.sum(array(x)) / len(x)

    if return_sd:
        sd = standardDeviation(x, avg = av) / Numeric.sqrt(len(x))
        return av, sd
    else:
        return av

def variance(x, avg = None):
    if avg is None:
        avg = average(x)

    return Numeric.sum(Numeric.power(Numeric.array(x) - avg, 2)) / (len(x) - 1.)

def standardDeviation(x, avg = None):
    return Numeric.sqrt(variance(x, avg))

def autoCorrelation(x, maxDist):

    """
    calculates the auto-correlation of a data-set 'x'.

    c(a) \propto <x(0)x(a)> - <x(0)><x(a)>
    """
    
    ac = []
    
    for i in range(1, maxDist + 1):
        ac.append(correlation(x[:-i], x[i:]))

    return Numeric.array(ac)

def pca(data):

    transposed = 0

    if shape(data)[0] < shape(data)[1]:
        transposed = 1
        data = transpose(data)
        
    cov = dot(transpose(data), data)

    ## eigenvectors are row vectors
    val, vec = eigenvectors(cov)

    try:
        val = val.real
    except:
        pass

    try:
        vec = vec.real
    except:
        pass

    order = argsort(val)

    val = Numeric.take(val, order)
    vec = Numeric.take(vec, order)

    pc = Numeric.dot(data, transpose(vec))

    if transposed:
        pc = Numeric.transpose(pc)
    
    return val, vec, pc

def covarianceMatrix(data, normalize = 1):
    npoints, dimension = shape(data)
    if normalize: 
        data = data - Numeric.sum(data)/npoints

    if dimension > npoints:
        return dot(data, Numeric.transpose(data)) / (npoints-1)
        
    return dot(transpose(data), data)/(npoints-1)

def principalComponents(data, normalize = 1, isCovarianceMatrix = 0):
    if not isCovarianceMatrix:
        return eigenvectors(covarianceMatrix(data, normalize))
    else:
        return eigenvectors(data)

def correlationMatrix(x):
    y = x - average(x)
    sd = standardDeviation(y)
    sdm = multiply.outer(sd, sd)

    n = shape(y)[0]
    c = dot(transpose(y), y) / (n - 1)
    return c / sdm

def zScores(data, ravel = None):
    import numpy.oldnumeric as Numeric #@Reimport

    if ravel is None:
        d = Numeric.array(data)
    else:
        d = Numeric.ravel(Numeric.array(data))
    average = average(d)
    sd = standardDeviation(d)

    return (data-average)/sd

def deleteRowAndColumn(matrix, row, column):
    n = shape(matrix)

    rowIndices = range(row) + range(row+1,n[0])
    columnIndices = range(column) + range(column+1,n[1])

    pruned = Numeric.take(matrix, rowIndices)
    return Numeric.take(pruned, columnIndices, 1)

def nonRedundantSet(d, threshold, distanceMatrix = 1):
    """
    returns an array consisting of entries having
    a maximum similarity (or distance) of 'threshold'.
    distanceMatrix <> None means matrix elemens are similarities.

    Ref.: Hobohm et al. (1992). Prot. Sci. 1, 409-417

    gives somehow weired results.
    """
    import whrandom #@UnresolvedImport

    d = Numeric.array(d).astype(Float32)
    if not distanceMatrix: d = less(d, threshold)
    else: d = greater(d, threshold)

    s = shape(d)
    d = Numeric.concatenate((reshape(range(s[0]),(-1,1)),d),1)

    ok = 1

    while ok:
        nNeighbours = Numeric.sum(d)
        if len(nNeighbours) <= 1: break
        maxx = max(nNeighbours[1:])
        others = Numeric.nonzero(equal(nNeighbours[1:], maxx))+1
        candidate = whrandom.choice(others)
        ok = nNeighbours[candidate]
        if ok: d = deleteRowAndColumn(d, candidate-1, candidate)
    # end while
    
    return d[:,0]

def non_redundant_set(d, threshold):
    """
    returns an array consisting of entries having
    a minimum pairwise distance of 'threshold'.

    Based on 

    Ref.: Hobohm et al. (1992). Prot. Sci. 1, 409-417
    """

#    import random

    d = Numeric.array(d).astype(Float32)
    d = less(d, threshold)

    s = shape(d)
    d = Numeric.concatenate((reshape(range(s[0]),(-1,1)),d),1)

    ok = 1

    while ok:
        nNeighbours = Numeric.sum(d)-1
        if len(nNeighbours) <= 1: break
        maxx = max(nNeighbours[1:])
        others = nonzero(equal(nNeighbours[1:], maxx))+1
        candidate = random.choice(others)
    
        ok = nNeighbours[candidate]

        if ok:
            d = deleteRowAndColumn(d, candidate-1, candidate)
    #end while
    return d[:,0]

def gaussArray(s, mu, sigma):
    """
    returns an 's'-shaped array, consisting
    of gaussian distributed floats
    """
#    import random

    try:
        l = s[0]*s[1]
    except:
        l=s[0]

    z = zeros(l,Float)
    for i in range(l):
        z[i] = random.gauss(mu, sigma)

    return reshape(z, s)

def density(x, nBins, range = None, steps = 1, hist = 0):
    """
    returns the normalized histogram of x
    steps = 1: histogram appears as a discrete graph
    """
    import numpy.oldnumeric as Numeric #@Reimport
    
    h = histogram(x, nBins, range)
    binWidth = h[1,0] - h[0,0]

    if not hist:
        i = Numeric.sum(h)[1]*binWidth
        h[:,1] = h[:,1]/i

    if steps:
        half = (h[1][0]-h[0][0])/2
        l = [(h[0][0]-half,0)]

        for row in h:
            l.append((row[0]-half,row[1]))
            l.append((row[0]+half,row[1]))

        l.append((h[-1][0]+half,0))

        h = l
        
    return Numeric.array(h)

def discrete_shannon_entropy(x, n_bins, _range = None):

    from R import digamma #@UnresolvedImport

    hist = density(x, n_bins, _range, steps = 0, hist = 1)
    x = hist[:,1]
    
    v = Numeric.sum(x)

    s = shape(x)
    z = zeros(s, Float)
    
    for i in range(s[0]):
        z[i] = digamma(x[i] + 1)

    return - Numeric.sum(x / v * (z - digamma(v + 1)))
    
def mutualInformation(counts):
    """
    bayesian estimator for the mutual information
    between two series of discrete numbers.
    'counts': matrix of counts
    """

    from R import digamma #@UnresolvedImport
    
    counts = Numeric.array(counts).astype(Float32)
    v = Numeric.sum(Numeric.sum(counts))
    r = digamma(v + 1)

    s = shape(counts)
    z = Numeric.zeros(shape(counts), Float)

    for i in range(s[0]):
        for j in range(s[1]):
            z[i,j] = digamma(counts[i,j] + 1)
    
    a = Numeric.sum(Numeric.sum(counts / v * (z - r)))
    
    m1 = Numeric.sum(counts, 1)
    m0 = Numeric.sum(counts)

    z0 = Numeric.zeros(shape(m0), Float)
    z1 = Numeric.zeros(shape(m1), Float)

    for i in range(len(m0)):
        z0[i] = digamma(m0[i] + 1)

    for i in range(len(z1)):
        z1[i] = digamma(m1[i] + 1)
    
    b = Numeric.sum(m0 / v * (z0 - r))
    c = Numeric.sum(m1 / v * (z1 - r))

    return a - b - c

def shannon_entropy(x, n_bins, _range):

    d = density(x, n_bins, range = _range, steps = 0)

    delta_x = d[1,0] - d[0,0]

    p = clip(d[:,1], 1.e-10, 1.e10)
    p = p / (Numeric.sum(p) * delta_x)

    S = - delta_x * Numeric.sum(p * Numeric.log(p))
    
    return S

def histogram2d(data, bins, xrange = None, yrange = None, as_matrix = 0):

    if as_matrix and (xrange is None or yrange is None):
        raise 'xrange and yrange not specified'

    try:
        data = Numeric.array(data, Float)
    except:
        raise TypeError, 'data: list or array excepted, %s given', \
              str(type(data))

    if not len(shape(data)) == 2:
        raise ValueError, 'shape of data array must be (n,2)'
    
    if type(bins) == type(0):
        bins = (bins, bins)
    elif not type(bins) in (type([]), type(())):
        raise TypeError, 'bins: int, list or tuple expected. %s given', \
              str(type(bins))

    if yrange is None:
        yrange = (min(data[:,1]), max(data[:,1]))

    x_min = min(data[:,0])
    x_max = max(data[:,0])
    x_spacing = (x_max - x_min) / bins[0]

    ystep = abs(yrange[1] - yrange[0]) / float(bins[1])

    if as_matrix:
        hist = []

    else:
        hist = zeros((0,3), Float)

    for y in arange(yrange[0] + ystep , yrange[1] + ystep, ystep):

        ## collect values which are in [y,y+ystep]

        mask = less_equal(data[:,1], y)
        set = compress(mask, data, 0)

        if not len(set):
            if as_matrix:
                hist.append(zeros(bins[1], Float))
                
            continue

        ## create histogram for x-dimension

        if shape(set[:,0])[0]:
            x_histogram = histogram(set[:,0], bins[0], range = xrange)
        else:
            x_bins = arange(x_min + x_spacing / 2., x_max + x_spacing / 2.,
                            x_spacing)

            ## no. of x_bins might be larger as it should be
            ## (due to numerical errors).

            if shape(x_bins)[0] - 1 == bins[0]:
                x_bins = x_bins[:-1]

            x_histogram = Numeric.concatenate((x_bins[:,NewAxis],
                                       zeros((bins[0],1))), 1)

        if as_matrix:
            hist.append(x_histogram[:,1])

        else:

            ## append #point per cell (x_i, y_i, n_i)

            s = ones(shape(x_histogram)[0]) * (y - ystep / 2.)
            n = Numeric.concatenate((x_histogram[:,:1],
                             s[:,NewAxis],
                             x_histogram[:,1:2]), 1)

            hist = Numeric.concatenate((hist, n))

        ## discard processed data

        data = Numeric.compress(Numeric.logical_not(mask), data, 0)

    return Numeric.array(hist)

def histogram2d_2(data, bins, xrange = None, yrange = None):

    try:
        data = Numeric.array(data, Float)
    except:
        raise TypeError, 'data: list or array excepted, %s given', \
              str(type(data))

    if not len(shape(data)) == 2:
        raise ValueError, 'shape of data array must be (n,2)'
    
    if type(bins) == type(0):
        bins = (bins, bins)
    elif not type(bins) in (type([]), type(())):
        raise TypeError, 'bins: int, list or tuple expected. %s given', \
              str(type(bins))

    if yrange is None:
        yrange = (min(data[:,1]), max(data[:,1]))

    x_min = min(data[:,0])
    x_max = max(data[:,0])
    x_spacing = (x_max - x_min) / bins[0]

    ystep = abs(yrange[1] - yrange[0]) / float(bins[1])

    X = []
    Y = []
    N = []

    for y in arange(yrange[0] + ystep , yrange[1] + ystep, ystep):

        ## collect values which are in [y,y+ystep]

        mask = less_equal(data[:,1], y)
        set = compress(mask, data, 0)

        ## create histogram for x-dimension

        if shape(set[:,0])[0]:
            x_histogram = histogram(set[:,0], bins[0], range = xrange)
        else:
            x_bins = arange(x_min + x_spacing / 2., x_max + x_spacing / 2.,
                            x_spacing)

            ## no. of x_bins might be larger as it should be
            ## (due to numerical errors).

            if shape(x_bins)[0] - 1 == bins[0]:
                x_bins = x_bins[:-1]

            x_histogram = Numeric.concatenate((x_bins[:,NewAxis],
                                       zeros((bins[0],1))), 1)

        ## append #point per cell (x_i, y_i, n_i)

        X.append(x_histogram[:,0])
        N.append(x_histogram[:,1])

        s = ones(shape(x_histogram)[0]) * (y - ystep / 2.)

        Y.append(s)

        ## discard processed data

        data = Numeric.compress(Numeric.logical_not(mask), data, 0)

    return Numeric.array(X), Numeric.array(Y), Numeric.array(N)

def write_as_table(x, filename):
    import os

    filename = os.path.expanduser(filename)

    f = open(filename, 'w')

    if len(shape(x)) == 1:
        template = '%e\n'
        make_tuple = 0
    else:
        template = '%e ' * shape(x)[1]
        template += '\n'
        make_tuple = 1

    for line in x:
        if make_tuple:
            line = tuple(line)
        f.write(template % line)

    f.close()

if __name__ == '__main__':

    from RandomArray import *

    r = random((10000,2))

    #x,y,n = histogram2d_2(r,(20,20))

