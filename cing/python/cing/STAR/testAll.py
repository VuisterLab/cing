import unittest

def testAll():
    modList = ( 
               "cing.STAR.TextTest", 
               "cing.STAR.UtilsTest", 
               "cing.STAR.TagTableTest", 
               "cing.STAR.SaveFrameTest", 
               "cing.STAR.FileTest", 
               )
    # Next line is to fool pydev extensions into thinking suite is defined in the regular way.
    suite = None
    for mod_name in modList:
        print "Importing ", mod_name
        exec("import %s" % (mod_name,))
        exec("suite = unittest.defaultTestLoader.loadTestsFromModule(%s)" % (mod_name,))
        unittest.TextTestRunner(verbosity=2).run(suite)
    
"""
Call by:
python testAll.py
"""
if __name__ == "__main__":
    testAll()