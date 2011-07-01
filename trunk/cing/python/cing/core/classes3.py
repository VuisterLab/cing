'''
Created on Aug 30, 2010

Simple class that doesn't import NTutils or sml in order to avoid cyclic behaviour.
'''
from cing.core.constants import * #@UnusedWildImport
#from cing.core.sml import SMLhandler

class SMLhandled(): # pylint: disable=R0903
    'The subclass has an SMLhandler. For example NTlist'
    def __init__(self):
#        self.SMLhandler = SMLhandler(DEFAULT_SML_HANDLER_STRING) # Just to make it official.
        if not hasattr(self, 'SMLhandler'): # it might already be initialize in which case nothing is done here.
            self.SMLhandler = None
    # end def
# end class

class Formatted(): # pylint: disable=R0903
    'Can be formatted as in having the __FORMAT__ attribute. E.g. NTlist'
    def __init__(self):
        self.__FORMAT__ = None
    # end def
# end class

class Lister(Formatted):
    """Example from 'Learning Python from O'Reilly publisher'"""
    MAX_LINE_SIZE_VALUE = 80 # who wants to see long lines of gibberish
    
    def __init__(self):
        Formatted.__init__(self)
            
    def __repr__(self):
        return ("<Instance of %s, address %s:\n%s>" %
           (self.__class__.__name__, id(self), self.attrnames()))

    def attrnames(self):
        result=''
        keys = self.__dict__.keys()
        keys.sort()
        for attr in keys:
            if attr[:2] == "__":
                result = result + "\tname %s=<built-in>\n" % attr
            else:
                valueStr = '%s' % self.__dict__[attr]
                if len(valueStr) > self.MAX_LINE_SIZE_VALUE:
                    valueStr = valueStr[:self.MAX_LINE_SIZE_VALUE]
                result = result + "\tname %s=%s\n" % (attr, valueStr)
        return result
    #end def
#end class
