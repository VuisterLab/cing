"""
Read PDB files for their dihedrals; not just phi psi anymore..


cd /Users/jd/tmp/cingTmp/d1d2_wi_db
python $CINGROOT/python/cing/Scripts/getPhiPsi.py 1fsg A
"""
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTmessageNoEOL
from cing.Libs.NTutils import NTzap
from cing.Libs.NTutils import floatFormat
from cing.Libs.NTutils import getDeepByKeysOrDefault
from cing.Libs.NTutils import gunzip
from cing.Libs.NTutils import switchOutput
from cing.Libs.fpconst import NaN
from cing.PluginCode.dssp import DSSP_STR
from cing.PluginCode.procheck import SECSTRUCT_STR
from cing.PluginCode.required.reqYasara import YASARA_STR
from cing.Scripts.getPhiPsiWrapper import Janin
from cing.Scripts.getPhiPsiWrapper import Ramachandran
from cing.Scripts.getPhiPsiWrapper import d1d2
from cing.Scripts.getPhiPsiWrapper import dihedralComboTodo # once executed all code there, hilarious locks until after an hour JFD realized.
from cing.Scripts.localConstants import pdbz_dir
from cing.core.classes import Project
from cing.core.constants import IUPAC
from cing.core.molecule import Chain
from cing.core.molecule import DIHEDRAL_NAME_Cb4C
from cing.core.molecule import DIHEDRAL_NAME_Cb4N
from cing.core.molecule import commonAAList
from matplotlib.cbook import flatten
import cing
import os
import sys

BFACTOR_COLUMN = 7
IDX_COLUMN = 8

if True: # for easy blocking of data, preventing the code to be resorted with imports above.
    switchOutput(False)
    try:
        import yasara
        yasara.info.mode = 'txt'
        yasara.Console('off')
    except:
        switchOutput(True)
        raise ImportWarning(YASARA_STR)
    finally: # finally fails in python below 2.5
        switchOutput(True)
    NTmessage('Using Yasara')

if dihedralComboTodo == Ramachandran:
    DIHEDRAL_NAME_1 = 'PHI'
    DIHEDRAL_NAME_2 = 'PSI'
elif dihedralComboTodo == Janin:
    # Can be called for phi, psi or any other combo like chi1, chi2
    DIHEDRAL_NAME_1 = 'CHI1'
    DIHEDRAL_NAME_2 = 'CHI2'
elif dihedralComboTodo == d1d2:
    DIHEDRAL_NAME_1 = DIHEDRAL_NAME_Cb4N
    DIHEDRAL_NAME_2 = DIHEDRAL_NAME_Cb4C

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

    # Add hydrogens using Yasara
    obj = yasara.LoadPDB(localPdbFileName, center = 'No', correct = 'No', model=1)
#    yasara.CleanAll() # needed for OptHydObj
#    yasara.OptHydObj(obj,method='Yasara')
    yasara.AddHydObj(obj)
    newPdbFileName = entryCode+chainCode+"_hyd.pdb"
    yasara.SavePDB(obj,newPdbFileName,format='IUPAC', transform='No')
    yasara.Clear()


    project = Project.open( entryCode+chainCode, status='new' )
    if project.removeFromDisk():
        NTerror("Failed to remove project from disk for entry: ", entryCode+chainCode)
    project = Project.open( entryCode+chainCode, status='new' )
    project.initPDB( pdbFile=newPdbFileName, convention = IUPAC, nmodels=1 )
    project.runDssp()
    if False:
        os.unlink(localPdbFileName)
        os.unlink(newPdbFileName)

#    project.procheck(createPlots=False, runAqua=False)
#    if not project.dssp():
#        NTerror('Failed DSSP on entry %s chain code: %s' % (entryCode,chainCode) )
#        return True

    NTdebug('Doing entry %s chain code: %s' % (entryCode,chainCode) )

    lineList = []
    idx = -1
    strSum = ''

    for chain in project.molecule.allChains():
        if chain.name != chainCode:
            NTdebug('Skipping chain in: entry %s for chain code: %s' % (entryCode,chain.name) )
            continue

        resList = chain.allResidues()
        for res in resList:
            if res.resName not in commonAAList:
#                NTdebug( "Skipping uncommon residue: %s" % res)
                continue

            if dihedralComboTodo == Ramachandran:
                if not (res.has_key(DIHEDRAL_NAME_1) and res.has_key(DIHEDRAL_NAME_2)):
                    NTdebug('Skipping residue without backbone angles complete in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
                    continue
            elif dihedralComboTodo == Janin:
                if not (res.has_key(DIHEDRAL_NAME_1) or res.has_key(DIHEDRAL_NAME_2)):
                    NTdebug('Skipping residue without any of the requested angles complete in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
                    continue
            elif dihedralComboTodo == d1d2:
                if not res.has_key(DIHEDRAL_NAME_1):
                    NTdebug('Skipping residue because no first requested angle in entry %s for chain code %s residue %s' % (entryCode,chainCode,res))
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

            dihedral1 = res[DIHEDRAL_NAME_1]
            atomList = dihedral1.atoms
            coordinatesList = NTzap(atomList, 'coordinates')
            # reshape resulting: NTlist(NTlist(Coordinate(
#            flatList = map( lambda c: c, flatten(coordinatesList) ) # works but next is nicer
            flatList = [c for c in flatten(coordinatesList)]

            bfactorList = NTzap(flatList,'Bfac')
            max_bfactor = max(bfactorList)
            idx += 1 # starts at 0 when inserted.
            lineItem = [ entryCode, chain.name, res.resName, res.resNum, secStruct, d1_value_str, d2_value_str, max_bfactor, idx ]
            lineList.append(lineItem)
            str = "%s,%s,%-4s,%4d,%1s,%6s,%6s,%6.1f\n" % tuple(lineItem[:IDX_COLUMN])
            NTmessageNoEOL(str)
            strSum += str # expensive

#    if project.removeFromDisk():
#        NTerror("Failed to remove project from disk for entry: ", entryCode)
    if not project.save():
        NTerror("Failed to save project to disk for entry: " + entryCode)

    file_name_base = (DIHEDRAL_NAME_1+DIHEDRAL_NAME_2).lower()
    resultsFileName = file_name_base + '_wi_db_%s.csv' % ( entryCode+chainCode )
    resultsFile = file(resultsFileName, 'w')
    resultsFile.flush()
    resultsFile.write(strSum)
#    NTdebug( '\n'+strSum )
    resultsFile.flush()


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    doEntry(*sys.argv[1:])
