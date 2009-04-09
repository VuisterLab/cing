#!/usr/bin/env python

import os,sys

# GET PYTHON VERSION
pythonversion = sys.version[:3]

# DECIDE ON OUR VERSION
if float(pythonversion)<=2.2:
  ourversion = '22'
else:
  ourversion = '23'

# SET PACKAGE NAME 
package = 'pypar_%s'%ourversion

# IMPORT MODULE
module = __import__(package,globals(),locals())
globals ().update (module.__dict__)
