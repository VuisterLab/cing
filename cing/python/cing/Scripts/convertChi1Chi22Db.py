from cing import cingDirData
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityOutput
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import appendDeepByKeys
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.NTutils import getEnsembleAverageAndSigmaFromHistogram
from cing.Libs.NTutils import gunzip
from cing.Libs.NTutils import setDeepByKeys
from cing.Libs.numpyInterpolation import interpn_linear
from cing.PluginCode.Whatif import DB_RAMCHK
from cing.PluginCode.Whatif import histBySsAndResType
from cing.PluginCode.dssp import DSSP_STR
from cing.PluginCode.dssp import to3StateUpper
from cing.PluginCode.procheck import SECSTRUCT_STR
from cing.core.classes import Project
from cing.core.constants import PDB
from matplotlib.numerix.mlab import amax
from matplotlib.pylab import axis
from matplotlib.pylab import colorbar
from matplotlib.pylab import contour
from matplotlib.pylab import imshow
from numpy.lib.index_tricks import ogrid
from numpy.lib.twodim_base import histogram2d
from pylab import nx
from cing.Libs.NTutils import floatParse
from cing.core.constants import ISNAN
import cing
import csv
import os
import shelve


"""
Takes a file with dihedral angles values and converts them to a python pickle file
with histograms for (combined) residue and sec. struct. types.

Janin et al. Conformation of amino acid side-chains in proteins. J Mol Biol (1978)

Using "Table 2. Rotamer library used for crystallographic model building with O" from
Kleywegt et al. Databases in protein crystallography. Acta Crystallogr D Biol
Crystallogr (1998) vol. 54 (Pt 6 Pt 1) pp. 1119-31
"""

file_name_base  = 'chi1chi2_wi_db'
# .gz extension is appended in the code.
cvs_file_name   = file_name_base + '.csv'
dbase_file_name = file_name_base + '.dat'
dir_name = os.path.join( cingDirData, 'PluginCode', 'WhatIf' )
cvs_file_abs_name   = os.path.join( dir_name, cvs_file_name )
dbase_file_abs_name = os.path.join( dir_name, dbase_file_name )

binSize   = 10
binCount  = 360/binSize
binCountJ = (binCount + 0)* 1j # used for numpy's 'gridding'.
dihedralName1= "CHI1"
dihedralName2= "CHI2"
project     = Project('janinPlot')
plotparams1 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')
plotparams2 = project.plotParameters.getdefault(dihedralName2,'dihedralDefault')
xRange = (plotparams1.min, plotparams1.max)
yRange = (plotparams2.min, plotparams2.max)

# Used for linear interpolation
xGrid,yGrid = ogrid[ plotparams1.min:plotparams1.max:binCountJ, plotparams1.min:plotparams1.max:binCountJ ]
bins = (xGrid,yGrid)

#pluginDataDir = os.path.join( cingRoot,'PluginCode','data')
os.chdir(cingDirTmp)


def main():
    cvs_file_abs_name_gz = cvs_file_abs_name + '.gz'
    gunzip( cvs_file_abs_name_gz )
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
        (entryId, _chainId, resType, _resNum, ssType, chi1, chi2) = row
        ssType = to3StateUpper(ssType)[0]
        resType = resType.strip()
        chi1 = floatParse(chi1)
        chi2 = floatParse(chi2)
        if not ISNAN(chi1):
            if not inRange(chi1):
                NTerror("chi1 not in range for row: %s" % `row`)
                return
            appendDeepByKeys(valuesBySsAndResType,      chi1,          ssType,resType,'chi1' )
            appendDeepByKeys(valuesByEntrySsAndResType, chi1, entryId, ssType,resType,'chi1' )
        if not ISNAN(chi2):
            if not inRange(chi2):
                NTerror("chi2 not in range for row: %s" % `row`)
                return
            appendDeepByKeys(valuesBySsAndResType,      chi2,          ssType,resType,'chi2' )
            appendDeepByKeys(valuesByEntrySsAndResType, chi2, entryId, ssType,resType,'chi2' )
    del(reader) # closes the file handles
    os.unlink(cvs_file_abs_name)
#    NTdebug('valuesByEntrySsAndResType:\n%s'%valuesByEntrySsAndResType)
#    (Cav, Csd, _Cn) = getRescaling(valuesByEntrySsAndResType)
    (Cav, Csd ) = ( 1.0, 1.0 )
    NTdebug("Overall found av,sd,n: " + `(Cav, Csd)`)

    for ssType in valuesBySsAndResType.keys():
        for resType in valuesBySsAndResType[ssType].keys():
            hist2d, _xedges, _yedges = histogram2d(
                valuesBySsAndResType[ssType][resType]['chi2'],
                valuesBySsAndResType[ssType][resType]['chi1'],
                bins = binCount,
                range= hrange)
#            hist2d = zscaleHist( hist2d, Cav, Csd )
            setDeepByKeys( histBySsAndResType, hist2d, ssType, resType )
#            NTdebug('hist2d ssType, resType: %s %s\n%s' % (ssType, resType, hist2d))

    for ssType in valuesBySsAndResType.keys():
        chi1 = []
        chi2 = []
        for resType in valuesBySsAndResType[ssType].keys():
            if resType == 'PRO' or resType == 'GLY':
                continue
            chi1 += valuesBySsAndResType[ssType][resType]['chi1']
            chi2 += valuesBySsAndResType[ssType][resType]['chi2']
        hist2d, _xedges, _yedges = histogram2d(
            chi2, # Note that the x is the chi2 for some stupid reason,
            chi1, # otherwise the imagery but also the [row][column] notation is screwed.
            bins = binCount,
            range= hrange)
#        hist2d = zscaleHist( hist2d, Cav, Csd )
        setDeepByKeys( histBySsAndCombinedResType, hist2d, ssType )

    chi1 = []
    chi2 = []
    for ssType in valuesBySsAndResType.keys():
        for resType in valuesBySsAndResType[ssType].keys():
            if resType == 'PRO' or resType == 'GLY':
                continue
            chi1 += valuesBySsAndResType[ssType][resType]['chi1']
            chi2 += valuesBySsAndResType[ssType][resType]['chi2']

    NTdebug('Total number of residues: %d' % len(chi2))
    hist2d, _xedges, _yedges = histogram2d(
        chi2, # Note that the x is the chi2 for some stupid reason,
        chi1, # otherwise the imagery but also the [row][column] notation is screwed.
        bins = binCount,
        range= hrange)
#    sumHistCombined = sum( hist2d )
#    sumsumHistCombined = sum( sumHistCombined )
    NTdebug('hist2d         : \n%s' % hist2d)
#    NTdebug('sumHistCombined   : %s' % `sumHistCombined`)
#    NTdebug('sumsumHistCombined: %.0f' % sumsumHistCombined)
#    hist2d = zscaleHist( hist2d, Cav, Csd )
#    NTdebug('hist2d scaled  : \n%s' % hist2d)


    dbase = shelve.open( dbase_file_abs_name )
    dbase[ 'histCombined' ]               = hist2d
    dbase[ 'histBySsAndCombinedResType' ] = histBySsAndCombinedResType
    dbase[ 'histBySsAndResType' ]         = histBySsAndResType
    dbase.close()

def zscaleHist( hist2d, Cav, Csd ):
    hist2d -= Cav
    hist2d /= Csd
    return hist2d

def getValueFromHistogramUsingInterpolation( hist, v0, v1):
    """Returns the value from the bin pointed to by v0,v1.
    """
    tx = ogrid[ v0:v0:1j, v1:v1:1j ]
    interpolatedValueArray = interpn_linear( hist, tx, bins )
    interpolatedValue = interpolatedValueArray[ 0, 0 ]
#    NTdebug( 'tx: %-40s bins[1]: \n%s \nhist: \n%s\n%s' % ( tx, bins[1], hist, interpolatedValue ))
    return interpolatedValue



def getRescaling(valuesByEntrySsAndResType):
    '''Use a jack knife technique to get an estimate of the average and sd over all entry) scores.
    http://en.wikipedia.org/wiki/Resampling_%28statistics%29#Jackknife
    '''
    C = NTlist()
    for entryId in valuesByEntrySsAndResType.keys():
        histBySsAndResTypeExcludingEntry = getSumHistExcludingEntry( valuesByEntrySsAndResType, entryId)
#        NTdebug("histBySsAndResTypeExcludingEntry: %s" % histBySsAndResTypeExcludingEntry )
        z = NTlist()
        for ssType in valuesByEntrySsAndResType[ entryId ].keys():
            for resType in valuesByEntrySsAndResType[ entryId ][ssType].keys():
                angleDict =valuesByEntrySsAndResType[  entryId ][ssType][resType]
                angleList0 = angleDict[ 'chi1' ]
                angleList1 = angleDict[ 'chi2' ]
                his = getDeepByKeys(histBySsAndResTypeExcludingEntry,ssType,resType)
                if his == None:
                    NTdebug('when testing not all residues are present in smaller sets.')
                    continue
                (c_av, c_sd) = getEnsembleAverageAndSigmaFromHistogram( his )
#                NTdebug("For entry %s ssType %s residue type %s found (c_av, c_sd) %8.3f %s" %(entryId,ssType,resType,c_av,`c_sd`))
                if c_sd == None:
                    NTdebug('Failed to get c_sd when testing not all residues are present in smaller sets.')
                    continue
                if c_sd == 0.:
                    NTdebug('Got zero c_sd, ignoring histogram. This should only occur in smaller sets.')
                    continue
                for k in range(len(angleList0)):
                    ck = getValueFromHistogramUsingInterpolation(
                        histBySsAndResTypeExcludingEntry[ssType][resType],
                        angleList0[k], angleList1[k])
                    zk = ( ck - c_av ) / c_sd
#                    NTdebug("For entry %s ssType %s residue type %s resid %3d found ck %8.3f zk %8.3f" %(entryId,ssType,resType,k,ck,zk))
                    z.append( zk )
        (av, sd, n) = z.average()
        NTdebug("%4s,%8.3f,%8.3f,%d" %( entryId, av, sd, n))
        C.append( av )
    (Cav, Csd, Cn) = C.average()
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
                angleList0 = valuesBySsAndResType[ssType][resType]['chi1']
                angleList1 = valuesBySsAndResType[ssType][resType]['chi2']
                appendDeepByKeys(result,angleList0,ssType,resType,'chi1')
                appendDeepByKeys(result,angleList1,ssType,resType,'chi2')


    for ssType in result.keys():
        for resType in result[ssType].keys():
            angleList0 = result[ssType][resType]['chi1']
            angleList1 = result[ssType][resType]['chi2']
#            NTdebug( 'entry: %s ssType %s resType %s angleList0 %s' % (
#                entryId, ssType, resType, angleList0 ))
            hist2d, _xedges, _yedges = histogram2d(
                angleList1, # think rows (y)
                angleList0, # think columns (x)
                bins = binCount,
                range= hrange)
            setDeepByKeys( histBySsAndResTypeExcludingEntry, hist2d, ssType, resType )

    return histBySsAndResTypeExcludingEntry



#def getValueFromHistogram( hist, angle0, angle1):
#    pass

def janinPlot(hist, titleStr):
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
    ps.hardcopy('Janin_%s.png' % titleStr)

def janinPlotTest(hist, titleStr):
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
    plot.dihedralComboPlot( hist )
    axis('off')
    ps.hardcopy('JaninZ_%s.png' % titleStr)

def testEntry():
    #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
    entryId = "1brv_1model"
#        entryId = "1tgq_1model"
    convention = PDB

    os.chdir(cingDirTmp)

    project = Project( entryId )
    project.removeFromDisk()
    project = Project.open( entryId, status='new' )
    cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
    pdbFileName = entryId+".pdb"
    pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
    NTdebug("Reading files from directory: " + cyanaDirectory)
    project.initPDB( pdbFile=pdbFilePath, convention = convention )
    if not project.dssp():
        NTerror("Failed to dssp project")
        return True
#        print project.cingPaths.format()
#    self.assertFalse(runWhatif(project))

    project.save()
    # seq:      VPCSTCEGNLACLSLCHIE
    _wiSstype = '  HHHHTT HHHHHH    '
    _pcSstype  = ' hHHHHhThHHHHHHh   '
    i=0
    for res in project.molecule.allResidues():
#        NTdebug(`res`)
#        whatifResDict = res.getDeepByKeys(WHATIF_STR)
#        if not whatifResDict:
#            continue
#        checkIDList = whatifResDict.keys()
#        for checkID in checkIDList:
#            if checkID != RAMCHK_STR:
#                continue
#            valueList = whatifResDict.getDeepByKeys(checkID,VALUE_LIST_STR)
#            qualList  = whatifResDict.getDeepByKeys(checkID,QUAL_LIST_STR)
#            NTdebug("%10s valueList: %-80s qualList: %-80s" % ( checkID, valueList, qualList))
        if not (res.has_key('CHI1') and res.has_key('CHI2')):
            continue
        if not (res.CHI1 and res.CHI2):
            continue

        chi1 = res.CHI1[0]
        chi2 = res.CHI2[0]
#        ssType = wiSstype[i]
#        ssTypeList = to3StateUpper( [pcSstype[i]] )
        ssTypeDsspList = getDeepByKeys(res,DSSP_STR,SECSTRUCT_STR)
        ssTypeList = to3StateUpper( ssTypeDsspList )
        ssType = ssTypeList.getConsensus()
        resType = res.resName
        hist = histBySsAndResType[ssType][resType]
        sumHist = sum(sum( hist ))
        maxHist = amax(amax( hist ))
        c_dbav, s_dbav = getEnsembleAverageAndSigmaFromHistogram( hist )
        Zscore = hist - c_dbav
        Zscore = Zscore / s_dbav
        # Note the reversal of chi1,chi2!
        ck = getValueFromHistogramUsingInterpolation(hist, chi2, chi1)
        zk = ck - c_dbav
        zk /= s_dbav
        ZscoreDB = zk - DB_RAMCHK[0] # av
        ZscoreDB /= DB_RAMCHK[1] # sd

        NTmessage("ssType [%s] resType %s sumHist %4.0f maxHist %4.0f c_dbav %6.1f s_dbav %6.1f ck %6.1f zk %8.3f ZscoreDB %8.3f" % (
            ssType, resType, sumHist, maxHist, c_dbav, s_dbav, ck, zk, ZscoreDB))
        i += 1

def inRange(a):
    if a < plotparams1.min or a > plotparams1.max:
        return False
    return True

if __name__ == '__main__':
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    main()
#    testEntry()
