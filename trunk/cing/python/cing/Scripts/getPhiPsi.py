"""
Read certain PDB files for their backbone dihedrals. 
"""
from cing import verbosityDebug
from cing import verbosityOutput
from cing import verbosityWarning
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Scripts.localConstants import pdbz_dir
from cing.core.classes import Project
from gzip import GzipFile
import sys
import cing
import os

def doEntry( entryCode, chainCode ):
    char23 = entryCode[1:3]
    pdbFileName = os.path.join(pdbz_dir, char23, 'pdb'+entryCode+'.ent')
    pdbFileNameZipped = pdbFileName+'.gz'
    if not os.path.exists(pdbFileNameZipped):
        NTdebug("%4s Skipping because no pdb file: %s" % ( entryCode, pdbFileNameZipped ))
        return True
    
    localPdbFileName = entryCode+chainCode+".pdb"
    inF = GzipFile(pdbFileNameZipped, 'rb');
    s=inF.read()
    inF.close()
    outF = file(localPdbFileName, 'wb');
    outF.write(s)
    outF.close()
    
    project = Project.open( entryCode+chainCode, status='new' )
    if project.removeFromDisk():
        NTerror("Failed to remove project from disk for entry: ", entryCode+chainCode)
    project = Project.open( entryCode+chainCode, status='new' )
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
#            NTmessageNoEOL(str)
            strSum += str # expensive
    if project.removeFromDisk():
        NTerror("Failed to remove project from disk for entry: ", entryCode)
        
    resultsFileName = 'phipsi_wi_db_%s.csv' % ( entryCode+chainCode )
    resultsFile = file(resultsFileName, 'w') 
    resultsFile.flush()
    resultsFile.write(strSum)
    NTdebug( strSum )
    resultsFile.flush()
    
    
  
if __name__ == "__main__":
    cing.verbosity = verbosityWarning
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    doEntry(*sys.argv[1:])
