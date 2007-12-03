from cing import cingDirTestsTmp
from unittest import TestCase
import biggles
import math
import numpy
import os
import unittest

class AllChecks(TestCase):
        
    def testparse(self):
        """(Singing) Make a little plot, do a little ouptut"""
        
        os.chdir(cingDirTestsTmp)
        x = numpy.arange( 0, 3*math.pi, math.pi/30 )
        c = numpy.cos(x)
        s = numpy.sin(x)
         
        p = biggles.FramedPlot()
        p.title = "title"
        p.xlabel = r"$x$"
        p.ylabel = r"$\Theta$"
         
        p.add( biggles.FillBetween(x, c, x, s) )
        p.add( biggles.Curve(x, c, color="red") )
        p.add( biggles.Curve(x, s, color="blue") )
        # BEFORE YOU TRY THE NEXT COMMAND READ on
        p.show() 
        # -1- X11 needs to be open 
        # -2- Your DISPLAY variable needs to be set right. 
        #   within Eclipse this means you might have to set it as an additional parameter.
        #   Either in the "External Tools" menus
        # Or by making sure Eclipse inherits the environment settings by calling Eclipse 
        # from the shell command instead of from the Dock in Mac OS X.
        p.write_eps( "example1.eps" )
        print "done writing eps file"
        p.write_img( 400, 400, "example1.gif" )
        print "done writing gif file"
        #print "Note that the last line of code here used to cause a core dump on Jurgen's 
        # installation on a Intel Mac OSX 10.4"
        #print "Apparently it has problems with jpg and png files so gif it is."
#        print "Trying to write png file"
#        p.write_img( 'png', 400, 400, "example1.png" )
#        print "done writing png file"
        
if __name__ == "__main__":
    unittest.main()