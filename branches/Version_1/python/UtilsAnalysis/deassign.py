"""
Execute in Analysis as:
CINGROOT = os.getenv('CINGROOT')
execfile('%s/python/UtilsAnalysis/deassign.py' % CINGROOT)
"""
from ccpnmr.format.process.stereoAssignmentSwap import StereoAssignmentSwapCheck
import os

CINGROOT = os.getenv('CINGROOT')
thisFile = '%s/python/UtilsAnalysis/deassign.py' % CINGROOT

print "Now in $CINGROOT/python/UtilsAnalysis/deassign.py"
if 'ccpnProject' not in locals():
    top = top #@UndefinedVariable # pylint: disable=E0601
    ccpnProject = top.getProject()


nmrConstraintStore = ccpnProject.findFirstNmrConstraintStore()
structureEnsemble = ccpnProject.findFirstStructureEnsemble()
numSwapCheckRuns = 3


if not nmrConstraintStore:
    print "Failed to find structureEnsemble; skipping swapCheck"

if not structureEnsemble:
    print "Failed to find nmrConstraintStore; skipping swapCheck"

swapCheck = StereoAssignmentSwapCheck(nmrConstraintStore,structureEnsemble,verbose = True)

#    violationCodes = {'xl': {'violation': 1.0, 'fraction': 0.00001},
#                      'l': {'violation': 0.5, 'fraction': 0.5}}
# Use more restrictive cutoffs than the above defaults.
violationCodes = {'xl': {'violation': 0.5, 'fraction': 0.00001},
                  'l': {'violation': 0.3, 'fraction': 0.5}}

for _swapCheckRun in range(0,numSwapCheckRuns):
    swapCheck.checkSwapsAndClean(violationCodes = violationCodes)

if True:
    # Deassigns all:
    violationCodes = {'xl': {'violation': -999.9, 'fraction': 0.00001},
                      'l': {'violation': -999.9, 'fraction': 0.5}}
    for _swapCheckRun in range(0,numSwapCheckRuns):
        swapCheck.checkSwapsAndClean(violationCodes = violationCodes)
