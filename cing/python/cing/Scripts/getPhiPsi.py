"""
Read PDB files for their dihedrals; not just phi psi anymore..


cd /Users/jd/tmp/cingTmp
python $CINGROOT/python/cing/Scripts/getPhiPsi.py 1aba A
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import copy
from cing.PluginCode.dssp import DSSP_STR
from cing.PluginCode.procheck import SECSTRUCT_STR
from cing.Scripts.getPhiPsiWrapper import Janin
from cing.Scripts.getPhiPsiWrapper import Ramachandran
from cing.Scripts.getPhiPsiWrapper import d1d2
from cing.Scripts.getPhiPsiWrapper import dihedralComboTodo # once executed all code there, hilarious locks until after an hour JFD realized.
from cing.Scripts.getPhiPsiWrapper import subdir
from cing.Scripts.localConstants import pdbz_dir
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Chain
from cing.core.molecule import commonAAList
from matplotlib.cbook import flatten

# Keep a copy of the CING project.
doSave = False

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

def getLocalPdbFileWithChain(entryCode, chainCode ):
    """Unzips the PDB file from default archive to local directory with the name:
    entryCode+chainCode+".pdb"

    The chainCode may not be the specific null value for chains but it may be None.
    If None, then the outputfilename will be:
    entryCode+".pdb"
    """
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
    if chainCode:
        localPdbFileName = entryCode+chainCode+".pdb"
    else:
        localPdbFileName = entryCode+".pdb"
    os.rename(pdbFileName, localPdbFileName)

def doYasaraAddHydrogens( entryCode, chainCode ):
    """Called from getPhiPsiWrapperYasara"""
    if getLocalPdbFileWithChain(entryCode, chainCode ):
        return True
    # above ensures it exists at this point.
    localPdbFileName = entryCode+chainCode+".pdb"

    import yasara
    yasara.info.mode = 'txt'
    yasara.Console('off')
    NTmessage('Using Yasara on %s' % entryCode)

    # Add hydrogens using Yasara
    obj = yasara.LoadPDB(localPdbFileName, center = 'No', correct = 'No', model=1)
#    yasara.CleanAll() # needed for OptHydObj
#    yasara.OptHydObj(obj,method='Yasara')
    yasara.AddHydObj(obj)
    newPdbFileName = entryCode+chainCode+"_hyd.pdb"
    yasara.SavePDB(obj,newPdbFileName,format='IUPAC', transform='No')
    yasara.Clear()
#    yasara.StopPlugin()
#    yasara.Exit()

    os.unlink(localPdbFileName)

def doYasaraRewritePdb( entryCode ):
    """Called from ipython"""

    os.chdir(cingDirTmp)

    inputDir              = os.path.join(cingDirTestsData, "cyana" )

    pdbFileName = os.path.join(inputDir, entryCode, entryCode+'_org.pdb')
    localPdbFileName = entryCode+"_org.pdb"
    copy(pdbFileName, localPdbFileName)

    import yasara
    yasara.info.mode = 'txt'
    yasara.Console('off')
    NTmessage('Using Yasara on %s' % entryCode)

    # Read all models.
#    obj = yasara.LoadPDB(localPdbFileName, center = 'No', correct = 'No', model=1)
    obj = yasara.LoadPDB(localPdbFileName, center = 'No', correct = 'No')
#    yasara.CleanAll() # needed for OptHydObj
#    yasara.OptHydObj(obj,method='Yasara')
#    yasara.AddHydObj(obj)
    os.unlink(localPdbFileName)

    newPdbFileName = entryCode+".pdb"
#    newPdbFileName = localPdbFileName

    yasara.SavePDB(obj,newPdbFileName,format='IUPAC', transform='No')
    yasara.Clear()
#    yasara.StopPlugin()
#    yasara.Exit()
#    os.unlink(localPdbFileName)

def doEntry( entryCode, chainCode ):
    """Returns True on error"""

    project = Project.open( entryCode+chainCode, status='new' )
    if project.removeFromDisk():
        NTerror("Failed to remove project from disk for entry: ", entryCode+chainCode)
        return True

    project = Project.open( entryCode+chainCode, status='new' )

    if dihedralComboTodo == d1d2:
        pdbFileName = os.path.join(cingDirTmp, subdir, 'pdb_hyd', entryCode+chainCode+"_hyd.pdb")
    else:
        if getLocalPdbFileWithChain(entryCode, chainCode ):
            return True
        # above ensures it exists at this point.
        pdbFileName = entryCode+chainCode+".pdb"

    project.initPDB( pdbFile=pdbFileName, convention = IUPAC, nmodels=1 )
    if dihedralComboTodo != d1d2:
        os.unlink(pdbFileName)
    project.runDssp()

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
            lineItem = ( entryCode, chain.name, res.resName, res.resNum, secStruct, d1_value_str, d2_value_str, max_bfactor )
            lineList.append(lineItem)
            str = "%s,%s,%-4s,%4d,%1s,%6s,%6s,%6.1f\n" % lineItem
            NTmessageNoEOL(str)
            strSum += str # expensive

    if doSave:
        if not project.save():
            NTerror("Failed to save project to disk for entry: " + entryCode)
            return True
    else:
        if project.removeFromDisk():
            NTerror("Failed to remove project from disk for entry: ", entryCode)
            return True

    file_name_base = (DIHEDRAL_NAME_1+DIHEDRAL_NAME_2).lower()
    resultsFileName = file_name_base + '_wi_db_%s.csv' % ( entryCode+chainCode )
    resultsFile = file(resultsFileName, 'w')
    resultsFile.flush()
    resultsFile.write(strSum)
#    NTdebug( '\n'+strSum )
    resultsFile.flush()
    resultsFile.close() # otherwise too many open files error.

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    doEntry(*sys.argv[1:])
