# Execute like e.g.:
# python $CINGROOT/python/cing/Scripts/FC/convertCcpn2Nmrstar.py VpR247Seattle . VpR247Seattle.str

"""
Original from Wim Vranken.
"""
from memops.general.Io import loadProject
from pdbe.nmrStar.IO.NmrStarExport import NmrStarExport # valid for use with python from API
import os
import sys
#from msd.nmrStar.IO import NmrStarExport # valid for use with python from Analysis
#from ccpnmr.eci import NmrStarExport

__author__ = "Wim Vranken <wim@ebi.ac.uk> Jurgen Doreleijers <jurgenfd@gmail.com>"

def convert(projectName, inputDir, outputFile, excludeSaveFrames = ('general_distance_constraints',) ):

    print "projectName: %s" % projectName
    print "inputDir: %s" % inputDir
    print "outputFile: %s" % outputFile
    print "excludeSaveFrames: %s" % excludeSaveFrames
    ccpnPath = os.path.join(inputDir, projectName)
    ccpnProject = loadProject(ccpnPath)

    # Try to find the CING setup info in the project.
    cingCalcStore = ccpnProject.findFirstNmrCalcStore(name='CING')
    if cingCalcStore is not None:
        nmrProject = cingCalcStore.nmrProject

        run = cingCalcStore.findFirstRun(status='pending')
        molSystem = (run.findFirstData(className='MolSystemData').molSystem or
                          run.findFirstData(className='MolResidueData').findFirstChain().molSystem)
        nmrConstraintStore = run.findFirstData(className='ConstraintStoreData').nmrConstraintStore
        nmrEntryStore = (ccpnProject.findFirstNmrEntryStore(name='newNmrEntryStoreName') or
                              ccpnProject.newNmrEntryStore(name='newNmrEntryStoreName'))

        nmrEntry = nmrEntryStore.newEntry(molSystem=molSystem, name='newNmrEntryName')
        structureGeneration = nmrProject.newStructureGeneration(name='newNmrStructureGeneration',
                                                                nmrConstraintStore=nmrConstraintStore)
        nmrEntry.addStructureGeneration(structureGeneration)

        nmrEntry.measurementLists = [x.measurementList for x in run.findAllData(className='MeasurementListData')]
        nmrEntry.structureAnalyses = nmrProject.sortedStructureAnalyses()
        nmrEntry.peakLists = [x.peakList for x in run.findAllData(className='PeakListData')]

        structureGeneration.structureEnsemble = run.findFirstData(className='StructureEnsembleData').structureEnsemble
    else:
        nmrEntryStore = ccpnProject.newNmrEntryStore(name = "newNmrEntryStoreName")
        molSystem = ccpnProject.findFirstMolSystem()
        nmrEntry = nmrEntryStore.newEntry( molSystem = molSystem, name = 'newNmrEntryName')

        nmrProject = ccpnProject.currentNmrProject
        #
        # nmrEntry.structureGenerations = nmrProject.sortedStructureGenerations()
        # if nmrEntry.structureGenerations:
        #     print "Using structureGenerations from nmrProject"
        structureGenerations = nmrProject.sortedStructureGenerations()

        if structureGenerations:
            # NBNB RHF October 2014. WATTOS breaks if there is more than one structureGeneration
            # Add the newest ony, and let the pre-existing code take care of ensembles
            nmrEntry.addStructureGeneration(structureGenerations[-1])
        else:
           ncs = ccpnProject.findFirstNmrConstraintStore()
           sG = None
           if not ncs:
               print "Failed to find any NmrConstraintStore from project"
           else:
               sG = ncs.findFirstStructureGeneration()
           if sG:
               nmrEntry.addStructureGeneration( sG )
               print "Using structureGenerations from nmrProject"
           else:
               print "Failed to find nmrEntry.structureGenerations from nmrProject or nmrConstraintStore; creating a new one."
               strucGen = nmrProject.newStructureGeneration()
               nmrEntry.addStructureGeneration(strucGen)
           # end if
           # end if
        # end if

        try: # ccpn stable as 08 Jul 2009
           nmrEntry.structureAnalyses = nmrProject.sortedStructureAnalysiss() # watch out for misspelling.
        except AttributeError: # ccpn trunk fixed misspelled function
           nmrEntry.structureAnalyses = nmrProject.sortedStructureAnalyses()
        if not nmrEntry.structureAnalyses:
           print "Failed to find nmrEntry.structureAnalyses"
        nmrEntry.measurementLists = nmrProject.sortedMeasurementLists()
        if not nmrEntry.measurementLists:
           print "Failed to find nmrEntry.measurementLists"


        # TJR, RHF 16 Oct 2014
        # DIfferent hack. We now have only ever allow 1 (ONE) structureGeneration.
        assert len(nmrEntry.root.sortedStructureEnsembles()) == 1, "Must have one and only one ensemble"
        assert len(nmrProject.sortedNmrConstraintStores()) == 1, "Must have one and only one set of constraints"

        #
        #  Hack to hook up coordinates, hopefully correctly (Wim 30/04/2009)
        #    if nmrEntry.structureGenerations:
        #       hasStructureEnsemble = False
        #       for strucGen in nmrEntry.structureGenerations:
        #           if strucGen.structureEnsemble:
        #               hasStructureEnsemble = True
        #               break
        #           # end if
        #       # end for
        #
        #       print "hasStructureEnsemble: %s" % hasStructureEnsemble
        #       # This will only work dependably if there is one structureGeneration, one structureEnsemble...
        #       # Take the one that was created last in any case, fingers crossed that they match up!
        #       if not hasStructureEnsemble and ccpnProject.structureEnsembles:
        #           nmrEntry.sortedStructureGenerations()[-1].structureEnsemble = ccpnProject.sortedStructureEnsembles()[-1]
        #       # end if
        #    # end if

        for ne in nmrProject.sortedExperiments(): # will be sortedNmrExperiments
           for ds in ne.sortedDataSources():
               for pl in ds.sortedPeakLists():
                   nmrEntry.addPeakList(pl)

    nmrStarExport = NmrStarExport(nmrEntry, nmrStarVersion = '3.1', forceEntryId = '1')
    nmrStarExport.createFile(outputFile, excludeSaveFrames= excludeSaveFrames, verbose = True)

    # Set the header comment - only set this if you need a standard header!
    topComment = "# File written for CING by NmrStarExport.py code"
    nmrStarExport.writeFile(title = "CING", topComment=topComment, verbose = True)


if __name__ == '__main__':
    #    cing.verbosity = verbosityDebug
    #    projectName = "1brv"
    #    inputDir = cingDirTmp
    #    outputFile = os.path.join(cingDirTmp, projectName + ".str")
    _scriptName = sys.argv[0]
    projectName = sys.argv[1]
    inputDir = sys.argv[2]
    outputFile = sys.argv[3]
    convert(projectName, inputDir, outputFile)
