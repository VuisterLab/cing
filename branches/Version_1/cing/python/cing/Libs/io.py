"""
General I/O routines (non cing specific)
"""
import sys
#import os
import time

import cing


class Time(float):
    """Simple class to print time in ascii, represented as floats as in time.time()"""
    def __str__(self):
        """Print as a string"""
        return time.asctime(time.localtime(self))

    def __repr__(self):
        return 'Time(%s)' % float.__repr__(self)

    @staticmethod
    def fromString(string):
        """Make from a string, inverse of __str__"""
        return Time(time.mktime(time.strptime(string)))
#end class


def now():
    return Time(time.time())
day = 24*3600.0
week = 7*day
year = 365*day


def formatDictItems(theDict, fmt='{key:20} : {value!s}\n'):
    """Use format on key,value pairs of items of theDict
    """
    return ''.join([fmt.format(key=k,value=v) for k, v in theDict.items()])
#end def


def message(fmt, *args, **kwds):
     """Output to stdout depending on verbosity level
       (defined as in cing)
     """
     if cing.verbosity >= cing.verbosityOutput:
         sys.stdout.write(fmt.format(*args, **kwds))
#end def


def warning(fmt, *args, **kwds):
     """Output stderr depending on verbosity level
       (defined as in cing)
     """
     if cing.verbosity >= cing.verbosityWarning:
         sys.stdout.write(fmt.format(*args, **kwds))
#end def


def error(fmt, *args, **kwds):
     """Output stderr depending on verbosity level
       (defined as in cing)
     """
     if cing.verbosity >= cing.verbosityError:
         sys.stderr.write(fmt.format(*args, **kwds))
#end def


def debug(fmt, *args, **kwds):
     """Output stderr depending on verbosity level
       (defined as in cing)
     """
     if cing.verbosity >= cing.verbosityDebug:
         sys.stderr.write(fmt.format(*args, **kwds))
#end def