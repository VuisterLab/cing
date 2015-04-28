'''
Created on May 25, 2011

@author: Karen Berntsen

This script will load a PDB file, takes the first model and makes two extra models, one with the Leucines in g+
and one with the Leucines in trans. These three models will be saved as a new PDB-file.
The project will be copied and in the copy, all the models will be deleted and the new PDB-file with the three models
will be imported.

Run as in test_RotateLeucines.py
'''
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import rmdir
from cing.Scripts.CombineRestraints import CHI1_LIST
from cing.Scripts.CombineRestraints import CHI1_LOW_DEFAULT
from cing.Scripts.CombineRestraints import CHI2_LIST
from cing.Scripts.CombineRestraints import CHI2_UPP_DEFAULT
from cing.Scripts.CombineRestraints import CV_THRESHOLD_SELECTION
from cing.Scripts.CombineRestraints import ROTL_STR
from cing.core.classes import Project
from yasaramodule import * #@UnusedWildImport
import shutil
import yasara #@UnresolvedImport 


def selectBadLeucineList(proj, cv=CV_THRESHOLD_SELECTION, useAll=False):
    '''
    Finds a list of leucine residues that have an average chi 1 and 2 in the forbidden region.
    Return None on error.
    '''
    nTmessage("Starting %s" % getCallerName())
    nTmessage("Finds a list of leucine residues that have an average chi 1 and 2 in the forbidden region.")
    
    leuList = []  # Residue object list.
    mol = proj.molecule
    leuSel = mol.residuesWithProperties('LEU')
    for leu in leuSel:
        chi1cv = getDeepByKeysOrAttributes(leu, CHI1_STR, CV_STR)
        chi2cv = getDeepByKeysOrAttributes(leu, CHI2_STR, CV_STR)
        chi1cav = getDeepByKeysOrAttributes(leu, CHI1_STR, CAV_STR)
        chi2cav = getDeepByKeysOrAttributes(leu, CHI2_STR, CAV_STR)
        if chi1cv == None or chi2cv == None:
            nTmessage("Skipping Leu residues without both chi: " + str(leu))
            continue
        # end if
        nTdebug("Looking at %s chi1/2: cav: %8.3f %8.3f cv: %8.3f %8.3f" % (leu, chi1cav, chi2cav, chi1cv, chi1cv))
        if chi1cav < 0 or chi2cav < 0: # JFD adding error checking.
            nTcodeerror("Code assumed the dihedral circular averages are always positive but exception found for leu: " % str(leu))
            return None
        # end if
        if not leu.hasCoordinates():
            nTmessage("Skipping without coordinates: %s" % leu)
            continue
        # end if
        if useAll or (chi1cav > CHI1_LOW_DEFAULT and chi2cav > CHI2_UPP_DEFAULT and chi1cv < cv and chi2cv < cv):
            leuList.append(leu)
        # end if
    # end for
    nTmessage('Found %s wrong leucines (useAll=%s): %s' % (len(leuList), useAll, str(leuList)))
    return leuList
# end def

def copyProject(proj_path, proj_name, prl_name):
    locIn = '%s/%s.cing' % (proj_path, proj_name)
    locOut = '%s/%s.cing' % (proj_path, prl_name)
    nTdebug("Copying project from %s to %s" % (locIn, locOut))
    shutil.copytree(locIn, locOut)
    nTmessage('Project has been copied')
# end def

def rotating(proj_path, prl_name, molec_name, leuList, modelCount, chi1list=CHI1_LIST, chi2list=CHI2_LIST):
    """
    From a project read the PDB exported file from: 
        %s/%s.cing/Export/PDB/%s.pdb'   % (proj_path,prl_name,molec_name)
    Rotate for each chi1,2 combo each leucine.
    Write to:
        '%s/%s'                         % (proj_path,prl_name)
    Return True on error.
    """
    countChiCombos = len(chi1list)
    countLeu = len(leuList)
    nTmessage("Will rotate (%s times) %s leucines: %s " % ((countChiCombos, countLeu, str(leuList))))
    if countChiCombos != len(chi1list):
        nTerror("Found different lengths between chi 1 and 2 lists")
        return True
    # end if
    pdb_path = '%s/%s.cing/Export/PDB/%s.pdb' % (proj_path, prl_name, molec_name)
    if not os.path.exists(pdb_path):
        nTerror("Failed to find input for Yasara: %s" % pdb_path)
        return True
    # end if
    for i in range(countChiCombos): #number of different chi1/chi2 combinations
        yasara.LoadPDB(pdb_path)
    # end for
    nTmessage('Rotating leucines with Yasara:')
    for i in range(countChiCombos): # ten conformations
        for j in range(countLeu): # zero or more leu
            leu = leuList[j]
            resNumber = leu.resNum
            chainId = leu._parent.name
            modelId = str(modelCount * i + 1)
            res = 'Res LEU %s Mol %s Obj %s-%s' % (resNumber, chainId, modelId, modelId)
# yasara otherwise can throw:
#RuntimeError: YASARA raised error 219: Dihedral angle to set (requested value 300.00 should be in [-180.00..180.00]) out of range.
            chi1 = nTlimitSingleValue(chi1list[i], -180., 180.)
            chi2 = nTlimitSingleValue(chi2list[i], -180., 180.)
            yasara.Dihedral('N  %s' % res, 'CA %s' % res, 'CB %s' % res, 'CG  %s' % res, bound='Yes', set=chi1)
            yasara.Dihedral('CA %s' % res, 'CB %s' % res, 'CG %s' % res, 'CD1 %s' % res, bound='Yes', set=chi2)
        # end for
    # end for
    modelCountOverall = countChiCombos * modelCount
    yasara.SavePDB('objects 1-%s' % modelCountOverall, '%s/%s' % (proj_path, prl_name), format='IUPAC', transform='No')
# end def

def deleteDirs(proj_path, proj_name, molec_name):
    deldirlist = ['Dssp', 'Macros', 'Procheck', 'Queeny', 'Shiftx', 'Wattos', 'Whatif', 'X3DNA', 'talosPlus']
    for d in deldirlist:
        shutil.rmtree('%s/%s.cing/%s/%s' % (proj_path, proj_name, molec_name, d), [True])
# end def

def changeCoordinates(proj_path, prl_name):
    '''
    Load the coordinates from the PDB file into CING project.
    NB: also already saves the project.
    Return True on error.    
    '''
    prl = Project.open('%s/%s' % (proj_path, prl_name), status='old')
    molec = prl.molecule
    molec.initCoordinates()
    molec.importFromPDB('%s/%s.pdb' % (proj_path, prl_name), convention='IUPAC')
    prl.save()
# end def

def rotateLeucines(proj_path, proj_name, molec_name, leuList, modelCount):
    '''
    Create a new project whose name is postfixed with ROTL_STR.
    Return True on error.
    '''
    yasara.info.mode = "txt"
    yasara.info.licenseshown = 0
    #yasara.Console('Off')
    prl_name = '%s_%s' % (proj_name, ROTL_STR)
    locOut = '%s/%s.cing' % (proj_path, prl_name)
    if os.path.exists(locOut):
        nTmessage("Removing previously existing directory: %s" % locOut)
        rmdir(locOut)
    # end if
    copyProject(proj_path, proj_name, prl_name)
    if rotating(proj_path, prl_name, molec_name, leuList, modelCount):
        nTerror("Failed rotating")
        return True
    # end if
    deleteDirs(proj_path, proj_name, molec_name)
    if changeCoordinates(proj_path, prl_name):
        nTerror("Failed changeCoordinates")
        return True
    # end if
    nTmessage("Done with rotateLeucines")
# end def

def runRotateLeucines(runDir, inputArchiveDir, entryId, cv=CV_THRESHOLD_SELECTION, useAll=False, useLeuList = None):
    '''
    Return True on error.
    If useAll is set then all leucines will be rotated.
    '''
    nTmessage("Starting %s" % getCallerName())
    mkdirs(runDir)
    os.chdir(runDir)
    cingFile = os.path.join(inputArchiveDir, entryId + ".cing.tgz")
    if not os.path.exists(cingFile):
        nTerror("The .tgz %s is missing." % cingFile)
        return True
    # end if
    cingDirNew = os.path.join(runDir, entryId + ".cing")
    if os.path.exists(cingDirNew):
        nTmessage("Removing old cing project directory: " + cingDirNew)
        shutil.rmtree(cingDirNew)
    # end if
    cingFileNew = os.path.join(runDir, entryId + ".cing.tgz")
    if cingFile == cingFileNew:
        nTdebug("Skipping copy because there is already a .cing.tgz that will be used.")
    else:
        shutil.copy(cingFile, runDir)
    # end if
    project = Project.open(entryId, status='old') # will work from .cing over .cing.tgz
#    os.remove(cingFileNew)
    if not os.path.exists(cingFileNew):
        nTerror("The .tgz %s is missing." % cingFile)
        return True
    # end if
    molecule = project.molecule
    moleculeName = molecule.name
    if not project:
        nTerror('Failed opening project: ' + entryId)
        return True
    # end if
    if not project.export2PDB():
        nTerror('Failed to export2PDB')
        return True
    # end if
    #### BLOCK BEGIN repeated in test_combineRestraints
    if not useAll and useLeuList:
        leuList = project.decodeResidueList( useLeuList )
        if not leuList:
            nTerror('Failed to decodeResidueList')
            return True
        # end if            
    else:
        leuList = selectBadLeucineList(project, cv, useAll=useAll)
    # end if
    if leuList == None:
        nTerror('Failed to selectBadLeucineList')
        return True
    # end if
    #### BLOCK BEGIN
    modelCount = len(project.models)
    if rotateLeucines(runDir, entryId, moleculeName, leuList, modelCount):
        nTerror('Failed to rotateLeucines')
        return True
    # end if
    project.close(save = True) # Save is already done.
    del project # Garbage collect it out of memory.
# end def

if __name__ == '__main__':
    # Localize next three lines.
    runDir = os.path.join(cingDirTmp, 'test_RotateLeucinesInYasara')
    inputArchiveDir = os.path.join(cingDirTestsData, "cing")
    entryId = '1brv'

    if runRotateLeucines(runDir, inputArchiveDir, entryId):
        nTerror("Failed runRotateLeucines")
        sys.exit(1)
    # end if    
# end if
