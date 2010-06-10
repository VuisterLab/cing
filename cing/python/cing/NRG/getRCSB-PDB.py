"""
Collect data needed for nrgcing from RCSB-PDB REST calls.

Execute like:

python $CINGROOT/python/cing/NRG/getRCSB-PDB.py

JFD: funny, this is the only project pydev isn't analyzing.
"""
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.PDBEntryLists import getPdbEntries
from cing.NRG.PDBEntryLists import writeEntryListToFile
import unittest

cing.verbosity = cing.verbosityDebug
os.chdir(cingDirTmp)

testing = False
if testing: # testing with smaller set
    pdbList = getPdbEntries(mustHaveExperimentalNmrData = True,onlySolidState=True)
else:
    pdbList = getPdbEntries(mustHaveExperimentalNmrData = True)

NTmessage("getPdbEntries exp: %d" % (len(pdbList)))

writeEntryListToFile('hasExpData.csv', pdbList)

