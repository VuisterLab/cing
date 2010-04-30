from cing import cingDirData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityOutput
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import appendDeepByKeys
from cing.Libs.NTutils import getEnsembleAverageAndSigmaFromHistogram
from cing.Libs.NTutils import gunzip
from cing.Libs.NTutils import setDeepByKeys
from cing.PluginCode.required.reqDssp import to3StateUpper
from cing.core.molecule import common20AADict
from cing.core.validate import binCount
from cing.core.validate import bins180
from cing.core.validate import inRange
from cing.core.validate import plotparams180
from cing.core.validate import xGrid180
from cing.core.validate import yGrid180
from numpy.lib.twodim_base import histogram2d
import cPickle
import cing
import csv
import os

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

dihedralName1= "PHI"
dihedralName2= "PSI"
plotparams1 = plotparams180
plotparams2 = plotparams180
xRange = (plotparams1.min, plotparams1.max)
yRange = (plotparams2.min, plotparams2.max)
isRange360=False
xGrid,yGrid = xGrid180,yGrid180
bins = bins180

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
    histRamaCtupleBySsAndResType = {}
    valuesByEntrySsAndResType       = {}
    hrange = (xRange, yRange)

    rowCount = 0
    for row in reader:
        rowCount += 1
#        7a3h,A,VAL ,   5,H, -62.8, -52.8
#        7a3h,A,VAL ,   6,H, -71.2, -33.6
#        7a3h,A,GLU ,   7,H, -63.5, -41.6
        (entryId, _chainId, resType, _resNum, ssType, phi, psi, _max_bfactor) = row
        ssType = to3StateUpper(ssType)[0]
        resType = resType.strip()
        phi = float(phi)
        psi = float(psi)
        if not (inRange(phi, isRange360=isRange360) and inRange(psi, isRange360=isRange360)):
            NTerror("phi and/or psi not in range for row: %s" % `row`)
            return
        if not common20AADict.has_key( resType):
            NTdebug("Residue not in common 20 for row: %s" % `row`)
            rowCount -= 1
            continue

        appendDeepByKeys(valuesBySsAndResType, phi, ssType,resType,'phi' )
        appendDeepByKeys(valuesBySsAndResType, psi, ssType,resType,'psi' )
#        NTdebug('resType,ssType,phi,psi: %4s %1s %8.3f %8.3f' % (resType,ssType,phi,psi))
        appendDeepByKeys(valuesByEntrySsAndResType, phi, entryId, ssType,resType,'phi' )
        appendDeepByKeys(valuesByEntrySsAndResType, psi, entryId, ssType,resType,'psi' )
    del(reader) # closes the file handles
    os.unlink(cvs_file_abs_name)
    NTdebug('Total number of included residues including PRO/GLY: %d' % rowCount)
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
            cTuple = getEnsembleAverageAndSigmaFromHistogram( hist2d )
            (c_av, c_sd) = cTuple
            NTdebug("For ssType %s residue type %s found (c_av, c_sd) %8.3f %s" %(ssType,resType,c_av,`c_sd`))
#            NTdebug("xedges %s" % `xedges`)
#            sys.exit(1)
            if c_sd == None:
                NTdebug('Failed to get c_sd when testing not all residues are present in smaller sets.')
                continue
            if c_sd == 0.:
                NTdebug('Got zero c_sd, ignoring histogram. This should only occur in smaller sets. Not setting values.')
                continue
            setDeepByKeys( histRamaCtupleBySsAndResType, cTuple, ssType, resType)

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

    NTdebug('Total number of residues without PRO/GLY: %d' % len(psi))
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

    if os.path.exists(dbase_file_abs_name):
        os.unlink(dbase_file_abs_name)
#    dbase = shelve.open( dbase_file_abs_name )
    output = open(dbase_file_abs_name, 'wb')
#    dbase = {'bar':'milky'}
    dbase = {}
    # Pickle the list using the highest protocol available.
    dbase[ 'histRamaCombined' ]               = hist2d
    dbase[ 'histRamaBySsAndCombinedResType' ] = histRamaBySsAndCombinedResType
    dbase[ 'histRamaBySsAndResType' ]         = histRamaBySsAndResType
    dbase[ 'histRamaCtupleBySsAndResType' ]   = histRamaCtupleBySsAndResType
#    pickle.dump(dbase, output, -1)
#    pickle.dump(dbase, output)
    cPickle.dump(dbase, output, -1) # now the same as the other 2 scripts.
    # If the protocol parameter is omitted, protocol 0 is used.
    # If protocol is specified as a negative value or HIGHEST_PROTOCOL, the highest protocol version will be used.

    output.close()
#    dbase.close()

if __name__ == '__main__':
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    main()
