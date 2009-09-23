"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_Procheck.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.PluginCode.procheck import Procheck #@UnusedImport Keep to indicate dep and proper handeling.
from cing.core.classes import Project
from cing.core.constants import CYANA
from cing.core.constants import IUPAC
from cing.core.constants import PDB
from cing.core.constants import XPLOR
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def testProcheckNMR_Aqua(self):
        runAqua = True
        showProcheckResults = False
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
        entryId = "1dsv"
#        entryId = "1brv_1model" # Small much studied PDB NMR entry
#        entryId = "1YWUcdGMP" # Example entry from external user, Martin Allan
        ranges = None
        pdbConvention = IUPAC
        restraintsConvention = CYANA
        if entryId.startswith("1YWUcdGMP"):
            pdbConvention = XPLOR
        if entryId.startswith("2hgh"):
            pdbConvention = CYANA
        if entryId.startswith("1tgq"):
            pdbConvention = PDB
        if entryId.startswith("1brv"):
            pdbConvention = IUPAC

        if entryId == "2hgh":
            # Note that CING doesn't support chain ids in range selection for procheck. TODO
            # in the case of 2hgh this is not a problem because the residue numbering doesn't
            # overlap between the chain A protein and chain B RNA.
            ranges = "2-11,13-33,35-54"
                # 1 and 55 are 5' and 3' terminii which are a little looser.
                # 12, and 34 are bases that are not basepaired.
            ranges += ",104-105,115-136,145-190"
                # 106-114 is a loop
                # 137-144 is a loop
                # 191-193 are 3 Zn ions.
    #This leads to a procheck ranges file like:
    #        RESIDUES   2  B   11  B
    #        RESIDUES  13  B   33  B
    #        RESIDUES  35  B   54  B
    #        RESIDUES 104  A  105  A
    #        RESIDUES 115  A  136  A
    #        RESIDUES 145  A  190  A

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        project = Project( entryId )
        self.failIf( project.removeFromDisk() )
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
        self.failIf(project.runProcheck(ranges = ranges, createPlots=True, runAqua=runAqua) is None)

        if showProcheckResults:
            for res in project.molecule.allResidues():
                NTdebug(`res` +" "+ `res.procheck.secStruct`)

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()

