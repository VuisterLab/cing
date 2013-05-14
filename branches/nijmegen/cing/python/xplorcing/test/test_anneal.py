"""
Unit test execute as:
python $CINGROOT/python/xplornih/test/test_anneal.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import copydir
from cing.Libs.forkoff import do_cmd
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    'Test case'
    entryList = "2fwu".split()
#    entryList = "protG".split()
#    entryList = "1brv".split()
    def _test_anneal(self):
        'Test the anneal'
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)
        inputArchiveDir = os.path.join(cingDirTestsData, "xplor")
        for _i,entryId in enumerate(AllChecks.entryList):
            nTmessage('Doing entry %s' % entryId)
            cingDirTmpTestEntry = entryId
            mkdirs( cingDirTmpTestEntry )
            self.failIf(os.chdir(cingDirTmpTestEntry), msg =
                "Failed to change to test entry directory for files: " + cingDirTmpTestEntry)
            do_cmd( "rm -f *_extended_*.pdb* >& /dev/null" )
            inputDir = os.path.join(inputArchiveDir, entryId )
            self.failIf( not os.path.exists(inputDir), "Missing input dir " + inputDir)
            nTmessage('Trying to copy input files' )
            copydir( os.path.join(inputDir, '*'), '.')
            xplorExecutable = '/Users/jd/workspace/xplor-nih-2.27/bin/xplor'
            xplorScript = '$CINGROOT/python/xplorcing/anneal.py'
            cmd = 'env -i PATH=$PATH HOME=$HOME USER=$USER %s -py %s %s >& anneal.log' % (
                xplorExecutable, xplorScript,
                entryId,
#                os.getcwd(), # inputDir
#                os.getcwd(), # outputDir
                )
            if do_cmd( cmd ):
                nTerror("Failed anneal")
            else:
                nTmessage("Succeeded anneal")


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
