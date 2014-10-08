# pylint: disable=C0302
"""
NMR Tools utilities
"""
import cing
import cing.constants as constants
import cing.definitions as cdefs
from cing.core import pid
import cing.Libs.xmlTools as xmlTools
from cing.Libs.xmlTools import quote
import cing.Libs.jsonTools as jsonTools

import cing.Libs.io as io
from cing.Libs.io import fprintf
from cing.Libs.io import sprintf  #unused here but for compatibility
from cing.Libs.io import printf   #unused here but for compatibility
from cing.Libs.io import mprintf  #unused here but for compatibility


from cing.constants import NaNstring
from cing.definitions import verbosityDebug
from cing.definitions import verbosityDefault #@UnusedImport actually used by wild imports of this module (NTutils)
from cing.definitions import verbosityDetail
from cing.definitions import verbosityError
from cing.definitions import verbosityNothing
from cing.definitions import verbosityOutput
from cing.definitions import verbosityWarning

from cing.Libs.disk import mkdirs #@UnusedImport
from cing.Libs.fpconst import NaN
from cing.Libs.fpconst import isNaN
from cing.core.classes3 import Lister
from cing.core.classes3 import SMLhandled
from cing.constants import * #@UnusedWildImport
from copy import deepcopy
from fnmatch import fnmatch
from gzip import GzipFile
from numpy.core import fromnumeric
from numpy.core.fromnumeric import amax
from numpy.core.fromnumeric import amin
from os import makedirs
from os.path import dirname
from os.path import exists
from os.path import expanduser
from os.path import normpath
from random import random #@UnusedImport for outside this module
from subprocess import PIPE
from subprocess import Popen

import array
import datetime
import locale # used in nrgCingRdb @UnusedImport
import math
import optparse
import os
import pydoc
import re
from string  import find
import sys
import time


FAC = 180.0/math.pi
SMALLEST_BMRB_ID = 3
LARGEST_BMRB_ID = 99*1000

# For plotting with thousand separators.
# Disabled in an emergency fix for this failed after upgrade Mac Ports to 2.6.7
# Not important enough to reenable.
#locale.setlocale(locale.LC_ALL, "")

# def quote(inputString):
#     "return a single or double quoted string"
#     single = (find(inputString, "'") >= 0)
#     double = (find(inputString, '"') >= 0)
#     if single and double:
#         nTerror("in quote: both single and double quotes in [%s]" % inputString)
#         return None
#     if double:
#         return "'" + inputString + "'"
#     return '"' + inputString + '"'
# #end def

# pylint: disable=R0902
class NTlist(list, Lister, SMLhandled):
    """
    NTlist: list which is callable:
      __call__(index=-1) index<0: returns last item added or None for empty list
                         index>=0: returns item 'index'

    Methods:
      index( item ):    returns -1 when item is not present
      push( item ):     pushes item at position 0 (front) of list
      pop( index=0 ):   pops item at position index
      last():           returns last element of list or None on empty list
      replace(item, newItem ):
                        replaces item with newItem

    Methods for numeric lists (None elements ignored):
      average():        returns (av,sd,n) triple of a numeric list
                        stores av,sd,n as attributes of the list
      cAverage(min=0,max=360,radians=0):
                        returns (cav, cv, cn) triple of a numeric list
                        stores cav,cv,cn as attributes of the list
      min()             Returns minimum value or None on emptylist.
      max()             Returns maximum value or None on empty list.
      minItem()         Returns (index,minimumValue) tuple or (None,None) on emptylist.
      maxItem()         Returns (index,maximumValue) tuple or (None,None) on emptylist.
      sum( start=0 )    Return sum of list.
      sumsq( start=0 )  Return squared sum of list.
      limit( min, max): limit between min and max by adding/subtracting
                        (max-min)

    Other methods as in list

    """
    #--------------------------------------------------------------
    # Basic methods
    #--------------------------------------------------------------
    def __init__(self, *args):
        list.__init__(self)
        Lister.__init__(self)
        SMLhandled.__init__(self)

        self.current = None
#        if args: # handle case when called with None type. Failes as of yet.
        for a in args:
            self.append(a)
        #end for
        self.av = None
        self.sd = None
        self.name = None # Assumed by SMLhandler.list2SML in case of e.g.

        self.cav = None
        self.cv  = None
        self.cn  = None

        # DistanceRestraintList
        self.status = None # same
        self.n = 0
    #end def

    def clear(self):
        'Total wipe out.'
        self.__init__()
    # end def

    def copy(self):
        """Generate a copy with 'shallow' references"""
        result = NTlist()
        result.addList(self)
        return result
    # end def

    def __call__(self, index=-1):
        if index < 0:
            return self.current
        else:
            return self[ index ]
        #end if
    #end def

    def __getslice__(self, i, j):
        """To implement slicing"""
        return NTlist(*list.__getslice__(self, i, j))
    #end def

    def __getitem__(self, item):
        """To implement extended slicing"""
        if type(item) == slice:
            return NTlist(*list.__getitem__(self, item))
        else:
            return list.__getitem__(self, item)
    #end def

    def __add__(self, other):
        return NTlist(*list.__add__(self, other))
    #end def

    def doc(self):
        """
        Generate pydoc output of self
        """
        pydoc.doc(self, title='%s')
    #end def

    def lenRecursive(self, max_depth = 5):
        "convenience method"
        return lenRecursive(self, max_depth = max_depth )
    # end def

    def statsFloat(self):
        """Return standard statistics in case the data is interpreted as floats.
        Assumes numeric list, None elements ignored.
        """
        fmt = '%8.3f'
        self.average()
        text = """Count              %8d
Average            %s
Standard deviation %s
Minimum            %s
Maximum            %s
Sum                %s""" % (
        self.n,
        val2Str(self.av, fmt),
        val2Str(self.sd, fmt),
        val2Str(self.min(), fmt),
        val2Str(self.max(), fmt),
        val2Str(self.sum(), fmt) )
        return text

    def getConsensus(self, minFraction=1., useLargest=False):
        'Convenience method.'
        return self.setConsensus(minFraction=minFraction, useLargest=useLargest)
#        w = getattr(self, CONSENSUS_STR)
#        print 'w: ', w
#        return w
    # end def

    def setConsensus(self, minFraction=1., useLargest=False):
        """Where there are only the same values set the consensus to it
        otherwise set it to None.
        They don't all need to be the same, at least the given fraction
        should be the same. If the fraction is set to .5 or lower the result
        is undefined.

        Return consensus or False if set to None. Consensus can be None.
        """
        setattr(self, CONSENSUS_STR, None)
        count = {}
        n = len(self)
        minCount = minFraction * n
#        print 'minCount: ', minCount
        for v in self:
            count.setdefault(v, 0)
            count[v] +=1
#            print 'count: ', count
        for v in count:
#            print 'considering v: ', v
            if count[v] >= minCount:
                setattr(self, CONSENSUS_STR, v)
#                print 'returning v: ', v
                return v
        if not useLargest:
            return False
        v = getKeyWithLargestCount(count) # could be inlined for speed of course.
        return v
    #end def

    def append(self, *items):
        for item in items:
            list.append(self, item)
            self.current = item
        #end for
    #end def

    def add(self, *items):
        '''Add a new item to a list only if not there before, like 'add' method
           for set() - AWSS 24OCT07'''
        for item in items:
            if not self.count(item):
                list.append(self, item)
                self.current = item
            #end if
        #end for
    #end def

    def addList(self, list_new):
        'Add given list to self.'
        for item in list_new:
            list.append(self, item)
            self.current = item
        #end for
    #end def

    def insert(self, i, item):
        'Convenience method.'
        list.insert(self, i, item)
        self.current = item
    #end def

    def remove(self, item):
        'Convenience method.'
        list.remove(self, item)
        if item == self.current:
            self.current = self.last()
        #end if
    #end def

    def removeIfPresent(self, item):
        'Look up by index and removed.'
        if self.index(item)>=0:
            self.remove(item)
        #end if
    #end def

    def replace(self, item, newItem):
        'Convenience method.'
        index = self.index(item)
        if (index < 0):
            return
        self.remove(item)
        self.insert(index, newItem)
    #end def

    def index(self, item):
        """
        Notes that this method is now twice as fast.
        This was a very rate limiting piece of code when a chain
        had many residues (E.g. an X-ray structure with many waters).
        """
        try:
            return list.index(self, item)
        except ValueError:
            pass
        return -1
#        if item in self:
#            return list.index( self, item )
#        return -1
    #end def

    def last(self):
        'Returns None if no item is present or [-1]'
        myLength = len(self)
        if (myLength == 0):
            return None
        #end if
        return self[myLength-1]  # equivalent to self[-1:][0] or simply self[-1]
    #end def

    def push(self, item):
        'Insert at position 0'
        self.insert(0, item)
    #end def

    def pop(self, index=0):
        "Return index'ed item from list or None on empty list"
        if len(self) == 0:
            return None
        item = list.pop(self, index)
        if item == self.current:
            self.current = self.last()
        #end if
        return item
    #end def

    def zap(self, *byItems):
        """use nTzap to yield a new list from self, extracting byItem from each
           element of self.
        """
        return nTzap(self, *byItems)
    #end def

    def selectByItems(self, *byItems):
        """use zap to yield a new sublist from self where items were found.
        E.g.        vadl = NTdb.allAtomDefs().selectByItems( 'type', 'C_VIN' )
        gives a list of all vinyl typed atom definitions in CING.
        """
        if len(byItems) < 2:
            nTwarning("Use NTlist.selectByItems only for multiple levels. Otherwise use withProperties??")
            return
        result = NTlist()
        byItemsTrunc = byItems[:-1]
        fullList = zip( self, self.zap(*byItemsTrunc))
        finalItemValue = byItems[-1]
        for item, value in fullList:
            if value != finalItemValue:
                continue
            result.append(item)
        return result
    #end def

    def removeDuplicates(self, useVersion = 2):
        """
        Removes all duplicate from self so this is an in-place operation.
        Can be optimized when needed by doing a sorted lookup table; It is extremely slow to take a slice every time.
        Return the duplicate list when using version 2 but None otherwise.
        """

        if len(self) <= 1:
            return
#        useVersion = 2
        if useVersion == 0:
            i = 1
            while i < len(self):
#                nTdebug( '>i=%s     len=%s     item=%s' % ( i, len(self), self[i]))
                if self[i] in self[0:i]:
#                    nTdebug ( '>popping %s' %  i )
                    self.pop(i)
                else:
                    i += 1
            #end while
        elif useVersion == 1:
            i = len(self) - 1
            while i > 0:
#                nTdebug( '>i=%s     len=%s     item=%s' % ( i, len(self), self[i]))
                iObject = self[i] # for speed take a convenience variable.
                objectIfound = False
                for j in range(i):
#                    nTdebug ( '>Checking for j = %s' %  j )
                    if iObject == self[j]:
#                        nTdebug ( 'objectIfound i = %s' %  i )
                        objectIfound = True
                        break # only breaks inner loop over j
                    # end if
                # end for
                if objectIfound:
#                    nTdebug ( '>popping i = %s' %  i )
#                    del iObject # fails
                    del self[i]
                # end if
                i -= 1
            #end while
        else:
            # Only add new items to a temporary list
            duplicateList = NTlist()
            seenDictionary = {}
            result = []
            for i in range(len(self)):
                if not seenDictionary.has_key(self[i]):
                    seenDictionary[ self[i] ] = None
                    result.append( self[i] )
                else:
                    duplicateList.append( self[i] )
            #end for
            del self[0:len(self)]
            self.addList(result)
            return duplicateList
        # end if
    #end def

    def difference(self, other):
        """Returns a new set of self minus other
        This is a common operation. Order in list will not be altered.
        Capitalization will not be altered.
        If duplicates are present in this/self list then they might not all be removed (multiset semantics).
        """
        result = deepcopy(self)
        hashedSelf = NTdict() # use in order to speed up operations.
        hashedSelf.appendFromList(self)
#        nTdebug("Created hash of self with elements: %s" % len(hashedSelf.keys()))
        for element in other:
#            nTdebug("difference: Trying element: %s" % element)
            if hashedSelf.has_key(element):
                idx = result.index(element)
                if idx < 0:
                    nTcodeerror("Skipping element [%s] in other because after all it was not in result" % element)
                del result[idx]
        return result
    # end def

    def union(self, other):
        """Returns a new set of self plus other
        This is a common operation. Order in list will not be altered.
        So by examples at: http://en.wikipedia.org/wiki/Multiset

        { 1, 1, 1, 3 } intersection { 1, 1, 2 } = { 1, 1 }         # intersection (upside down letter u)
        { 1, 1 } unionMinus { 1, 2 }            = { 1, 1, 2 }      # union because only one 1 is present in the second set one 1 from the first set gets added. This may be implemented in another union
        { 1, 1 } unionPlus  { 1, 2 }            = { 1, 1, 1, 2 }   # union (letter u) -This method-.
        { 1, 2, 3} \ {2,3,4}                    = { 1 }            # difference (backslash) An example from http://en.wikipedia.org/wiki/Difference_(set_theory)
        """
        result = deepcopy(self)
        hashedSelf = NTdict() # use in order to speed up operations.
        hashedSelf.appendFromList(self)
#        nTdebug("Created hash of self with elements: %s" % len(hashedSelf.keys()))
        for element in other:
#            nTdebug("union: Trying element: %s" % element)
            if not hashedSelf.has_key(element):
                result.append(element)
        return result

    def intersection(self, other):
        """Returns a new set of self minus other
        This is a common operation. Order in list will not be altered.
        Capitalization will not be altered.
        If duplicates are present in this/self list then they might not all be removed (multiset semantics).
        """
        result = NTlist()
        hashedOther = NTdict() # use in order to speed up operations.
        hashedOther.appendFromList(other)
#        nTdebug("Created hash of other with elements: %s" % len(hashedOther.keys()))
        for element in self:
#            nTdebug("intersection: Trying element: %s" % element)
            if hashedOther.has_key(element):
                result.append(element)
        return result
    # end def


    def reorder(self, indices):
        """Return a new NTlist, ordered according to indices or None on error
        """
        if (len(indices) != len(self)):
            return None

        result = NTlist()
        for idx in indices:
            result.append(self[idx])
        #end for
        return result
    #end def

    def sort(self, byItem=None ):
        "Sort the list byItem"
        NTsort( self, byItem, inplace=True)
        return self
    #end def

    def reverse(self):
        """Reverse the list, returning self. Regular list does not return anything.

        This allows for
        e.g.
            myList.sort('id').reverse()[0]
        """
        list.reverse(self)
        return self
    #end def

    def setCurrent(self, item):
        'Silent function setting item as current if present.'
        if item in self:
            self.current = item
        #end if
    #end def

    def getDeepByKeysOrDefault(self, default, *keyList):
        'Convenience method.'
        result = self.getDeepByKeys(*keyList)
        if result == None:
            return default
        return result
    # end def

    def getDeepByKeys(self, *keyList):
        """Return arbitrary deep element or None if key is absent at some point.
        The essence here is silence."""
        lk = len(keyList)
#        nTdebug("Now in getDeepByKeys for keylist length: %d" % lk)
        if not lk:
#            nTdebug("Asked for a get on a dictionary without a key")
            return None
        key = keyList[0]

        if isinstance(key, int):
            if key >= len(self):
                nTwarning("int key in NTlist.getDeepByKeys too large for this NTlist: %r" % key)
                return None
            value = self[key]
        else:
            if not hasattr(self, key):
                nTwarning("no int key/attribute in NTlist.getDeepByKeys: %r" % key)
                return None
            value = getattr(self, key)
            # end if
        # end else

        if lk == 1:
#            nTdebug("value : " + repr(value))
            return value
        if hasattr(value, 'getDeepByKeys'):
#            nTdebug("Going one level deeper")
            reducedKeyList = keyList[1:]
#            nTdebug("In NTdict.getDeepByKeys the value is not a NTdict or subclass instance,"+
#                    " but there still are keys to go for digging deeper")
#            nTdebug(" for value : [" + repr(value) +']')
#            nTdebug(" type value: [" + repr(type(value)) +']')
            return value.getDeepByKeys(*reducedKeyList)
        return None
    # end def

    def average(self, byItem=None):
        """return (av,sd,n) tuple of self
           Store av,sd,n as attributes of self
           Assumes numeric list, None elements ignored
           See also nTaverage routine
        """
        self.av, self.sd, self.n = nTaverage(self, byItem)
        return (self.av, self.sd, self.n)
    #end def

    def average2(self, byItem=None, fmt='%f +- %f' ):
        """Return average as NTvalue object.
           Store av,sd,n as attributes of self
           Assumes numeric list, None elements ignored.
           See also nTaverage2 routine
       """
        result = nTaverage2( self, byItem, fmt=fmt )
        self.av = result.av
        self.sd = result.sd
        self.n  = self.n
        return result
    #end def

    def cAverage(self, minValue=0.0, maxValue=360.0, radians = 0, byItem=None):
        """ Circular average.
           return (cav,cv,cn) tuple of a list
           return cav on minValue-maxValue interval (that has to be spaced
           360 or 2pi depending on radians )
           Store cav,cv,cn as attributes of self
           Assumes numeric list, None elements ignored.
           If only None elements are found the cav, cv, cn will be set tO:
               ( None, None, 0)
           See also nTcAverage routine
        """
        self.cav, self.cv, self.cn = nTcAverage(self, minValue, maxValue, radians, byItem)
        return (self.cav, self.cv, self.cn)
    #end def

    def min(self):
        'Silent convenience method.'
        if len(self) == 0:
            return None
        #end if
        return min(self)
    #end def

    def max(self):
        'Silent convenience method.'
        if len(self) == 0:
            return None
        #end if
        return max(self)
    #end def

    def sum(self, start=0):
        'Starting from given point sum the elements as if they are numbers.'
        return sum(self, start)
    #end def

    def sumsq(self, start=0):
        'Starting from given point sum the square of the elements as if they are numbers.'
        return sum(map(nTsq, self), start)
    #end def

    def rms(self):
        "Return the rms average value."
#        nTdebug("NTlist serie: %r" % self)
        self.n = len(self)
        if not self.n:
            return NaN
        sumsq = float(self.sumsq(0)) # continue with float arithmetics.
        result = math.sqrt(sumsq/self.n)
#        nTdebug("result: %s" % result)
        return result
    #end def

    def limit(self, minVal, maxVal, byItem=None):
        """Use nTlimit on self, return self
        """
        nTlimit(self, minVal, maxVal, byItem)
        return self
    #end def

    def __str__(self):
        'Formatting, str, XML etc.'
        if len(self) == 0:
            return '[]'
        #end if

        msg = '['
        for item in self:
            msg = msg + str(item) +', '
        #end for
        msg = msg[:-2]+']'
        return msg
    #end def

    def __repr__(self):
        'gv 19 Jun 08: reintroduced functionality, but shorter'
        msg = list.__repr__(self)
        return 'NTlist(' + msg[1:-1] + ')'
    #end def

    def format(self, fmt = None):
        """
        Use the given format string or the self's __FORMAT__
        to return a string.
        It will call recursively all elements of a list.
        """
        if len(self) == 0:
            return ''
        #end if

#        if (fmt == None and hasattr(self, '__FORMAT__')):
#            fmt = self.__FORMAT__
#        #end if
        if fmt == None:
            fmt = self.__FORMAT__ # Garanteed now.
        #end if
        msg = ''
        for item in self:
            if fmt:
                if isinstance(item, list):
                    for subitem in item:
                        msg += fmt % subitem
                else:
                    msg += fmt % item
            else:
                msg += repr(item) +' '
            #end if
        #end for
        return msg
    #end def

    def formatAll(self, start=0, stop=None):
        """
        Generate string with every element of self on a single line using the format() method of the items
        Optionally run from start to stop
        """
        if stop == None:
            stop = len(self)
        msg = ''
        for i in range(start, stop):
            obj = self[i]
            if hasattr(obj, 'format'):
                msg +=  obj.format() + '\n'
            else:
                msg +=  str(obj) + '\n'
        #end for
        return msg
    #end def


#    def formatHtml(self):
#        if not self.format():
#            return ''
#        #end if
#        htmlLine = ''
#        formatLine = self.format().split('\n')[:-1]
#        for item in formatLine:
#            htmlLine = htmlLine + '<a> %s</a><br/>' % item
#        #end for
#        return htmlLine
#    #end def

    # def toXML(self, depth=0, stream=sys.stdout, indent='\t', lineEnd='\n'):
    #     """
    #     Write XML-representation of elements of self to stream
    #     """
    #     nTindent(depth, stream, indent)
    #     fprintf(stream, "<NTlist>")
    #     fprintf(stream, lineEnd)
    #
    #     for a in self:
    #         xmlTools.nTtoXML(a, depth+1, stream, indent, lineEnd)
    #     #end for
    #     nTindent(depth, stream, indent)
    #     fprintf(stream, "</NTlist>")
    #     fprintf(stream, lineEnd)
    # #end def

    def toSML(self, stream=sys.stdout):
        'Write by looked-up handler if available. An implementing class needs to have one defined it in order to be allowed to be called.'
        if not hasattr(NTlist, 'SMLhandler'):
            nTerror('NTlist.toSML: no SMLhandler defined')
            return
        #end if
#        NTlist.SMLhandler.toSML(self, stream) # TODO: check if this can be rewritten.
        self.SMLhandler.toSML(self, stream)
    #end def
#end class



def nTfill(value, n):
    """Return a NTlist instance with n elements of value"""
    result = NTlist()
    i=0
    while i<n:
        result.append(value)
        i +=1
    #end while
    return result
#end def

def nThistogram(theList, low, high, bins):
    """Return a histogram of theList"""
    if bins < 1:
        return None

    his = nTfill(0, bins) # Returns NTlist
    binSize = (high-low)/bins

    his.low = low           # pylint: disable=W0201
    his.high = high         # pylint: disable=W0201
    his.bins = bins         # pylint: disable=W0201
    his.binSize= binSize    # pylint: disable=W0201


    tmp = theList[:] # creates a copy.
    tmp.sort()

    # reworked logic a bit.
    binIdx = 0
    currentBinlow  = low+binIdx*binSize
    currentBinhigh = currentBinlow + binSize
    for item in tmp:
        if item < currentBinlow:
            continue
        if item >= currentBinlow and item < currentBinhigh:
            his[binIdx] += 1
            continue
        while binIdx < bins and item > currentBinhigh:
            binIdx += 1
            currentBinlow  = low+binIdx*binSize
            currentBinhigh = currentBinlow + binSize
        if binIdx < bins:
            his[binIdx] += 1
    return his
#end def


class NTvector(list):
    """Lightweight class to implement a few vector operations
       Numeric or Numpy has compiled code; this is a python
       only class based on list
       See also:
       http://www.python.org/doc/2.4/ref/numeric-types.html
    """

    def __init__(self, *values):
        list.__init__(self)
        for v in values:
            self.append(v)
        #end for
        self.fmt = '%.2f'
    #end def

    def length(self):
        'Mathematical size of a vector.'
        result = 0
        for i in range(0, len(self)):
            result += self[i]*self[i]
        #end for
        return math.sqrt(result)
    #end def

    def norm(self):
        'NTvector norm of a vector. Unused in CING. Watch out using it for the first time then.'
        lgth = self.length()
        result = NTvector()
        for i in range(0, len(self)):
            result.append(self[i]/lgth)
        #end for
        return result
    #end def

    def polar(self, radians = False):
        """
        Return triple of polar coordinates (r,u,v)
        with:
          -pi<=u<=pi
          -pi/2<=v<=pi/2

          x = rcos(v)cos(u)
          y = rcos(v)sin(u)
          z = rsin(v)
        """
        if len(self) != 3:
            return None
        fac = 1.0
        if not radians:
            fac = 180.0/math.pi

        r = self.length()
        u = math.atan2(self[1], self[0])
#        if u<0: u+=math.pi*2.0
        v = math.asin(self[2]/r)
        return r, u*fac, v*fac
    #end def

    def setFromPolar(self, polarCoordinates, radians = False):
        """
        set vector using polarCoordinates (r,u,v)
        with:
          0<=u<=2pi
          -pi/2<=v<=pi/2

          x = rcos(v)cos(u)
          y = rcos(v)sin(u)
          z = rsin(v)
        """
        if len(self) != 3:
            return
        fac = 1.0
        if not radians:
            fac = math.pi/180.0

        r, u, v = polarCoordinates
        self[0] = r*math.cos(v*fac)*math.cos(u*fac)
        self[1] = r*math.cos(v*fac)*math.sin(u*fac)
        self[2] = r*math.sin(v*fac)
    #end def

    def rotX(self, angle, radians=False):
        'Rotate around x-axis by given amount in degrees by default.'
        if len(self) != 3:
            return None

        fac = 1.0
        if not radians:
            fac = math.pi/180.0
        result = NTvector()
        m = [ NTvector(1.0, 0.0, 0.0),
              NTvector(0.0, math.cos(angle*fac), -math.sin(angle*fac)),
              NTvector(0.0, math.sin(angle*fac), math.cos(angle*fac))
            ]
        for v in m:
            result.append(v.dot(self))
        #end for
        return result
    #end def

    def rotY(self, angle, radians=False):
        'Rotate around y-axis by given amount in degrees by default.'
        if len(self) != 3:
            return None

        fac = 1.0
        if not radians:
            fac = math.pi/180.0
        result = NTvector()
        m = [ NTvector(math.cos(angle*fac), 0.0, -math.sin(angle*fac)),
              NTvector(0.0, 1.0, 0.0),
              NTvector(math.sin(angle*fac), 0.0, math.cos(angle*fac))
            ]
        for v in m:
            result.append(v.dot(self))
        #end for
        return result
    #end def

    def rotZ(self, angle, radians=False):
        'Rotate around z-axis by given amount in degrees by default.'
        if len(self) != 3:
            return None

        fac = 1.0
        if not radians:
            fac = math.pi/180.0
        result = NTvector()
        m = [
              NTvector(math.cos(angle*fac), -math.sin(angle*fac), 0.0),
              NTvector(math.sin(angle*fac), math.cos(angle*fac), 0.0),
              NTvector(0.0, 0.0, 1.0),
            ]
        for v in m:
            result.append(v.dot(self))
        #end for
        return result
    #end def

    def dot(self, other):
        'Return scalar for dot product.'
        myLength = len(self)
        if myLength != len(other):
            return None
        result = 0
        for i in range(0, myLength):
            result += self[i]*other[i]
        #end for
        return result
    #end def

    def cross(self, other):
        """
        Return cross vector spanned by self and other
          result = self x other
        or None on error
        Definitions from Kreyszig, Advanced Enginering Mathematics, 4th edition, Wiley and Sons, p273
        NB: Only 3D vectors
        """
        myLength = len(self)
        if myLength != 3:
            return None
        if myLength != len(other):
            return None

        result = NTvector()
        result.append(self[1]*other[2]-self[2]*other[1]) # x-coordinate
        result.append(self[2]*other[0]-self[0]*other[2]) # y-coordinate
        result.append(self[0]*other[1]-self[1]*other[0]) # z-coordinate
        return result
    #end def


#    def triple( self, b, c):
#        """
#        return triple product of self,b,c
#        or None on error
#        """
#        myLength = len(self)
#        if myLength != 3: return None
#        if myLength != len(b): return None
#        if myLength != len(c): return None
#        return    self[0] * (b[1]*c[2]-b[2]*c[1] )
#                - self[1] * (b[0]*c[2]-b[2]*c[0] )
#                + self[2] * (b[0]*c[1]-b[1]*c[0] )
    # end if

    def angle(self, other, radians = False):
        """
        return angle spanned by self and other
        or None on error
        range = [0, pi]
        positive angle is counterclockwise (to be in-line with 'polar' methods
        and atan2 routines).
        """
        myLength = len(self)
        if myLength != len(other):
            return None

        fac = 1.0
        if not radians:
            fac = 180.0/math.pi


        c = self.dot(other) /(self.length()*other.length())
        c = min(c, 1.0)
        c = max(c, -1.0)
        angle = math.acos(c)
        return (angle * fac)
    #end def

    def distance(self, other):
        """
        return distance between self and other
        or None on error
        """
        myLength = len(self)
        if myLength != len(other):
            return None
        diff = self-other
        return diff.length()
    #end def

    def __add__(self, other):
        myLength = len(self)
        if myLength != len(other):
            return None
        result = NTvector()
        for i in range(0, myLength):
            result.append(self[i]+other[i])
        #end for
        return result
    #end def

    def __radd__(self, other):
        myLength = len(self)
        if myLength != len(other):
            return None
        result = NTvector()
        for i in range(0, myLength):
            result.append(self[i]+other[i])
        #end for
        return result
    #end def

    def __iadd__(self, other):
        myLength = len(self)
        if myLength != len(other):
            return None
        for i in range(0, myLength):
            self[i] += other[i]
        #end for
        return self
    #end def

    def __sub__(self, other):
        myLength = len(self)
        if myLength != len(other):
            return None
        result = NTvector()
        for i in range(0, myLength):
            result.append(self[i]-other[i])
        #end for
        return result
    #end def

    def __rsub__(self, other):
        myLength = len(self)
        if myLength != len(other):
            return None
        result = NTvector()
        for i in range(0, myLength):
            result.append(other[i]-self[i])
        #end for
        return result
    #end def

    def __isub__(self, other):
        myLength = len(self)
        if myLength != len(other):
            return None
        for i in range(0, myLength):
            self[i] -= other[i]
        #end for
        return self
    #end def

    def __neg__(self):
        myLength = len(self)
        result = NTvector()
        for i in range(0, myLength):
            result.append(-self[i])
        #end for
        return result
    #end def

    def __pos__(self):
        myLength = len(self)
        result = NTvector()
        for i in range(0, myLength):
            result.append(self[i])
        #end for
        return result
    #end def
    #--------------------------------------------------------------
    # Formatting, str, XML etc
    #--------------------------------------------------------------
    def __str__(self):
        if len(self) == 0:
            return '(V:)'
        #end if

        msg = '(V: '
        for item in self:
            msg += sprintf(self.fmt, item) +', '
        #end for
        msg = msg[:-2]+')'
        return msg
    #end def
#end class


class NTset(NTlist):
    """
    Class to define sets; i.e. list of objects
    A set is equal to another set if they have at least one element in common
    """

    def __eq__(self, other):
        if other == None:
            return False
        else:
            for item in self:
                if item in other:     # maybe to be replaced by (faster?):  if other.has_key( item ):
                    return True
            #end for
            return False
        #end if
    #end def

    def __ne__(self, other):
        return not (self == other)
    #end def

    def __str__(self):

        if len(self) == 0:
            return '//'

        string = '/'
        for item in self:
            string = string + str(item) +', '
        string = string[:-2]+'/'
        return string
    #end def

    # def toXML(self, depth=0, stream=sys.stdout, indent='\t', lineEnd='\n'):
    #     """
    #     Write XML-representation of elements of self to stream
    #     """
    #     nTindent(depth, stream, indent)
    #     fprintf(stream, "<NTset>")
    #     fprintf(stream, lineEnd)
    #
    #     for a in self:
    #         xmlTools.nTtoXML(a, depth+1, stream, indent, lineEnd)
    #     #end for
    #     nTindent(depth, stream, indent)
    #     fprintf(stream, "</NTset>")
    #     fprintf(stream, lineEnd)
    # #end def
#end class


class Odict(dict):
    """ Ordered dictionary.
        Adapted from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747
    """
    def __init__(self, *args):
        self._keys = []
        dict.__init__(self)
        self.append( *args )

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._keys.remove(key)
    # end if

    def __setitem__(self, key, item):
        if not dict.has_key(self, key):
            self._keys.append(key)
        dict.__setitem__(self, key, item)
    # end if

    def clear(self):
        dict.clear(self)
        self._keys = []
    # end if

    def copy(self):
        newInstance = Odict()
        newInstance.update(self)
        return newInstance
    # end if

    def keys(self):
        """
        methods iterkeys(), values(), itervalues(), items() and iteritems()
        now all decend from method keys().
        """
        return self._keys
    # end def

    def iterkeys( self ):
        for key in self.keys():
            yield key
    # end def

    def values( self ):
        return map( self.get, self.keys() )
    # end def

    def itervalues( self ):
        for value in self.values():
            yield value
    # end def

    def items( self ):
        return zip( self.keys(), self.values() )
    # end def

    def iteritems( self ):
        for item in self.items():
            yield item
    # end def

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)
    # end def

    def setdefault(self, key, failobj = None):
        if key not in self._keys:
            self._keys.append(key)
        return dict.setdefault(self, key, failobj)
    # end def

    def update(self, myDict):
        myDict.update(self, myDict)
        for key in myDict.keys():
            if key not in self._keys:
                self._keys.append(key)
    # end def

    def append( self, *items):
        'Add the given arguments to self.'
        for key, value in items:
            self.__setitem__( key, value )
    # end def
#end class


NTdictObjectId = 0
# Variables to limit recursion and prevent cycles in __repr__() call
NTdictDepth    = 0
NTdictMaxDepth = 1
NTdictCycles   = []
class NTdict(dict):
    """
        class NTdict: Base class for all mapping NT objects.

        Keys can be referenced as in dictionary methods, or as an attribute; e.g.

            aap = NTdict( noot=3, mies=4, kees='not awake' )
            print aap['noot']
            > 3
            print aap.noot
            > 3

        Hashing and compare implemented.

        Methods:
            __call__( **kwds )                            Calling will update kwds and return self.

            format( format=None )                         Format the object according to format or __FORMAT__ (when
                                                          format == None) attribute.
            keysformat()                                  Set __FORMAT__ to include all keys.
            printAttr( hidden=0 )                         Print all attributes to stream (mainly for debugging purposes).
                                                          Also print 'hidden' attributes when hidden!=0.

            getdefault( key, defaultKey )                 Return self[key] if key exists, self[defaultKey] otherwise.
            uniqueKey( key )                              Return an unique key derived from key.

            saveXML( *attrs ):                            Add attrs to the list to save in XML format.
            toXML( stream=sys.stdout )                    Write XML code of object to stream; recursively decend; i.e.
                                                          cycles will wreck this routine.

        Inherited methods:
            most methods defined as in dict()

            methods __iter__(),iterkeys(), values(), itervalues(), items() and iteritems()
            len(), popitem(), clear(), update() all decend from method keys().
            Hence when subclassing, overriding the keys() method effectively implements the other methods

            popitem() returns None upon empty dictionary

        Reserved attributes:
            attribute '__CLASS__'                         is reserved to store a class identifier; useful for subtyping
            attribute '__OBJECTID__'                      is reserved to store an unique object id
            attribute '__FORMAT__'                        is reserved to store format for method format()
            attribute '__HIDDEN__'                        is reserved to store the hidden attributes
            attribute '__SAVEXML__'                       is reserved to store the name of attributes saved as XML
            attribute '__SAVEALLXML__'                    is reserved to indicate saving all attributes as XML

        GV 12 Sep 2007:
          removed implementation with global storage in NTstructObjects since it was never used and
          will result in objects persisting even if they could be deleted (i.e. a memory leak).

        GV 26 Nov 2008:
          Changed implementation compare: removed __cmp__ and implemented __lt__, __le__, __gt__, __ge__;
          adapted __eq__.
          Changed implementation in __hash__ due to recursion error.
    """

    # Made into class object because it is the same for each instance.
    hiddenAttributesMap = {'__OBJECTID__':0, '__CLASS__':0, '__FORMAT__':0, '__SAVEXML__':0, '__SAVEALLXML__':0}
    hiddenAttributesSize = len( hiddenAttributesMap.keys() )
    def __init__(self, *args, **kwds):
        global NTdictObjectId # pylint: disable=W0603
        #print '>>>', args, kwds
        self.__CLASS__ = 'NTdict'
        self.__FORMAT__ = None
        self.__SAVEXML__ = None
        self.__SAVEALLXML__ = True
        dict.__init__(self, *args, **kwds)
#        SMLhandled.__init__(self) # Will not overwrite.

#        self.setdefault('__CLASS__', 'NTdict')
#        self.setdefault('__FORMAT__', None)      # set to None, which means by default not shown in repr() and toXML() methods
#        self.setdefault('__SAVEXML__', None)
#        self.setdefault('__SAVEALLXML__', True)   # when True, save all attributes in toXML() methods
#        self.__getstate__ =  self  # Trick for fooling shelve.

        self.__OBJECTID__ = NTdictObjectId
#        self['__OBJECTID__'] = NTdictObjectId
        NTdictObjectId      += 1
    #end def

    #------------------------------------------------------------------
    # Basic functionality
    #------------------------------------------------------------------
    def __getattr__(self, attr):
        """Implement basic functionality:
           Keys can be referenced as in dictionary methods, or as an attribute.
        """
#        if attr == '__getstate__':
#        return
#        if hasattr(self, attr):
        if not self.has_key(attr):
            # Happens at H2_2Ca_64_100.cing TODO: fix.
#            print 'CODE ERROR "%s" not found.' % attr
#            return ""
            raise AttributeError( '"%s" not found.' % attr )
        return self[attr]
    #end def


    def __setattr__(self, attr, value):
        """Implement basic functionality:
           Keys can be referenced as in dictionary methods, or as an attribute.
        """
        self[attr] = value

    def __delattr__(self, attr):
        """Implement basic functionality:
           Keys can be referenced as in dictionary methods, or as an attribute.
        """
        del(self[attr])

    def __lt__(self, other):
        if other == None:
            return False
        if not isinstance(other, NTdict): # eg when comparing with tuple.
            return False
        return self['__OBJECTID__'] < other['__OBJECTID__']

    def __le__(self, other):
        if other == None:
            return False
        if not isinstance(other, NTdict): # eg when comparing with tuple.
            return False
        return self['__OBJECTID__'] <= other['__OBJECTID__']

    def __eq__(self, other):
        if other == None:
            return False
        if not isinstance(other, NTdict): # eg when comparing with tuple.
            return False
        return self['__OBJECTID__'] == other['__OBJECTID__']

    def isEquivalent(self, other):
        "More extensive test if regular equivalence check doesn't suffice."
        if other == None:
#            nTdebug("other == None")
            return False
        # NTdict and regular dictionaries can be considered equivalent for this.
        if not isinstance(other, dict): # eg when comparing with tuple.
#            nTdebug("not isinstance(other, dict)")
            return False
        for key in self:
#            nTdebug("key %s" % key)
            if not (other.has_key(key) or hasattr(other, key)):
#                nTdebug("No key %s" % key)
                return False
            valueKeySelf = self[key]
            valueKeyOther = other[key]
            if isinstance(valueKeySelf, NTdict):
#                nTdebug("Comparing NTdict of selfKey")
                return valueKeySelf.isEquivalent( valueKeyOther )
            if isinstance(valueKeyOther, NTdict):
#                nTdebug("Comparing NTdict of otherKey")
                return valueKeyOther.isEquivalent( valueKeySelf )
            if valueKeySelf != valueKeyOther:
#                nTdebug("Comparing identity showing mismatch between self %r and other %r keys" % (valueKeySelf, valueKeyOther))
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if other == None:
            return False
        if not isinstance(other, NTdict): # eg when comparing with tuple.
            return False
        return self['__OBJECTID__'] > other['__OBJECTID__']

    def __ge__(self, other):
        if other == None:
            return False
        if not isinstance(other, NTdict): # eg when comparing with tuple.
            return False
        return self['__OBJECTID__'] >= other['__OBJECTID__']

#
#    def __cmp__(self, other):
#        """Optimized for speed a bit"""
#        if not hasattr(other, '__OBJECTID__'): return -1
#        if self.__OBJECTID__ == other.__OBJECTID__:
#            return 0
#        if self.__OBJECTID__ < other.__OBJECTID__:
#            return -1
#        return 1

    def __hash__(self):
        #print 'hash>', self, self['__OBJECTID__']
        return int(self['__OBJECTID__'])
        #return hash(self['__OBJECTID__'])
    #end def

    def __str__(self):
#        return '<%s-object (%d)>' % (self.__CLASS__,self.__OBJECTID__ )
#        return self.format()
        return '<%s-object (%d)>' % (self._className(), self.__OBJECTID__)

    def _className(self):
        'Convenience method. Just the subclass name.'
        return str(self.__class__)[7:-2].split('.')[-1:][0]
    #end def

    def __repr__(self, showEmptyElements = True):
        """Show all but empty items if desired"""
        if not showEmptyElements:
            c = NTdict()
            for key in self.keys():
                if self[key] != 0:
                    c[key] = self[key]
            return c.__repr__(showEmptyElements = True) # default but shown for clarity.

#        return dict.__repr__( self )
#        return '<%s-object (%d)>' % (self.__CLASS__,self.__OBJECTID__ )
        global NTdictDepth, NTdictMaxDepth, NTdictCycles # pylint: disable=W0602

        #prevent cycles
        if (NTdictDepth == 0):
            NTdictCycles = []
        #end if

        if (self.__OBJECTID__ in NTdictCycles):
            return  '<%s-object (%d)>' % (self.__CLASS__, self.__OBJECTID__)
        #end if
        NTdictCycles.append(self.__OBJECTID__)

        NTdictDepth += 1
        if (NTdictDepth > NTdictMaxDepth):
            NTdictDepth -= 1
            return '<%s-object (%d)>' % (self.__CLASS__, self.__OBJECTID__)
        #end if

        string = self.__CLASS__ + '( '
        remove2chars = 0
        for k in self.keys():
            string = string + str(k) + ' = ' + repr(self[k]) + ', '
            remove2chars = 1
        #end for
        #check if we also need to store some internals
        for k in ['__FORMAT__', '__SAVEXML__']:
            if self[k] != None:
                string = string + k + ' = ' + repr(self[k]) + ', '
                remove2chars = 1
        #end for
        #check if we need to remove the final (not needed) 2 chars
        if remove2chars:
            string = string[0:len(string)-2]
        # append closing paren
        string = string + ' )'

        NTdictDepth -= 1
        return string
    #end def

    def format(self, format=None): # pylint: disable=W0622
        """Return a formatted string of the items
           Uses format or stored attribute __FORMAT__ or default
        """
#        nTdebug("Now in %s" % getCallerName())
        if (format == None):
            # use the predefined format if no format given
            format = self.__FORMAT__

        if (format == None):
            # use the default format if None
            format ='<%(__CLASS__)s-object (%(__OBJECTID__)d)>'
        try:
            result = format % self
        except: # Happens at H2_2Ca_64_100.cing
            nTtracebackError()
            return ""
        return result
    #end def

    def keysformat(self, mdots=dots20):
        """set __FORMAT__ to list all keys
        """
        fmt = self.header(mdots) + '\n'
        for key in self.keys():
            s = '%-' + str(len(mdots)) + 's '
            fmt += s%(str(key)+':') + '%(' + str(key) + ')s\n'
        #end for
        fmt += self.footer(mdots=mdots)
        self.__FORMAT__ = fmt
    #end def

    def lenRecursive(self, max_depth = 5):
        "convenience method"
        return lenRecursive(self, max_depth = max_depth)

#    def printAttr(self, stream=sys.stdout, hidden=0):
    def printAttr(self, hidden=0):
        """print attributes of structure; mainly fo debugging."""
        msg = sprintf('=== <%s-object (%d)> ===\n', self.__CLASS__, self.__OBJECTID__)
        # append hidden keys if asked for
        keys = self.keys()
        if hidden:
            keys = keys + NTdict.hiddenAttributesMap.keys()
#    print '>>',keys
        for key in keys:
            msg += sprintf('%-12s : %s\n', key, str(self[key]))
        return msg
    #end def

    def header(self, mdots = dots20):
        """Generate a header using __CLASS__ and dots.
        """
        return sprintf('%s %s %s', mdots, self.__CLASS__, mdots)
    #end def

    def footer(self, mdots = dots20):
        """Generate a footer using dots of the same length as header.
        """
        header = self.header(mdots = mdots)
        lheader = len(header)
        s = mdots
        while len(s) < lheader:
            s += mdots
        #end while
        return s[0:lheader]
    #end def

    #------------------------------------------------------------------
    # Misc routines
    #------------------------------------------------------------------
    def doc(self):
        """
        Generate pydoc output of self
        """
        pydoc.doc(self, title='%s')
    #end def

    def copy(self):
        """Generate a copy with 'shallow' references"""
        newInstance = self.__class__(**dict(self.items()))
        for k in ['__SAVEXML__', '__FORMAT__']:
            newInstance[k] = self[k]
        #end for
        return newInstance

    def invert(self):
        'Swaps key and value.'
        result = NTdict()
        for key in self.keys():
            value = self[key]
            result[value] = key
        return result

    def __call__(self, **kwds):
        self.update(kwds)
        return self
    #end def

    def setDeepByKeys(self, value, *keyList):
        """Set arbitrary deep element to value by keyList.
        The essence here is silence.
        keyList needs to have at least one key.
        Return None on success and True on error.
        """
        lk = len(keyList)
        if not lk:
            nTerror("Can't setDeepByKeys without any key")
            return True

        k = keyList[0]
        if lk == 1:
            self[k] = value
            return

        if self.has_key(k):
            deeper = self[k]
        else:
            deeper = NTdict()
            self[k] = deeper

        reducedKeyList = keyList[1:]
        return deeper.setDeepByKeys(value, *reducedKeyList)

    def appendFromTable(self, myTable, idxColumnKey=0, idxColumnValue=0):
        """
        Maps from table column to table column or row idx if target column idx is -1.
        Return True on error.
        """
#        n = len(self)
        sizeRowsTable = len(myTable)
        if not sizeRowsTable:
            nTerror("Found no row in appendFromTable")
            return True
        sizeColumnsTable = len(myTable[0])
        if not sizeColumnsTable:
            nTwarning("Found no column in appendFromTable")
            return
#        nTdebug("Found %d rows and %d columns in appendFromTable" % (sizeRowsTable, sizeColumnsTable))
        # coded for speed:
        if idxColumnValue == -1:
            for row_idx, row in enumerate(myTable):
#                nTdebug("row_idx, row: %s %s" % (row_idx, row))
                self[ row[idxColumnKey] ] = row_idx
        else:
            for row in myTable:
                self[ row[idxColumnKey] ] = row[idxColumnValue]
#        m = len(self)
#        nTdebug("NTdict grew from %d to %d items" % ( n, m))

    def appendFromTableGeneric(self, myTable=None, *idxColumnKeyList, **kwds):
        '''
        Creates a nested dictionary with at each level the next column.
        See unit test examples.
        '''

        if getDeepByKeysOrAttributes(kwds, 'appendBogusColumn'):
            value = getDeepByKeysOrAttributes(kwds, 'appendBogusColumn')
#            nTdebug("First appendBogusColumn input table.")
            myTable = myTable[:] # shallow copy
            myTable.append( [value]*len(myTable[0]) ) # add a bogus column for the below feature.
#            nTdebug("myTable: %s" % str(myTable))
        # end if

        if getDeepByKeysOrAttributes(kwds, 'invertFirst'):
#            nTdebug("First transposing input table.")
            myTable = transpose(myTable)
        # end if

        n = len(self)
        nTable = len(myTable)
        if nTable == 0:
            nTwarning("Empty table not appended.")
            return
        firstRow = myTable[0]
        cTable = len(firstRow)
        if cTable == 0:
            nTwarning("Empty table (no columns) not appended.")
            return

        if len(idxColumnKeyList) == 0: # do all.
            idxColumnKeyList = range(cTable)

        for row in myTable:
#            nTdebug("Looking at row %s" % str(row))
            keyList = [ row[idx] for idx in idxColumnKeyList]
#            nTdebug("Found keyList %s" % str(keyList))
            if len(keyList) > 1:
                value = row[ idxColumnKeyList[-1] ]
                truncatedKeyList = keyList[:-1]
                setDeepByKeys(self, value, *truncatedKeyList)
            else:
                setDeepByKeys(self, None, *keyList)
        m = len(self)
        _msg = "NTdict grew from %d to %d items" % ( n, m)
#        nTdebug(msg)
    # end def

    def appendFromList(self, myList):
        'Simply add each value in the list as a key in self with the value as the value.'
#        n = len(self)
        for value in myList:
            self[ value ] = value
#        m = len(self)
#        nTdebug("NTdict grew from %d to %d items" % ( n, m))

    def appendDeepByKeys(self, value, *keyList):
        """Append value to arbitrary deep list.
        The essence here is silence.
        keyList needs to have at least one key.
        Return None on success and True on error.
        """
        lk = len(keyList)
#        nTdebug("Now in appendDeepByKeys with keyList: %s", repr(keyList))
        if not lk:
            nTerror("Can't appendDeepByKeys without any key")
            return True

        k = keyList[0]
        if lk == 1:
            if not self.has_key(k):
                self[k] = []
            self[k].append(value) # No extra checks done here for speed purposes.
            return

        if self.has_key(k):
            deeper = self[k]
        else:
            deeper = NTdict()
            self[k] = deeper

        reducedKeyList = keyList[1:]
        return deeper.appendDeepByKeys(value, *reducedKeyList)


    def getDeepByKeysOrDefault(self, default, *keyList):
        'Convenience method.'
        result = self.getDeepByKeys(*keyList)
        if result == None:
            return default
        return result

    def getDeepByKeys(self, *keyList):
        """
        Return arbitrary deep element or default=None if key is absent at some point.
        The essence here is silence.
        """
        lk = len(keyList)
#      nTdebug("Now in getDeepByKeys for keylist length: %d" % lk)
        if not lk:
#            nTdebug("Asked for a get on a dictionary without a key")
            return None
        key = keyList[0]

        if not self.has_key(key):
#          nTdebug("no key: " + repr(key))
            return None
        value = self[key]
        if lk == 1:
#          nTdebug("value : " + repr(value))
            return value
        if hasattr(value, 'getDeepByKeys'):
#          nTdebug("Going one level deeper")
            reducedKeyList = keyList[1:]
            return value.getDeepByKeys(*reducedKeyList)
#      nTdebug("In NTdict.getDeepByKeys the value is not a NTdict or subclass instance but there still are keys to go for digging deeper")
#      nTdebug(" for value : [" + repr(value) +']')
#      nTdebug(" type value: [" + repr(type(value)) +']')
        return None


    def getDeepAvgByKeys(self, *keyList):
        """Return first item only of tuple with av, sd, n for NTlist if found
        otherwise return None.
        If the first element of the list to average is a string then the consensus of
        the list will be returned instead of a numerical value.
        """
        result = self.getDeepByKeys(*keyList)
        if result == None:
#            nTdebug("None returned by getDeepByKeys() in getDeepAvgByKeys")
            return None
        if not isinstance(result, NTlist):
            nTerror("result is not an instance of NTlist so it can't be averaged")
            return None
        if not result:
#            nTdebug("result is an empty list in getDeepAvgByKeys")
            return None
        if isinstance(result[0], str):
#            nTdebug("result is a string list in getDeepAvgByKeys")
            x = result.setConsensus()
#            nTdebug("x returned by getConsensus() in getDeepAvgByKeys %s" % x)
            return x

        try:
            r = result.average()
        except:
            nTerror("Rare case throws an error on bad ")
            nTtracebackError()
            r = None

        if r == None:
#            nTdebug("None returned by average() in getDeepAvgByKeys")
            return None
        return r[0]

    def getDeepFirstByKeys(self, *keyList):
        """Return first item only if found otherwise return None"""
        result = self.getDeepByKeys(*keyList)
        if result == None:
            return None
        if not isinstance(result, list):
            nTerror("result is not an instance of NTlist in getDeepFirstByKeys.")
            return None
        if not len(result):
            nTerror("result is empty NTlist in getDeepFirstByKeys.")
            return None
        return result[0]


    def getdefault(self, key, defaultKey):
        'Return self[key] if key exists, self[defaultKey] otherwise'
        if self.has_key(key):
            return self[key]
        else:
            return self[defaultKey]
    #end def

    def uniqueKey(self, key):
        """return a unique key derived from key"""
        i = 1
        newkey = key
        while (newkey in self):
            newkey = sprintf('%s_%d', key, i)
            i += 1
        #end while
        return newkey
    #end def

    #------------------------------------------------------------------
    # methods __iter__(), iterkeys(),
    #         values(),   itervalues(),
    #         items(),    iteritems()
    #         len(),      popitem(),     clear(),   update()
    # now all decend from method keys().
    #------------------------------------------------------------------
    def keys(self):
        keys = dict.keys(self)
        # i.e. we only need to remove the 'local' stuff here
        # remove keys that should be hidden
        m = NTdict.hiddenAttributesMap
#        if False:
#            for key in m.keys():
##                if not (key in keys):
##                    nTerror("Failed for key %s and keys for %s" % (key,self))
##                    return []
#                keys.remove(key)
#            # sort keys as well
#            keys.sort()
#            return keys
        goodKeys = []
        for key in keys:
            if not m.has_key(key):
#                continue
                goodKeys.append(key)
        goodKeys.sort()
        return goodKeys

    def __iter__(self):
        """__iter__ returns keys
        """
        for key in self.keys():
            yield key
    #end def

    def iterkeys(self):
        for key in self.keys():
            yield key

    def values(self):
        return map(self.get, self.keys())

    def itervalues(self):
        for value in self.values():
            yield value

    def items(self):
        return zip(self.keys(), self.values())

    def iteritems(self):
        for item in self.items():
            yield item

    def __len__(self):
        # Soeeded up reading pdb file 1brv from 11 to 5 seconds.
#        return len(self.keys())
        keys = dict.keys(self)
        return len(keys) - NTdict.hiddenAttributesSize

    def popitem(self):
        keys = self.keys()
        try:
            key = keys[0]
        except IndexError:
            return None

        val = self[key]
        del self[key]
        return (key, val)

    def clear(self):
        p = self.popitem()
        while p:
            p = self.popitem()
    # end def

    def update(self, fromDict):
        for key, value in fromDict.iteritems():
            self[key] = value
    # end def

    def toDict(self):
        'Convert to regular dictionary.'
        result = {}
        for key, value in self.iteritems():
            result[ key ] = value
        return result
    # end def

    #------------------------------------------------------------------
    # XML routines
    #------------------------------------------------------------------
#     def toXML(self, depth=0, stream=sys.stdout, indent='  ', lineEnd='\n'):
#         """
#         Write XML-representation of keys/attributes of self (defined by the
#         saveXML or saveAllXML methods) to stream
#         """
#         nTindent(depth, stream, indent)
#         fprintf(stream, "<%s>", self.__CLASS__)
#         fprintf(stream, lineEnd)
# #       print node
#
#         # check for what we need to write out
#         if (self.__SAVEALLXML__):
#             keys = self.keys()
#         elif (self.__SAVEXML__ != None):
#             keys = self.__SAVEXML__
#         else:
#             keys = []
#         #end if
#
#         for a in keys:
#             nTindent(depth+1, stream, indent)
#             fprintf(stream, "<Attr name=%s>", quote(a))
#             fprintf(stream, lineEnd)
#
#             xmlTools.nTtoXML(self[a], depth+2, stream, indent, lineEnd)
#
#             nTindent(depth+1, stream, indent)
#             fprintf(stream, "</Attr>")
#             fprintf(stream, lineEnd)
#         #end for
#         nTindent(depth, stream, indent)
#         fprintf(stream, "</%s>", self.__CLASS__)
#         fprintf(stream, lineEnd)
    #end def

    def saveXML(self, *attrs):
        """add attrributes to save list
        """
        if self.__SAVEXML__ == None:
            self.__SAVEXML__ =  []
        self.__SAVEALLXML__ = False

        for a in attrs:
            if a not in self.__SAVEXML__:
                self.__SAVEXML__.append(a)
        #end for
    #end def

    def removeXML(self, *attrs):
        """remove attrributes from __SAVEXML__ list
        """
        if self.__SAVEXML__:
            for a in attrs:
                if a in self.__SAVEXML__:
                    self.__SAVEXML__.remove(a)
                #end if
            #end for
        #end if
    #end def

    def saveAllXML(self):
        """Define __SAVEALLXML__
        """
        self.__SAVEALLXML__ = True
    #end def

    def toSML(self, stream=sys.stdout):
        "Not all NTdicts have this attribute and it's only an error when this is called"
        sMLhandler = getDeepByKeysOrAttributes(NTdict, 'SMLhandler')
        if sMLhandler:
            sMLhandler.toSML(self, stream)
        else:
            nTerror('NTdict.toSML: no SMLhandler defined')
        #end if
    #end def
#end class

#LEGACY
NTstruct = NTdict

class CountMap(NTdict):
    'A Hash to int map. Superclass to AssignmentCountMap'
    def __init__(self, *args, **kwds):
        NTdict.__init__(self, *args, **kwds)
        if self.__CLASS__ == 'NTdict': # Allow kwds to override class name but set when it just defaulted.
            self.__CLASS__ = 'CountMap'
    def __str__(self, **kwds):
        'Default is to have no zero elements. Using trick with different method name to prevent recursion.'
        showEmptyElements = True
        if kwds.has_key('showEmptyElements'):
            showEmptyElements = kwds['showEmptyElements']
        return self.__repr__(showEmptyElements=showEmptyElements)
    def toString(self):
        'Sorted by key not by value.'
        lineList = []
        keyList = self.keys()
        keyList.sort()
#        keyList.reverse()
        for key in keyList:
            v = self[key]
            if v == 0:
                nTdebug("Skipping item with zero count.")
                continue
            lineList.append( "%s: %s" % ( key, v ))
        # end for
        lineList.append( "overallCount: %s" % self.overallCount())
        msg = '\n'.join(lineList)
        return msg
    # end def
    def increaseCount(self, k, v):
        if not self.has_key(k):
            self[k] = 0
        self[k] += v
    # end def
    def overallCount(self):
        r = sum([self[key] for key in self.keys()]) # numpy.int64 type because sum is from numpy.
        r = int(r)
#        nTdebug("type of overall count %s: %s" % ( r, r.__class__))
        return r
    # end def
#end class


class NoneObjectClass(NTdict):
    """
    Class representing None; based on NTdict

    Allows attribute assignment, extraction, deletion
    Allows iteration
    Allows calling

    Returns self where ever appropriate

    NB: Only one instance should be used:

        from NTutils import NoneObject

    Experimental
    """
    def __init__(self):
        NTdict.__init__(self, __CLASS__ = 'NoneObjectClass')
    #end def

#    def __getattr__(self, attr):
#        return dict.__getattr__( self, attr )
#    #end def

    def __setattr__(self, attr, value):
        pass

    def __delattr__(self, attr):
        pass
    #end def

    def __nonzero__(self):
        return False

    # To allow iteration
    def keys(self):
        return []
    #end def

    def __call__(self, *args, **kwds):
        return self
    #end def

    def __str__(self):
        'simply returns a fixed string.'
        return 'NoneObject'

    def __repr__(self): #pylint: disable=W0221
        'simply returns a fixed string.'
        return 'NoneObject'

#    def format(self, *args, **kwds):
    def format(self):  #pylint: disable=W0221
        'simply returns a fixed string.'
        return '<NoneObject>'
#end def
NoneObject = NoneObjectClass()
#NoneObject = None
noneobject = NoneObject


class NTtree(NTdict):
    """NTtree class
       Linked tree-like structure class
    """

    def __init__(self, name, **kwds):
        kwds.setdefault('__CLASS__', 'NTtree')
        NTdict.__init__(self, **kwds)
        self._parent   = None
        self._children = NTlist()
        self._iter = 0 # For iteration by __iter__
        # set names
        self.name = name        # keeping name is essential for later referencing
    #end def

    def cName(self, depth=0):
        """Return name constructor with 'depth' levels"""
        result = self.name
        parent = self._parent
        while depth != 0 and parent != None:
            result = parent.name + '.' + result
            depth -= 1
            parent = parent._parent # pylint: disable=W0212
        return result

    def cName2(self, depth=0):
        """Return name constructor using ['name']
           with 'depth' levels
        """
        result = sprintf('[%s]', quote(self.name))
        parent = self._parent
        while (depth != 0 and parent != None):
            result = sprintf('[%s]', quote(parent.name)) + result
            depth -= 1
            parent = parent._parent # pylint: disable=W0212
        return result

    def __str__(self):
        return '<%s %s>' % (self._className(), self.name)

    def __repr__( self ):  #pylint: disable=W0221
        return '<%s:%s>' % (self._className(), self.cName( -1 ))
    #end def

    def asPid(self):
        return pid.Pid('%s:%s' % (self._className(), self.cName( -1 )))

    def _decodeTreeName(self, nodeNames ):
        """
        Decode a list of nodeNames relative to self;
        uses recursion
        return NTtree object or None on error
        """
        #print ">>", self, nodeNames
        if len(nodeNames) == 0:
            return None
        elif len(nodeNames) == 1:
            if nodeNames[0] != self.name:
                return None
            return self
        else:
            if not self.has_key(nodeNames[1]):
                return None
            return self[nodeNames[1]]._decodeTreeName( nodeNames[1:]) # pylint: disable=W0212
    #end def

    def _decodeCname(self, cName):
        """Decode a cName relative to self"""
        return self._decodeTreeName( cName.split('.') )
    #end def

    def getParent(self, level=1):
        'Silent method returning parent or None.'
        if level < 0:
            nTerror("NTtree.getParent called with level < 0: n being: %s" % level)
            return None
        if level == 0:
            return self # Luke, I'm you're father.
        parent = self._parent
        if parent == None:
            return None
        return parent.getParent(level=level-1)
    #end def

    def addChild(self, name, **kwds):
        'Adds a new NTtree instance as child and returns it.'
        child = NTtree(name=name, **kwds)
        self.addChild2(child)
        return child
    #end def

    def addChild2(self, child):
        """Add given already generated child"""
        self._children.append(child)
        self[child.name] = child
        self[child]      = child
        child._parent    = self
        return child
    #end def

    def removeChild(self, child):
        'Silent method for removing if child exists.'
        if not child in self._children:
#            nTdebug("not child in self._children: for %s in %s", child, self._children)
            return None
        if child.name in self:
            del(self[ child.name ])
        self._children.remove(child)
        child._parent = None
        return child

    def renameChild(self, child, newName):
        'Convoluted method taking care of internal components.'
        if not child in self._children:
            return None
        if child.name in self:
            del(self[ child.name ])
        child.name = newName
        self[child.name] = child
        return child
    #end def

    def replaceChild(self, child, newChild):
        'Convoluted method taking care of internal components.'
        if (not child in self._children):
            return None
        if child.name in self:
            del(self[ child.name ])
        child._parent = None
        self._children.replace(child, newChild)
        self[newChild.name] = newChild
        newChild._parent = self
        return newChild
    #end def

    def _sibling(self, relativeIndex):
        """Internal routine: Return index relative to self
           or -1 if it does not exist.
           This routine is the slowest part in a typical read of a molecule
           at the point of trying to match atom specifications in a dihedral
           which can span the residue.
        """
        if not self._parent:
            return -1
        # end if

        selfIndex = self._parent._children.index(self) # pylint: disable=W0212
        if selfIndex < 0:
            nTerror('NTtree.sibling: child "%s" not in parent "%s". This should never happen!!\n',
                    str(self), str(self._parent))
            return -1
        # end if

        targetIndex = selfIndex + relativeIndex
        if targetIndex < 0:
            return -1
        # end if
        if targetIndex >= len(self._parent._children): # pylint: disable=W0212
            return -1
        # end if
        return targetIndex
    #end def

    def sibling(self, relativeIndex):
        """Return NTtree instance (relative to self)
           or None if it does not exist
        """
        # Next check greatly speeds up trivial lookups.
        if relativeIndex == 0:
            return self

        targetIndex = self._sibling(relativeIndex)
        if targetIndex < 0:
            return None
        else:
            return self._parent._children[targetIndex] # pylint: disable=W0212
    #end def

    def youngerSiblings(self):
        """return NTlist of elements following self
           or None in case of error
        """
        if self._parent == None:
            return None
        sibling = self._sibling(1)
        if sibling < 0:
            return []
        return self._parent._children[sibling:] # pylint: disable=W0212

    def olderSiblings(self):
        """return NTlist of elements preceding self
           or None if it does not exist
        """
        if self._parent == None:
            return None
        sibling = self.sibling(-1)
        if sibling == None:
            return []
        return self._parent._children[0:sibling+1] # pylint: disable=W0212
    # end def

    def __iter__(self):
        """iteration routine: loop of children"""
        self._iter = 0
        return self
    # end def

    def next(self):
        'With error checking get the next child thru _iter.'
        if self._iter >= len(self._children):
            raise StopIteration
#            return None
        s = self._children[self._iter]
        self._iter += 1
        return s
    # end def

    def traverse(self, depthFirst=1, result = None, depth = -1):
        """
        Traverse the tree, infinite depth recursion for depth < 0
        finite depth recursion for depth > 0
        """
#        print '>>', self, depth
        if result == None:
            result = NTlist()

        result.append(self)
        for child in self._children:
            if depth != 0:
                child.traverse(depthFirst=depthFirst, result = result, depth = depth-1)
        return result
    # end def

    def subNodes(self, result = None, depth = -1):
        """Traverse the tree, returning all subnodes at depth
        """
#        print '>>', self, depth

        if result == None:
            result = NTlist()
        #end if
        if depth == 0:
            result.append(self)
        elif depth > 0:
            for child in self._children:
                child.subNodes(result = result, depth = depth-1)
        return result
    # end def

    def header(self, mdots = dots):
        """Subclass header to generate using __CLASS__, name and dots.
        """
        return sprintf('%s %s: %s %s', mdots, self.__CLASS__, self.name, mdots)
    # end def
#end class


class NTparameter(NTtree): # pylint: disable=R0904
    """
    Class to generate a parameter tree

    Methods:
        set( value )                    Set value of parameter
        __call__()                      Calling returns value of parameter
        setDefault( recursion = True )  Set parameters to default value
        allLeaves()                     Return all leaves of parameter tree, i.e.
                                        the 'active' parameters
        allBranches()                   Return all the branches of parameter tree

    Methods inherited form NTtree and NTdict
    """

    def __init__(self, name, **kwds):
        NTtree.__init__(self,
                           __CLASS__ = 'NTparameter',
                           branch    =  False, # branch=True indicate a node
                                                   # without a value
                                                   # Leaves carry a value
                           mutable   =  True,
                           parType   = 'generic', # 'generic', 'string', 'integer'
                                                   # 'float', 'enumerate','boolean'
                           name      =  name,
                           value     =  None,
                           default   =  None,
                           options   =  None,
                           minValue  =  None,
                           maxValue  =  None,
                           prettyS   =  None,
                           help      =  None,
                         )
        self.update(kwds)
        self.value = self.default
    # end def

    def update(self, fromDict):
        """Update preserves/establises the linked structure
        """
        for key, value in fromDict.iteritems():
#            print '>>', repr(self), type(self), repr(value), type(value)
            if (type(self) == type(value) and not self.has_key(key)):
                self.addChild2(value)
            else:
                self[key] = value
            #end if
        #end for
    #end def

    def set(self, value):
        'Silent convenience method.'
        if self.mutable:
            self.value = value
        #end if
    #end def

    def __call__(self):
        'Convenience method.'
        return self.value
    #end def

    def setDefault(self, recursion = True):
        'Using default attribute of self and leaves to set them.'
        if recursion:
            for p in self.allLeaves():
                p.set(p.default)
            #end for
        else:
            self.set(self.default)
        #end if
    #end def

    def allLeaves(self):
        'Return the children from all levels of the tree in a flat list.'
        leaves = NTlist()
        for p in self.traverse():
            if not p.branch:
                leaves.append(p)
            #end if
        #end for
        return leaves
    #end def

    def allBranches(self):
        'Get flat list of all branches.'
        branches = NTlist()
        for p in self.traverse():
            if p.branch:
                branches.append(p)
            #end if
        #end for
        return branches
    #end def

    def writeFile(self, fileName):
        'Convenience method.'
        fp = open(fileName, 'w')
        for p in self.allLeaves():
            fprintf(fp, '%-40s = %s\n', p.cName(-1) + '.value', repr(p))
        #end for
        fp.close()
    #end def

    def __str__(self):
        'Convenience method.'
        return self.cName(-1)
    #end def

    def __repr__(self):
        'Convenience method.'
        return repr(self.value)
    #end def

    def format(self): # pylint: disable=W0221
        if self.branch:
            return str(self)
        else:
            return sprintf('%s: %s', str(self), str(self.value))
    #end def
#end class


class NTvalue(NTdict):
    """
    Class to store a value and its error
    Callable: returns value
    Simple arithmic: +, -, *, /, ==, !=, >, >=, <, <=,
    fmt2 will be used when value exists but error does not.
    """
    defaultFormat  = '%s (+- %s)'
    defaultFormat2 = '%s'

    def __init__(self, value, error=NaN, fmt=None, fmt2=None, **kwds):
        kwds.setdefault('__CLASS__', 'NTvalue')
        # hack to get default values from NTvalues defs
        if fmt == None:
            kwds.setdefault('fmt', NTvalue.defaultFormat)
        else:
            kwds.setdefault('fmt', fmt)
        if fmt2 == None:
            kwds.setdefault('fmt2', NTvalue.defaultFormat2)
        else:
            kwds.setdefault('fmt2', fmt2)

        NTdict.__init__(self, **kwds)
        self.value = value
        self.error = error
#        NTdict.__init__(self, value=value, error=error, fmt=fmt, fmt2=fmt2, **kwds)
        # always map av and sd as alternatives for value and error, set default n
        self.av = self.value
        self.sd = self.error
        self.setdefault('n',1)
        self.saveXML('value', 'error', 'n','fmt', 'fmt2')
    #end def

    def __call__(self):
        return self.value
    #end def

    def __str__(self):
        # Note that the below cases for None value/error loose fixed width formatting.
        if self.value == None or isNaN(self.value):
            return '%s (+- %s)' % (NaNstring, NaNstring)
        if self.error == None or isNaN(self.error):
#            return repr(self.value)+' (+- %s)' % (NaNstring)
            # The problem here is of course that the whole fmt is lost if only the error is unknonw.
            # Added new parameter to init of this class to cover it.
            r = self.fmt2 % self.value
            return r + ' (+- %s)' % (NaNstring)
        return  self.fmt % (self.value, self.error)
    #end def

    def format(self): # pylint: disable=W0221
        return str(self)
    # end def

    def __repr__(self): # pylint: disable=W0221
        return sprintf('NTvalue( value = %s, error = %s, n = %r, fmt = %r, fmt2 = %r )',
                       repr(self.value), repr(self.error), self.n, self.fmt, self.fmt2)
    #end def

    def __add__(self, other):
        if hasattr(other, 'value'):
            v = self.value+other.value
            e = math.sqrt(self.error**2+other.error**2)
        else:
            v = self.value+other
            e = self.error
        return NTvalue(v, e, self.fmt, self.fmt2)
    #end def

    def __radd__(self, other):
        v = other + self.value
        return NTvalue(v, self.error, self.fmt, self.fmt2)
    #end def

    def __iadd__(self, other):
        if hasattr(other, 'value'):
            self.value += other.value
            self.error = math.sqrt(self.error**2+other.error**2)
        else:
            self.value += other
        return self
    #end def

    def __sub__(self, other):
        if hasattr(other, 'value'):
            v = self.value-other.value
            e = math.sqrt(self.error**2+other.error**2)
        else:
            v = self.value-other
            e = self.error
        return NTvalue(v, e, self.fmt, self.fmt2)
    #end def

    def __rsub__(self, other):
        v = other - self.value
        return NTvalue(v, self.error, self.fmt, self.fmt2)
    #end def

    def __isub__(self, other):
        if hasattr(other, 'value'):
            self.value -= other.value
            self.error = math.sqrt(self.error**2+other.error**2)
        else:
            self.value -= other
        return self
    #end def

    def __mul__(self, other):
        if hasattr(other, 'value'):
            v = self.value*other.value
            e = v*math.sqrt((self.error/self.value)**2+(other.error/other.value)**2)
        else:
            v = self.value*other
            e = self.error*other
        return NTvalue(v, e, self.fmt, self.fmt2)
    #end def

    def __rmul__(self, other):
        v = other * self.value
        e = v*self.error/self.value
        return NTvalue(v, e, self.fmt, self.fmt2)
    #end def

    def __imul__(self, other):
        if hasattr(other, 'value'):
            v = self.value
            self.value *= other.value
            self.error = v*math.sqrt((self.error/self.value)**2+(other.error/other.value)**2)
        else:
            self.value *= other
            self.error *= other
        return self
    #end def

    def __div__(self, other):
        if hasattr(other, 'value'):
            v = self.value/other.value
            e = v*math.sqrt((self.error/self.value)**2+(other.error/other.value)**2)
        else:
            v = self.value/other
            e = self.error/other
        return NTvalue(v, e, self.fmt, self.fmt2)
    #end def

    def __rdiv__(self, other):
        v = other / self.value
        e = v*self.error/self.value
        return NTvalue(v, e, self.fmt, self.fmt2)
    #end def

    def __idiv__(self, other):
        if hasattr(other, 'value'):
            self.value /= other.value
            # JFD: Next line should be checked
            self.error = self.value*math.sqrt((self.error/self.value)**2+(other.error/other.value)**2)
        else:
            self.value /= other
            self.error /= other
        return self
    #end def

    def __neg__(self):
        v = -self.value
        e = self.error
        return NTvalue(v, e, self.fmt, self.fmt2)
    #end def

    def __pos__(self):
        v = self.value
        e = self.error
        return NTvalue(v, e, self.fmt, self.fmt2)
    #end def

    def __abs__(self):
        v = abs(self.value)
        e = self.error
        return NTvalue(v, e, self.fmt, self.fmt2)
    #end def

    def __cmp__(self, other):
        if isinstance(other, NTvalue):
            value = other.value
        else:
            value = other
        #endif
        if (self.value < value):
            return -1
        elif (self.value > value):
            return 1
        else:
            return 0
        #end if
    #end def

    def __eq__(self, other):
        if other == None:
            return False
        elif isinstance(other, NTvalue):
            return self.value == other.value
        else:
            return self.value == other
        #end if
    #end def

    def __ne__(self, other):
        if other == None:
            return True
        elif isinstance(other, NTvalue):
            return self.value != other.value
        else:
            return self.value != other
        #end if
    #end def

    def sqrt(self):
        "Returns NTvalue with corrected error if value isn't zero"
        if self.value < 0:
            raise ValueError

        v = self.value
        e = self.error
        if self.value != 0:
            v = math.sqrt(self.value)
            e = self.error / (2.0*self.value) # y = sqrt(x) ==> dY = 1/(2*sqrt(x)) *dx
        return NTvalue(v, e, self.fmt, self.fmt2)
    #end def

    def toTuple(self):
        """
        Return a (value,error) tuple
        """
        return (self.value, self.error)
    #end def
#end class


class NTplist(NTdict):
    """
    Class to parse plist files
    """
    def __init__(self):
        NTdict.__init__(self, __CLASS__ = 'plist')
    #end def
#end class


def nTlimit(theList, minim, maxim, byItem=None):
    """
    Limit the the values of theList between minim and maxim, assuming periodicity
    i.e, like for angles.
    Assumes numeric list, None elements are ignored
    Elements are modified in-place
    byItem allows for list of lists
    """
    myLength = len(theList)
    listRange = maxim-minim
    for i in range(0, myLength):
        if (theList[i] != None):
            if byItem == None:
                while theList[i] < minim:
                    theList[i] += listRange
                while theList[i] > maxim:
                    theList[i] -= listRange
            else:
                while theList[i][byItem] < minim:
                    theList[i][byItem] += listRange
                while theList[i][byItem] > maxim:
                    theList[i][byItem] -= listRange
        #end if
    #end for
#end def

def nTlimitSingleValue(value, minim, maxim):
    """
    Limit the the values of theList between minim and maxim, assuming periodicity
    i.e, like for angles.
    Assumes numeric value, None element is ignored.

    Could easily be optimized. If the value is far away from the allowed range
    then round off errors also become important with this algorithm.
    """
    listRange = maxim-minim
    if value == None:
        return value

    while value < minim:
        value += listRange
    while value > maxim:
        value -= listRange
    return value
# end if

def nTaverage2(theList, byIndex=None, fmt='%f +- %f' ):
    """Calculate average of theList
       Assumes numeric list, None elements are ignored
       byIndex allows for list of tuples r other elements

       returns
           NTvalue object with attr. av, sd and n
           or None on Error
    """
    av,sd,n = nTaverage(theList, byIndex)
    result = NTvalue( av, sd, n=n, fmt=fmt )
    return result
#end def

def nTaverage(theList, byIndex=None ): # pylint: disable=C0103
    """Calculate average of theList
       Assumes numeric list (might throw exception otherwise), None elements are ignored
       byIndex allows for list of tuples r other elements

       returns

           (av, sd, n) tuple of theList or
           (None, None, 0) in case of zero elements in theList
     """
    s = 0.0
    sumsqd = 0.0
    n = 0.0
    for item in theList:
        if item != None:
            if byIndex == None:
                val = item
            else:
                val = item[byIndex]
            if not isNaN(val):
                s   += val
                n += 1
            #end if
    #end fpr

    if n == 0:
        return (NaN, NaN, 0)
    if n == 1:
        return (s, NaN, 1) # sd not defined for serie of length one.
#    fn = float(n)
#    print '>>', n, s, sumsq, sumsq/(fn-1.0), (s*s)/(fn*(fn-1.0))
    av = s/n
    # routine below makes it much slower but easier to read than one pass.
    for item in theList:
        if item != None:
            if byIndex == None:
                val = item
            else:
                val = item[byIndex]
            if not isNaN(val):
                sumsqd += (val-av)*(val-av) # s of squared deviations.

    # some python implementations (Linux) crash in case of all same numbers,
    # => zero sd, but roundoffs likely generate a very small negative number
    # here
    sd = sumsqd/(n-1)
    if sd <= 0.0:
        sd = 0.0
    sd = math.sqrt(sd)
    return (av, sd, int(round(n)))
#end def

def nTcAverage(theList, minim=0.0, maxim=360.0, radians = 0, byIndex=None):
    """return (circularAverage,circularVariance,n) tuple of thelist or
       (None, None, 0) in case of zero elements in theList
       return circularMean on minim-maxim interval (that has to be spaced
       360 or 2pi depending on radians )
       Assumes numeric list, None elements ignored
       byIndex allows for list of tuples
    """
    n    = 0
    csum = 0.0
    ssum = 0.0
    if radians:
        fac = 1.0
        fac2 = math.pi
    else:
        fac = math.pi/180.0
        fac2 = 360.0
    #end if
    for item in theList:
        if item != None:
            if byIndex == None:
                v = item
            else:
                v = item[byIndex]
            #end if
            if (v != None):
                csum += math.cos(v*fac)
                ssum += math.sin(v*fac)
                n += 1
            #end if
        #end if
    #end for

    if not n:
        return(None, None, 0)
    #end if

    #calculate cmean, avoid zero divisions
    if (math.fabs(csum) < 1e-10):
        csum = 1e-10
    #end if
    cav = math.atan(ssum/csum)
    if (csum < 0):
        cav += math.pi
    #end if
    cav /= fac

    #now scale on minim-maxim interval
    while (cav < minim):
        cav += fac2
    #end while
    while (cav > maxim):
        cav -= fac2
    #end while

    #calculate cv
    cv = 1.0 - math.sqrt(csum*csum + ssum*ssum) / n

    return (cav, cv, n)
#end def

def nTcVarianceAverage( cvList ):
    """Average cv values like phi/psi
    See:    http://www.ebi.ac.uk/thornton-srv/software/PROCHECK/nmr_manual/man_cv.html
    Circular variance average here is different than the one in Wattos.
    Returns None when the list only contains None values.
    None input values are ignored and are 'legal'.
    """
    sumSquares = 0.
    n = len(cvList)
    for cv in cvList:
        if cv == None:
            n -= 1
        else:
            r = 1. - cv
            sumSquares += r * r
    if n <= 0:
        return None
    r2 = sumSquares / n
    cvResult = 1. - math.sqrt( r2 )
    return cvResult
# end if

def nTzap(theList, *byItems):
    """yield a new list from theList, extracting byItems from each
       element of theList or None if not present
    """
    result = NTlist()
    for v in theList:
        # Removed extra check which is done in routine below anyway.
        # The check was also wrong in the case of empty NTlists
        result.append(getDeepByKeysOrAttributes(v, *byItems))
    #end for
    return result
#end def

def nTsq(value):
    'Convenience method.'
    return value*value # fastest
#end def


class Sorter:
    '''
    Sorting class for sorting dictionaries such as NTdict. Used to be called Sorter.
    NTsort( self, byItem, inplace=True)
    '''
    def __init__(self):
        pass
    #end def

    # pylint: disable=R0201
    def _helper (self, data, aux, inplace):
        'Internal method doing the actual sort.'
#        print DATA_STR, data
        aux.sort()

        result = [data[i] for dummy, i in aux]
        if inplace:
            data[:] = result
        return result
    #end def

    def byItem(self, data, itemindex=None, inplace=False):
        'Sorting the data by given index'
#        print "Now in byItem with data: %s and itemindex %s" % (data, itemindex)
        if itemindex is None:
            if inplace:
#                data.sort() # Gave recursion
                list.sort(data)
                result = data
            else:
                result = data[:]
#                result.sort()
                list.sort(result)
            #end if
            return result
        else:
            aux = []
            for i in range(len(data)):
                try:
                    aux.append((data[i][itemindex], i))
                except KeyError:
                    aux.append((None, i))
                except IndexError:
                    aux.append((None, i))
#           aux = [(data[i][itemindex], i) for i in range(len(data))]
            return self._helper(data, aux, inplace)
        #end if
    #end def

    # a couple of handy synonyms
    sort = byItem
    __call__ = byItem

    def byAttribute(self, data, attributename, inplace=False):
        'Sorting the data by given index'
#        aux = [(getattr(data[i], attributename), i) for i in range(len(data))]
        aux = []
        for i in range(len(data)):
            aux.append( getattr(data[i], attributename), i)
        # end for
        return self._helper(data, aux, inplace)
    #end def
#end class
NTsort = Sorter()



def asci2list(inputStr, onlyStartStopIdx = False):
    """ Convert a string with "," and "-" (or :) to a list of integers
    eg. 1,2,5-8,11,20-40 or
        -20:-19,-2:-1,3:4

    returns empty list on empty inputStr

    NB: - returns empty list when an invalid construct is entered.
        - boundaries are inclusive at both ends unlike python array selections.
        - Do not mix - and : either.

    Possible 5 situations:
    a      # 1 # positive int
    -a     # 2 # single int
    -a-b   # 3 #
    -a--b  # 4 #
    a-b    # 5 # most common

    If onlyStartStopIdx is set then only pairs of start stop are returned.
    """
    result = NTlist()

    if inputStr == None:
        return result
    if len(inputStr) == 0:
        return result

    # Get rid of all whitespace
    inputStrCollapsed = inputStr.replace(' ', '')

    try:
        for elm in inputStrCollapsed.split(','):
#            nTdebug("Looking at elm: [%s]" % elm)
            if elm.count(':'):
                tmpList = elm.split(':')
            else:
                countDash = elm.count('-')
#                countDubbleDash = elm.count('--')

                if countDash == 0:
#                    nTdebug("State 1 elm: [%s]" % elm)
                    intElm = int(elm)
                    if not onlyStartStopIdx:
                        result.append(intElm)
                    else:
                        result += [intElm, intElm]
                    # end if
                    continue
                idxMinus = elm.index('-') # first occurance
                if idxMinus == 0 and countDash == 1:
#                    nTdebug("State 2 elm: [%s]" % elm)
                    intElm = int(elm)
                    if not onlyStartStopIdx:
                        result.append(intElm)
                    else:
                        result += [intElm, intElm]
                    # end if
                    continue
                # end if
#                nTdebug("State 3-5 elm: [%s]" % elm)
                # Only states 3-5 left which are all ranges and thus contain an int separating dash
                offset = 0
                if idxMinus == 0:
                    offset = 1
                # end if
                idxRangeDash = elm.index('-',offset) # The dash that separates the two ints,
                start = elm[:idxRangeDash]
                end = elm[idxRangeDash+1:]
                tmpList = [ int(x) for x in [start,end ] ]
                if tmpList[0] > tmpList[1]: # equality is still ok
                    nTerror('asci2list: invalid construct "%s" with start %s and end %s skipping element: %s' % (inputStr, start, end, elm))
                    continue
                # end else
            # end else
#            nTdebug("tmpList: [%s]" % str(tmpList))
            intList = [ int(x) for x in tmpList ]
#            nTdebug("intList: [%s]" % str(tmpList))
            tmpListSize = len(tmpList)
            if tmpListSize == 1:
                if not onlyStartStopIdx:
                    result.append(intList[0])
                else:
                    result += [intList[0], intList[0]]
                # end if
            elif tmpListSize == 2:
                if not onlyStartStopIdx:
                    for i in range(intList[0], intList[1]+1):
                        result.append(i)
                    # end for
                else:
                    result += [intList[0], intList[1]]
                # end if
            else:
                nTerror('asci2list: invalid construct "%s" caused a tmpListSize of %s skipping element: %s' % (inputStr, tmpListSize, elm))
            #end if
        #end for elm
    except:
#        NTtracebackError() # disable this verbose messaging after done debugging.
        nTerror('asci2list: failed to convert to int for construct "%s"' % inputStr)
    # end try
    return result
#end def


def list2asci(theList):
    """ Converts the numeric integer list theList to a string with "," and "-"
    eg. 1,3,5-8,11,20-40
    nb. inverse of asci2list
    returns '' for empty list
    """
    if len(theList) == 0:
        return ''

    myList = theList[:]
    myList.sort()

    # reduce this sorted list myList to pairs start, stop
    ls = myList[0:1]
    #print '>>',ls
    for i in range(0, len(myList)-1):
        if myList[i] < myList[i+1]-1:
            ls.append(myList[i])
            ls.append(myList[i+1])
        #end if
    #end for
    ls.append(myList[-1])

    #print '>>',ls

    # generate the string from ls
    result = ''
    for i in range(0, len(ls), 2):
        #print '>', i, result
        if ls[i] == ls[i+1]:
            result = sprintf('%s%s,', result, str(ls[i]))
        else:
            result = sprintf('%s%s-%s,', result, str(ls[i]), str(ls[i+1]))
        #end if
    #end for
    return result[0:-1]
#end def

def list2string(mylist):
    "Return a string representation of mylist"
    if len(mylist) == 0:
        return ''
    result = ''
    for e in mylist:
        result = result + str(e) + ' '
    #end for
    return result[0:-1]
#end def

def nTsign(value):
    """return sign of value; -1.0 for negative numbers"""
    if value < 0.0:
        return -1.0
    #end if
    return 1.0
#end def


def length(obj):
    """return length obj
    """
    try:
        myLength = len(obj)
        return myLength
    except TypeError:
        return 1
#end def

def object2list(obj):
    """return obj as list
    """
    if obj==None:
        return []
    if isinstance(obj, list):
        return obj
    else:
        return [obj]
#end def

# pylint: disable=R0903
class CommandWrap:
    """Wrapper for command callbacks
       From Python Cookbook, section 9.1 (p. 302)
    """

    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.callback(*self.args, **self.kwargs)

# pylint: disable=R0903
class EventWrap:
    """Wrapper for event callbacks
         Adapted from Python Cookbook, section 9.1 (p. 302)
    """

    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self, event):
        return self.callback(event, *self.args, **self.kwargs)
    #end def
#end class


# pylint: disable=R0903
class EventSkip:
    """
    Wrapper for callbacks, skipping the event argument
    Adapted from Python Cookbook, section 9.1 (p. 302)
    """

    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self, event):
        return self.callback(*self.args, **self.kwargs)
    #end def
#end class

class NTprogressIndicator: # pylint: disable=R0903
    """
    Iterator class to loop over myList and print dots
    """
    def __init__(self, theList, charactersPerLine = 80):
        self._iter = -1
        self._len   = len(theList)
        self._list  = theList
        self._charactersPerLine = charactersPerLine
        self._printedDots = 0
    #end def

    def __iter__(self):
        """iteration routine: loop of children"""
        self._iter = 0
        self._printedDots = 0
        return self
    #end def

    def next(self):
        'Prints the progress for the next item if anything.'
        if self._iter >= self._len:
            nTmessage("")
            raise StopIteration
#            return None

        if not self._printedDots % 10:
            digit = self._printedDots / 10
            nTmessageNoEOL(repr(digit))
        else:
            nTmessageNoEOL('.')
        #end if
        self._printedDots += 1
        if not self._printedDots % self._charactersPerLine:
            nTmessage("")
            self._printedDots = 0

        s = self._list[self._iter]
        self._iter += 1
        return s
    #end def
#end class


class PrintWrap:
    '''
    Base class for all messaging for example nTmessage()
    '''
    def __init__(self, stream = None,
                       autoFlush = True,
                       verbose=verbosityOutput,
                       noEOL=False,
                       useDate=False,
                       useProcessId=False,
                       doubleToStandardStreams=False,
                       prefix = ''
                ):
        self.autoFlush = autoFlush
        self.verbose   = verbose
        self.noEOL     = noEOL
        self.useDate        = useDate
        self.useProcessId   = useProcessId
        self.doubleToStandardStreams = doubleToStandardStreams
        self.stream2   = None

        if self.verbose > verbosityError:
            self.stream = sys.stdout
        else:
            self.stream = sys.stderr
        if stream: # Allow override.
            self.stream = stream
        self.prefix = prefix
    # end def

    def __call__(self, form, *args):
        if self.verbose > cing.verbosity: # keep my mouth shut per request.
            return
        if self.prefix:
            form = self.prefix + form
        if self.doubleToStandardStreams:
            fmt = form
            if not self.noEOL:
                fmt += '\n'
            fprintf(sys.stdout, fmt, *args)
        if self.useDate:
            at = time.asctime()
            dateStr = str(at)
            form = dateStr + ' ' + form
        if self.useProcessId:
            processId = "[%s] " % os.getpid()
            form = processId + form
        if not self.noEOL:
            form += '\n'
        # cache for speed.
        if args == None:
            finalMsg = form
        elif len(args) == 0:
            finalMsg = form
        else:
            finalMsg = sprintf(form, *args)
        fprintf(self.stream, finalMsg)
        if self.stream2 != None:
#            if self.stream2.writable(): # stupid slowing down check because JFD can't seem to get it closed proper.
            fprintf(self.stream2, finalMsg)
        if self.prefix.find('EXCEPTION')>=0:
            pass
#            fprintf( self.stream, "Exception below:\n" )
#            traceback.print_exc() # Just prints None on my Mac. Strange.
        if self.autoFlush:
#            self.stream.flush() # JFD seems double.
            self.flush()
    # end def

    def flush(self):
        'Used every time when autoflushing is on.'
        self.stream.flush()
        if self.stream2 != None:
            try:
                self.stream2.flush()
            except:
                nTdebug("Failed to flush stream2")
    # end def

    def setVerbosity(self, verbose):
        'Convenience method.'
        self.verbose=verbose
    # end def

    def addStream(self, stream):
        'Add a second stream (called stream2) for echoing.'
        if self.stream2 != None:
#            self.stream2.flush()
#            print "DDD: Flushed 2nd stream and closing before adding new one."
            try:
                self.stream2.close()
            except:
                nTdebug("Failed to close stream2")
#        print "DDD: Adding 2nd stream to %s." % self
        self.stream2 = stream
    # end def

    def removeStream(self):
        'Remove the second stream if set.'
        if self.stream2 == None:
#            print "DDD: Strange 2nd stream was already closed in %s." % self
            return
#        self.stream2.flush()
#        print "DDD: Flushed 2nd stream and closing."
#        self.stream2.close()
        self.stream2 = None
    # end def
# end class

def nTexit(msg, exitCode=1):
    'Convenience method.'
    nTerror(msg)
    sys.exit(exitCode)
# end def

class SetupError(Exception):
    "Setup check error"

class CodeError(Exception):
    "Program code error"
# end class

# New in version 2.5 it already is a class.
#class ImportWarning(Exception):
#    "Optional code warning"
# end class


class NTfile(file):
    """
File class with a binary read/write typecode as defined for array module:

This module defines an object type which can efficiently represent an array of basic values: characters, integers,
floating point numbers. Arrays are sequence types and behave very much like lists, except that the type of objects
stored in them is constrained. The type is specified at object creation time by using a type code, which is a single
character. The following type codes are defined:

 Type code  C-Type          Python-Type         Minimum size in bytes
'c'         char            character           1
'b'         signed char     int                 1
'B'         unsigned char   int                 1
'u'         Py UNICODE      Unicode character   2
'h'         signed short    int                 2
'H'         unsigned short  int                 2
'i'         signed int      int                 2
'I'         unsigned int    long                2
'l'         signed long     int                 4
'L'         unsigned long   long                4
'f'         float           float               4
'd'         double          float               8

The actual representation of values is determined by the machine architecture (strictly speaking, by the C imple-
mentation). The actual size can be accessed through the itemsize attribute. The values stored for 'L' and
'I' items will be represented as Python long integers when retrieved, because Python's plain integer type cannot
represent the full range of C's unsigned (long) integers.
    """
    def __init__(self, *args, **kwds):
        file.__init__(self, *args, **kwds)
    #end def

    def binaryWrite(self, typecode, *numbers):
        """Binary write of numbers
           typecode as defined for array module
        """
        n = array.array(typecode, numbers)
        n.tofile(self)
    #end def

    def binaryRead(self, typecode, size):
        """Return a list of numbers
        """
        n = array.array(typecode)
        n.fromfile(self, size)
        return n.tolist()
    #end def

    def rewind(self):
        """rewind the file"""
        self.seek(0)
    #end def
#end class

#DEPRECIATED: use routines from disk.py instead
def removedir(path):
    """Recursive remove path"""
    while (1):
        try:
            filelist=os.listdir(path)
        except:
            nTerror('Subdirectory "%s" could not be entered', path)
        # DELETE ALL THE FILES
        for fileName in filelist:
            fileName=os.path.join(path, fileName)
            try:
                os.remove(fileName)
            except:
                if os.path.isdir(fileName):
                    removedir(fileName)
        try:
            os.rmdir(path)
        except:
            nTerror('Directory "%s" could not be removed, most likely an NFS problem. Try again later.', path)
#            continue # disabled because was leading to a infinite loop
        break
    #end while
#end def

#DEPRECIATED: use routines from disk.py instead
def nTpath(path):

    """Return a triple (directory, basename, extension) from path"
    """
    d = os.path.split(path)
    dname = d[0]
    if len(dname) == 0:
        dname = '.'
    f = os.path.splitext(d[1])
    return dname, f[0], f[1]
#end def

#DEPRECIATED: use routines from disk.py instead
def getFileName(path):
    """Return a basename.extension from path"
    May be empty:
CING 11> os.path.split('/a/')
Out[11]: ('/a', '')

CING 12> os.path.split('/a')
Out[12]: ('/', 'a')
    """
    d = os.path.split(path)
    return d[1]
#end def

#DEPRECIATED: use routines from disk.py instead
def nTmkdir(path):

    """ creates missing directories for the given path and
        returns a normalized absolute version of the path.

    - if the given path already exists in the filesystem
      the filesystem is not modified.

    - otherwise makepath creates directories along the given path
      using the dirname() of the path. You may append
      a '/' to the path if you want it to be a directory path.

    from holger@trillke.net 2002/03/18
    Adusted gv with expanduser

    """
    path=expanduser(path)
    dpath = normpath(dirname(path))
    if not exists(dpath):
        makedirs(dpath)
    return normpath(path)
#end def

#DEPRECIATED:
def showNTobject(nTobject=None):
    '''Used to conflict with matplotlib show so renamed.
    Haven't seen a usage for this in the CING api.
    '''
    if nTobject != None and hasattr(nTobject, 'format'):
        nTmessage("%s", nTobject.format())
    else:
        nTmessage("%s %s", type(nTobject), str(nTobject))
    #end if
# end def

def formatList(theList, fmt = '%s\n'):
    """
    Apply the format method to every element of theList,
    and return their joined strings.
    """
    result = []
    for element in theList:
#        nTdebug("Doing element: " +repr(element))
        result.append(fmt%element.format())
    return ''.join(result)
#end def


class ExecuteProgram(NTdict):
    """
    Base Class for executing external programs on Unix like systems.

    The redirect to file includes also the stderr output stream.
    """
    def __init__(self, pathToProgram,
                 rootPath = None,
                 redirectOutput= True,
                 redirectOutputToFile = False,
                 redirectInputFromDummy = False,
                 redirectInputFromFile = False,
                 appendPathList = None,
                 appendEnvVariableDict = None,
                 *args, **kwds):

        NTdict.__init__(self,    *args, **kwds )

        self.pathToProgram = pathToProgram
        self.rootPath = rootPath
        self.redirectOutput = redirectOutput
        self.redirectOutputToFile = redirectOutputToFile
        self.redirectInputFromDummy = redirectInputFromDummy
        self.redirectInputFromFile = redirectInputFromFile
        self.appendPathList = appendPathList
        self.appendEnvVariableDict = appendEnvVariableDict

        self.jobcount = 0
    #end def

    def __call__(self, *args):
        """
        Execute the program.
        Return exit code. An exit code of zero means success.
        """
        if not self.pathToProgram:
            raise SetupError("No program given for arguments: %r" % args)

        if self.rootPath:
            cmd = sprintf('cd "%s"; %s %s', self.rootPath, self.pathToProgram, " ".join(args))
        else:
            cmd = sprintf('%s %s', self.pathToProgram, " ".join(args))
        #end if

        if self.appendPathList:
            pathListAllTogether = ':'.join( self.appendPathList )
            cmdPathAppend = 'export PATH=%s:$PATH' % pathListAllTogether
            cmd = cmdPathAppend + '; ' + cmd

        if self.appendEnvVariableDict:
            envVariableList = self.appendEnvVariableDict.keys()
            envVariableList.sort()
            extraEnvList = []
            for envVariable in envVariableList:
                extraEnvList.append( 'export %s=%s' % (envVariable, self.appendEnvVariableDict[ envVariable ]))
            extraEnvCmd = ':'.join( extraEnvList )
            cmd = extraEnvCmd + '; ' + cmd


        if self.redirectInputFromDummy and self.redirectInputFromFile:
            nTerror("Can't redirect from dummy and from a file at the same time")
            return 1

        if self.redirectOutputToFile and self.redirectOutput:
#            nTdebug("Can't redirect output to standard filename and given file name at the same time; will use specific filename")
            self.redirectOutput = False


        if self.redirectInputFromDummy:
            cmd = sprintf('%s < /dev/null', cmd)
        elif self.redirectInputFromFile:
            cmd = '%s < %s' % (cmd, self.redirectInputFromFile)


        if self.redirectOutput:
            _dir, name, _ext = nTpath(self.pathToProgram)
            # python call shell sh and in some os (e.g. linux) >& may not work
            # see http://diveintomark.org/archives/2006/09/19/bad-fd-number
            cmd = sprintf('%s > %s.out%d 2>&1', cmd, name, self.jobcount)
            self.jobcount += 1
        elif self.redirectOutputToFile:
            cmd = sprintf('%s > %s 2>&1', cmd, self.redirectOutputToFile)
            self.jobcount += 1
#        nTdebug('==> Executing ('+cmd+') ... ')
#        nTdebug("Executing command: [%s]" % cmd)
        if 1: # take alternative without output buffering?
            code = os.system(cmd)
        else:
            pass
#        nTdebug( "Got back from system the exit code: " + repr(code) )
        return code
    # end def
#end class

def getOsResult( cmd ):
    """
    Returns tuple (status, msg)
    status 0 for success. > 0 for failure.
    """
#    nTdebug( "Doing command: %s" % cmd )

    ##  Try command and check for non-zero exit status
#    pipe = os.popen( cmd )
    pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
    output = pipe.read()

    ##  The program exit status is available by the following construct
    ##  The status will be the exit number unless the program executed
    ##  successfully in which case it will be None.
    status = pipe.close()

#    if output:
#        nTdebug( "Found os msg: %s" % output )

#    if status:
#        nTdebug("Failed shell command:")
#        nTdebug( cmd )
#        nTdebug("Output: %s" % output)
#        nTdebug("Status: %s" % status)

    return ( status, output )


class OptionParser (optparse.OptionParser):
    """
    OptionParser.py: implement required options
    from: http://docs.python.org/lib/optparse-extending-examples.html
    """
    def check_required (self, opt):
        'Only overriding method from standard api.'
        option = self.get_option(opt)
        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)
    #end def
#end class


def findvisitor((matches, pattern), thisdir, nameshere):
    "Taken from O'Reilly book"
    for name in nameshere:
        if fnmatch(name, pattern):
            fullpath = os.path.join(thisdir, name)
            matches.append(fullpath)
# end def

#DEPRECIATED: use routines from disk.py instead
def findFiles(pattern, startdir, exclude=[]): # pylint: disable=W0102
    """
    Find files matching pattern, based upon os.walk
    """
    result = []
    #print exclude
    for dirpath, _dirs, files in os.walk(startdir):

        excludePath = False
        for e in exclude:
            #print '>>',dirpath,e
            if fnmatch(str(dirpath), e):
                excludePath = True
                break
            #end if
        #end for
        #print '>>',dirpath, excludePath

        if not excludePath:
            for fileName in files:
                if fnmatch(fileName, pattern):
                    result.append(os.path.join(dirpath, fileName))
                #end if
            #end for
        #end if
    #end for
    result.sort()
    #print '>>',result
    return result
#end def

def matchString( source, target ):
    """
    Poor mans approach to match a target with wildcards (*) to source.
    Does not properly match XZS* yet because aaXZSxx wil also yield True
    Returns True upon match or False otherwise
    """
    parts = target.split('*')
    for p in parts:
        if source.find(p) < 0:
            return False
    #end for
    return True
#end def

def val2Str(value, fmt, count=None, useNanString=True):
    """Utility for translating numeric values to strings allowing the value
    to be a None and returning the NaNstring in such case. When the value is
    None the count determines how long the return string will be.
    Regular formatting is used otherwise.
    If the input is not a None or of type float it will return None.
    """

    if value==None:
        pass
#        value = None
    elif not isinstance(value, float):
#        try to parse it as a float and see
        try:
            # reduce the next message to debug or lower when happy.
#            if not isinstance(value, int): # no debug warning for ints; easy to parse.
#                nTdebug("In val2Str the input [%s] was not a None and also not of type float; trying to parse as float now" % value)
            value = float(value)
        except:
            nTwarning("In val2Str the input was not a None and also not of type float; failed to parse as float as well.")
            return None
    elif isNaN(value):
        value = None
    if value == None:
        if not count:
            if not useNanString:
                return ''
            return NaNstring
        return ("%"+str(count)+"s") % NaNstring
    return fmt % value
# end def

def limitToRange(v, low, hi):
    """Return a value in range [low,hi}
    truncating the value to given bounds
    E.g. a value of 5 with bounds [0,1] will
    return 1.
    """
    # use equal signs for speed.
    if v >= hi:
        return hi
    if v <= low:
        return low
    return v
# end def

def nTmax(*args):
    """Useful as mat plot lib overrides buildin"""
    result = args[0]
    for a in args:
        if a > result:
            result = a
    return result
# end def

def nTmin(*args):
    """Useful as mat plot lib overrides buildin"""
    result = args[0]
    for a in args:
        if a < result:
            result = a
    return result
# end def


def cross3Dopt(a, b):
    'Cross product (vector) maybe redundant with method in NTvector?'
    return [
        a[1]*b[2]-a[2]*b[1], # x-coordinate
        a[2]*b[0]-a[0]*b[2], # y-coordinate
        a[0]*b[1]-a[1]*b[0]  # z-coordinate
    ]
# end def

def dot3Dopt(a, b):
    'Dot product (scalar) maybe redundant with method in NTvector?'
    return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
# end def

def length3Dopt(a):
    'Vector size (scalar) maybe redundant with method in NTvector?'
    return math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])
# end def


def angle3Dopt(a, b):
    """
    return angle spanned by a and b
    or None on error
    range = [0, pi]
    positive angle is counterclockwise (to be in-line with 'polar' methods
    and atan2 routines).
    """
    # optimized out.
#        c = self.dot(other) /(self.length()*other.length())
    c = dot3Dopt(a, b)
    c /= length3Dopt(a)
    c /= length3Dopt(b)

    # Are the below needed for rounding effects?
    c = min(c, 1.0)
    c = max(c, -1.0)
#        if radians:
#            return math.acos( c )
    return math.acos(c) * FAC
# end def

def appendDeepByKeys(c, value, *keyList):
    """
    Append value to arbitrary deep list.
    If value is a (subclass of) list then append individual values from the list
    to the c (complex object) which needs to be a (subclass of) list itself.
    The essence here is silence.

    NB:
    - keyList needs to have at least one key.

    - All but the last level of the complex object should be (subclasses of)
    dictionaries. The last level must be a (subclasses of) list. If the
    itermediate objects (dictionaries and list) do not exist, they will be
    silently created.

    - The last key is not the id to the list to append to.

    - The complex argument needs to exist.

    Return None on success and True on error.
    """

    if c == None:
        nTerror("Can't appendDeepByKeys without complex object on input.")
        return True

    lk = len(keyList)
#  nTdebug("Now in appendDeepByKeys with keyList: %s", repr(keyList))
    if not lk:
        nTerror("Can't appendDeepByKeys without any key")
        return True

    key = keyList[0]

    # At the level where only one key exists; do the actual append to the list.
    if lk == 1:
        # First make sure the list to append to exists.
        if isinstance(c, list):
            # Make sure the list already has an element with the key as index.
            if key >= len(c):
                nTwarning("Impossible situation: trying to go into a list at an index that isn't present.")
                nTwarning("key: %d and list length: %d" % (key, len(c)))
                return True
        elif isinstance(c, dict):
            if not c.has_key(key):
                c[key] = [] # For last level a new -list- is made when absent.
        else:
            nTwarning("The input complex object needs to be a (subclass of) dict or list")
            return True

        myList = c[key]
        if not isinstance(myList, list):
            nTwarning("At the bottom level the input complex object needs to be a (subclass of) list")
            return True
        if isinstance(value, list):
            for v in value:
                myList.append(v)
            return
        myList.append(value) # No extra checks done here for speed purposes.
        return
    # end if on lk==1, above section was misalligned before.

    if c.has_key(key):
        deeper = c[key]
    else:
        deeper = {}
        c[key] = deeper

    reducedKeyList = keyList[1:]
    return appendDeepByKeys(deeper, value, *reducedKeyList)
# end def


def setDeepByKeys(d, value, *keyList):
    """Set arbitrary deep element to value by keyList.
    The essence here is silence.
    keyList needs to have at least one key.
    Return None on success and True on error.
    """
    lk = len(keyList)
    if not lk:
        nTerror("Can't setDeepByKeys without any key")
        return True

    k = keyList[0]
    if lk == 1:
        d[k] = value
        return

    if d.has_key(k):
        deeper = d[k]
    else:
        deeper = {}
        d[k] = deeper

    reducedKeyList = keyList[1:]
    return setDeepByKeys(deeper, value, *reducedKeyList)
# end def

def addDeepByKeys(d, value, *keyList):
    """Increase found value (or zero in case absent) by given value.
    Return None on success and True on error.
    """
    v = d.getDeepByKeys(*keyList)
    if not v:
        v = 0
    v += value
    return d.setDeepByKeys(v, *keyList)
# end def

def getDeepByKeysOrDefault(c, default, *keyList):
    """NEW: store default if returned; remember silence is key.
    """
    result = getDeepByKeys(c, *keyList)
    if result == None:
        setDeepByKeys(c, default, *keyList)
#        nTdebug("Also set deep by keys the default that is returned now")
        return default
    return result
# end def

def getDeepByKeys(c, *keyList):
    """Return arbitrary deep element or None if key is absent at some point.
    The essence here is silence.
    If the key is an integer and the dict is not a dict but a list of sorts
    then the nice thing is that the element can be returned too!

    c for complex object.
    """
    lk = len(keyList)
#      nTdebug("Now in getDeepByKeys for keylist length: %d" % lk)
    if not lk:
#        nTdebug("Asked for a get on a dictionary without a key")
        return None
    key = keyList[0]

    if isinstance(c, dict):
        if not c.has_key(key):
#          nTdebug("no key: " + repr(key))
            return None
        value = c[key]
        if lk == 1:
#          nTdebug("value : " + repr(value))
            return value
#      nTdebug("Going one level deeper")
        reducedKeyList = keyList[1:]
        return getDeepByKeys(value, *reducedKeyList)

    if not isinstance(c, list):
#      nTdebug("complex object not an instance of list")
        return None

    if not isinstance(key, int):
#      nTdebug("no int key in getDeepByKeys: " + repr(key))
        return None

    if key >= len(c):
#      nTdebug("int key in getDeepByKeys to large for this NTlist: " + repr(key))
        return None

    value = c[key]
    if lk == 1:
#      nTdebug("value : " + repr(value))
        return value

#  nTdebug("Going one level deeper")
    reducedKeyList = keyList[1:]
    return getDeepByKeys(value, *reducedKeyList)
#end def

def getDeepWithNone(c, *keyList):
    'Replace one NaN for a python None while getting value.'
    value = getDeepByKeysOrAttributes(c, *keyList)
    if isNaN(value):
        return None
    return value
# end def

def getDeepByKeysOrAttributes(c, *keyList):
    """Return arbitrary deep element or None if key is absent at some point.
    The essence here is silence.

    If the key is an integer and the dict is not a dict but a list of sorts
    then the nice thing is that the element can be returned too!

    If a key contains a period character then the keyList will be transformed to the split elements.
    Use keys like 'a.b.c' and not: 'a..b', '.a', or 'a.'. They will not be caught.

    c for complex objects.
    Hacked for attributes too, in case key does not exist

    NB getDeepByKeysOrAttributes(o, '__class__', '__name__' ) doesn't give what you would expect.
    """
    if c == None:
        return None

    lk  = len(keyList)
    key = keyList[0]
#    nTdebug("Found keyList: "+repr(keyList))
#    nTdebug("Found key:     %s" % key)
    if isinstance(key, str):
        if key.find('.') > 0:
            keyListTruncated = list(keyList[1:]) # can only concatenate with list not tuple.
#            nTdebug("Found keyListTruncated: "+repr(keyListTruncated))
            keyListTruncated = key.split('.') + keyListTruncated
#            nTdebug("Found keyListTruncated expanded: "+repr(keyListTruncated))
            return getDeepByKeysOrAttributes(c, *keyListTruncated)
    #nTdebug("getDeepByKeysOrAtributes: c:%s  keylist:%s  lk:%d  key: %s", c, keyList, lk, key)

    if not lk:
        return None

    value = None
    if isinstance(c, dict):
        if c.has_key(key):
            value = c[key]
        elif isinstance(key, str) and hasattr(c, key): # attributes need to be strings.
            value = getattr(c, key)
        else:
            return None
        #endif

        if lk == 1:
            return value

    elif isinstance(c, list):
        if isinstance(key, int):
            if key < len(c):
                value = c[key]
            else:
                return None
            #endif
        elif hasattr(c, key):
            value = getattr(c, key)
        else:
            return None
        #endif

    elif isinstance(c, tuple):
        if isinstance(key, int) and key < len(c):
            value = c[key]
        else:
            return None

    else:
        if hasattr(c, key):
            value = getattr(c, key)
        else:
            return None
        #endif
    #end if

    #nTdebug("getDeepByKeysOrAtributes: value: %s", value)

    if lk-1 == 0 or value==None:
        return value

    # still have keys left; use recursion for next element
    reducedKeyList = keyList[1:]
    return getDeepByKeysOrAttributes(value, *reducedKeyList)
#end def

def gunzip(fileNameZipped, outputFileName=None, removeOriginal=False):
    """Returns true on error. Uses python api instead of OS defaults"""
    if not fileNameZipped.endswith('.gz'):
        nTerror("Expected zipped file to have .gz extension; giving up.")
        return True

    inF = GzipFile(fileNameZipped, 'rb')
    s=inF.read()
    inF.close()
    fileName = fileNameZipped[:-3]
    if outputFileName:
        fileName = outputFileName
    outF = file(fileName, 'wb')
    outF.write(s)
    outF.close()
    if removeOriginal:
#        nTdebug("Removing file: %s" % fileNameZipped)
        os.unlink(fileNameZipped)
# end def

def getEnsembleAverageAndSigmaHis(his):
    """According to Rob's paper. Note that weird cases exist which to me
    are counter intuitive
[[ 0.  0.  0.  0.  0.  0.]
 [ 0.  0.  0.  0.  0.  0.]
 [ 0.  0.  0.  0.  0.  0.]
 [ 0.  0.  0.  0.  1.  0.]
 [ 0.  0.  0.  0.  0.  0.]
 [ 0.  0.  1.  0.  0.  0.]]
Gives an c_av of 1. And the c_sd can't be calculated.
Rob might have caught this by requiring c_av be at least 2.0.

        # Calculate the count database average for this histogram and
        # the sigma (s.d.) of it. this is done as defined by equations
        # in: Hooft et al. Objectively judging the quality of a protein
        # structure from a Ramachandran plot. Comput.Appl.Biosci. (1997)
        # vol. 13 (4) pp. 425-430

    """
#    nTdebug("getEnsembleAverageAndSigmaHis on his:\n%s" % his)
    (nr, nc) = his.shape
    s = 0.
    sumsq = 0.
    for r in range(nr):
        for c in range(nc):
            v = his[r, c] # convenience variable
            s += v
            sumsq += v*v
    c_av = sumsq / s # this is not a regular average as far as I can tell.
    if s <= 1.: # possible for small sets.
        nTerror("In getEnsembleAverageAndSigmaHis expected the sum of the histogram to be above one. Returning without s.d. and min/max")
        return (c_av, None, None, None)
    sumsdsq = 0.
    for r in range(nr):
        for c in range(nc):
            v = his[r, c] # convenience variable
            v2 = v - c_av # convenience variable
            sumsdsq += v * v2*v2
#    nTdebug("sumsdsq: %8.3f" % sumsdsq)
    c_sd = sumsdsq / (s-1.)
    c_sd = math.sqrt(c_sd)
    hisMin = amin(his)
    hisMax = amax(his)
    return (c_av, c_sd, hisMin, hisMax)
# end def

def getArithmeticAverageAndSigmaHis(his):
    """Straight up arithmetic average and sd as if linear."""
    if his == None:
        nTerror("Failed getArithmeticAverageAndSigmaHis for his is None")
        return None
    if his.size == 0: # check for preventing division by zero
        nTerror("Failed getArithmeticAverageAndSigmaHis for his size is 0")
        return None
    c_sd = fromnumeric.std(his)
    hisSum = fromnumeric.sum(his)
    c_av = float(hisSum) / his.size
    hisMin = amin(his)
    hisMax = amax(his)
    return (c_av, c_sd, hisMin, hisMax)
# end def

def floatFormat(v, form):
    ''' Just check for nans.'''
    if isNaN(v):
        return NaNstring
    return form % v
# end def

def floatParse(v_str):
    '''Just check for nans.'''
#    nTdebug('''NaNstring [%s]''' % NaNstring)
#    nTdebug('''v_str [%s]''' % v_str)
    if v_str == NaNstring:
        return NaN
    return float(v_str)
# end def

def getTextBetween(s, startString, endString, startIncl=True, endIncl=True):
    """Slice the text to include only that inbetween. Input strings maybe None"""
    if startString:
        startIdx = s.find(startString)
    else:
        startIdx = 0
    if startIdx < 0:
        nTwarning('Failed to find starting string in given string')
        return
    if endString:
        endIdx = s.find(endString, startIdx)
    else:
        endIdx = len(s)

    if endIdx < 0:
        nTwarning('Failed to find ending string in given string')
        return
    if not startIncl:
        startIdx += len(startString)
    if endIncl:
        if endString:
            endIdx += len(endString)
        else:
            endIdx = len(s)

    return s[startIdx:endIdx]
# end def

def stripExtension(path):
    'Given a file or directory name, remove the part with the dot.'
    directory, basename, _extension = nTpath(path)
    return os.path.join(directory, basename)
# end def

def stripExtensions(pathList):
    'Convenience method'
    result = []
    for path in pathList:
        result.append(stripExtension(path))
    return result
# end def

_visitedHashes = {}
def removeRecursivelyAttribute(x, attributeToRemove):
    'Removes an attribute throughout a complex object'
    _visitedHashes.clear()
    _removeRecursivelyAttribute(x, attributeToRemove)
    _visitedHashes.clear()
# end def

def _removeRecursivelyAttribute(x, attributeToRemove):
    """Watch out because this can remove any attribute; be carefull what argument you give."""
    #    Needed for cyclic graphed objects such as project...
    # TODO: make it work more than once...
    if isinstance(x, int) or isinstance(x, float) or x == None:
        return

    h = id(x)
    if not h:
        return
    if _visitedHashes.has_key(h):
        return
    _visitedHashes[h] = None

    if isinstance(x, list) or isinstance(x, tuple):
        for e in x:
            if e == attributeToRemove:
                del x[e]
            _removeRecursivelyAttribute(e, attributeToRemove)
    if isinstance(x, dict):
        for k in x.keys():
            if k == attributeToRemove:
                del x[k]
            else:
                _removeRecursivelyAttribute(x[k], attributeToRemove)
# end def


def bytesToFormattedString(size):
    """1600 bytes will be rounded to 2K"""
    k = 1024
    m = k*k
    g = k*m
    t = m*m
    ck = 'K'
    cM = 'M'
    cG = 'G'
    cT = 'T'
    postFix = ck

    divider = k
    if  size < m:
        divider = k
        postFix = ck
    elif size < g:
        divider = m
        postFix = cM
    elif size < t:
        divider = g
        postFix = cG
    else:
        divider = t
        postFix = cT

    r = size/float(divider)
    result = ("%.0f" % r) + postFix
    return result
# end def

_patternValidPdbId = re.compile( '^\d\w\w\w$' )
_patternInvalidPdbId = re.compile( '^\d\d\d\d$' )
def is_pdb_code( chk_string ):
    """
    This function checks to see if the string is a reasonable candidate for a
    pdb entry code
    """
    match = _patternValidPdbId.match( chk_string )
    if match:
        match = _patternInvalidPdbId.match( chk_string )
        if match:
            if chk_string == '1914': # This may change in the future.
                return True
            # end if
            nTdebug("Currently only PDB ID 1914 has all digits; yet tested: [%s]. Assuming to be valid; please update code." % chk_string)
            return False
        # end if
        return True
    # end if
    return False
# end def

def is_bmrb_code( chk_int ):
    """
    This function checks to see if the input integer is a reasonable candidate for a
    BMRB entry ID that is numeric.
    """
    if not isinstance(chk_int, int):
        nTwarning("Input of %s should be int but is: [%s]" % ( getCallerName(), chk_int))
        return False
    # end if
    # 3 PDB ID 1acp was the first still in existence.
    # 20128 (no PDB ID) was the most recent one in Oct 2012.
    rangeStr = "[%s,%s]" % ( SMALLEST_BMRB_ID, LARGEST_BMRB_ID )
    if chk_int < SMALLEST_BMRB_ID or chk_int > LARGEST_BMRB_ID:
        nTdebug("Input of %s is not a valid BMRB ID because it lies outside the known range: %s" % ( chk_int, rangeStr))
        return False
    # end if
#    nTdebug("Input of %s is a valid BMRB ID because it lies inside the known range: %s" % ( chk_int, rangeStr ))
    return True
# end def

def symlink( file_1, file_2 ):
    """
    Use OS's ln for symlinking.
    """
    cmd = "ln -s %s %s" % (file_1, file_2 )
#    nTdebug( "Running cmd: " + cmd )
    os.system(cmd)

def getDateTimeFromFileName(fn):
    """
    Return False on error
    """
    if not os.path.exists(fn):
        nTerror("File: %s does not exist" % fn)
        return
    timeStamp = os.path.getmtime(fn)
    dateTimeObj = datetime.datetime.fromtimestamp(timeStamp)
    return dateTimeObj

def getDateTimeStampFromFileName(fn):
    """
    Return False on error. This algorithm needs to match it's reversal in
    getDateTimeStampForFileName.

    E.g. NRG-CING/data/br/1brv/log_validateEntry/1brv_2010-09-01_15-51-22.log

    Make sure the time stamp is the last part of the file name and is preceded by an _
    or the only string in the base name.
    """

    _root, name, _ext = nTpath(fn)
    dtList = name.split('_')
    if len(dtList) < 2:
        nTerror("Failed to find date from fn %s with base name %s" % (fn, name))
        return
    dtList = dtList[-2:]
    dtListStr = '-'.join(dtList)
    dtList = dtListStr.split('-')
    dtListInt = [int(x) for x in dtList]
    if len(dtListInt) != 6:
        nTerror("Failed to find date from fn %s with derived int list %s" % (fn, str(dtListInt)))
        return
    dt = datetime.datetime(*dtListInt)
    return dt
# end def

def getTimeStampFromFileName(fn):
    "Convenience method."
    dt = getDateTimeStampFromFileName(fn)
    if not dt:
        return
    t = time.mktime(dt.timetuple())
    return t
# end def

def getDateTimeStampForFileName(nadaDateOrFilename=None):
    """
    Return False on error. This algorithm needs to match it's reversal in
    getDateTimeStampFromFileName
    """
    if not nadaDateOrFilename:
        specDate = datetime.datetime.now()
    elif isinstance(nadaDateOrFilename, datetime.datetime):
        pass
    elif isinstance(nadaDateOrFilename, str):
        if not os.path.exists(nadaDateOrFilename):
            nTerror("Assumed file name argument: %s is not an existing file" % nadaDateOrFilename)
            return
        specDate = getDateTimeFromFileName(nadaDateOrFilename)
        if not specDate:
            nTerror("File: %s gave no datetime" % nadaDateOrFilename)
            return
    else:
        nTerror("Failed to get input that is either nothing, a datetime object or a file name.")
        return
    date_stamp = specDate.isoformat('_')
    date_stamp = re.sub( '[:]', '-', date_stamp )
    date_stamp = re.sub( '\.[0-9]+', '', date_stamp )
    return date_stamp
# end def

def readLinesFromFile(fileName, doStrip=True):
    "Throws exception on failure"
#    nTdebug("Reading from file %s" % ( fileName))
    if doStrip:
        lineList = [ line.strip() for line in open(fileName).readlines() ]
    else:
        lineList = open(fileName).readlines()
#    nTdebug("Read number of lines: %d" %  len(lineList))
    return lineList
# end def

def readTextFromFile(fileName):
    "Return the string or None on error."
#    nTdebug("Reading from file %s" % ( fileName))
    if not os.path.exists(fileName):
        nTwarning("Failed to find %s" % fileName )
        return None
    fp = open(fileName, 'r')
    content = fp.read()
    return content
# end def

def writeTextToFile(fileName, txt, mode='w'):
    """
    Returns True on error. Txt is assumed to be the empty string if None given.
    If the mode is changed to 'a+' appending will be used.
    """
    if not txt:
#        nTdebug("Writing empty file: %s" % fileName)
        txt = EMPTY_STRING
#        nTerror("Failed to writeTextToFile for text: [%s]" % str(txt))
#        return True
    # end def
#    nTdebug("Writing to %s text (first 20 chars) [%s]" % ( fileName, txt[:20]))
    try:
        fp = open(fileName, mode)
        fprintf(fp, txt)
        fp.close()
    except:
        nTtracebackError()
        return True
# end def

def appendTextFileToFile( srcFile, dstFile):
    'Creates a new file if needed.'
    txt = readTextFromFile(srcFile)
    if txt == None:
        nTerror('Failed appendFileToFile because failed to read.')
        return True
    if writeTextToFile(dstFile, txt, mode='a+'):
        nTerror('Failed appendFileToFile because failed to append.')
        return True
# end def

def writeDataToFile(fileName, data):
    """Returns True on error"""
#    nTdebug("Writing to %s text (first 20 chars) [%s]" % ( fileName, txt[:20]))
    try:
        fp = open(fileName, 'wb')
        fp.write(data)
        fp.close()
    except:
        nTtracebackError()
        return True
# end def

def toCsv(inObject):
    'Return None on empty or invalid inObject.'
    if not inObject:
        return None
    result = ''
    if isinstance(inObject, list):
        for item in inObject:
            result += "%s\n" % item
    if isinstance(inObject, dict):
        keyList = inObject.keys()
        keyList.sort()
        for key in keyList:
            result += "%s,%s\n" % ( key, str(inObject[key]) )
    return result
# end def

def updateAndReturnDict(d, fromDict):
    e = NTdict()
    e( **d )
    e( **fromDict )
    return e
# end def



prefixError     = 'ERROR: '
prefixCodeError = 'ERROR IN CODE: '
prefixException = 'EXCEPTION CAUGHT: '
prefixWarning   = 'WARNING: '
prefixDebug     = 'DEBUG: '

nTnothing = PrintWrap(verbose=verbosityNothing) # JFD added but totally silly
nTerror   = PrintWrap(verbose=verbosityError, prefix = prefixError, stream=sys.stderr)
nTcodeerror=PrintWrap(verbose=verbosityError, prefix = prefixCodeError, stream=sys.stderr)
nTexception=PrintWrap(verbose=verbosityError, prefix = prefixException, stream=sys.stderr)
nTwarning = PrintWrap(verbose=verbosityWarning, prefix = prefixWarning, stream=sys.stderr)
nTmessage = PrintWrap(verbose=verbosityOutput)
nTdetail  = PrintWrap(verbose=verbosityDetail)
nTdebug   = PrintWrap(verbose=verbosityDebug, prefix = prefixDebug, stream=sys.stderr)
nTmessageNoEOL = PrintWrap(verbose=verbosityOutput, noEOL=True)

kwdsPrintWrap = {'useDate':True, 'useProcessId':True, 'doubleToStandardStreams': True}
nTnothingT              = PrintWrap(verbose=verbosityNothing                            , **kwdsPrintWrap)
nTerrorT                = PrintWrap(verbose=verbosityError, prefix = prefixError        , **kwdsPrintWrap)
nTcodeerrorT            = PrintWrap(verbose=verbosityError, prefix = prefixCodeError    , **kwdsPrintWrap)
nTexceptionT            = PrintWrap(verbose=verbosityError, prefix = prefixException    , **kwdsPrintWrap)
nTwarningT              = PrintWrap(verbose=verbosityWarning, prefix = prefixWarning    , **kwdsPrintWrap)
nTmessageT              = PrintWrap(verbose=verbosityOutput                             , **kwdsPrintWrap)
nTdetailT               = PrintWrap(verbose=verbosityDetail                             , **kwdsPrintWrap)
nTdebugT                = PrintWrap(verbose=verbosityDebug, prefix = prefixDebug        , **kwdsPrintWrap)
nTmessageNoEOLT         = PrintWrap(verbose=verbosityOutput, noEOL=True                 , **kwdsPrintWrap)

nTmessageList = ( #@UnusedVariable used in NTutils2
  nTnothing,  nTerror ,  nTcodeerror ,  nTexception ,  nTwarning ,  nTmessage ,  nTdetail ,  nTdebug,  nTmessageNoEOL,
  nTnothingT, nTerrorT , nTcodeerrorT , nTexceptionT , nTwarningT , nTmessageT , nTdetailT , nTdebugT, nTmessageNoEOLT
)

# Block with depreciated aliases. Please add.
NTnothing       = nTnothing
NTerror         = nTerror
NTcodeerror     = nTcodeerror
NTexception     = nTexception
NTwarning       = nTwarning
NTmessage       = nTmessage
NTdetail        = nTdetail
NTdebug         = nTdebug
NTmessageNoEOL  = nTmessageNoEOL
# repeat with T
NTnothingT       = nTnothingT
NTerrorT         = nTerrorT
NTcodeerrorT     = nTcodeerrorT
NTexceptionT     = nTexceptionT
NTwarningT       = nTwarningT
NTmessageT       = nTmessageT
NTdetailT        = nTdetailT
NTdebugT         = nTdebugT
NTmessageNoEOLT  = nTmessageNoEOLT
# Other functions
NTaverage          = nTaverage
NTaverage2         = nTaverage2
NTcAverage         = nTcAverage
NTcVarianceAverage = nTcVarianceAverage
NTexit             = nTexit
NTfill             = nTfill
NThistogram        = nThistogram

NTlimit            = nTlimit
NTlimitSingleValue = nTlimitSingleValue
NTmax              = nTmax
NTmin              = nTmin
NTmkdir            = nTmkdir
NTpath             = nTpath
NTsign             = nTsign
NTsq               = nTsq
NTzap              = nTzap

# Block the import so it stays here.
if 1:
    from cing.Libs.NTutils2 import * #@UnusedWildImport
