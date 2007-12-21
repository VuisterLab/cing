from cing.core.test.test_All import testAll as testCore
from cing.PluginCode.test.test_All import testAll as testPluginCode
"""
Call by:
python testAll.py
"""

def testAll():
    testCore()   
    testPluginCode()

if __name__ == '__main__':
    testAll()