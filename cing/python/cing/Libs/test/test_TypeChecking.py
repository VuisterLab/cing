from cing.Libs.TypeChecking import check_int
from unittest import TestCase
import unittest

class AllChecks(TestCase):
        
    def test(self):
        s="a string instead of int"
        i=s
        self.assertRaises(TypeError, check_int, i)
        i=1
        self.assertFalse( check_int( i ))
#        i=s
#        self.assertFalse( check_int( i )) # causes a TypeError
        
if __name__ == "__main__":
    unittest.main()
