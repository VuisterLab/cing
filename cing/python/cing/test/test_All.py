from cing.Libs.test.test_All import testAll as testLibs
from cing.PluginCode.test.test_All import testAll as testPluginCode
from cing.Scripts.test.test_All import testAll as testScripts
from cing.core.test.test_All import testAll as testCore

"""
Call by:
python testAll.py
"""

def testOverall():
    testCore()  
    testPluginCode()
    testScripts()
    testLibs()

if __name__ == '__main__':
    testOverall()