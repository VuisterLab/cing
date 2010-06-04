from cing import cingDirData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityOutput
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import appendDeepByKeys
from cing.Libs.NTutils import floatParse
from cing.Libs.NTutils import getEnsembleAverageAndSigmaFromHistogram
from cing.Libs.NTutils import gunzip
from cing.Libs.NTutils import setDeepByKeys
from cing.Libs.fpconst import isNaN
from cing.PluginCode.required.reqDssp import to3StateUpper
from cing.core.molecule import common20AADict
from cing.core.validate import binCount
from cing.core.validate import bins360
from cing.core.validate import plotparams360
from cing.core.validate import xGrid360
from cing.core.validate import yGrid360
from numpy.lib.twodim_base import histogram2d
import cPickle
import cing
import csv
import os


"""
Takes a file with dihedral angles values and converts them to a python pickle file
with histograms for (combined) residue and sec. struct. types.

Janin et al. Conformation of amino acid side-chains in proteins. J Mol Biol (1978)

Using "Table 2. Rotamer library used for crystallographic model building with O" from
Kleywegt et al. Databases in protein crystallography. Acta Crystallogr D Biol
Crystallogr (1998) vol. 54 (Pt 6 Pt 1) pp. 1119-31
"""

file_name_base = 'chi1chi2_wi_db'
# .gz extension is appended in the code.
cvs_file_name = file_name_base + '.csv'
dbase_file_name = file_name_base + '.dat'
dir_name = os.path.join(cingDirData, 'PluginCode', 'WhatIf')
cvs_file_abs_name = os.path.join(dir_name, cvs_file_name)
dbase_file_abs_name = os.path.join(dir_name, dbase_file_name)

dihedralName1 = "CHI1"
dihedralName2 = "CHI2"
plotparams1 = plotparams360
plotparams2 = plotparams360
xRange = (plotparams1.min, plotparams1.max)
yRange = (plotparams2.min, plotparams2.max)
isRange360 = True
xGrid, yGrid = xGrid360, yGrid360
bins = bins360

#pluginDataDir = os.path.join( cingRoot,'PluginCode','data')
os.chdir(cingDirTmp)


def main():
    cvs_file_abs_name_gz = os.path.join(cingDirData, 'PluginCode', 'Whatif', cvs_file_abs_name + '.gz')
    gunzip(cvs_file_abs_name_gz)
    reader = csv.reader(open(cvs_file_abs_name, "rb"), quoting=csv.QUOTE_NONE)
    valuesBySsAndResType = {}
    histJaninBySsAndResType = {}
    histJaninBySsAndCombinedResType = {}
#    histByCombinedSsAndResType = {}
    histJaninCtupleBySsAndResType = {}
    valuesByEntrySsAndResType = {}
    hrange = (xRange, yRange)

    rowCount = 0
    for row in reader:
        rowCount += 1
#        7a3h,A,VAL ,   5,H, -62.8, -52.8
#        7a3h,A,VAL ,   6,H, -71.2, -33.6
#        7a3h,A,GLU ,   7,H, -63.5, -41.6
        (entryId, _chainId, resType, _resNum, ssType, chi1, chi2, _max_bfactor) = row
        ssType = to3StateUpper(ssType)[0]
        resType = resType.strip()
        chi1 = chi1.strip()
        chi2 = chi2.strip()
        chi1 = floatParse(chi1)
        chi2 = floatParse(chi2)
        if isNaN(chi1) or isNaN(chi2):
            continue
        if not inRange(chi1):
            NTerror("chi1 not in range for row: %s" % `row`)
            return
        if not inRange(chi2):
            NTerror("chi2 not in range for row: %s" % `row`)
            return
        if not common20AADict.has_key(resType):
            NTdebug("Residue not in common 20 for row: %s" % `row`)
            rowCount -= 1
            continue

        appendDeepByKeys(valuesBySsAndResType, chi1, ssType, resType, 'chi1')
        appendDeepByKeys(valuesByEntrySsAndResType, chi1, entryId, ssType, resType, 'chi1')
        appendDeepByKeys(valuesBySsAndResType, chi2, ssType, resType, 'chi2')
        appendDeepByKeys(valuesByEntrySsAndResType, chi2, entryId, ssType, resType, 'chi2')
#        NTdebug('resType,ssType,chi1: %4s %1s %s' % (resType,ssType,floatFormat(chi1, "%6.1f")))
#        NTdebug('resType,ssType,chi2: %4s %1s %s' % (resType,ssType,floatFormat(chi2, "%6.1f")))
    del(reader) # closes the file handles
    os.unlink(cvs_file_abs_name)

    for ssType in valuesBySsAndResType.keys():
        for resType in valuesBySsAndResType[ssType].keys():
            chi1 = valuesBySsAndResType[ssType][resType]['chi1']
            chi2 = valuesBySsAndResType[ssType][resType]['chi2']
            if chi1 and chi2:
                hist2d, _xedges, _yedges = histogram2d(
                    chi2, chi1,
                    bins=binCount,
                    range=hrange)
                setDeepByKeys(histJaninBySsAndResType, hist2d, ssType, resType)
                cTuple = getEnsembleAverageAndSigmaFromHistogram(hist2d)
                (c_av, c_sd, hisMin, hisMax) = cTuple
                cTuple += tuple([str([ssType, resType])]) # append the hash keys as a way of id.
                NTdebug("For ssType %s residue type %s found (av/sd/min/max) %8.0f %8.0f %8.0f %8.0f" % (ssType, resType, c_av, c_sd, hisMin, hisMax))
                if c_sd == None:
                    NTdebug('Failed to get c_sd when testing not all residues are present in smaller sets.')
                    continue
                if c_sd == 0.:
                    NTdebug('Got zero c_sd, ignoring histogram. This should only occur in smaller sets. Not setting values.')
                    continue
                setDeepByKeys(histJaninCtupleBySsAndResType, cTuple, ssType, resType)

    for ssType in valuesBySsAndResType.keys():
        chi1 = []
        chi2 = []
        for resType in valuesBySsAndResType[ssType].keys():
            if resType == 'PRO' or resType == 'GLY':
                continue
            chi1 += valuesBySsAndResType[ssType][resType]['chi1']
            chi2 += valuesBySsAndResType[ssType][resType]['chi2']
        if chi1 and chi2:
            hist2d, _xedges, _yedges = histogram2d(
                chi2, # Note that the x is the chi2 for some stupid reason,
                chi1, # otherwise the imagery but also the [row][column] notation is screwed.
                bins=binCount,
                range=hrange)
    #        hist2d = zscaleHist( hist2d, Cav, Csd )
            setDeepByKeys(histJaninBySsAndCombinedResType, hist2d, ssType)

    # Throws a verbose error message on python 2.6.3 as per issue http://code.google.com/p/cing/issues/detail?id=211
    # Using Pickle instead
#    dbase = shelve.open( dbase_file_abs_name )
#    dbase.close()

    if os.path.exists(dbase_file_abs_name):
        os.unlink(dbase_file_abs_name)
    output = open(dbase_file_abs_name, 'wb')
    dbase = {}
    dbase[ 'histJaninBySsAndCombinedResType' ] = histJaninBySsAndCombinedResType
    dbase[ 'histJaninBySsAndResType' ] = histJaninBySsAndResType
    dbase[ 'histJaninCtupleBySsAndResType' ] = histJaninCtupleBySsAndResType
    histJaninCtupleBySsAndResType
    cPickle.dump(dbase, output, 2)
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
