"""
Collect data needed for nrgcing from RCSB-PDB REST calls.

Excecute like:

python $CINGROOT/python/cing/NRG/getRCSB-PDB.py
"""
from cing.NRG.PDBEntryLists import getPdbEntries
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.Libs.NTutils import NTmessage
from cing import cingDirTmp

import cing
import os
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

