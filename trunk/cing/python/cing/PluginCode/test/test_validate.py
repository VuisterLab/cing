"""
Unit test
python $CINGROOT/python/cing/PluginCode/test/test_validate.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.core.classes import Project
from cing.core.constants import BMRB
from cing.core.constants import CYANA
from cing.core.constants import PDB
from cing.core.constants import XPLOR
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):
 
    def testRun(self):
        htmlOnly=False # default is False but enable it for faster runs without some actual data.
        pdbConvention = BMRB
        restraintsConvention = CYANA
#        entryId = "1brv"        # Small much studied PDB NMR entry 
        entryId = "2hgh_1model" # RNA-protein complex.
#        entryId = "1brv_1model" 
#        entryId = "1tgq_1model" # withdrawn entry
#        entryId = "1brv_1model" # withdrawn entry
#        entryId = "1YWUcdGMP" # Example entry from external user, Martin Allan
        
        if entryId.startswith("1YWUcdGMP"):
            pdbConvention = XPLOR
        if entryId.startswith("2hgh"):
            pdbConvention = CYANA
        if entryId.startswith("1tgq"):
            pdbConvention = PDB
        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
        NTdebug("Reading files from directory: " + cyanaDirectory)
        kwds = {'uplFiles': [ entryId ],
                'acoFiles': [ entryId ]              
                  }
        if entryId.startswith("1YWUcdGMP"):
            del(kwds['acoFiles'])
            
        if os.path.exists( os.path.join( cyanaDirectory, entryId+".prot")):
            self.assertTrue( os.path.exists( os.path.join( cyanaDirectory, entryId+".seq")),
                "Converter for cyana also needs a seq file before a prot file can be imported" )
            kwds['protFile'] = entryId
            kwds['seqFile']  = entryId

        # Skip restraints if absent.
        if os.path.exists( os.path.join( cyanaDirectory, entryId+".upl")):
            project.cyana2cing(cyanaDirectory=cyanaDirectory, convention=restraintsConvention,
                        copy2sources = True,
                        **kwds )
        project.save()
        self.assertFalse( project.validate(htmlOnly=htmlOnly))

if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
    unittest.main()
