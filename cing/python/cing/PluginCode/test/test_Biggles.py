from unittest import TestCase
import unittest
import biggles
import math
import numpy

class AllChecks(TestCase):
        
    def testparse(self):
        """(Singing) Make a little plot, do a little ouptut"""
        
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
        p.show()         
#        p.show() # X11
        print "Trying to write eps file"
        p.write_eps( "example1.eps" )
        print "done writing eps file"
        p.write_img( 400, 400, "example1.gif" )
        print "done writing gif file"
        #print "Note that the last line of code here causes a core dump on Jurgen's installation on a Intel Mac OSX 10.4"
        #print "Apparently it has problems with jpg and png files so gif it is."
        print "Trying to write png file"
        p.write_img( 'png', 400, 400, "example1.png" )
        print "done writing png file"
        
if __name__ == "__main__":
    unittest.main()

