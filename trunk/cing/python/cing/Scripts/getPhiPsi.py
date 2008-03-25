"""
Read certain PDB files for their backbone dihedrals. 
"""
from cing import cingDirTestsTmp
from cing import cingPythonCingDir
from cing import verbosityDebug
from cing import verbosityOutput
from cing import verbosityWarning
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTmessageNoEOL
from cing.Libs.NTutils import SetupError
from cing.Scripts.localConstants import pdbz_dir
from cing.core.classes import Project
from gzip import GzipFile
import cing
import os
import string
#import cProfile
#import pstats

START_ENTRY_ID = 0
MAX_ENTRIES_TODO = 20
def main():
    if os.chdir(cingDirTestsTmp):
        raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)
    
    resultsFileName = 'phipsi_wi_db.csv'
    resultsFile = file(resultsFileName, 'wa') # appending 
    
    chainGangFileName = os.path.join(cingPythonCingDir, 'Scripts', 'data', 'PDB.LIS')
    chainGangFile = file(chainGangFileName, 'r')
    entryCodeList = []
    chainCodeList = []
    for line in chainGangFile.readlines():
        entryCode = string.lower( line[0:4] )
        chainCode =               line[4:5]
        entryCodeList.append( entryCode )
        chainCodeList.append( chainCode )
    lastEntry = min(len(entryCodeList), START_ENTRY_ID+MAX_ENTRIES_TODO)
    entryCodeList = entryCodeList[START_ENTRY_ID:lastEntry]

#    entryCode = '1n62'
#    entryCode = '1brv'
#    entryCodeList = [ entryCode ]
#    entryCodeList = [ '1ai0' ]
#    chainCodeList = [ 'A' ]

    
    NTmessage('doing %04d entries: %s' % (len(entryCodeList), entryCodeList ))  
    
    i = 0
    for entryCode in entryCodeList:
        chainCode = chainCodeList[i]
        i+=1
        char23 = entryCode[1:3]
        pdbFileName = os.path.join(pdbz_dir, char23, 'pdb'+entryCode+'.ent')
        pdbFileNameZipped = pdbFileName+'.gz'
        if not os.path.exists(pdbFileNameZipped):
            NTdebug("%4s Skipping because no pdb file: %s" % ( entryCode, pdbFileNameZipped ))
            continue
        
        localPdbFileName = entryCode+".pdb"
        inF = GzipFile(pdbFileNameZipped, 'rb');
        s=inF.read()
        inF.close()
        outF = file(localPdbFileName, 'wb');
        outF.write(s)
        outF.close()
        
        project = Project.open( entryCode, status='new' )
        if project.removeFromDisk():
            NTerror("Failed to remove project from disk for entry: ", entryCode)
        project = Project.open( entryCode, status='new' )
        project.initPDB( pdbFile=localPdbFileName, convention = 'BMRB' )
        os.unlink(localPdbFileName)
        project.procheck(createPlots=False, runAqua=False)                   
        
        NTdebug('Doing entry %s chain code: %s' % (entryCode,chainCode) )
        
        strSum = ''
        for chain in project.molecule.allChains():
            if chain.name != chainCode:
                NTdebug('Skipping chain in: entry %s for chain code: %s' % (entryCode,chain.name) )
                continue

            for res in chain.allResidues():
                if not (res.has_key('PHI') and res.has_key('PSI')):
                    NTdebug('Skipping residue without backbone angles complete in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
                    continue
                if not res.PHI:
                    NTdebug('Skipping terminii II on phi etc in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
                    continue
                if not res.PSI:
                    NTdebug('Skipping terminii II on psi etc in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
                    continue
                secStruct = res.getDeepByKeys( 'procheck', 'secStruct' ) 
                if secStruct == None:
                    NTdebug('Skipping because no procheck secStruct in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
                    continue
                secStruct = secStruct[0]
                str = "%s,%s,%-4s,%4d,%1s,%6.1f,%6.1f\n" % (entryCode, chain.name, res.resName, res.resNum, secStruct, res.PHI[0], res.PSI[0] )
                NTmessageNoEOL(str)
                strSum += str # expensive
        if project.removeFromDisk():
            NTerror("Failed to remove project from disk for entry: ", entryCode)
                
        resultsFile.write(strSum)
    resultsFile.close() 
            
if __name__ == "__main__":
    cing.verbosity = verbosityWarning
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
#    cProfile.run('main()', 'fooprof')
#    p = pstats.Stats('fooprof')
#    p.sort_stats('time').print_stats(100)
#    p.sort_stats('cumulative').print_stats(200)
    main()
    # Follow progress with something like:
    # nawk -F',' '{print $1}' $CINGROOT/Tests/data/tmp/phipsi_wi_db.csv | sort -u | wc