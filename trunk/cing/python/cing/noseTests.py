'''
Created on Jun 17, 2011

FAILS

@author: jd
'''

#from cing.main import getNameList
import nose
#import sys

#sys.path.insert(0,"../src")    # add Pyro source directory
#nameList = getNameList()
#--cover-package=cing
nose.main(argv='noserunner --cover-package=cing.core.test --cover-erase --with-coverage --with-xunit'.split())
#nose.run()
