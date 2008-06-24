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
from cing.core.constants import CYANA
from cing.core.constants import PDB
from cing.core.constants import XPLOR
from unittest import TestCase
from cing.core.constants import IUPAC
import cing
import os
import unittest

class AllChecks(TestCase):

    def testRun(self):
        # TODO: the htmlOnly set to True currently fails. To fix!
        htmlOnly = True # default is False but enable it for faster runs without some actual data.
        doWhatif = False # disables whatif actual run
        doProcheck = False


#        entryId = "1ai0"
#        entryId = "1brv"        # Small much studied PDB NMR entry
#        entryId = "2hgh_1model" # RNA-protein complex.
        entryId = "1brv_1model"
#        entryId = "1hkt_1model" # Geerten's first structure in PDB
#        entryId = "1y4o_1model"
#        entryId = "1y4o"
#        entryId = "1i1s_1model" # withdrawn entry
#        entryId = "1ka3" # has been replaced by the authors in 2004 (new pdb entry 1tkv).
#        entryId = "1tkv" # replaced 1ka3
#        entryId = "1tgq" # withdrawn entry
#        entryId = "1tgq_1model" # withdrawn entry
#        entryId = "1brv_1model" # withdrawn entry
#        entryId = "1YWUcdGMP" # Example entry from external user, Martin Allan
#        entryId = "1hkt" # Geerten's first structure in PDB


        self.failIf( os.chdir(cingDirTmp),
                     msg="Failed to change to directory for temporary test files: "+cingDirTmp
                   )
        project = Project.open( entryId, status='new' )
        if not project:
            NTerror('Failed opening project %s', entryId)
            exit(1)

        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        NTdebug("Reading files from directory: " + cyanaDirectory)

        # Import of the raw data; different formats for each entry
        if entryId.startswith("1YWUcdGMP"):
            pdbConvention = XPLOR
        elif entryId.startswith("2hgh"):
            pdbConvention = CYANA
        elif entryId.startswith("1tgq"):
            pdbConvention = PDB
            project.initPDB( pdbFile=os.path.join(cyanaDirectory,entryId+'.pdb'), convention = pdbConvention )
        elif entryId.startswith("1brv_1model"):
            pdbConvention = IUPAC
            restraintsConvention = CYANA
            project.initPDB( pdbFile=os.path.join(cyanaDirectory,entryId+'.pdb'), convention = pdbConvention )
            project.cyana2cing(cyanaDirectory,
                               convention=restraintsConvention,
                               seqFile = entryId,
                               protFile = entryId,
                               uplFiles = [entryId],
                               acoFiles = [entryId]
                              )
        else:
            NTerror('Undefined entryId "%s"', entryId)
            exit(1)

#        kwds = {}

#        pdbFileName = entryId+".pdb"
#        kwds['pdbFile'] = os.path.join( cyanaDirectory, pdbFileName)
##        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
#
#        # Skip restraints if absent.
#        if os.path.exists( os.path.join( cyanaDirectory, entryId+".upl")):
#            kwds['uplFiles'] = [entryId]
#        if os.path.exists( os.path.join( cyanaDirectory, entryId+".aco")) and not entryId.startswith("1YWUcdGMP"):
#            kwds['acoFiles'] = [ entryId ]
#
#        if os.path.exists( os.path.join( cyanaDirectory, entryId+".seq")):
#            kwds['seqFile']  = entryId
#
#        if os.path.exists( os.path.join( cyanaDirectory, entryId+".prot")):
#            self.assertTrue( os.path.exists( os.path.join( cyanaDirectory, entryId+".seq")),
#                "Converter for cyana also needs a seq file before a prot file can be imported" )
#            kwds['protFile'] = entryId
#            kwds['seqFile']  = entryId
#
#        project.cyana2cing(cyanaDirectory=cyanaDirectory, convention=restraintsConvention,
#                           copy2sources = True,
#                           **kwds
#                          )
        project.save()
        self.assertFalse(
                         project.validate(
                                          htmlOnly=htmlOnly,
                                          doProcheck = doProcheck,
                                          doWhatif=doWhatif,
#                                         doProcheck=(not doWhatifValidationOnly),
                                         )
                         )

if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
#    cing.verbosity = verbosityOutput
    unittest.main()

