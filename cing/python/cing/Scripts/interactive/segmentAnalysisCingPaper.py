# python -u $CINGROOT/python/cing/Scripts/interactive/segmentAnalysisCingPaper.py

from cing.Libs.DBMS import getRelationFromCsvFile
from cing.Libs.NTutils import * #@UnusedWildImport

def run():
    relationName =  'nrgcing_ranges'
    fn = os.path.join( '/Users/jd/CMBI/Papers/CING/Data', relationName + '.csv')
    
    nchains = 7363
    nsegments = 0 
    
    r = getRelationFromCsvFile(fn)
    nentries = r.sizeRows()
    columnIdxId = 0
    columnIdxRange = 1
    for rowIdx in range( r.sizeRows()):
        pdb_id = r.getValue( rowIdx, columnIdxId)
        rangeStr = r.getValue( rowIdx, columnIdxRange)
        nTdebug( 'pdb_id:       %s' % pdb_id)
        nTdebug( 'rangeStr:     %s' % rangeStr)
        segmentList = rangeStr.split(',')
        nTdebug( 'segmentList:  %s' % str(segmentList) )
        nsegments += len(segmentList) 
    # end for    
    nsegments_per_chain = ( 1.0 * nsegments ) / nchains
    
    print "nchains:                 %s" % nchains
    print "nentries:                %s" % nentries
    print "nsegments:               %s" % nsegments
    print "nsegments_per_chain:     %s" % nsegments_per_chain
# end def

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug    
    run()
    
#nchains:                 7363
#nentries:                6383
#nsegments:               9953
#nsegments_per_chain:     1.35175879397
    