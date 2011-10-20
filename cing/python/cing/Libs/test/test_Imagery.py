"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_Imagery.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.Imagery import convert2Web
from cing.Libs.Imagery import convertImageMagick
from cing.Libs.Imagery import joinPdfPagesByGhostScript
from cing.Libs.Imagery import montage
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.parameters import cingPaths
from unittest import TestCase
import unittest
from cing.Libs.disk import rmdir

if not cingPaths.convert: # Requirement for test.
    raise ImportWarning('convert')

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    cingDirTmpTest = os.path.join( cingDirTmp, 'test_Imagery' )
    if os.path.exists(cingDirTmpTest):
        rmdir(cingDirTmpTest)
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testConvert2Web(self):

        fn = "pc_nmr_11_rstraints.ps"
#        fn = "1vnd_11_rstraints.ps"
        self.assertTrue( os.path.exists( cingDirTestsData) and os.path.isdir(cingDirTestsData ) )
        inputPath = os.path.join(cingDirTestsData,fn)
        fileList = convert2Web( inputPath, outputDir='.', doMontage=True )
        nTdebug( "Got back from convert2Web output file names: " + repr(fileList))
        self.assertNotEqual(fileList,True)
        if fileList != True:
            for file in fileList:
                self.assertNotEqual( file, None)
        fn1 = "pc_nmr_11_rstraints.pdf"
        self.assertFalse( joinPdfPagesByGhostScript( [fn1,fn1], "pc_nmr_11_rstraints_echo.pdf"))
        outputPath =  'pc_nmr_11_rstraints_pin.gif'
        self.assertFalse(convertImageMagick(inputPath, outputPath, options='-geometry 57x40'))
        self.assertTrue(os.path.exists(outputPath))

    def _testConvert2Html(self):
        inputPath = os.path.join( cingDirTestsData, 'imagery')
        inputPathList = map(os.path.join, [inputPath]*2, ['residuePlotSetAll001.png', 'residuePlotSetAll002.png'] )
        outputPath = os.path.join( self.cingDirTmpTest, 'residuePlotSetAll.png' )
        self.assertFalse( montage(inputPathList, outputPath) )
        
#    def _testConvertImageMagick(self):
#        x = convertImageMagick(inputPath,outputPath,options,extraOptions=None)
#    # end def
# end class

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
