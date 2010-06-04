'''
Created on Jun 2, 2010

To be executed on the Analysis command line for introspection.

Rather temporary code for learning the Analysis API

@author: jd
'''
from UtilsAnalysis.Utils import getPeakLists
from ccp.api.nmr.Nmr import Peak
from ccp.api.nmr.Nmr import PeakIntensity

top = top #@UndefinedVariable
p = top.getProject()


peakLists = getPeakLists(p)

lastPeakList = peakLists[-1]

firstPeak = Peak()
peakI = PeakIntensity()

firstPeak = lastPeakList.findFirstPeak()
print firstPeak

peakI = firstPeak.peakIntensities
print peakI

firstPeak.details