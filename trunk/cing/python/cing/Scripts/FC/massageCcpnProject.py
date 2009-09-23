"""
With help from Wim Vranken.
For example changing the MS name from 2kkx to ET109AredOrg

# Execute like e.g.:
# python -u $CINGROOT/python/cing/Scripts/FC/massageCcpnProject.py ET109AredOrg ET109AredUtrecht
if the input project is in cwd.

Most functionality is hard-coded here so be careful reading the actual code.
"""
from ccpnmr.format.converters import PseudoPdbFormat
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from glob import glob
from memops.general.Io import loadProject
from memops.general.Io import saveProject
import Tkinter
import cing
import os
import sys

__author__ = "Wim Vranken <wim@ebi.ac.uk> Jurgen Doreleijers <jurgenfd@gmail.com>"

def convert(projectName, inputDir, projectNameNew):
    # Adjust the parameters below!
    removeOriginalStructureEnsemble = True
    addStructureEnsemble = True # From all *.pdb files in inputDir.

    print "projectName: %s" % projectName
    print "projectNameNew: %s" % projectNameNew
    print "inputDir: %s" % inputDir
    ccpnPath = os.path.join(inputDir, projectName)
    ccpnProject = loadProject(ccpnPath)

    ccpnMolSystem = ccpnProject.findFirstMolSystem()
    print 'found ccpnMolSystem: %s' % ccpnMolSystem
#    print 'status: %s' % ccpnMolSystem.setCode(projectName) # impossible; reported to ccpn team.

    if removeOriginalStructureEnsemble:
        structureEnsemble = ccpnProject.findFirstStructureEnsemble()
        if structureEnsemble:
            NTmessage("Removing first found structureEnsemble")
            structureEnsemble.delete()
        else:
            NTwarning("No structureEnsemble found; can't remove it.")

    if addStructureEnsemble:
        structureGeneration = ccpnProject.newStructureGeneration()
        guiRoot = Tkinter.Tk()
        format = PseudoPdbFormat(ccpnProject, guiRoot, verbose = 1)

        globPattern = inputDir + '/*.pdb'
        fileList = glob(globPattern)
        NTdebug("From %s will read files: %s" % (globPattern,fileList))
        format.readCoordinates(fileList, strucGen = structureGeneration, minimalPrompts = 1, linkAtoms = 0)

    print 'saving to new path if all checks are valid'
    # the newPath basename will be taken according to ccpn code doc.
    ccpnPathNew = os.path.join(inputDir, projectNameNew)
    saveProject(ccpnProject, checkValid=True, newPath=ccpnPathNew, removeExisting=True)



if __name__ == '__main__':
    cing.verbosity = verbosityDebug
#    projectName = "1brv"
#    inputDir = cingDirTmp
#    outputFile = os.path.join(cingDirTmp, projectName + ".str")
    _scriptName = sys.argv[0]
    projectName = sys.argv[1]
    inputDir = sys.argv[2]
    projectNameNew = sys.argv[3]
    convert(projectName, inputDir, projectNameNew )