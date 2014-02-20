"""
New AwkLike implementation
GWV 2 Oct 2013

"""
import sys
import os
from cing.Libs import NTutils as ntu
from cing.Libs import fpconst


# pylint: disable=R0902
class _AwkLike(list):
    """
    Base class Awk-like functionality

    defines:
        NR
        NF
        self[0 , ... , NF]
        parsing and checking for conditions

    """

    def __init__(self, minLength = -1, commentString = None, minNF = -1,
                 skipHeaderLines = 0, separator = None):
        list.__init__(self)
        self.minLength = minLength
        self.commentString = commentString
        self.minNF = minNF
        self.skipHeaderLines = skipHeaderLines
        self.separator = separator
        self.NR = 0 # pylint: disable=C0103
        self.NF = 0 # pylint: disable=C0103
    #end def

    def __iter__(self):
        return self

    def next(self):
        pass

    def _parseLine(self, line):
        """Return -1 on error
           Return 0 on skip
           Return 1 on parse
        """
        #print '>>', line
        #print '>>', len(self), self

        #check if we need to remove the previous elements
        if len(self) > 0:
            del self[:]
        #end if

        # set self[0] to line
        self.append(line)
        self.NR += 1
        self.NF = 0

        l = len(self[0])
        if l > 0:
            for f in self[0].split(self.separator):
                # Skip everything after the comment?
                if self.commentString and f.startswith(self.commentString):
#                    nTdebug("Skipping fields after comment on line: [%s]" % self.line)
#                    nTdebug("   parsed so far: %s" % repr(self.dollar) )
                    break
#                nTdebug("Appending to parsed: [%s]" % f)
                self.append(f)
                self.NF += 1
            #end for
        #end if

        #print l, self.NR, self.NF, self.minLength

        # test conditions
        if self.minLength >= 0 and l < self.minLength:
            return 0
        elif self.minLength >= 0 and l >= self.minLength:
            return 1
        elif self.skipHeaderLines >= self.NR:
            return 0
        elif self.minNF > 0 and self.NF < self.minNF:
            return 0
        elif self.commentString and self.isComment( self.commentString ):
            return 0
        elif self.minLength < 0 and l >= 0:
            return 1
        #end if
        #print 'returning -1'
        return -1
    #end def

    def float(self, field):
        """Return field converted to float or NaN on error """
        try:
            return float(self[ field ])
        except ValueError:
            ntu.nTerror('AwkLike: expected float for "%s" (file: %s, line %d: "%s")',
                        self[field],
                        self.FILENAME,
                        self.NR,
                        self[0]
                        )
        except IndexError:
            ntu.nTerror('AwkLike: invalid field number "%d" (file: %s, line %d: "%s")',
                        field,
                        self.FILENAME,
                        self.NR,
                        self[0]
                        )
        return fpconst.NaN
    #end def

    def int(self, field):
        """Return field converted to int or NaN on error"""
        try:
            return int(self[ field ])
        except ValueError:
            ntu.nTerror('AwkLike: expected integer for "%s" (file: %s, line %d: "%s")',
                        self[field],
                        self.FILENAME,
                        self.NR,
                        self[0]
                        )
        except IndexError:
            ntu.nTerror('AwkLike: invalid field number "%d" (file: %s, line %d: "%s")',
                        field,
                        self.FILENAME,
                        self.NR,
                        self[0]
                        )
        return fpconst.NaN
    #end def

    def printit(self):
        ntu.nTmessage( '==> FILENAME=%s NR=%d NF=%d' % (self.FILENAME, self.NR, self.NF) )
        for i, field in self.enumerate(): # can't use enumerate as that will loop throught the 'lines'
            ntu.nTmessage('%2d >%s<' % (i, self[i]))
    #end def

    def isComment(self, commentString = '#'):
        """check for commentString on start of line
           return True or False
        """
        if self[0].strip().startswith(commentString):
            return True
        return False

    def isEmpty(self):
        return self.NF == 0

    def enumerate(self):
        for i in range(len(self)): # can't use enumerate() as that will loop throught the 'lines'
            yield((i, self[i]))
    #end def

    #backward compatibility: implement 'dollar' list
    # see evernote:///view/369088/s4/64797df2-2641-459c-bc13-d0da3802c8cf/64797df2-2641-459c-bc13-d0da3802c8cf/
    @property
    def dollar(self):
        return self
    #end def
#end class

#
#==============================================================================
#
class AwkLike(_AwkLike):
    """
    Awk-like functionality, reading from file

    """

    def __init__(self, filename=None, minLength = -1, commentString = None, minNF = -1,
                 skipHeaderLines = 0, separator = None):

        _AwkLike.__init__(self, minLength = minLength, commentString = commentString, minNF = minNF,
                          skipHeaderLines = skipHeaderLines, separator = separator)
        self.f = None

        if filename == None:
            self.f = sys.stdin
            self.FILENAME = 'stdin' # pylint: disable=C0103
        else:
            self.FILENAME = filename
            if not os.path.exists(filename):
                ntu.nTerror("Failed to find: [%s]" % filename)
                self.f = None
            else:
                self.f = open(filename,'r')
        #end if
    #end def

    def __iter__(self):
        """iterations routine
        """
        if not self.f:
            raise StopIteration

        for line in self.f:
            if line[-1:] == '\n':
                line = line[:-1] # strip any \n
            returnVal = self._parseLine( line )
            if returnVal < 0:
                self.close()
                raise StopIteration
            elif returnVal == 0:
                pass
            else:
                yield(self)
            #end if
        #end for
        self.close()
        raise StopIteration
    #end def

    def close(self):
        """internal routine"""
        if not self.f:
            ntu.nTerror("Can't close the file because it was not present.")
            return
        self.f.close()
        self.f = None
    #end if
#end class

#
#==============================================================================
#
class AwkLikeS( _AwkLike ):
    """
        Awk-like functionality on string

    """

    def __init__(self, str, minLength = -1, commentString = None, minNF = -1,
                 skipHeaderLines = 0, separator = None):

        _AwkLike.__init__(self, minLength = minLength, commentString = commentString, minNF = minNF,
                 skipHeaderLines = skipHeaderLines, separator = separator)

        if (not str) or (len(str)<=0):
            self.lines = None
            return None

        self.lines = str.splitlines()
        self.MAX_NR = len( self.lines) # pylint: disable=C0103
        self.FILENAME = 'string' # pylint: disable=C0103
    #end def

    def __iter__(self):
        for line in self.lines:
            returnVal = self._parseLine(line)
            if returnVal == -1:
                raise StopIteration
            elif returnVal == 0:
                pass
            else:
                yield(self)
            #end if
        #end for
    #end def
#end class

#
#==============================================================================
#

## testing only here
if __name__ == '__main__':

    txt = """
# From YASARA BioTools
# GWV 20130528: Added path routines
# Visit www.yasara.org for more...
# Copyright by Elmar Krieger
from glob import glob
from glob import glob1
from optparse import OptionParser
from string import digits
import fnmatch
import os
import re
import shutil
import sys
import time
import zipfile
10 1 2
x 10 5


# This program is free soft"""

    for line in AwkLikeS(txt):
        print line
