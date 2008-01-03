from cing.PluginCode.test.test_All import testAll as testPluginCode
from cing.Scripts.test.test_All import testAll as testScripts
from cing.Libs.test.test_All import testAll as testLibs

from cing.core.test.test_All import testAll #@UnresolvedImport

"""
Call by:
python testAll.py
"""

def testOverall():
    testAll()  
    testPluginCode()
    testScripts()
    testLibs()

if __name__ == '__main__':
    testOverall()