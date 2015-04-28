'''
Nijmegen Tools utilities, the extensions.

NTutils imports these extensions after it loads it's own code.

Meant to delineate the classes.
'''
from cing.Libs.NTutils import nTcodeerror
from cing.Libs.NTutils import nTcodeerrorT
from cing.Libs.NTutils import nTdebug
from cing.Libs.NTutils import nTdebugT
from cing.Libs.NTutils import nTdetail
from cing.Libs.NTutils import nTdetailT
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import nTerror
from cing.Libs.NTutils import nTerrorT
from cing.Libs.NTutils import nTexception
from cing.Libs.NTutils import nTexceptionT
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import nTmessage
from cing.Libs.NTutils import nTmessageList
from cing.Libs.NTutils import nTmessageNoEOL
from cing.Libs.NTutils import nTmessageNoEOLT
from cing.Libs.NTutils import nTmessageT
from cing.Libs.NTutils import nTnothingT
from cing.Libs.NTutils import nTwarning
from cing.Libs.NTutils import nTwarningT
from cing.Libs.NTutils import getDeepByKeysOrAttributes
from cing.Libs.NTutils import nTfill
from cing.Libs.NTutils import readTextFromFile
from cing.Libs.NTutils import sprintf
from cing.Libs.fpconst import isNaN
from cing.constants import * #@UnusedWildImport
from random import randint
from random import seed
from traceback import format_exc
import datetime
import inspect
import math
import os
import re
import sys
import time

class NTlistOfLists(NTlist):
    """
    Generate a NTlist of NTlist's of rowSize, colSize filled with default's
    """

    def __init__( self, rowSize, colSize, default=None ):
        NTlist.__init__( self )
        for _i in range(rowSize):
            self.append(nTfill(default, colSize))
        self.rowSize = rowSize
        self.colSize = colSize
    #end def

    def getRow( self, rowIndex ):
        """Get a row (trivial!)
        Return None on error
        """
        if rowIndex < 0 or rowIndex > len(self):
            return None
        return self[rowIndex]
    #end def

    def getColumn( self, columnIndex ):
        """Get a column (trivial!)
        Return None on error
        """
        if columnIndex < 0 or columnIndex > self.colSize:
            return None
        result = NTlist()
        for row in self:
            result.append( row[columnIndex] )
        return result
    #end def

    def getDiagonal(self):
        """
        Get the diagonal of a square NTlistOfLists
        return NTlist instance or None on error
        """
        if self.rowSize != self.colSize:
            nTerror('NTlistOflists.getDiagonal: unequal number of rows (%d) and collumns (%d)', self.rowSize, self.colSize)
            return None
        result = NTlist()
        for i in range(self.rowSize):
            result.append(self[i][i])
        #end for
        return result
    #end def

    def format( self, fmt = '%s' ):
        result = ''
        for i in range(self.rowSize):
            result = result + self[i].format(fmt=fmt) + '\n'
        return result
    #end def
#end class

def addStreamnTmessageList(stream):
    for nTm in nTmessageList:
#        print "EEE: starting addStream to %s" % nTm
        nTm.addStream(stream)
def removeStreamnTmessageList():
    for nTm in nTmessageList:
#        print "EEE: starting removeStream to %s" % nTm
        nTm.removeStream()

def teeToFile(logFile):
    '''
    Starts to tee the different verbosity messages to a possibly existing file.
    Return True on failure.
    '''
    stream = None
    try:
        stream = open(logFile, 'a')
    except:
        nTtracebackError()
        return True
    nTnothingT.stream = stream
    nTerrorT.stream = stream
    nTcodeerrorT.stream = stream
    nTexceptionT.stream = stream
    nTwarningT.stream = stream
    nTmessageT.stream = stream
    nTdetailT.stream = stream
    nTdebugT.stream = stream
    nTmessageNoEOLT.stream = stream
    nTnothingT.stream = stream


#class nTmessage2(PrintWrap):
#    def __init__(self):
#        PrintWrap.__init__(self, stream, autoFlush, verbose, noEOL, useDate, useProcessId, doubleToStandardStreams, prefix)
#    def __call__(self):
#

def nTtracebackError():
    traceBackString = format_exc()
#    print 'DEBUG: nTtracebackError: [%s]' % traceBackString
    if traceBackString == None:
        traceBackString = 'No traceback error string available.'
    nTerror(traceBackString)

_outOutputStreamContainerList = [ nTmessageNoEOL, nTdebug, nTdetail, nTmessage, nTwarning ]
_errOutputStreamContainerList = [ nTerror, nTcodeerror, nTexception ]

#: To dump some output to never see again
_bitBucket = open('/dev/null', 'aw')
#: Regular output at the start of the program"
_returnMyStdOut = sys.stdout
#: Error output at the start of the program"
_returnMyStdErr = sys.stderr

def _setStdOutStreamsTo(stream):
    return _setOutStreamList(stream, _outOutputStreamContainerList)

def _setStdErrStreamsTo(stream):
    return _setOutStreamList(stream, _errOutputStreamContainerList)

def _setOutStreamList(stream, outputStreamContainerList):
    for outputStreamContainer in outputStreamContainerList:
#        print "Setting the outputStreamContainer [%s] stream to: %s" % (outputStreamContainer, stream)
        outputStreamContainer.flush()
        outputStreamContainer.stream = stream



def switchOutput( showOutput, doStdOut=True, doStdErr=False):
    """
    Switch away from output. Might be useful to silence verbose part of code or external program.

    False: store original stream and switch to bit bucket.
    True: return to original stream.
    """
    if showOutput:
        if doStdOut:
            sys.stdout = _returnMyStdOut
            _setStdOutStreamsTo( _returnMyStdOut )
#            print "1DEBUG: enabled stdout"
        if doStdErr:
            sys.stderr = _returnMyStdErr
            _setStdErrStreamsTo( _returnMyStdErr )
#            print "1DEBUG: enabled stderr"
        return
    if doStdOut:
#        print "1DEBUG: disabling stdout"
        sys.stdout = _bitBucket
        _setStdOutStreamsTo( _bitBucket )
    if doStdErr:
#        print "1DEBUG: disabling stderr"
        sys.stderr = _bitBucket
        _setStdErrStreamsTo( _bitBucket )

class MsgHoL(NTdict):
    def __init__(self):
        NTdict.__init__(self)
        self[ ERROR_ID ] =  NTlist()
        self[ WARNING_ID ] =  NTlist()
        self[ MESSAGE_ID ] =  NTlist()
        self[ DEBUG_ID ] =  NTlist()

    def appendError(self, msg):
        self[ ERROR_ID ].append(msg)
    def appendWarning(self, msg):
        self[ WARNING_ID ].append(msg)
    def appendMessage(self, msg):
        self[ MESSAGE_ID ].append(msg)
    def appendDebug(self, msg):
        self[ DEBUG_ID ].append(msg)

    def showMessage( self, max_errors = 5, max_warnings = 5, max_messages = 5, max_debugs = 20 ):
        "Limited printing of errors and the like; might have moved the arguments to the init but let's not waste time."

        typeCountList = { ERROR_ID: max_errors, WARNING_ID: max_warnings, MESSAGE_ID: max_messages, DEBUG_ID: max_debugs }
        typeReportFunctionList = { ERROR_ID: nTerror, WARNING_ID: nTwarning, MESSAGE_ID: nTmessage,  DEBUG_ID: nTdebug }

        for t in typeCountList:
            if not self.has_key(t):
                continue

            typeCount = typeCountList[ t ]
            msgList = self[t]
            typeReportFunction = typeReportFunctionList[ t ]
            msgListLength = len(msgList)
#            nTdebug("now for typeCount: %d found %d" % (typeCount, msgListLength))
            for i in range(msgListLength):
                if i >= typeCount:
                    typeReportFunction("and so on for a total of %d messages" % len(msgList))
                    break
                typeReportFunction(msgList[i])
    #end def
# end classs

class BitSet(NTlist):
    """From Java for Stereo"""
    def __init__(self):
        NTlist.__init__(self)

    def get(self, idx):
        if idx >= self.n:
            return False
        return self[idx]


def isAlmostEqual( ntList, epsilon):
    e = ntList[0] - ntList[1]
    e = math.fabs(e)
    if e < epsilon:
        return True
    return False
# end def

def toPoundedComment(msg):
    ' Return a string with for each line in msg a pound character and space added.'
    result = []
    for line in msg.split('\n'):
#        nTdebug("Processing line: [%s]" % line)
        result.append( '# %s' % line )
    resultStr = '\n'.join(result)
    return resultStr

def nTlist2dict(lst):
    """Takes a list of keys and turns it into a dict where the values are counts of how many times the key ocurred."""
    dic = {}
    for k in lst:
        if dic.has_key(k):
            dic[k] = dic[k] + 1
        else:
            dic[k] = 1
    return dic
list2dict = nTlist2dict

def getKeyWithLargestCount(count):
    """Return the key in the hashmap of count for which the value
    is the largest.
    Return None if count is empty.
    """
    countMax = -1
    for v in count:
        countV = count[v]
#        nTdebug("Considering key/value %s/%s" % (v,countV))
        if countV > countMax:
            countMax = countV
            vMax = v
#            nTdebug("Set max key/value %s/%s" % (vMax,countMax))
    if countMax < 0: # nothing found
        return None
    return vMax

def grep(fileName, txt, resultList = None, doQuiet=False, caseSensitive=True):
    """
    Exit status is 0 if selected lines are found and 1 if none are found.
    Exit status 2 is returned if an error occurred, unless the -q or --quiet or --silent option is used and a selected line is found.
    Instead of printing, a resultList will be filled if provided.
    """
    if not os.path.exists(fileName):
        return 2
    if not caseSensitive:
        txt = txt.lower()

    matchedLine = False
    for line in open(fileName):
        if len(line):
            line = line[:-1] # must be at least 1 char long
        else:
            nTcodeerror("Fix code in grep")
        lineMod = line
        if not caseSensitive:
            lineMod = lineMod.lower()
        if txt in lineMod:
#            nTdebug("Matched line in grep: %s" % lineMod)
            if resultList != None:
                resultList.append(line)
            if doQuiet:
                # important for not scanning whole file.
                return 0
            matchedLine = True
    if matchedLine:
        return 0
    return 1

def timedelta2Hms( s ):
    'Returns integer numbers for number of minutes and seconds of given float of seconds; may be negative'
    result = [0, 0, 0]
    t = s
    result[0] = int(t / 3600)
    t -= 3600 * result[0]
    result[1] = int(t / 60)
    t -= 60 * result[1]
    result[2] = int(t)
    return tuple(result)

def lenNonZero(myList, eps=EPSILON_RESTRAINT_VALUE_FLOAT):
    'Counts the non zero eelements when compared to epsilon'
    if myList == None:
        return 0
#    if len(myList) == 0:
#        return 0
    n = 0
    for item in myList:
        if math.fabs(item) > eps:
            n += 1
    return n

def stringMeansBooleanTrue(inputStr):
    """
    Returns True if it's a string that is either 1 (any non-zero), True, etc.
    Optimized for speed. See unit test.
    """
    if inputStr == None:
        return False
    if not isinstance(inputStr, str):
        return False
    inputStrlower = inputStr.lower()
    if inputStrlower == 'true':
        return True
    if inputStrlower == 'false':
        return False
    if inputStrlower == 't':
        return True
    if inputStrlower == 'f':
        return False
    if inputStrlower == 'y':
        return True
    if inputStrlower == 'n':
        return False
    if inputStrlower == 'yes':
        return True
    if inputStrlower == 'no':
        return False

    try:
        inputInt = int(inputStr)
    except:
        nTwarning("Failed to get integer after testing string possibilities")
        inputInt = 0

    if inputInt:
        return True
    return False
# end def

def truthToInt(i):
    if i == None:
        return None
    if i:
        return 1
    return 0
# end def

def getCallerName():
    callerFrame = inspect.stack()[1]
#    nTdebug("callerFrame: %s" % str(callerFrame))
    return callerFrame[3]
# end def

def getCallerFileName():
    callerFrame = inspect.stack()[1]
    # Not using inspect.getsourcefile(object) because:
    # This will fail with a TypeError if the object is a built-in module, class, or function.
#    nTdebug("callerFrame: %s" % str(callerFrame))
    return callerFrame[1]
# end def

def getRandomKey(size=6):
    """Get a random alphanumeric string of a given size"""
    alphaNumericList = [chr(x) for x in range(48, 58) + range(65, 91) + range(97, 123)]
    #random.shuffle(alphaNumericList)

    n = len(alphaNumericList) - 1
    seed(time.time()*time.time())

    return ''.join([alphaNumericList[randint(0, n)] for x in range(size)])
# end def

def isNoneorNaN(value):
    if value == None:
        return True
    return isNaN(value)
# end def



def getUniqueName(objectListWithNameAttribute, baseName, nameFormat = "%s_%d" ):
    """
    Return unique name or False on error.
    E.g. for ResonanceSources object in which the ResonanceList objects have a name attribute.

    nameFormat may be specified to receive a string and an integer argument.
    Works on any NTlist that has name attributes in each element.
    """
    nameList = objectListWithNameAttribute.zap( NAME_STR )
#    nTdebug("Already have names: %s" % str(nameList))

    nameDict = nTlist2dict(nameList)
    if not nameDict.has_key( baseName):
        return baseName
    i = 1
    while i < MAX_TRIES_UNIQUE_NAME: # This code is optimal unless number of objects get to 10**5.
        newName = sprintf( nameFormat, baseName, i)
        if not nameDict.has_key( newName ):
            return newName
        i += 1
# end def

def getObjectByName(ll, name):
    """
    Return list by name or False.
    Works on any NTlist that has name attributes in each element.

    E.g. for ResonanceSources object in which the ResonanceList objects have a name attribute.
    """
#    nTdebug("Working on ll: %s" % str(ll))
#    nTdebug("ll[0].name: %s" % ll[0].name)
    names = ll.zap('name')
#    nTdebug("names: %s" % str(names))
    idx = names.index(name)
    if idx < 0:
        return
    return ll[idx]
# end def

def getObjectIdx(ll, obj):
    """
    Return list by name or False.
    Works on any NTlist that has name attributes in each element.
    """
    name = obj.name
    names = ll.zap('name')
    return names.index(name)
# end def


def filterListByObjectClassName( myList, className ):
    'Return new list with only those objects that have given class name.'
    result = []
    if myList == None:
        return result
    if not isinstance(myList, list):
        nTerror('Input is not a list but a %s' % str(myList))
        return result
#    if len(myList) == 0:
#        return result
    for obj in myList:
        oClassName = getDeepByKeysOrAttributes(obj, '__class__', '__name__' )
#        nTdebug("oClassName: %s" % oClassName)
        if oClassName == className:
            result.append(obj)
    return result
# end def

def getRevDateCingLog( fileName ):
    """Return int revision and date or None on error."""
    txt = readTextFromFile(fileName)
    if txt == None:
        nTerror("In %s failed to find %s" % ( getCallerName(), fileName))
        return None
    # Parse
##======================================================================================================
##| CING: Common Interface for NMR structure Generation version 0.95 (r972)       AW,JFD,GWV 2004-2011 |
##======================================================================================================
#User: i          on: vc (linux/32bit/8cores/2.6.4)              at: (10370) Sat Apr 16 14:24:12 2011
    txtLineList = txt.splitlines()
    if len(txtLineList) < 2:
        nTerror("In %s failed to find at least two lines in %s" % ( getCallerName(), fileName))
        return None
    txtLine = txtLineList[1]
    reMatch = re.compile('^.+\(r(\d+)\)') # The number between brackets.
    searchObj = reMatch.search(txtLine)
    if not searchObj:
        nTerror("In %s failed to find a regular expression match for the revision number in line %s" % ( getCallerName(), txtLine))
        return None
    rev = int(searchObj.group(1))

    if len(txtLineList) < 4:
        nTerror("In %s failed to find at least four lines in %s" % ( getCallerName(), fileName))
        return None
    txtLine = txtLineList[3]
    reMatch = re.compile('^.+\(\d+\) (.+)$') # The 24 character standard notation from time.asctime()
    searchObj = reMatch.search(txtLine)
    if not searchObj:
        nTerror("In %s failed to find a regular expression match for the start timestamp in line %s" % ( getCallerName(), txtLine))
        return None
    tsStr = searchObj.group(1) #    Sat Apr 16 14:24:12 2011
    try:
#        struct_timeObject = time.strptime(tsStr)
        dt = datetime.datetime(*(time.strptime(tsStr)[0:6]))
#        dt = datetime.datetime.strptime(tsStr)
    except:
        nTtracebackError()
        nTerror("Failed to parse datetime from: %s" % tsStr )
        return None

    return rev, dt
# end def

def execfile_(filename, globals_=None, locals_=None):
    "Carefull this program can kill."
    if globals_ is None:
        globals_ = globals()
    if locals_ is None:
        locals_ = globals_
    text = file(filename, 'r').read()
    exec text in globals_, locals_
# end def

def nTflatten(obj):
    'Returns a tuple instead of the more commonly used NTlist or straight up list because this is going to be used for formatted printing.'
    if not isinstance(obj, (list, tuple)):
        nTerror("Object is not a list or tuple: %s", obj)
        return None
    result =[]
    for element in obj:
        if isinstance(element, (list, tuple)):
            elementFlattened = nTflatten(element)
            if not isinstance(elementFlattened, (list, tuple)):
                nTerror("ElementFlattened is not a list or tuple: %s", obj)
                return None
            result += elementFlattened
        else:
            result.append(element)
        # end if
    # end for
    return tuple( result )
# end def

def transpose(a):
    '''Compute the transpose of a matrix. Moved from svd package where it was disabled.'''
    m = len(a)
    n = len(a[0])
    at = []
    for i in range(n):
        at.append([0.0]*m)
    for i in range(m):
        for j in range(n):
            at[j][i]=a[i][j]
    return at
# end def


def lenRecursive(obj, max_depth = 5):
    """Count the number of values recursively. Walk thru any children elements that are also of type dict
    {a:{b:None, c:None} will give a length of 2
    """
    if not isinstance(obj, (list, tuple, dict)):
        nTerror("In lenRecursive the input was not a dict or list instance but was a %s" % str(obj))
        return None
    count = 0
    eList = obj
    if isinstance(obj, dict):
        eList = obj.values()
    for element in eList:
        if element == None:
            count += 1
            continue
        if isinstance(element, (list, tuple, dict)):
            new_depth = max_depth - 1
            if new_depth < 0:
                count += 1 # still count but do not go to infinity and beyond
                continue
            count += lenRecursive(element, new_depth)
            continue
        count += 1
    # end for
    return count
# end def

def setToSingleCoreOperation():
    'Set the cing attribute .ncpus to 1'
    if cing.ncpus > 1:
        nTmessage("Scaling back to single core operations.")
        cing.ncpus = 1
        return
    nTmessage("Maintaining single core operations.")
# end def

def capitalizeFirst(s):
    if s == None:
        return
    # end if
    if not isinstance(s, str):
        nTcodeerror('Failed capitalizeFirst with non string argument: [%s]' % str(s))
        return
    # end if
    if len(s) < 1:
        return ''
    # end if
    firstChar = s[0].capitalize()
    if len(s) == 1:
        return firstChar
    # end if
    return firstChar + s[1:]
# end def

def flatten(inputList):
    'Very simple routine to prevent dependency on IPython.utils.data#flatten'
    if not isinstance(inputList,list):
        return inputList
    # end if
    result = reduce(lambda x,y: x+y,inputList)
    return result
# end def
