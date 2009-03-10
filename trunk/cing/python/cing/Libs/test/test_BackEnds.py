from cing import cingDirTmp
from cing import verbosityDebug
from matplotlib.pylab import close
from matplotlib.pylab import plot
from matplotlib.pylab import savefig
from unittest import TestCase
import cing
import os
import unittest



class AllChecks(TestCase):

    def testBackEnd(self):

        # important to switch to temp space before starting to generate files for the project.
        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)

        # Trying to plot without GUI backend.
#        use('Agg') Already present in NTplot.py
        
        plot( [1,2,3] , 'go' )
        
        savefig('backendPlot.png')
        savefig('backendPlot.pdf')
        close()
        
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
