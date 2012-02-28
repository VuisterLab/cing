# python -u $CINGROOT/python/cing/Scripts/interactive/segmentAnalysisCingPaper.py

"""
Result on 2012-02-27:
nentries:                6460
nchains:                 7735
nsegments:               10088
nresidues:               624958
chainsPerEntry:          1.30420168067
segmentsPerEntry:        1.56160990712
segmentsPerChain:        1.30420168067
residuesPerEntry:        96.7427244582
residuesPerChain:        80.7961215255
residuesPerSegments:     61.9506344171
residuesMin:             1
residuesMinEntry:        1g70

1b2i with range A.-4--1,A.1-34,A.36-59,A.61-81 and segment ['A', -4, -1] is 4
1cww with range -3--1,1-97 and segment ['A', -3, -1] is 3
1fhb with range -3--1,1-102 and segment ['A', -3, -1] is 3
1g70 with range A.1-22,B.41-52,B.54,B.60-64,B.66-79 and segment ['B', 54, 54] is 1
1gac with range A.1-4,B.1-4 and segment ['A', 1, 4] is 4
1gac with range A.1-4,B.1-4 and segment ['B', 1, 4] is 4
1go0 with range -2--1,1-97 and segment ['A', -2, -1] is 2
1iio with range -3--1,1-81 and segment ['A', -3, -1] is 3
1kx7 with range A.-2--1,A.1-78 and segment ['A', -2, -1] is 2
1ry3 with range -18--1,1-4,10-40 and segment ['A', 1, 4] is 4
1yo4 with range -2--1,1-70 and segment ['A', -2, -1] is 2
2hac with range A.-3--1,A.1-25,B.-3--1,B.1-25 and segment ['A', -3, -1] is 3
2hac with range A.-3--1,A.1-25,B.-3--1,B.1-25 and segment ['B', -3, -1] is 3
2k2i with range A.102-170,B.647,B.649-660 and segment ['B', 647, 647] is 1
2kei with range A.3-62,B.3-62,C.-1,C.1-22,D.-1,D.1-22 and segment ['C', -1, -1] is 1
2kei with range A.3-62,B.3-62,C.-1,C.1-22,D.-1,D.1-22 and segment ['D', -1, -1] is 1
2kej with range A.2-62,B.2-60,C.-1,C.1-22,D.-1,D.1-22 and segment ['C', -1, -1] is 1
2kej with range A.2-62,B.2-60,C.-1,C.1-22,D.-1,D.1-22 and segment ['D', -1, -1] is 1
2kek with range A.2-61,B.3-59,C.-1,C.1-22,D.-1,D.1-22 and segment ['C', -1, -1] is 1
2kek with range A.2-61,B.3-59,C.-1,C.1-22,D.-1,D.1-22 and segment ['D', -1, -1] is 1
2kla with range -2--1,1-102 and segment ['A', -2, -1] is 2
2knf with range -4--1,1-82 and segment ['A', -4, -1] is 4
2kua with range -4--2,0-164 and segment ['A', -4, -2] is 3
2kym with range A.-2--1,A.1-117,B.-9-6 and segment ['A', -2, -1] is 2
2l0s with range -3--1,1-34,36-57,59-80 and segment ['A', -3, -1] is 3
2lcs with range A.-2--1,A.1-69,B.-7-6 and segment ['A', -2, -1] is 2
2lir with range A.-3--1,A.1-21,A.27-103 and segment ['A', -3, -1] is 3
2lit with range A.-3--1,A.1-102 and segment ['A', -3, -1] is 3
2rnn with range -3--1,1-111 and segment ['A', -3, -1] is 3
2w1o with range A.-1,A.1-66,B.-1,B.1-66 and segment ['A', -1, -1] is 1
2w1o with range A.-1,A.1-66,B.-1,B.1-66 and segment ['B', -1, -1] is 1

The few observed segments above with segment size of 4 or less residues are caused by:

ID  PDB  REMARK
-1- 1b2i Absent residue with residue number zero. This is actually correct. Only the syntax doesn't recognize the 
            the fact that they are in fact consecutive.
-2- 1g70 Discontinuous numbering again for residue without backbone cv. But backbone is continuous so actually ok.
-3- 1gac Chain is only 4 long so included all residues. Weird that this entry is in cingsummary because it seems
            to be too light. It has 24 uncommon residues and just made the cut. Good to exclude from selection
            entry_list_selection by number of residues in cing to be at least 30.
-4- 2k2i B.647 is by itself? Yes the numbering is non-consecutive. Algorithm improved: A.102-170,B.649-660
-5- 2kua -4--2 was too short but improved by changes above.

Only ~30 segments with bad estimates remain but will not be fixed.
"""

from cing.Libs.DBMS import getRelationFromCsvFile
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.molecule import Molecule

def run():
    relationName =  'nrgcing_ranges'
    fn = os.path.join( '/Users/jd/CMBI/Papers/CING/Data', relationName + '.csv')
    
    nentries = 0
    nchains = 0
    nsegments = 0 
    nresidues = 0
    nresiduesMin = 999
    nresiduesMinEntry = None
    r = getRelationFromCsvFile(fn)
    
    columnIdxId = 0
    columnIdxRange = 1
    
    for rowIdx in range(r.sizeRows()):
        if rowIdx >= 200000:
            print "Stopping early."
            break
        # end if
        nentries += 1
        pdb_id = r.getValue( rowIdx, columnIdxId)
        rangeStr = r.getValue( rowIdx, columnIdxRange)
        chain_id = None
#        nTdebug( 'pdb_id:       %s' % pdb_id)
#        nTdebug( 'rangeStr:     %s' % rangeStr)
        startStopLoL = Molecule.ranges2StartStopLoLStatic(rangeStr)
#        nTdebug( 'startStopLoL:  %s' % str(startStopLoL) )
        nsegments += len(startStopLoL)
        for startStopList in startStopLoL:
            residueCount = startStopList[2] - startStopList[1] + 1
            nresidues += residueCount
            if residueCount < nresiduesMin:
                nresiduesMin = residueCount
                nresiduesMinEntry = pdb_id
            # end for
            if residueCount < 5:
                nTdebug( 'residueCount for %s with range %s and segment %s is %s' % ( pdb_id, rangeStr, str(startStopList), residueCount))
            # end for            
            segmentChainId = startStopList[0]
            if segmentChainId != chain_id:
                chain_id = segmentChainId
                nchains += 1
            # end if
        # end for
    # end for    
    
    print "nentries:                %s" % nentries
    print "nchains:                 %s" % nchains
    print "nsegments:               %s" % nsegments
    print "nresidues:               %s" % nresidues
    print "chainsPerEntry:          %s" % (nsegments / float(nchains))
    print "segmentsPerEntry:        %s" % (nsegments / float(nentries))
    print "segmentsPerChain:        %s" % (nsegments / float(nchains))
    print "residuesPerEntry:        %s" % (nresidues / float(nentries))
    print "residuesPerChain:        %s" % (nresidues / float(nchains))
    print "residuesPerSegments:     %s" % (nresidues / float(nsegments))
    print "residuesMin:             %s" % nresiduesMin
    print "residuesMinEntry:        %s" % nresiduesMinEntry
# end def

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug    
    run()
    