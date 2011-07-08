'''
Created on May 25, 2011

@author: Karen Berntsen

This script will load a PDB-file, takes the first model and makes two extra models, one with the Leucines in g+
and one with the Leucines in tr. These three models will be saved as a new PDB-file.
The project will be copied and in the copy, all the models will be deleted and the new PDB-file with the three models
will be imported.

Run as:

'''
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.disk import rmdir
from cing.core.classes import * #@UnusedWildImport
from cing.core.molecule import * #@UnusedWildImport
from yasaramodule import * #@UnusedWildImport
import shutil
import yasara #@UnresolvedImport

def selectBadLeucineList(proj,cv):
#    leucines=[] # String list
    leuList=[]  # Residue object list.
    mol = proj.molecule
    modelCount=len(proj.models)
    leuSel=mol.residuesWithProperties('LEU')
    for leu in leuSel:
        chi1cv  = getDeepByKeysOrAttributes(leu, CHI1_STR, CV_STR)
        chi2cv  = getDeepByKeysOrAttributes(leu, CHI2_STR, CV_STR)
        chi1cav = getDeepByKeysOrAttributes(leu, CHI1_STR, CAV_STR)
        chi2cav = getDeepByKeysOrAttributes(leu, CHI2_STR, CAV_STR)
        if chi1cv == None or chi2cv == None:
            NTmessage("Skipping Leu residues without both chi: " + str(leu))
            continue
        NTdebug("Looking at %s chi1/2: cav: %8.3f %8.3f cv: %8.3f %8.3f" % (leu, chi1cav, chi2cav, chi1cv, chi1cv))
        if chi1cav < 0 or chi2cav < 0: # JFD adding error checking.
            NTcodeerror("Code assumed the dihedral circular averages are always positive but exception found for leu: " % str(leu))
            return None
        if chi1cav>125 and chi2cav>245 and chi1cv<cv and chi2cv<cv:
#            leucines.append(str(leu.resNum))
            leuList.append(leu)
        elif proj.name.startswith('1brv'):
            NTdebug("For testing purposes all 1brv leu are included.")
            leuList.append(leu)
        # end if
    # end for
    # WARNING: Special case. For this project also leu618 is taken
    if proj.name.startswith('H2_2Ca'):
        NTdebug("For initial study purposes leu618 is additionally included.")
        leuList.append(leuSel[4])
#    leucines.append(str(leuSel[4].resNum))
    NTmessage('Found wrong leucines: ' + str(leuList))
    return leuList,modelCount
# end def

def copyProject(proj_path,proj_name,prl_name):
    locIn  = '%s/%s.cing'%(proj_path,proj_name)
    locOut = '%s/%s.cing'%(proj_path,prl_name)
    NTdebug("Copying project from %s to %s" % (locIn, locOut))
    shutil.copytree(locIn,locOut)
    NTmessage('Project has been copied')
# end def

def rotating(proj_path,prl_name,molec_name,leuList,modelCount):
    """
    load original pdb
    Soup needs to be empty when starting?
    Return True on error.
    """
    pdb_path='%s/%s.cing/Export/PDB/%s.pdb'%(proj_path,prl_name,molec_name)
    if not os.path.exists(pdb_path):
        NTerror("Failed to find input for Yasara: %s" % pdb_path)
        return True
    #CHI1=[-60,180]
    #CHI1=[-60,-49,-41,-48,-53,-63,-75,-79,-78,-70,180,-169,-163,-162,-170,180,171,168,166,173]
    CHI1=[-60,-60,-41,-53,-75,-78,180,-169,-162,180,168,173]
    #CHI2=[180,60]
    #CHI2=[-165,-173,180,169,161,154,157,167,180,-171,79,75,68,60,53,49,54,60,69,73]
    CHI2=[180,-165,180,161,157,180,60,75,60,49,60,73]
    if prl_name.startswith('1brv'):
        CHI1=[-60,-53,180,173]
        CHI2=[180,161,60,73]
    lc=len(CHI1)
    for i in range(lc):#number of different chi1/chi2 combinations
        yasara.LoadPDB(pdb_path)
    NTmessage('Rotating Leucines with Yasara:')
    for i in range(lc): # ten conformations
        for j in range(len(leuList)): # zero or more leu
            leu = leuList[j]
            resNumber = leu.resNum
            chainId = leu._parent.name
            res='Res LEU %s Mol %s Obj %s-%s'%(resNumber,chainId,str(modelCount*i+1),str(modelCount*(i+1)))
            yasara.Dihedral('N  %s'%res,'CA %s'%res,'CB %s'%res,'CG  %s'%res,bound='Yes',set=CHI1[i])
            yasara.Dihedral('CA %s'%res,'CB %s'%res,'CG %s'%res,'CD1 %s'%res,bound='Yes',set=CHI2[i])
    yasara.SavePDB('objects 1-%s'%(lc*modelCount),'%s/%s'%(proj_path,prl_name),format='IUPAC',transform='No')
# end def

def deleteDirs(proj_path,proj_name,molec_name):
    deldirlist=['Dssp','Macros','Procheck','Queeny','Shiftx','Wattos','Whatif','X3DNA','talosPlus']
    for d in deldirlist:
        shutil.rmtree('%s/%s.cing/%s/%s'%(proj_path,proj_name,molec_name,d),[True])
# end def

def changeCoordinates(proj_path,prl_name):
    'Return True on error.'
    prl = Project.open('%s/%s'%(proj_path,prl_name),status = 'old')
    molec=prl.molecule
    molec.initCoordinates()
    molec.importFromPDB('%s/%s.pdb'%(proj_path,prl_name),convention='IUPAC')
    prl.save()
# end def

def rotateLeucines(proj_path,proj_name,molec_name,leuList,modelCount):
    'Return True on error.'
    yasara.info.mode = "txt"
    yasara.info.licenseshown = 0
    #yasara.Console('Off')
    prl_name='%s_%s_rotleucines'%(proj_name,str(len(leuList)))
    locOut = '%s/%s.cing'%(proj_path,prl_name)
    if os.path.exists(locOut):
        NTmessage("Removing previously existing directory: %s" % locOut)
        rmdir( locOut )
    copyProject(proj_path,proj_name,prl_name)
    if rotating(proj_path,prl_name,molec_name,leuList,modelCount):
        return True
    deleteDirs(proj_path,proj_name,molec_name)
    if changeCoordinates(proj_path,prl_name):
        return True
    NTmessage("Done with rotateLeucines")
# end def

def runRotateLeucines(runDir, inputArchiveDir, entryId, cv = 0.1):
    'Return True on error.'
    mkdirs( runDir )
    os.chdir(runDir)
    cingFile = os.path.join(inputArchiveDir, entryId + ".cing.tgz")
    if not os.path.exists(cingFile):
        NTerror("The .tgz %s is missing." % cingFile)
        return True
    # end if

    cingDirNew = os.path.join(runDir, entryId + ".cing")
    if os.path.exists(cingDirNew):
        NTmessage("Removing old cing project directory: " + cingDirNew )
        shutil.rmtree( cingDirNew )

    shutil.copy(cingFile, runDir)
    project = Project.open(entryId, status = 'old')
    molecule = project.molecule
    moleculeName = molecule.name
    if not project:
        NTerror('Failed opening project: ' + entryId)
        return True
    # end if
    if not project.export2PDB():
        NTerror('Failed to export2PDB')
        return True
    # end if

    leuList,modelCount = selectBadLeucineList(project,cv)
    if leuList == None:
        NTerror('Failed to selectBadLeucineList')
        return True
    # end if

    if rotateLeucines(runDir, entryId, moleculeName, leuList,modelCount):
        NTerror('Failed to rotateLeucines')
        return True
    # end if
# end def

if __name__ == '__main__':
    # Localize next three lines.
    runDir = os.path.join(cingDirTmp, 'test_RotateLeucinesInYasara')
    inputArchiveDir = os.path.join(cingDirTestsData, "cing")
    entryId = '1brv'

    if runRotateLeucines(runDir, inputArchiveDir, entryId):
        NTerror("Failed runRotateLeucines")
        sys.exit(1)
    # end if
# end if