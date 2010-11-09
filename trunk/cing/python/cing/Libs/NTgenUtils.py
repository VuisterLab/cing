'''
Created on Nov 5, 2010

@author: jd
'''
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport

def analyzeCingLog(logFile):
    """
    Returns [timeTaken, crashed, nr_error, nr_warning, nr_message, nr_debug]
    Return None on error.

    The numbers of lines should add up to the total number of lines.
    For a specific other log file type look at the example in cing.Scripts.FC.utils

    The
    """
    result = [ None, None, 0, 0, 0, 0 ]
    if not logFile:
        NTerror("logFile %s was not specified." % logFile)
        return None
    if not os.path.exists(logFile):
        NTerror("logFile %s was not found." % logFile)
        return None

    for r in AwkLike(logFile):
        line = r.dollar[0]
        if line.startswith(prefixError):
            result[2] += 1
        elif line.startswith(prefixWarning):
            result[3] += 1
        elif line.startswith(prefixDebug):
            result[5] += 1
        else:
            result[4] += 1
            if line.startswith('CING took       :'):
    #            NTdebug("Matched line: %s" % line)
                timeTakenStr = r.dollar[r.NF - 1]
                result[0] = float(timeTakenStr)
    #            NTdebug("Found time: %s" % self.timeTakenDict[entry_code])
            elif line.startswith('Traceback (most recent call last)'):
    #            NTdebug("Matched line: %s" % line)
                result[1] = True
        # end else
    return result
# end def

def analyzeFcLog(logFile):
    """
    Returns [timeTaken, crashed, nr_error, nr_warning, nr_message, nr_debug]
    Return None on error.

    The numbers of lines should add up to the total number of lines.
    For a specific other log file type look at the example in cing.Scripts.FC.utils
    """
    result = [ None, None, 0, 0, 0, 0 ]
    if not logFile:
        NTerror("logFile %s was not specified." % logFile)
        return None
    if not os.path.exists(logFile):
        NTerror("logFile %s was not found." % logFile)
        return None

    for r in AwkLike(logFile):
        line = r.dollar[0]
        line = line.lower()
        if line.count('error'):
            result[2] += 1
        elif line.count('warning'):
            result[3] += 1
        elif line.count('debug'):
            result[5] += 1
        else:
            result[4] += 1
#            if line.startswith('CING took       :'):
#    #            NTdebug("Matched line: %s" % line)
#                timeTakenStr = r.dollar[r.NF - 1]
#                result[0] = float(timeTakenStr)
#    #            NTdebug("Found time: %s" % self.timeTakenDict[entry_code])
            if line.startswith('traceback (most recent call last)'): # watch out this needs to be lowercase here.
    #            NTdebug("Matched line: %s" % line)
                result[1] = True
        # end else
    return result
# end def

def analyzeWattosLog(logFile):
    """
    Returns [timeTaken, crashed, nr_error, nr_warning, nr_message, nr_debug]
    Return None on error.

    The numbers of lines should add up to the total number of lines.
    For a specific other log file type look at the example in cing.Scripts.FC.utils

    The
    """
    result = [ None, None, 0, 0, 0, 0 ]
    if not logFile:
        NTerror("logFile %s was not specified." % logFile)
        return None
    if not os.path.exists(logFile):
        NTerror("logFile %s was not found." % logFile)
        return None

    for r in AwkLike(logFile):
        line = r.dollar[0]
        if line.startswith(prefixError):
            result[2] += 1
        elif line.startswith(prefixWarning):
            result[3] += 1
        elif line.startswith(prefixDebug):
            result[5] += 1
        else:
            result[4] += 1
            # Wattos took (#ms): 2332
            if line.startswith('Wattos took'): # TODO: check.
                NTdebug("Matched line: %s" % line)
                timeTakenStr = r.dollar[r.NF - 1]
                result[0] = float(timeTakenStr)
                if result[0]:
                    result[0] /= 1000. # get seconds
                NTdebug("Found time: %s" % timeTakenStr)
            elif line.startswith('Exception in thread'): # TODO: check.
                NTdebug("Matched line: %s" % line)
                result[1] = True
        # end else
    return result
# end def

