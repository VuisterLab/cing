"""
Read PDB files for their dihedrals.
"""
from cing import verbosityDebug
from cing import verbosityOutput
from cing import verbosityWarning
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import floatFormat
from cing.Libs.NTutils import getDeepByKeysOrDefault
from cing.Libs.NTutils import gunzip
from cing.Libs.fpconst import NaN
from cing.PluginCode.dssp import DSSP_STR
from cing.PluginCode.procheck import SECSTRUCT_STR
from cing.Scripts.getPhiPsiWrapper import doRamachandran # once executed all code there, hilarious locks until after an hour JFD realized.
from cing.Scripts.localConstants import pdbz_dir
from cing.core.constants import IUPAC
from cing.core.classes import Project
from cing.core.molecule import Chain
import cing
import os
import sys
#from cing.core.constants import NAN_FLOAT


# Can be called for phi, psi or any other combo like chi1, chi2
DIHEDRAL_NAME_1 = 'CHI1'
DIHEDRAL_NAME_2 = 'CHI2'

if doRamachandran:
    DIHEDRAL_NAME_1 = 'PHI'
    DIHEDRAL_NAME_2 = 'PSI'

def doEntry( entryCode, chainCode ):
    char23 = entryCode[1:3]
    pdbFileName = os.path.join(pdbz_dir, char23, 'pdb'+entryCode+'.ent')
    pdbFileNameZipped = pdbFileName+'.gz'
    if not os.path.exists(pdbFileNameZipped):
        NTerror("%4s Skipping because no pdb file: %s" % ( entryCode, pdbFileNameZipped ))
        return True

    if Chain.isNullValue(chainCode):
        NTerror("didn't expect null value for chain")
        return True

    gunzip(pdbFileNameZipped)
    localPdbFileName = entryCode+chainCode+".pdb"
    os.rename(pdbFileName, localPdbFileName)

    project = Project.open( entryCode+chainCode, status='new' )
    if project.removeFromDisk():
        NTerror("Failed to remove project from disk for entry: ", entryCode+chainCode)
    project = Project.open( entryCode+chainCode, status='new' )
    project.initPDB( pdbFile=localPdbFileName, convention = IUPAC )
    os.unlink(localPdbFileName)
#    project.procheck(createPlots=False, runAqua=False)
#    if not project.dssp():
#        NTerror('Failed DSSP on entry %s chain code: %s' % (entryCode,chainCode) )
#        return True

    NTdebug('Doing entry %s chain code: %s' % (entryCode,chainCode) )

    strSum = ''
    for chain in project.molecule.allChains():
        if chain.name != chainCode:
            NTdebug('Skipping chain in: entry %s for chain code: %s' % (entryCode,chain.name) )
            continue

        for res in chain.allResidues():
#            NTdebug( "Considering: %s,%s,%-4s,%4d" % (entryCode, chain.name, res.resName, res.resNum))
            if doRamachandran:
                if not (res.has_key(DIHEDRAL_NAME_1) and res.has_key(DIHEDRAL_NAME_2)):
                    NTdebug('Skipping residue without backbone angles complete in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
                    continue
            else:
                if not (res.has_key(DIHEDRAL_NAME_1) or res.has_key(DIHEDRAL_NAME_2)):
                    NTdebug('Skipping residue without any of the requested angles complete in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
                    continue
            secStruct = res.getDeepByKeys( DSSP_STR, SECSTRUCT_STR)
            if secStruct == None:
                NTdebug('Skipping because no dssp secStruct in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
                continue
            secStruct = secStruct[0]
            # Make sure we always have something to hold onto.
            d1_value_list = getDeepByKeysOrDefault( res, [ NaN ], DIHEDRAL_NAME_1)
            d2_value_list = getDeepByKeysOrDefault( res, [ NaN ], DIHEDRAL_NAME_2)
            if len( d1_value_list ) == 0:
                d1_value_list = [ NaN ]
            if len( d2_value_list ) == 0:
                d2_value_list = [ NaN ]

            d1_value_str = floatFormat( d1_value_list[0], "%6.1f" ) # counterpart is floatParse
            d2_value_str = floatFormat( d2_value_list[0], "%6.1f" )
            str = "%s,%s,%-4s,%4d,%1s,%6s,%6s\n" % (entryCode, chain.name, res.resName, res.resNum, secStruct,
                d1_value_str, d2_value_str )
#            NTmessageNoEOL(str)
            strSum += str # expensive
    if project.removeFromDisk():
        NTerror("Failed to remove project from disk for entry: ", entryCode)

    file_name_base = (DIHEDRAL_NAME_1+DIHEDRAL_NAME_2).lower()
    resultsFileName = file_name_base + '_wi_db_%s.csv' % ( entryCode+chainCode )
    resultsFile = file(resultsFileName, 'w')
    resultsFile.flush()
    resultsFile.write(strSum)
    NTdebug( '\n'+strSum )
    resultsFile.flush()


if __name__ == "__main__":
    cing.verbosity = verbosityWarning
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    doEntry(*sys.argv[1:])
