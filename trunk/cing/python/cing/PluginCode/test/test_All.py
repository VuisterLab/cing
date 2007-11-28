import unittest

"""
Call by:
python testAll.py
"""
if __name__ == "__main__":
    modList = ( 
               # Prerequisites general setup
               "PluginCode.test.test_Biggles", 
#               "PluginCode.test.test_ExternalImports", 
               # Prerequisites external structural biology programs
               "PluginCode.test.test_Procheck", 
#               "PluginCode.test.test_Whatif", 
               # Prerequisites internal Cing code
               
               )
    # Next line is to fool pydev extensions into thinking suite is defined in the regular way.
    suite = None
    for mod_name in modList:
        print "Importing ", mod_name
        exec("import %s" % (mod_name,))
        exec("suite = unittest.defaultTestLoader.loadTestsFromModule(%s)" % (mod_name,))
        print "Testing"
        unittest.TextTestRunner(verbosity=2).run(suite)
