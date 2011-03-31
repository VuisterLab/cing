#!/usr/bin/env python
# Run like (replace 1brv with any PDB entry)
# Execute in a directory with both a CCPN and a CING project directory named 1brv and 1brv.cing respectively.
# $CINGROOT/python/cing/Scripts/FC/vascoCingRefCheck.py 1brv

from cing import cingDirScripts
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Ccpn import Ccpn
from cing.PluginCode.required.reqVasco import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.classes2 import ResonanceList
from cing.core.parameters import moleculeDirectories
from matplotlib import mlab
from memops.api import Implementation
from memops.general.Io import loadProject
from memops.universal.Util import returnInt, returnFloat
#from pdbe.software.vascoReferenceCheck import VascoReferenceCheck
from pdbe2.analysis.shifts.vascoReferenceCheck import VascoReferenceCheck
import glob


"""
Additional install:

vascoRefData/ files, for statistical info.
vascoReferenceCheck.py, in pdbe.software (now part of SF CVS)

"""

class VascoCingReferenceCheck(VascoReferenceCheck):
    
    vascoRefDataPath = os.path.join(cingDirScripts, 'FC', 'vascoRefData')
    if not os.path.exists(vascoRefDataPath):
        NTerror("In CING using vascoRefDataPath %s but is absent" % vascoRefDataPath)            

    def setupDirectories(self, cingProject, ccpnDir=None):
        self.cingProject = cingProject
        entryCode = self.cingProject.name
        self.cingMoleculeDir = cingProject.moleculePath()
        self.dsspDataDir = os.path.join(self.cingMoleculeDir, moleculeDirectories.dssp) # Use 'Dssp'
        self.whatIfDataDir = os.path.join(self.cingMoleculeDir, moleculeDirectories.whatif)

        if ccpnDir:
            self.ccpnDir = ccpnDir
        else:
            self.ccpnDir = '%s' % entryCode
    
    
    def writePdbFile(self):
        pass

    def createSsInfo(self):

#        NTdebug("Fetching DSSP secondary structure info...")

        fileNames = glob.glob(os.path.join(self.dsspDataDir, "model_*.dssp"))

        self.allSsInfo = {}
        for fileName in fileNames:
            self.readDsspInfoFile(fileName)

        #
        # Now determine the most common SS element for each
        #

        self.ssInfo = {}

        for chainCode in self.allSsInfo.keys():
            self.ssInfo[chainCode] = {}
            for residueKey in self.allSsInfo[chainCode].keys():

                ssCodeDict = {}

                for ssCode in self.allSsInfo[chainCode][residueKey]:
                    if not ssCodeDict.has_key(ssCode):
                        ssCodeDict[ssCode] = 0
                    ssCodeDict[ssCode] += 1

                ssCodeMax = 0
                ssCode = None
                for ssCodeTemp in ssCodeDict.keys():
                    if ssCodeDict[ssCodeTemp] > ssCodeMax:
                        ssCodeMax = ssCodeDict[ssCodeTemp]
                        ssCode = ssCodeTemp

                # Convert...
                if ssCode in (' ',):
                    ssCode = 'C'

                self.ssInfo[chainCode][residueKey] = ssCode

    def readDsspInfoFile(self, fileName):

        fin = open(fileName)
        lines = fin.readlines()
        fin.close()

        dataLine = False
        for line in lines:
            cols = line.split()

            if cols[0] == '#' and cols[1] == 'RESIDUE':
                dataLine = True

            elif dataLine:
                # Note; No insertion code?
                seqCodeStr = line[5:10]
                seqCodeStr = seqCodeStr.strip()
                if len(seqCodeStr) < 1:
                    NTdebug("Skipping line with empty seqCode string: " + line) # happens for PDB entry 1cjg for 2 residues
                    continue    
                
                seqCode = returnInt(seqCodeStr)
                chainCode = line[11:12]
                secStruc = line[16:17]

                if not self.allSsInfo.has_key(chainCode):
                    self.allSsInfo[chainCode] = {}

                seqKey = (seqCode, ' ')

                if not self.allSsInfo[chainCode].has_key(seqKey):
                    self.allSsInfo[chainCode][seqKey] = []

                self.allSsInfo[chainCode][seqKey].append(secStruc)
    # end def
    
    def createAsaInfo(self):
        'Return True on error.'
        if self.showMessages:
            NTdebug( "Fetching WHATIF per-atom surface accessibility info..." )

        fileNames = glob.glob(os.path.join(self.whatIfDataDir, "wsvacc*.log"))

        self.allWhatIfInfo = {'chains': {}}
        for fileName in fileNames:
            if self.readWhatIfAsaInfoFile(fileName): # fills self.allWhatIfInfo
                NTerror("Failed %s when reading file." % (getCallerName()))
                return True
        # end for
        
        #
        # Now determine the median ASA for each
        #
        # whatIfInfo is used in super class whereas allWhatIfInfo was filled before. 
        self.whatIfInfo = self.allWhatIfInfo
        d = self.whatIfInfo['chains']
#        medianIndex = None
        for chainCode in d.keys():
            for seqKey in d[chainCode].keys():
                for atomName in d[chainCode][seqKey]['atoms'].keys():
                    asaList =   d[chainCode][seqKey]['atoms'][atomName]
                    asaList.sort()
#                    if not medianIndex:
#                    medianIndex = int((len(asaList) / 2.0) + 0.5) # fails with round off on single element lists.
                    ml = mlab.prctile(asaList,[50])                    
#                    if medianIndex < 0 or medianIndex >= len(asaList):
#                        NTerror("Found improper median index %s for %s" % (medianIndex, str(asaList)))
#                        return True
#                    d[chainCode][seqKey]['atoms'][atomName] = [asaList[medianIndex]] # Resetting list to only include median
                    d[chainCode][seqKey]['atoms'][atomName] = [ml[0]] # Reseting array because JFD is not sure it's a regular array from mlab.
                # end for
            # end for
        # end for
    # end def

    def readWhatIfAsaInfoFile(self, fileName):
        'Return True on error.'

#        NTdebug('Now in ' + getCallerName() + ' for ' + fileName)
        fin = open(fileName)
        lines = fin.readlines()
        fin.close()
        atomsRead = 0
        hydrogensSkipped = 0
        skipHydrogens = False # already corrected for elsewhere?
        dataLine = False #@UnusedVariable
        for line in lines:
            line = line.strip()
#            NTdebug('Line: ' + line)
            if line[0] == '*' or not line:
                continue

            fields = line.split(';')

            resLabel = fields[1]
            seqId = fields[2]
            insertionCode = fields[3]
            chainCode = fields[4]
            # field 5 has nothing?
            atomName = fields[6]
            accessibility = fields[7]
            
            
            if skipHydrogens and atomName[0] == 'H':
                hydrogensSkipped += 1 # are zero anyway.
                continue
            
            if not insertionCode:
                insertionCode = ' '
            seqKey = (returnInt(seqId), insertionCode)

            if not (accessibility[0] == '|' and accessibility[-1] == '|'):
                NTerror("Skipping line without valid format for accessibility: " + line)
                continue
            if len(accessibility) < 3:
                NTerror("Skipping line with too short accessibility string: " + line)
                continue
            accessibilityStr = accessibility[1:-1]
            accessibilityStr = accessibilityStr.strip()
            if len(accessibilityStr) < 1:
                NTerror("Skipping line with empty accessibility string: " + line) # happens for PDB entry 1cjg for 2 residues
                continue         
            accessibility = returnFloat(accessibilityStr)
            d = self.allWhatIfInfo['chains']
            if not d.has_key(chainCode):
                   d[chainCode] = {}
            if not d[chainCode].has_key(seqKey):                
                   d[chainCode][seqKey] = {'hasBadAtoms': False, 'resLabel': resLabel, 'atoms': {}}
            if not d[chainCode][seqKey]['atoms'].has_key(atomName):
                   d[chainCode][seqKey]['atoms'][atomName] = []

            d[chainCode][seqKey]['atoms'][atomName].append(accessibility)
            atomsRead += 1
        # end for
#        NTdebug("Read %s atoms" % atomsRead)
#        NTdebug("Skipped %s hydrogen" % hydrogensSkipped)
#        NTdebug("Seen %s atoms" % (atomsRead + hydrogensSkipped))
        if not atomsRead:
            NTerror("Failed to read any atom")
            return True
        # end if
    # end def

    def findResidue(self, chain, seqKey):
        return chain.findFirstResidue(seqCode=seqKey[0], seqInsertCode=seqKey[1])
    # end def

    def checkAllShiftLists(self):
        """
        Return True on error
        """        
        if not self.showMessages:
#            print 'switching messaging off temporarily.'
            switchOutput(False)        
        ccpnProject = loadProject(self.ccpnDir)
        if not self.showMessages:
            print 'switching messaging on again.'
            switchOutput(True)
        if ccpnProject == None:
            NTerror("Failed to load CCPN project from: %s" % self.ccpnDir)
            return True
        
#        shiftLoL = ccpnProject.currentNmrProject.findAllMeasurementLists(className='ShiftList')
        # Use sorting by CCPN.
        shiftLoL = filterListByObjectClassName( ccpnProject.currentNmrProject.sortedMeasurementLists(), Ccpn.CCPN_CS_LIST )
#        NTdebug("Working on shiftLoL %s", str(shiftLoL))
        
        for i,shiftList in enumerate(shiftLoL):
            shiftListSerial=shiftList.serial
#            NTdebug("Working on shiftListSerial %s", shiftListSerial)
            self.checkProject(ccpnProject=ccpnProject, shiftListSerial=shiftListSerial)
            self.tagProject()
            if self.tagCingProject(shiftList, i):
                return True

    def tagProject(self):
        """
        Return True on error
        """
        for atomKey in vascoAtomIdLoL:
            atomType = atomKey[0]
            (rerefValue, rerefError) = self.rerefInfo[atomKey]
            if rerefValue != None:
                appData1 = Implementation.AppDataFloat(value=rerefValue, application='VASCO', keyword='correction_%s' % atomType)
                appData2 = Implementation.AppDataFloat(value=rerefError, application='VASCO', keyword='correctionError_%s' % atomType)
                self.shiftList.addApplicationData(appData1)
                self.shiftList.addApplicationData(appData2)
#        NTdebug("%s" % self.shiftList.findAllApplicationData(application='VASCO'))
    # end def

    def tagCingProject(self, ccpnShiftList, i):
        """
        Return True on error.
        
        Ensure that the name used below stays in sync with the scheme used by the CING CCPN importer.
        In other words: no changes are allowed in the order of CS lists between CING and CCPN projects.
        """
        mol = self.cingProject.molecule
#        resonanceListName = getDeepByKeysOrAttributes( ccpnShiftList, NAME_STR )
#        if resonanceListName == None:
#            NTerror("Failed to get resonanceListName from CCPN which will not allow CING to match later on for e.g. Vasco. Continuing.")
#            resonanceListName = 'source'
#        idx = getObjectIdxByName( mol.resonanceSources, resonanceListName ) 
#        if i < 0:
#            NTerror("Failed to get idx for resonanceListName %s" % resonanceListName )
#            return True
#        resonanceListName = mol.resonanceSources[idx]
#        if resonanceListName == None:
#            NTerror("Failed to get resonanceListName from CCPN which will not allow CING to match later on for e.g. Vasco. Continuing.")
#            return True
        
        resonanceList = getDeepByKeysOrAttributes( mol.resonanceSources, i)
        if not isinstance(resonanceList, ResonanceList):
            NTerror("Failed to get resonanceList by idx: %s" % i)
            NTerror("mol.resonanceSources: %s" % str(mol.resonanceSources))
            return True
        NTmessage("==> Tagging CING project with Vasco results for resonanceList: %s" % resonanceList)        
        
        if resonanceList.vascoApplied: # boolean xor is equivalent of the above line.
#            NTdebug("CS were rereferenced before so first undoing previous application.")
            if mol.applyVascoChemicalShiftCorrections( resonanceList = resonanceList, doRevert = True ):
                NTerror("Failed to undo Vasco rereferencing for: %s" % resonanceList)
                return True
            # end def
        # end def
            
        if mol.setVascoChemicalShiftCorrections(self.rerefInfo, resonanceList ):
            NTerror("Failed to setVascoChemicalShiftCorrections for: %s" % resonanceList)
            return True         
        if mol.applyVascoChemicalShiftCorrections( resonanceList = resonanceList ):
            NTerror("Failed to applyVascoChemicalShiftCorrections for: %s" % resonanceList)
            return True
        # end def
    # end def
# end class

if __name__ == '__main__':
    entryCode = sys.argv[1] # e.g. 1brv
    cingProject = Project.open(entryCode, status='old')

    if 0: # DEFAULT 0 for not using original implementation
          # Fails because of dependency on:
#              File "/Users/jd/workspace35/ccpn/python/pdbe/software/vascoReferenceCheck.py", line 178, in createSsInfo
#                from pdbe.analysis.external.stride.Util import StrideInfo #@UnresolvedImport
#            ImportError: No module named external.stride.Util          
        import Tkinter
        root = Tkinter.Tk()        
        ccpnDir = entryCode
        vascoReferenceCheck = VascoReferenceCheck(guiParent=root)
        vascoReferenceCheck.checkProject(ccpnDir=ccpnDir)
    else:
        # Try the CING based check
        vascoReferenceCheck = VascoCingReferenceCheck(guiParent=None)
        vascoReferenceCheck.setupDirectories(cingProject, ccpnDir=None)
        vascoReferenceCheck.checkAllShiftLists()
    #vascoReferenceCheck.ccpnProject.saveModified()
# end if