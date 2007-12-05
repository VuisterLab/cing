import unittest

"""
Call by:
python testAll.py
        # TODO: report a summary at beginning of what will be tested and at the end what works.
"""
def testAll():    
    modList = ( 
               "cing.PluginCode.test.test_Biggles", 
               "cing.PluginCode.test.test_Procheck", 
               "cing.PluginCode.test.test_validate", 
               "cing.PluginCode.test.test_Procheck", 
               "cing.PluginCode.test.test_Whatif", 
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