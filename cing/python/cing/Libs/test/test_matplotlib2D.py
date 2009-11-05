from cing.Libs.NTutils import NTdebug
from pylab import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testX(self):

#        palette = cm.gray
        palette  = matplotlib.colors.LinearSegmentedColormap.from_list('inv_gray', ('black', 'white'))
        palette.set_under(color = 'red', alpha = 0.0 )
#        self.assertEqual(palette(-1.0)[3],0.0) # should actually be true, alpha needs to be zero for under.
        # See issue 214

        NTdebug( palette([-1,     # under: red but with alpha zero.
                       0.,      # black with alpha 1
                       1,      # white with alpha 1
                       ],
        #               alpha=0
                       ))

if __name__ == "__main__":
    unittest.main()
