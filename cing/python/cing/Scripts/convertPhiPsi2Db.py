from cing import cingDirData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityOutput
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import appendDeepByKeys
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.NTutils import getEnsembleAverageAndSigmaFromHistogram
from cing.Libs.NTutils import gunzip
from cing.Libs.NTutils import setDeepByKeys
from cing.Libs.numpyInterpolation import interpn_linear
from cing.PluginCode.required.reqDssp import to3StateUpper
from cing.core.classes import Project
from numpy.lib.index_tricks import ogrid
from numpy.lib.twodim_base import histogram2d
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
# .gz extension is appended in the code.
cvs_file_name   = file_name_base + '.csv'
dbase_file_name = file_name_base + '.dat'
dir_name = os.path.join( cingDirData, 'PluginCode', 'WhatIf' )
cvs_file_abs_name   = os.path.join( dir_name, cvs_file_name )
dbase_file_abs_name = os.path.join( dir_name, dbase_file_name )

binSize   = 10
binCount  = 360/binSize
binCountJ = (binCount + 0)* 1j # used for numpy's 'gridding'.
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

#pluginDataDir = os.path.join( cingRoot,'PluginCode','data')
os.chdir(cingDirTmp)

      
def main():
    cvs_file_abs_name_gz = cvs_file_abs_name + '.gz'
    gunzip( cvs_file_abs_name_gz )
    reader = csv.reader(open(cvs_file_abs_name, "rb"), quoting=csv.QUOTE_NONE)
    valuesBySsAndResType       = {}
    histRamaBySsAndResType         = {}
    histRamaBySsAndCombinedResType = {}
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
    del(reader) # closes the file handles 
    os.unlink(cvs_file_abs_name)
#    NTdebug('valuesByEntrySsAndResType:\n%s'%valuesByEntrySsAndResType)
#    (Cav, Csd, _Cn) = getRescaling(valuesByEntrySsAndResType)
    (Cav, Csd ) = ( 1.0, 1.0 )
    NTdebug("Overall found av,sd,n: " + `(Cav, Csd)`)
    
    for ssType in valuesBySsAndResType.keys():
        for resType in valuesBySsAndResType[ssType].keys():
            hist2d, _xedges, _yedges = histogram2d(
                valuesBySsAndResType[ssType][resType]['psi'], 
                valuesBySsAndResType[ssType][resType]['phi'], 
                bins = binCount, 
                range= hrange)
#            hist2d = zscaleHist( hist2d, Cav, Csd )
            setDeepByKeys( histRamaBySsAndResType, hist2d, ssType, resType )
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
#        hist2d = zscaleHist( hist2d, Cav, Csd )
        setDeepByKeys( histRamaBySsAndCombinedResType, hist2d, ssType )

    phi = []
    psi = []
    for ssType in valuesBySsAndResType.keys():
        for resType in valuesBySsAndResType[ssType].keys():
            if resType == 'PRO' or resType == 'GLY':
                continue
            phi += valuesBySsAndResType[ssType][resType]['phi']
            psi += valuesBySsAndResType[ssType][resType]['psi']
    
    NTdebug('Total number of residues: %d' % len(psi))
    hist2d, _xedges, _yedges = histogram2d(
        psi, # Note that the x is the psi for some stupid reason,
        phi, # otherwise the imagery but also the [row][column] notation is screwed.
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
    dbase[ 'histRamaCombined' ]               = hist2d
    dbase[ 'histRamaBySsAndCombinedResType' ] = histRamaBySsAndCombinedResType
    dbase[ 'histRamaBySsAndResType' ]         = histRamaBySsAndResType
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
        histRamaBySsAndResTypeExcludingEntry = getSumHistExcludingEntry( valuesByEntrySsAndResType, entryId)
#        NTdebug("histRamaBySsAndResTypeExcludingEntry: %s" % histRamaBySsAndResTypeExcludingEntry )
        z = NTlist()
        for ssType in valuesByEntrySsAndResType[ entryId ].keys():
            for resType in valuesByEntrySsAndResType[ entryId ][ssType].keys():
                angleDict =valuesByEntrySsAndResType[  entryId ][ssType][resType]
                angleList0 = angleDict[ 'phi' ]
                angleList1 = angleDict[ 'psi' ]
                his = getDeepByKeys(histRamaBySsAndResTypeExcludingEntry,ssType,resType)
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
                        histRamaBySsAndResTypeExcludingEntry[ssType][resType], 
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
    histRamaBySsAndResTypeExcludingEntry = {}
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
#            NTdebug( 'entry: %s ssType %s resType %s angleList0 %s' % (
#                entryId, ssType, resType, angleList0 ))
            hist2d, _xedges, _yedges = histogram2d(
                angleList1, # think rows (y)
                angleList0, # think columns (x)
                bins = binCount, 
                range= hrange)
            setDeepByKeys( histRamaBySsAndResTypeExcludingEntry, hist2d, ssType, resType )

    return histRamaBySsAndResTypeExcludingEntry


    
def inRange(a): 
    if a < plotparams1.min or a > plotparams1.max:
        return False
    return True
             
if __name__ == '__main__':
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    main()
