"""
Original from Wim Vranken.
"""

from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from memops.general.Io import loadProject
from msd.nmrStar.IO.NmrStarExport import NmrStarExport
import cing
import os
import sys

__author__ = cing.__author__ + "Wim Vranken <wim@ebi.ac.uk>"

def convert(projectName, inputDir, outputFile):

    NTdebug("projectName: %s" % projectName)
    NTdebug("inputDir: %s" % inputDir)
    NTdebug("outputFile: %s" % outputFile)
    ccpnPath = os.path.join(inputDir, projectName)
    ccpnProject = loadProject(ccpnPath)


    nmrEntryStore = ccpnProject.newNmrEntryStore(name = "newNmrEntryStoreName")
    molSystem = ccpnProject.findFirstMolSystem()
    nmrEntry = nmrEntryStore.newEntry( molSystem = molSystem, name = 'newNmrEntryName')

    nmrProject = ccpnProject.currentNmrProject

    nmrEntry.structureGenerations = nmrProject.sortedStructureGenerations()
    nmrEntry.structureAnalyses = nmrProject.sortedStructureAnalysiss() # watch out for misspelling.
    nmrEntry.measurementLists = nmrProject.sortedMeasurementLists()

    for ne in nmrProject.sortedExperiments(): # will be sortedNmrExperiments
        for ds in ne.sortedDataSources():
            for pl in ds.sortedPeakLists():
                nmrEntry.addPeakList(pl)

    nmrStarExport = NmrStarExport(nmrEntry, nmrStarVersion = '3.1', forceEntryId = '1')
    nmrStarExport.createFile(outputFile, verbose = True)

    # Set the header comment - only set this if you need a standard header!
    topComment = "# File written for CING by NmrStarExport.py code"
    nmrStarExport.writeFile(title = "CING", topComment=topComment, verbose = True)


if __name__ == '__main__':
    cing.verbosity = verbosityDebug
#    projectName = "1brv"
#    inputDir = cingDirTmp
#    outputFile = os.path.join(cingDirTmp, projectName + ".str")
    _scriptName = sys.argv[0]
    projectName = sys.argv[1]
    inputDir = sys.argv[2]
    outputFile = sys.argv[3]
    convert(projectName, inputDir, outputFile)
