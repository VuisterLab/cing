"""
Takes a file with dihedral angles values and converts them to a python pickle file
with histograms for (combined) residue and sec. struct. types.

Unlike convertD1D2_2Db this script collects the data into a different data structure.

Because of the symmetry between the x/y axes in the d1d2 plot the axes can be compiled
together per residue type vs residue type pair (e.g. Pro (i-1)/Gly(i) and then convoluted  with
another; e.g. Gly(i)/Ala(i+1) to get the d1d2 plot for a triple Pro (i-1)/Gly(i)/Ala(i+1)
Run:
python $CINGROOT/python/cing/Scripts/convertD1D2_2Db2.py
"""

from cing import cingDirData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqDssp import to3StateDssp
from cing.Scripts.getPhiPsiWrapper import BFACTOR_COLUMN
from cing.Scripts.getPhiPsiWrapper import DEFAULT_BFACTOR_PERCENTAGE_FILTER
from cing.Scripts.getPhiPsiWrapper import DEFAULT_MAX_BFACTOR
from cing.Scripts.getPhiPsiWrapper import IDX_COLUMN
from cing.core.database import NTdb
from cing.core.molecule import common20AAList
from cing.core.validate import binCount
from cing.core.validate import bins360
from cing.core.validate import plotparams360
from cing.core.validate import xGrid360
from cing.core.validate import yGrid360
from matplotlib.pyplot import hist
from numpy.ma.core import multiply
from numpy.matrixlib.defmatrix import mat
import cPickle
import csv



file_name_base = 'cb4ncb4c_wi_db'
#file_name_base2 = 'cb4ncb4c_wi_db2'
# .gz extension is appended in the code.
cvs_file_name = file_name_base + '.csv'
dbase_file_name = file_name_base + '.dat'
dir_name = os.path.join(cingDirData, 'PluginCode', 'WhatIf')
cvs_file_abs_name = os.path.join(dir_name, cvs_file_name)
dbase_file_abs_name = os.path.join(dir_name, dbase_file_name)

plotparams1 = plotparams360
plotparams2 = plotparams360
xRange = (plotparams1.min, plotparams1.max)
yRange = (plotparams2.min, plotparams2.max)
isRange360=True
xGrid,yGrid = xGrid360,yGrid360
bins = bins360

os.chdir(cingDirTmp)

lineCountMax = 1000 * 1000 * 100 # in fact only 1 M lines
#lineCountMax = 2 # testing order

def main():
    'See above.'
    cvs_file_abs_name_gz = os.path.join(cingDirData, 'PluginCode', 'Whatif', cvs_file_abs_name + '.gz')
    gunzip(cvs_file_abs_name_gz)
    reader = csv.reader(open(cvs_file_abs_name, "rb"), quoting=csv.QUOTE_NONE)
    valueBySs0AndResTypes = {} # keys are SSi,   RTi, RTi-1
    valueBySs1AndResTypes = {} # keys are SSi-1, RTi, RTi-1
    valueByResTypes = {}
    valueBySs0 = {} # keys are SSi
    valueBySs1 = {} # keys are SSi-1
    histd1CtupleBySsAndResTypes = {}
    value = [] # NB is an array without being keyed.

    histd1BySs0AndResTypes = {} # keys are SSi,   RTi, RTi-1
    histd1BySs1AndResTypes = {} # keys are SSi-1, RTi, RTi-1
    histd1ByResTypes = {}
    histd1BySs0 = {}
    histd1BySs1 = {}


    linesByEntry = {}
    lineCount = 0
    for row in reader:
        lineCount += 1
        if lineCount > lineCountMax:
            break
        entryId = row[0]
        if not linesByEntry.has_key(entryId):
            linesByEntry[ entryId ] = []
        linesByEntry[ entryId ].append( row )

    skippedResTypes = []
    entryIdList = linesByEntry.keys()
    entryIdList.sort()

    # Do some pre filtering.
    for entryId2 in entryIdList:
        lineList = linesByEntry[ entryId2 ]
        for idx,line in enumerate(lineList):
            line.append(idx)
        lineListSorted = NTsort(lineList,BFACTOR_COLUMN,inplace=False)
        # Now throw away the worst 10 % of residues.
        n = len(lineListSorted)
        bad_count = int(round((n * DEFAULT_BFACTOR_PERCENTAGE_FILTER) / 100.))
        to_remove_count = n-bad_count
#        nTmessage("Removing at least %d from %d residues" % (bad_count,n))
        badIdxList = [lineItem[IDX_COLUMN] for lineItem in lineListSorted[to_remove_count:n]]
        iList = range(n)
        iList.reverse()
        for i in iList:
            lineItem = lineList[i]
            max_bfactor = float(lineItem[BFACTOR_COLUMN])
            if max_bfactor > DEFAULT_MAX_BFACTOR:
#                nTdebug('Skipping because max bfactor in dihedral %.3f is above %.3f %s' % (max_bfactor, DEFAULT_MAX_BFACTOR, lineItem))
                del lineList[i] # TODO: check if indexing is still right or we shoot in the foot.
                continue
            if i in badIdxList:
#                nTdebug('Skipping because bfactor worst %.3f %s' % (max_bfactor, lineItem))
                del lineList[i]
                continue
        removed_count = n - len(lineList)
#        nTdebug("Reduced list by %d" % removed_count)
        if removed_count < bad_count:
            nTwarning("Failed to remove at least %d residues" % bad_count)

    for entryId2 in entryIdList:
        prevChainId = None
        prevResType = None
        prevResNum = None
        prevSsType = None
        for _r, row in enumerate(linesByEntry[ entryId2 ]):
    #1zzk,A,GLN ,  17,E, 205.2, 193.6
    #1zzk,A,VAL ,  18,E, 193.6, 223.2
    #1zzk,A,THR ,  19,E, 223.2, 190.1
            (entryId, chainId, resType, resNum, ssType, d1, _d2, _max_bfactor, _idx) = row
            resNum = int(resNum)
            ssType = to3StateDssp(ssType)[0]
            resType = resType.strip()
            db = NTdb.getResidueDefByName( resType )
            if not db:
                nTerror("resType not in db: %s" % resType)
                return
            resType = db.nameDict['IUPAC']
            d1 = d1.strip()
            d1 = floatParse(d1)
            if isNaN(d1):
#                nTdebug("d1 %s is a NaN on row: %s" % (d1,row))
                continue
            if not inRange(d1):
                nTerror("d1 not in range for row: %s" % str(row))
                return

            if not (resType in common20AAList):
    #            nTmessage("Skipping uncommon residue: %s" % resType)
                if not ( resType in skippedResTypes):
                    skippedResTypes.append( resType )
                continue

            if isSibling(chainId, resNum, prevChainId, prevResNum):
                appendDeepByKeys(valueBySs0AndResTypes, d1, ssType,     resType, prevResType)
                appendDeepByKeys(valueBySs1AndResTypes, d1, prevSsType, resType, prevResType)
                appendDeepByKeys(valueByResTypes, d1, resType, prevResType)
                appendDeepByKeys(valueBySs0, d1, ssType)
                appendDeepByKeys(valueBySs1, d1, prevSsType)
                value.append( d1 )
            prevResType = resType
            prevResNum = resNum
            prevChainId = chainId
            prevSsType = ssType

    os.unlink(cvs_file_abs_name)
    nTmessage("Skipped skippedResTypes: %r" % skippedResTypes )
    nTmessage("Got count of values: %r" % len(value) )
    # fill FOUR types of hist.
    # TODO: filter differently for pro/gly
    keyListSorted1 = valueBySs0AndResTypes.keys()
    keyListSorted1.sort()
    for isI in (True, False):
        if isI:
            valueBySs = valueBySs0
            valueBySsAndResTypes = valueBySs0AndResTypes
            histd1BySs = histd1BySs0
            histd1BySsAndResTypes = histd1BySs0AndResTypes
        else:
            valueBySs = valueBySs1
            valueBySsAndResTypes = valueBySs1AndResTypes
            histd1BySs = histd1BySs1
            histd1BySsAndResTypes = histd1BySs1AndResTypes
        for ssType in keyListSorted1:
#            keyListSorted1b = deepcopy(keyListSorted1)
    #        for ssTypePrev in keyListSorted1b:
            d1List = valueBySs[ssType]
            if not d1List:
                nTerror("Expected d1List from valueBySs[%s]" % (ssType))
                continue
            hist1d, _bins, _patches = hist(d1List, bins=binCount, range=xRange)
            nTmessage("Count %6d in valueBySs[%s]" % (sum(hist1d), ssType))
            setDeepByKeys(histd1BySs, hist1d, ssType)

            keyListSorted2 = valueBySsAndResTypes[ssType].keys()
            keyListSorted2.sort()
            for resType in keyListSorted2:
    #            nTmessage("Working on valueBySsAndResTypes for [%s][%s]" % (ssType, resType)) # nice for balancing output verbosity.
                keyListSorted3 = valueBySsAndResTypes[ssType][resType].keys()
                keyListSorted3.sort()
                for prevResType in keyListSorted3:
    #                nTmessage("Working on valueBySsAndResTypes[%s][%s][%s]" % (ssType, resType, prevResType))
                    d1List = valueBySsAndResTypes[ssType][resType][prevResType]
                    if not d1List:
                        nTerror("Expected d1List from valueBySsAndResTypes[%s][%s][%s]" % (ssType, resType, prevResType))
                        continue
                    hist1d, _bins, _patches = hist(d1List, bins=binCount, range=xRange)
    #                nTmessage("Count %6d in valueBySsAndResTypes[%s][%s][%s]" % (sum(hist1d), ssType, resType, prevResType))
                    setDeepByKeys(histd1BySsAndResTypes, hist1d, ssType, resType, prevResType)
            # Now that they are all in we can redo this.
    # Delete the reference -not- the object.
    valueBySs = None
    valueBySsAndResTypes = None
    histd1BySs = None
    histd1BySsAndResTypes = None

    for ssType in keyListSorted1:
        for resType in keyListSorted2:
#            nTmessage("Working on valueBySsAndResTypes for [%s][%s]" % (ssType, resType)) # nice for balancing output verbosity.
            keyListSorted3 = valueBySs0AndResTypes[ssType][resType].keys()
            keyListSorted3.sort()
            for resTypePrev in keyListSorted3:
                keyListSorted4 = keyListSorted3[:] # take a copy
                for resTypeNext in keyListSorted4:
                    hist1 = getDeepByKeys(histd1BySs0AndResTypes, ssType, resType, resTypePrev) # x-axis
                    # This was bug! It needs to be hashed on the ssType of resType -not- on resTypeNext
                    hist2 = getDeepByKeys(histd1BySs1AndResTypes, ssType, resTypeNext, resType) 
                    if hist1 == None:
                        nTdebug('skipping for hist1 is empty for [%s] [%s] [%s]' % (ssType, resTypePrev, resType))
                        continue
                    if hist2 == None:
                        nTdebug('skipping for hist2 is empty for [%s] [%s] [%s]' % (ssType, resType, resTypeNext))
                        continue
                    m1 = mat(hist1,dtype='float')
                    m2 = mat(hist2,dtype='float')
                    m2 = m2.transpose() # pylint: disable=E1101
                    hist2d = multiply(m1,m2)

                    cTuple = getEnsembleAverageAndSigmaHis( hist2d )
                    (_c_av, c_sd, _hisMin, _hisMax) = cTuple #@UnusedVariable
                    cTuple += tuple([str([ssType, resType, resTypePrev, resTypeNext])]) # append the hash keys as a way of id.
#                    nTdebug("For ssType %s residue types %s %s %s found (av/sd/min/max) %8.0f %8.0f %8.0f %8.0f" % (
#                        ssType, resType, resTypePrev, resTypeNext, c_av, c_sd, hisMin, hisMax))
                    if c_sd == None:
                        nTdebug('Failed to get c_sd when testing not all residues are present in smaller sets.')
                        continue
                    if c_sd == 0.:
                        nTdebug('Got zero c_sd, ignoring histogram. This should only occur in smaller sets. Not setting values.')
                        continue
                    setDeepByKeys( histd1CtupleBySsAndResTypes, cTuple, ssType, resType, resTypePrev, resTypeNext)
    # end for isI

    keyListSorted1 = valueByResTypes.keys()
    keyListSorted1.sort()
    for resType in keyListSorted1:
        keyListSorted2 = valueByResTypes[resType].keys()
        keyListSorted2.sort()
        for prevResType in keyListSorted2:
            d1List = valueByResTypes[resType][prevResType]
            if not d1List:
                nTerror("Expected d1List from valueByResTypes[%s][%s]" % (resType, prevResType))
                continue
            hist1d, _bins, _patches = hist(d1List, bins=binCount, range=xRange)
#            nTmessage("Count %6d in valueByResTypes[%s][%s]" % (sum(hist1d), resType, prevResType))
            setDeepByKeys(histd1ByResTypes, hist1d, resType, prevResType)

    histd1, _bins, _patches = hist(value, bins=binCount, range=xRange)
    nTmessage("Count %6d in value" % sum(histd1))
#    setDeepByKeys(histd1, hist1d, resType, prevResType)

    if os.path.exists(dbase_file_abs_name):
        os.unlink(dbase_file_abs_name)
    output = open(dbase_file_abs_name, 'wb')
    dbase = {}
    dbase[ 'histd1BySs0AndResTypes' ] = histd1BySs0AndResTypes # 92 kb uncompressed in the case of ~1000 lines only
    dbase[ 'histd1BySs1AndResTypes' ] = histd1BySs1AndResTypes
    dbase[ 'histd1CtupleBySsAndResTypes' ] = histd1CtupleBySsAndResTypes
    dbase[ 'histd1ByResTypes' ] = histd1ByResTypes # 56 kb
    dbase[ 'histd1BySs0' ] = histd1BySs0 # 4 kb
    dbase[ 'histd1BySs1' ] = histd1BySs1
    dbase[ 'histd1' ] = histd1 #  4 kb

    cPickle.dump(dbase, output, 2)
    output.close()


def inRange(a):
    if a < plotparams1.min or a > plotparams1.max:
        return False
    return True

def isSibling(chainId, resNum, prevChainId, prevResNum):
    if prevResNum == None:
        return False
    if prevChainId == None:
        return False
    if resNum != prevResNum + 1:
        return False
    if chainId != prevChainId:
        return False
    return True

if __name__ == '__main__':
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    main()
#    testEntry()
