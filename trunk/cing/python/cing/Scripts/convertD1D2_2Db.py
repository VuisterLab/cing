"""
Takes a file with dihedral angles values and converts them to a python pickle file
with histograms for (combined) residue and sec. struct. types.

Run:
python $CINGROOT/python/cing/Scripts/convertD1D2_2Db.py
"""

from cing import cingDirData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityOutput
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import appendDeepByKeys
from cing.Libs.NTutils import floatParse
from cing.Libs.NTutils import gunzip
from cing.Libs.NTutils import setDeepByKeys
from cing.Libs.fpconst import isNaN
from cing.PluginCode.required.reqDssp import to3StateUpper
from cing.core.classes import Project
from numpy.lib.index_tricks import ogrid
from numpy.lib.twodim_base import histogram2d
import cPickle
import cing
import csv
import os



file_name_base  = 'cb4ncb4c_wi_db'
# .gz extension is appended in the code.
cvs_file_name   = file_name_base + '.csv'
dbase_file_name = file_name_base + '.dat'
dir_name = os.path.join( cingDirData, 'PluginCode', 'WhatIf' )
cvs_file_abs_name   = os.path.join( dir_name, cvs_file_name )
dbase_file_abs_name = os.path.join( dir_name, dbase_file_name )

binSize   = 10
binCount  = 360/binSize
binCountJ = (binCount + 0)* 1j # used for numpy's 'gridding'.
dihedralName1= "d1"
dihedralName2= "d2"
project     = Project('d1d2Plot')
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
    cvs_file_abs_name_gz = os.path.join(cingDirData, 'PluginCode', 'Whatif', cvs_file_abs_name + '.gz')
    gunzip( cvs_file_abs_name_gz )
    reader = csv.reader(open(cvs_file_abs_name, "rb"), quoting=csv.QUOTE_NONE)
    valuesBySsAndResType       = {}
    histd1d2BySsAndResType         = {}
    histd1d2BySsAndCombinedResType = {}
#    histByCombinedSsAndResType = {}
    valuesByEntrySsAndResType       = {}
    hrange = (xRange, yRange)

    for row in reader:
#        7a3h,A,VAL ,   5,H, -62.8, -52.8
#        7a3h,A,VAL ,   6,H, -71.2, -33.6
#        7a3h,A,GLU ,   7,H, -63.5, -41.6
        (entryId, _chainId, resType, _resNum, ssType, d1, d2) = row
        ssType = to3StateUpper(ssType)[0]
        resType = resType.strip()
        d1 = d1.strip()
        d2 = d2.strip()
        d1 = floatParse(d1)
        d2 = floatParse(d2)
        if isNaN(d1) or isNaN(d2):
            continue
        if not inRange(d1):
            NTerror("d1 not in range for row: %s" % `row`)
            return
        if not inRange(d2):
            NTerror("d2 not in range for row: %s" % `row`)
            return
        appendDeepByKeys(valuesBySsAndResType,      d1,          ssType,resType,'d1' )
        appendDeepByKeys(valuesByEntrySsAndResType, d1, entryId, ssType,resType,'d1' )
        appendDeepByKeys(valuesBySsAndResType,      d2,          ssType,resType,'d2' )
        appendDeepByKeys(valuesByEntrySsAndResType, d2, entryId, ssType,resType,'d2' )
#        NTdebug('resType,ssType,d1: %4s %1s %s' % (resType,ssType,floatFormat(d1, "%6.1f")))
#        NTdebug('resType,ssType,d2: %4s %1s %s' % (resType,ssType,floatFormat(d2, "%6.1f")))
    del(reader) # closes the file handles
    os.unlink(cvs_file_abs_name)

    for ssType in valuesBySsAndResType.keys():
        for resType in valuesBySsAndResType[ssType].keys():
            d1 = valuesBySsAndResType[ssType][resType]['d1']
            d2 = valuesBySsAndResType[ssType][resType]['d2']
            if d1 and d2:
                hist2d, _xedges, _yedges = histogram2d(
                    d2, d1,
                    bins = binCount,
                    range= hrange)
                setDeepByKeys( histd1d2BySsAndResType, hist2d, ssType, resType )

    for ssType in valuesBySsAndResType.keys():
        d1 = []
        d2 = []
        for resType in valuesBySsAndResType[ssType].keys():
            if resType == 'PRO' or resType == 'GLY':
                continue
            d1 += valuesBySsAndResType[ssType][resType]['d1']
            d2 += valuesBySsAndResType[ssType][resType]['d2']
        if d1 and d2:
            hist2d, _xedges, _yedges = histogram2d(
                d2, # Note that the x is the d2 for some stupid reason,
                d1, # otherwise the imagery but also the [row][column] notation is screwed.
                bins = binCount,
                range= hrange)
    #        hist2d = zscaleHist( hist2d, Cav, Csd )
            setDeepByKeys( histd1d2BySsAndCombinedResType, hist2d, ssType )

    # Throws a verbose error message on python 2.6.3 as per issue http://code.google.com/p/cing/issues/detail?id=211
    # Using Pickle instead
#    dbase = shelve.open( dbase_file_abs_name )
#    dbase.close()

    if os.path.exists(dbase_file_abs_name):
        os.unlink(dbase_file_abs_name)
    output = open(dbase_file_abs_name, 'wb')
    dbase = {}
    dbase[ 'histd1d2BySsAndCombinedResType' ] = histd1d2BySsAndCombinedResType
    dbase[ 'histd1d2BySsAndResType' ]         = histd1d2BySsAndResType
    cPickle.dump(dbase, output, -1)
    output.close()



def inRange(a):
    if a < plotparams1.min or a > plotparams1.max:
        return False
    return True

if __name__ == '__main__':
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    main()
#    testEntry()
