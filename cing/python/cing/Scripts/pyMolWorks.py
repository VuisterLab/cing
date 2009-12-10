#!/usr/bin/env python
# Or execute: python -u $CINGROOT/python/cing/Scripts/pyMolWorks.py
# From http://pymolwiki.org/index.php/Launching_From_a_Script
import __main__
import sys
import time
import urllib2


try:
    # Importing the PyMOL module will create the window.
    import pymol #@UnresolvedImport
    from pymol import cmd #@UnresolvedImport
except:
    print "Failed to import pymol; python will stack dump next:"

# Tell PyMOL we don't want any GUI features.
__main__.pymol_argv = [ 'pymol', '-Gi' ]

# Call the function below before using any PyMOL modules.

pymol.finish_launching()

cmd.stereo('walleye')
cmd.set('stereo_shift', 0.23)
cmd.set('stereo_angle', 1.0)

cmd.spectrum()

try:
   pdbCode = '1brv'
   pdbFile = urllib2.urlopen('file:///Users/jd/workspace35/cing/Tests/data/pdb/'+
        pdbCode + '/pdb' +
        pdbCode + '.ent')
   cmd.read_pdbstr(pdbFile.read(), pdbCode)
except:
  print "Unexpected error:", sys.exc_info()[0]

time.sleep(5)
#cmd.quit()