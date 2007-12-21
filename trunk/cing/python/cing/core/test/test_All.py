import unittest

"""
Call by:
python testAll.py
"""
def testAll():    
    modList = ( 
               "cing.core.test.test_classes",
               )
    # Next line is to fool pydev extensions into thinking suite is defined in the regular way.
    suite = None
    for mod_name in modList:
        print "Importing ", mod_name
        exec("import %s" % (mod_name,))
        exec("suite = unittest.defaultTestLoader.loadTestsFromModule(%s)" % (mod_name,))
        print "Testing"
        unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    testAll()