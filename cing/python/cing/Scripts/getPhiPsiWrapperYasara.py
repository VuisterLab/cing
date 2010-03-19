"""
python $CINGROOT/python/cing/Scripts/getPhiPsiWrapper.py

Use below to find the entries done and todo:

"""
from cing import cingDirScripts
from cing import cingDirTmp
from cing.Libs.NTutils import NTmessage
from cing.Scripts.getPhiPsi import doYasaraAddHydrogens
import cing
import os

Ramachandran = 'Ramachandran'
Janin = 'Janin'
d1d2 = 'd1d2'
#dihedralTodo = Ramachandran
#dihedralTodo = Janin
dihedralComboTodo = d1d2
# Throw away the worst 10 % within the chain.
DEFAULT_BFACTOR_PERCENTAGE_FILTER = 10 # integer number please.
# Then after the above check throw away additionaly any residue above 20
DEFAULT_MAX_BFACTOR = 40
BFACTOR_COLUMN = 7
IDX_COLUMN = 8

def main():
    """This is a potentially dangerous script. It took JFD an hour one time
    to realize it was called inadvertently by not having it wrappen in a function.
"""

    if dihedralComboTodo == Ramachandran:
        subdir = 'phipsi_wi_db'
    elif dihedralComboTodo == Janin:
        subdir = 'chi1chi2_wi_db'
    elif dihedralComboTodo == d1d2:
        subdir = 'd1d2_wi_db'

    # parameters for doScriptOnEntryList
    startDir              = os.path.join(cingDirTmp,     subdir)
    entryListFileName     = os.path.join(cingDirScripts, 'data', 'PDB_todo.txt')

    START_ENTRY_ID                 =0 # default 0
    MAX_ENTRIES_TODO               =20 # default a ridiculously large number like 999999

    os.chdir(os.path.join(startDir, 'pdb_hyd'))
    entryListFile = file(entryListFileName, 'r')
    entryCodeList = []
    chainCodeList = []
    entryCountTotal = 0
    for line in entryListFile.readlines():
        line = line.strip()
        entryCountTotal += 1
        entryCode = line[0:4].lower()
        entryCodeList.append( entryCode )
        chainCode = ''
        chainCode = line[4].upper()
        chainCodeList.append(chainCode)
    entryListFile.close()

    entryCountSelected = len( entryCodeList )
    # lastEntryId is id of last entry excluding the entry itself.
    lastEntryId = min(len(entryCodeList), START_ENTRY_ID+MAX_ENTRIES_TODO)
    entryCodeList = entryCodeList[START_ENTRY_ID:lastEntryId]

    NTmessage('Read      %04d entries    ' % entryCountTotal)
    NTmessage('Selected  %04d entries    ' % entryCountSelected)
    NTmessage('Sliced    %04d entries: %s' % (len(entryCodeList), entryCodeList ))

    for i, entryCode in enumerate(entryCodeList):
        chainCode = chainCodeList[i]
        doYasaraAddHydrogens( entryCode, chainCode )

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
    main()