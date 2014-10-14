"""
Original from Wim Vranken.
Used for eNMR workshop Frankfurt data sets.
"""

from ccpnmr.format.converters.PseudoPdbFormat import PseudoPdbFormat
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
from glob import glob
from memops.api import Implementation
import Tkinter
import shutil

__author__     = cing.__author__ + "Wim Vranken <wim@ebi.ac.uk>"

def convert(projectName, rootDir):
    datasetDir = os.path.join(rootDir, projectName)
    nijmegenDir = os.path.join(datasetDir, "Nijmegen")
    authorDir = os.path.join(datasetDir, "Authors")
    os.chdir(nijmegenDir)

    projectPath = os.path.join(nijmegenDir, projectName)
    if os.path.exists(projectPath):
        shutil.rmtree(projectPath)

    project = Implementation.MemopsRoot(name = projectName)

    nmrProject = project.newNmrProject(name = project.name)
    structureGeneration = nmrProject.newStructureGeneration()
    guiRoot = Tkinter.Tk()
    format = PseudoPdbFormat(project, guiRoot, verbose = 1)

    globPattern = authorDir + '/*.pdb'
    fileList = glob(globPattern)
    nTdebug("From %s will read files: %s" % (globPattern,fileList))
    format.readCoordinates(fileList, strucGen = structureGeneration, minimalPrompts = 1, linkAtoms = 0)

    project.saveModified()
    tgzFileName = "../"+projectName + ".tgz"
    cmd = "tar -czf %s %s" % (tgzFileName, projectName)
    do_cmd(cmd)

if __name__ == '__main__':

    cing.verbosity = verbosityDebug
    rootDir = "/Users/jd/workspace35/cing/Tests/data/eNMR"
#    projectName = sys.argv[0]
    projectList = """CuTTHAcisFrankfurt CuTTHAtransFrankfurt ParvulustatFrankfurt
TTScoFrankfurt apoTTHAcisFrankfurt apoTTHAtransFrankfurt mia40Frankfurt wln34Frankfurt""".split()

    for projectName in projectList:
        convert(projectName, rootDir)
