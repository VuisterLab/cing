'''
Created on Feb 7, 2012

@author: jd
'''
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.helper import detectCPUs
from cing.Scripts.doScriptOnEntryList import doFunctionOnEntryList

def generateHeat(bogusArgument=None):
    """
    Generate heat for space while waiting for Elfstedentocht.
    """
    i = 0
    while True:        
        i += 1
        if i > 10:
            i = 0
        # end if
    # end while
# end def

def generateHeatRun():
    """
    Produce heat for 8 hours
    """
    ncpus = detectCPUs()
    doFunctionOnEntryList(generateHeat,
                        entryListFileName = None,
                        entryList = range(ncpus),
                        processes_max = ncpus,
                        max_time_to_wait = 8 * 60 * 60)
# end def

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
    generateHeatRun()
# end if
