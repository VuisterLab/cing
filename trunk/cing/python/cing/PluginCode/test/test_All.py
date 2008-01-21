import unittest

"""
Call by:
python test_All.py
"""
def testAll():    
    modList = ( 
               "cing.PluginCode.test.test_Biggles", 
               "cing.PluginCode.test.test_Molgrap", 
               "cing.PluginCode.test.test_Procheck", 
               "cing.PluginCode.test.test_STAR",
               "cing.PluginCode.test.test_validate", 
               "cing.PluginCode.test.test_Wattos", 
               "cing.PluginCode.test.test_Whatif" 
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