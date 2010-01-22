"""
Read PDB files for their dihedrals; not just phi psi anymore..


cd /Users/jd/tmp/cingTmp/d1d2_wi_db
python $CINGROOT/python/cing/Scripts/getPhiPsi.py 1a7S A
"""
from cing import verbosityDebug
from cing import verbosityOutput
from cing import verbosityWarning
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import floatFormat
from cing.Libs.NTutils import getDeepByKeysOrDefault
from cing.Libs.NTutils import gunzip
from cing.Libs.fpconst import NaN
from cing.PluginCode.dssp import DSSP_STR
from cing.PluginCode.procheck import SECSTRUCT_STR
from cing.Scripts.getPhiPsiWrapper import Janin
from cing.Scripts.getPhiPsiWrapper import Ramachandran
from cing.Scripts.getPhiPsiWrapper import d1d2
from cing.Scripts.getPhiPsiWrapper import dihedralComboTodo # once executed all code there, hilarious locks until after an hour JFD realized.
from cing.Scripts.localConstants import pdbz_dir
from cing.core.classes import Project
from cing.core.constants import IUPAC
from cing.core.molecule import Chain
from cing.core.molecule import Dihedral
import cing
import os
import sys

if dihedralComboTodo == Ramachandran:
    DIHEDRAL_NAME_1 = 'PHI'
    DIHEDRAL_NAME_2 = 'PSI'
elif dihedralComboTodo == Janin:
    # Can be called for phi, psi or any other combo like chi1, chi2
    DIHEDRAL_NAME_1 = 'CHI1'
    DIHEDRAL_NAME_2 = 'CHI2'
elif dihedralComboTodo == d1d2:
    DIHEDRAL_NAME_1 = 'Cb4N'
    DIHEDRAL_NAME_2 = 'Cb4C'

range0_360 = [0.0,360.0]

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
    project.runDssp()
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

        resList = chain.allResidues()
        for res in resList:
            triplet = NTlist()
            for i in [-1,0,1]:
                triplet.append( res.sibling(i) )
#            NTdebug( "Considering: %s,%s,%-4s,%4d" % (entryCode, chain.name, res.resName, res.resNum))

            if dihedralComboTodo == Ramachandran:
                if not (res.has_key(DIHEDRAL_NAME_1) and res.has_key(DIHEDRAL_NAME_2)):
                    NTdebug('Skipping residue without backbone angles complete in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
                    continue
            elif dihedralComboTodo == Janin:
                if not (res.has_key(DIHEDRAL_NAME_1) or res.has_key(DIHEDRAL_NAME_2)):
                    NTdebug('Skipping residue without any of the requested angles complete in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
                    continue
            elif dihedralComboTodo == d1d2:
                if None in triplet:
#                    NTdebug( 'Skipping residue without triplet %s' % res)
                    continue
                CA_atms = triplet.zap('CA')
                CB_atms = triplet.zap('CB')
#                print res, triplet, CA_atms, CB_atms
                if None in CB_atms: # skip Gly for now
#                    NTdebug( 'Skipping for absent CB (e.g. HOH & GLY) in triplet %s' % res )
                    continue

                d1 = Dihedral( res, DIHEDRAL_NAME_1, range=range0_360)
                d1.atoms = [CB_atms[0], CA_atms[0], CA_atms[1], CB_atms[1]]
                d1.calculateValues()
                res[DIHEDRAL_NAME_1] = d1 # append dihedral to residue

                d2 = Dihedral( res, DIHEDRAL_NAME_2, range=range0_360)
                d2.atoms = [CB_atms[1], CA_atms[1], CA_atms[2], CB_atms[2]]
                d2.calculateValues()
                res[DIHEDRAL_NAME_2] = d2 # append dihedral to residue

                if not (res.has_key(DIHEDRAL_NAME_1) and res.has_key(DIHEDRAL_NAME_2)):
                    NTdebug('Skipping residue both requested angles complete in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
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
#    NTdebug( '\n'+strSum )
    resultsFile.flush()


if __name__ == "__main__":
    cing.verbosity = verbosityWarning
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    doEntry(*sys.argv[1:])
