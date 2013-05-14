# NEW Tim is taking the data from the csv files at:
#NMR          http://nmr.cmbi.ru.nl/NRG-CING/entry_list_nmr.csv;
#NRG          http://nmr.cmbi.ru.nl/NRG-CING/entry_list_nrg.csv;
#NRG-DOCR     http://nmr.cmbi.ru.nl/NRG-CING/entry_list_nrg_docr.csv;
#NRG-CING     http://nmr.cmbi.ru.nl/NRG-CING/entry_list_done.csv;

#The WHY_NOT comments need to be presented in a .txt file at cmbi8:/usr/scratch/whynot/comments. 
#The fixed format looks like:

#
#PDBID        : 2q23
#Database     : PDB_REDO
#Property     : Exists
#Boolean      : false
#Comment      : Cannot reproduce Rfactor within 0.10 tolerance
#//
#PDBID        : 1gi7
#Database     : PDB_REDO
#Property     : Exists
#Boolean      : true
#Comment      : No R-free set in experimental data
#//
#PDBID        : 1gi7
#Database     : PDB_REDO
#Property     : Exists
#Boolean      : false
#Comment      : refmac: error in initial R-free calculation
#//
#PDBID        : 1gi8
#Database     : PDB_REDO
#Property     : Exists
#Boolean      : true
#Comment      : No R-free set in experimental data
#//
from cing import issueListUrl
from cing.Libs.NTutils import * #@UnusedWildImport

booleanStrTrue = 'true'
booleanStrFalse = 'false'

PROJECT_ID_BMRB     = 'BMRB'
PROJECT_ID_CCPN     = 'CCPN'
PROJECT_ID_CING     = 'CING'
PROJECT_ID_NRG      = 'NRG'
PROJECT_ID_PDB      = 'PDB'
PROJECT_ID_WATTOS   = 'WATTOS'

# In future there might be better trackers.
PROJECT_ISSUE_URL_BMRB      = issueListUrl
PROJECT_ISSUE_URL_CCPN      = 'http://sourceforge.net/tracker/?func=detail&group_id=120914&atid=688631&aid='
PROJECT_ISSUE_URL_CING      = issueListUrl
PROJECT_ISSUE_URL_NRG       = 'http://code.google.com/p/nmrrestrntsgrid/issues/detail?id='
PROJECT_ISSUE_URL_PDB       = issueListUrl
PROJECT_ISSUE_URL_WATTOS    = 'http://code.google.com/p/wattos/issues/detail?id='

NOT_NMR_ENTRY = "Not an NMR entry."
NO_EXPERIMENTAL_DATA = "No experimental data."
FAILED_TO_BE_CONVERTED_NRG = "Failed to be converted in NRG."
TO_BE_VALIDATED_BY_CING = "To be validated by CING"
FAILED_TO_BE_VALIDATED_CING = "Failed to be validated in CING."
# entries simply present in CING don't need to be written out in the comments file.
PRESENT_IN_CING = "Present in CING."
#PRESENT_IN_CING = ""


# pylint: disable=R0903
class WhyNotEntry:
    def __init__(self, entryId, exists=True, comment=''):
        self.entryId = entryId
        self.exists = exists
        self.comment = comment

class WhyNot(dict):
    def __str__(self):
        result = ''
        keyList = self.keys()
        keyList.sort()
        for key in keyList:
            whyNotEntry = self[key]
            boolStr = booleanStrFalse
            if whyNotEntry.exists:
                boolStr = booleanStrTrue
            entryText = \
"""PDBID        : %s
Database     : NRG-CING
Property     : Exists
Boolean      : %s
Comment      : %s
//
""" % (whyNotEntry.entryId, boolStr, whyNotEntry.comment,)
            result += entryText
        return result
