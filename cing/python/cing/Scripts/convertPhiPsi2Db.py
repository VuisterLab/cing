from cing import cingDirTestsTmp
from cing import cingPythonCingDir
from cing import verbosityDebug
from cing import verbosityOutput
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import appendDeepByKeys
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.NTutils import setDeepByKeys
from cing.Libs.numpyInterpolation import interpn_linear
from cing.PluginCode.procheck import to3StateUpper
from cing.core.classes import Project
from matplotlib.numerix.mlab import amax
from matplotlib.pylab import axis
from matplotlib.pylab import colorbar
from matplotlib.pylab import contour
from matplotlib.pylab import imshow
from numpy.lib.index_tricks import ogrid
from numpy.lib.twodim_base import histogram2d
from pylab import nx
import cing
import csv
import os
import shelve


"""
Takes a file with dihedral angles values and converts them to a python pickle file
with histograms for (combined) residue and sec. struct. types.

Please note well that the values are per residue and that the value range is much
smaller than per molecule values. The per-molecule values are scaled by a sigma. 
See formula 8 in Rob Hooft's paper:

Hooft et al. Objectively judging the quality of a protein structure from a 
Ramachandran plot. Comput.Appl.Biosci. (1997) vol. 13 (4) pp. 425-430
"""

file_name_base  = 'phipsi_wi_db'
cvs_file_name   = file_name_base + '.csv'
dbase_file_name = file_name_base + '.dat'

binSize   = 60
binCount  = 360/binSize
binCountJ = (binCount + 0)* 1j # used for numpy's gridding.
dihedralName1= "PHI"
dihedralName2= "PSI"
project     = Project('ramachandranPlot')
plotparams1 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')
plotparams2 = project.plotParameters.getdefault(dihedralName2,'dihedralDefault')
xRange = (plotparams1.min, plotparams1.max)
yRange = (plotparams2.min, plotparams2.max)

# Used for linear interpolation
xGrid,yGrid = ogrid[ plotparams1.min:plotparams1.max:binCountJ, plotparams1.min:plotparams1.max:binCountJ ]
bins = (xGrid,yGrid)

pluginDataDir = os.path.join( cingPythonCingDir,'PluginCode','data')
os.chdir(cingDirTestsTmp)

def inRange(a):
    if a < plotparams1.min or a > plotparams1.max:
        return False
    return True
      
def main():
    cvs_file_abs_name = os.path.join( pluginDataDir, cvs_file_name )
    reader = csv.reader(open(cvs_file_abs_name, "rb"), quoting=csv.QUOTE_NONE)
    valuesBySsAndResType       = {}
    histBySsAndResType         = {}
    histBySsAndCombinedResType = {}
#    histByCombinedSsAndResType = {}
    valuesByEntrySsAndResType       = {}
    hrange = (xRange, yRange)
        
    for row in reader:
#        7a3h,A,VAL ,   5,H, -62.8, -52.8
#        7a3h,A,VAL ,   6,H, -71.2, -33.6
#        7a3h,A,GLU ,   7,H, -63.5, -41.6
        (entryId, _chainId, resType, _resNum, ssType, phi, psi) = row
        ssType = to3StateUpper(ssType)[0]
        resType = resType.strip()
        phi = float(phi)
        psi = float(psi)
        if not (inRange(phi) and inRange(psi)):
            NTerror("phi and/or psi not in range for row: %s" % `row`)
            return
        appendDeepByKeys(valuesBySsAndResType, phi, ssType,resType,'phi' )
        appendDeepByKeys(valuesBySsAndResType, psi, ssType,resType,'psi' )
#        NTdebug('resType,ssType,phi,psi: %4s %1s %8.3f %8.3f' % (resType,ssType,phi,psi))
        appendDeepByKeys(valuesByEntrySsAndResType, phi, entryId, ssType,resType,'phi' )
        appendDeepByKeys(valuesByEntrySsAndResType, psi, entryId, ssType,resType,'psi' )

    (Cav, Csd, _Cn) = getRescaling(valuesByEntrySsAndResType)
#    (Cav, Csd) = ( 1.0, 1.0 )
    
    for ssType in valuesBySsAndResType.keys():
        for resType in valuesBySsAndResType[ssType].keys():
            hist2d, _xedges, _yedges = histogram2d(
                valuesBySsAndResType[ssType][resType]['psi'], 
                valuesBySsAndResType[ssType][resType]['phi'], 
                bins = binCount, 
                range= hrange)
            hist2d = zscaleHist( hist2d, Cav, Csd )
            setDeepByKeys( histBySsAndResType, hist2d, ssType, resType )
#            NTdebug('hist2d ssType, resType: %s %s\n%s' % (ssType, resType, hist2d))
    
    for ssType in valuesBySsAndResType.keys():
        phi = []
        psi = []
        for resType in valuesBySsAndResType[ssType].keys():
            if resType == 'PRO' or resType == 'GLY':
                continue
            phi += valuesBySsAndResType[ssType][resType]['phi']
            psi += valuesBySsAndResType[ssType][resType]['psi']
        hist2d, _xedges, _yedges = histogram2d(
            psi, # Note that the x is the psi for some stupid reason,
            phi, # otherwise the imagery but also the [row][column] notation is screwed.
            bins = binCount, 
            range= hrange)
        hist2d = zscaleHist( hist2d, Cav, Csd )
        setDeepByKeys( histBySsAndCombinedResType, hist2d, ssType )

    phi = []
    psi = []
    for ssType in valuesBySsAndResType.keys():
        for resType in valuesBySsAndResType[ssType].keys():
            if resType == 'PRO' or resType == 'GLY':
                continue
            phi += valuesBySsAndResType[ssType][resType]['phi']
            psi += valuesBySsAndResType[ssType][resType]['psi']
#    NTdebug('total number of residues B: %d' % len(psi))
    hist2d, _xedges, _yedges = histogram2d(
        psi, # Note that the x is the psi for some stupid reason,
        phi, # otherwise the imagery but also the [row][column] notation is screwed.
        bins = binCount, 
        range= hrange)
    hist2d = zscaleHist( hist2d, Cav, Csd )
    sumHistCombined = sum(sum( hist2d ))
    NTdebug('histCombined elements: %.0f' % sumHistCombined)

    
    dbase_file_abs_name = os.path.join( pluginDataDir, dbase_file_name )
    dbase = shelve.open( dbase_file_abs_name )
    dbase[ 'histCombined' ]               = hist2d
    dbase[ 'histBySsAndCombinedResType' ] = histBySsAndCombinedResType
    dbase[ 'histBySsAndResType' ]         = histBySsAndResType
    dbase.close()

def zscaleHist( hist2d, Cav, Csd ):
    return (hist2d - Cav) / Csd

def getValueFromHistogramUsingInterpolation( hist, v0, v1):
    """Returns the value from the bin pointed to by v0,v1.
    """
    tx = ogrid[ v0:v0:1j, v1:v1:1j ]
    interpolatedValueArray = interpn_linear( hist, tx, bins )
    interpolatedValue = interpolatedValueArray[ 0, 0 ]
    NTdebug( 'tx: %-40s bins[1]: \n%s \nhist: \n%s\n%s' % ( tx, bins[1], hist, interpolatedValue ))
    return interpolatedValue
    
def getRescaling(valuesByEntrySsAndResType):
    '''Use a jack knife technique to get an estimate of the average and sd over all entry) scores.
    http://en.wikipedia.org/wiki/Resampling_%28statistics%29#Jackknife
    '''            
    C = NTlist()
    for entryId in valuesByEntrySsAndResType.keys():
        histBySsAndResTypeExcludingEntry = getSumHistExcludingEntry( valuesByEntrySsAndResType, entryId)
        z = NTlist()
        for ssType in valuesByEntrySsAndResType[ entryId ].keys():
            for resType in valuesByEntrySsAndResType[ entryId ][ssType].keys():
                angleDict =valuesByEntrySsAndResType[  entryId ][ssType][resType]
                angleList0 = angleDict[ 'phi' ]
                angleList1 = angleDict[ 'psi' ]
                for i in range(len(angleList0)):
                    his = getDeepByKeys(histBySsAndResTypeExcludingEntry,ssType,resType)
                    if not his: # when testing not all residues are present in smaller sets.
                        continue 
                    zi = getValueFromHistogramUsingInterpolation( 
                        histBySsAndResTypeExcludingEntry[ssType][resType], 
                        angleList0[i], angleList1[i])
                    z.append( zi )
        (av, _sd, _n) = z.average()
        NTdebug("For entry %s found av,sd,n: %s" %(entryId,(av, _sd, _n)))
        C.append( av )
    (Cav, Csd, Cn) = C.average()
    NTdebug("Overall found av,sd,n: " + `C.average()`)
    return (Cav, Csd, Cn)


def getSumHistExcludingEntry( valuesByEntrySsAndResType,  entryIdToExclude):
    hrange = (xRange, yRange)
    histBySsAndResTypeExcludingEntry = {}
    result = {}

    for entryId in valuesByEntrySsAndResType.keys():
        if entryId == entryIdToExclude:
            continue
        valuesBySsAndResType = valuesByEntrySsAndResType[entryId]
        for ssType in valuesBySsAndResType.keys():
            for resType in valuesBySsAndResType[ssType].keys():
                angleList0 = valuesBySsAndResType[ssType][resType]['phi']
                angleList1 = valuesBySsAndResType[ssType][resType]['psi']
                appendDeepByKeys(result,angleList0,ssType,resType,'phi')
                appendDeepByKeys(result,angleList1,ssType,resType,'psi')
        
        
    for ssType in result.keys():
        for resType in result[ssType].keys():
            angleList0 = result[ssType][resType]['phi']
            angleList1 = result[ssType][resType]['psi']
            NTdebug( 'entry: %s ssType %s resType %s angleList0 %s' % (
                entryId, ssType, resType, angleList0 ))
            hist2d, _xedges, _yedges = histogram2d(
                angleList1, # think rows (y)
                angleList0, # think columns (x)
                bins = binCount, 
                range= hrange)
            setDeepByKeys( histBySsAndResTypeExcludingEntry, hist2d, ssType, resType )

    return histBySsAndResTypeExcludingEntry


    
#def getValueFromHistogram( hist, angle0, angle1):
#    pass

def ramachandranPlot(hist, titleStr):
#    extent = (range[0][0],range[0][1],range[1][0],range[1][1])
    sumHist = sum(sum( hist ))
    maxHist = amax(amax( hist ))
#    vmax = maxHist # Focus on low density regions? 
#    norm = colors.Normalize(vmin=0, vmax=vmax)
    NTdebug('hist sumHist, max: %12s %5.0f %5.0f' % (titleStr,sumHist, maxHist))
    levels = nx.arange(maxHist*0.05, maxHist*0.5+1, maxHist*0.1)    
    ps = NTplotSet() # closes any previous plots
    ps.hardcopySize = [600,600]
#    NTdebug( 'plotparams1: %r' % plotparams1)
#    NTdebug( 'xRange: %r' % `xRange`)
    xTicks = range(int(plotparams1.min), int(plotparams1.max+1), plotparams1.ticksize)
    yTicks = range(int(plotparams2.min), int(plotparams2.max+1), plotparams2.ticksize)
    plot = NTplot( title  = titleStr,
      xRange = xRange,
      xTicks = xTicks,
      xLabel = dihedralName1,
      yRange = yRange,
      yTicks = yTicks,
      yLabel = dihedralName2)
    ps.addPlot(plot)

#    x = nx.arange(plotparams1.min, plotparams1.max+0.01, binSize)
#    y = nx.arange(plotparams2.min, plotparams2.max+0.01, binSize)
#    X, Y = meshgrid(x, y)
    Z = hist
    extent = xRange + yRange
#    NTdebug("Covering extent: " +`extent`)
    im = imshow( Z, 
#            interpolation='bilinear', 
            interpolation = 'nearest',
            origin='lower',
            extent=extent )
#    im.set_norm(norm)

#    cset1 = contourf(X, Y, Z, levels,
#                            cmap=cm.get_cmap('jet', len(levels)-1),
#                            )

#    cset1 = contourf(X, Y, Z, levels, 
#        cmap=cm.get_cmap('jet', len(levels)-1), 
#        origin='lower')
    cset2 = contour(Z, levels,
        colors = 'black',
        hold='on',
        extent=extent,
        origin='lower')
    for c in cset2.collections:
        c.set_linestyle('solid')
#    cset = contour(Z, cset1.levels, hold='on', colors = 'black',
#            origin='lower', 
#            extent=extent)
    colorbar(im)
#    colorbar(cset2)
    # It is easier here to make a separate call to contour than
    # to set up an array of colors and linewidths.
    # We are making a thick green line as a zero contour.
    # Specify the zero level as a tuple with only 0 in it.
#    colorbar(cset1)
#    ps.show()
    ps.hardcopy('Ramachandran_%s.png' % titleStr)

def ramachandranZPlotTest(hist, titleStr):
    ps = NTplotSet() # closes any previous plots
    ps.hardcopySize = [400,400]
#    NTdebug( 'plotparams1: %r' % plotparams1)
#    NTdebug( 'xRange: %r' % `xRange`)
    xTicks = range(int(plotparams1.min), int(plotparams1.max+1), plotparams1.ticksize)
    yTicks = range(int(plotparams2.min), int(plotparams2.max+1), plotparams2.ticksize)
    plot = NTplot( 
      title  = titleStr,
      xRange = xRange,
      xTicks = xTicks,
      xLabel = dihedralName1,
      yRange = yRange,
      yTicks = yTicks,
      yLabel = dihedralName2)
    ps.addPlot(plot)
#    kwds = {
#      'left': 0.0,   # the left side of the subplots of the figure
#      'right': 1.0,    # the right side of the subplots of the figure
#      'bottom': 0.0,   # the bottom of the subplots of the figure
#      'top': 1.0,      # the top of the subplots of the figure
#            }
#    ps.subplotsAdjust(**kwds)    
#    X, Y = meshgrid(x, y)
#    extent = xRange + yRange
    plot.ramachandranZPlot( hist )
    axis('off')
    ps.hardcopy('RamachandranZ_%s.png' % titleStr)

def testPlot():
    dbase = shelve.open( dbase_file_name )
    histCombined               = dbase[ 'histCombined' ]
#    histBySsAndResType         = dbase[ 'histBySsAndResType' ]
#    histBySsAndCombinedResType = dbase[ 'histBySsAndCombinedResType' ]
    dbase.close()

#    for ssType in  'E','H',' ':
#        for resType in histBySsAndResType[ssType].keys():
#            titleStr = ssType + '_' + resType
#            hist = histBySsAndResType[ssType][resType]
#            ramachandranZPlot(hist, titleStr)
#            
#    for ssType in  'E','H',' ':
#        titleStr = ssType + '_ALL'
#        hist = histBySsAndCombinedResType[ssType]
#        ramachandranZPlot(hist, titleStr)

#    ramachandranPlot(histCombined, 'ALL_ALL')
    ramachandranZPlotTest(histCombined, 'ALL_ALL')
             
if __name__ == '__main__':
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    main()
#    testPlot()