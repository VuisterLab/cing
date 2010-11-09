"""
Author: Jurgen F. Doreleijers, BMRB, June 2006

python -u $CINGROOT/python/cing/NRG/PDBEntryLists.py
"""
from cing import cingPythonDir
from cing import cingRoot
from cing.Libs.DBMS import DBMS
from cing.Libs.NTutils import * #@UnusedWildImport
import urllib
import urllib2

urlDB2 = "http://restraintsgrid.bmrb.wisc.edu/servlet_data/viavia/mr_mysql_backup/"
#urlDB2 = "http://restraintsgrid.bmrb.wisc.edu/servlet_data/viavia/mr_mysql_backupAn_2009-08-03/"
#urlDB2 = "http://nmr.cmbi.ru.nl/~jd/viavia/mr_mysql_backup/"

#ocaUrl = "http://oca.ebi.ac.uk/oca-bin/ocaids"
ocaUrl = "http://www.ebi.ac.uk/msd-srv/oca/oca-bin/ocaids"

testingLocally = False
if testingLocally:
    urlDB2 = "http://localhost/servlet_data/viavia/mr_mysql_backup/" # For fastest develop.
    ocaUrl = "http://localhost/oca" # For fastest develop.

matchBmrbPdbDataDir = "data/NRG/bmrbPdbMatch" # wrt $CINGROOT
matchBmrbPdbTable = 'newMany2OneTable'

def getEntryListFromCsvFile(urlLocation):
  result = []
##108d
##149d
  r1 = urllib.urlopen(urlLocation)
  data = r1.read()
  r1.close()
  dataLines = data.split("\n")
  for dataLine in dataLines:
    if dataLine:
        (pdbCode,) = dataLine.split()
        result.append(pdbCode)
  return result

def getBmrbLinks():
    """ Returns None for failure
    Returns matches_many2one hash.
    """
    dbms = DBMS()
    matchBmrbPdbDataDirLocal = os.path.join(cingRoot, matchBmrbPdbDataDir) # Needs to change to live resource as well.
    dbms.readCsvRelationList([ matchBmrbPdbTable ], matchBmrbPdbDataDirLocal)
    mTable = dbms.tables[matchBmrbPdbTable]
#    NTmessage("mTable:\n%s" % mTable.__str__(show_rows=False))
    matches_many2one = mTable.getHash(useSingleValueOfColumn=1) # hashes by first column to the next by default already.
    NTmessage("Found %s matches from PDB to BMRB" % len(matches_many2one))
    return matches_many2one

def getBmrbNmrGridEntries():
  result = []
  urlLocation = urlDB2 + "/entry.txt"
##4583    \N    108d    \N    \N
##4584    \N    149d    \N    \N
  r1 = urllib.urlopen(urlLocation)
  data = r1.read()
  r1.close()
  dataLines = data.split("\n")
  for dataLine in dataLines:
    if dataLine:
        # b is for bogus/unused
        (_entryId, _bmrbId, pdbCode, _in_recoord, _in_dress) = dataLine.split()
        result.append(pdbCode)
  result.sort()
  return result

def getBmrbNmrGridEntriesDOCRfREDDone():
  result = []
  urlLocation = urlDB2 + "/mrfile.txt"
##61458    7567    4-filtered-FRED    2gov    2006-05-11
##61459    7567    4-filtered-FRED    2gov    2006-05-11
  r1 = urllib.urlopen(urlLocation)
  data = r1.read()
  r1.close()
  dataLines = data.split("\n")
  for dataLine in dataLines:
    if dataLine:
        (_mrfile_id, _entry_id, stage, pdbCode, _date_modified) = dataLine.split()
        if stage == "4-filtered-FRED":
            if pdbCode not in result:
                result.append(pdbCode)
  result.sort()
  return result

def getBmrbNmrGridEntriesDOCRDone():
  result = []
  urlLocation = urlDB2 + "/mrfile.txt"
##61458    7567    4-filtered-FRED    2gov    2006-05-11
##61459    7567    4-filtered-FRED    2gov    2006-05-11
  r1 = urllib.urlopen(urlLocation)
  data = r1.read()
  r1.close()
  dataLines = data.split("\n")
  for dataLine in dataLines:
    if dataLine:
        (_mrfile_id, _entry_id, stage, pdbCode, _date_modified) = dataLine.split()
        if stage == "3-converted-DOCR":
            if pdbCode not in result:
                result.append(pdbCode)
  result.sort()
  return result

def writeEntryListToFile(fileName, entryList):
    "Returns True on failure"
    csvText = toCsv(entryList)
    NTdebug("entryList: [%s]" % entryList)
    if not csvText:
        NTerror("Failed to get CSV for %s" % entryList)
        return True
    writeTextToFile(fileName, csvText)

def readEntryListFromFile(fileName):
    "Throws exception on failure"
    return readLinesFromFile(fileName)

def getPdbEntries(onlyNmr = False, mustHaveExperimentalNmrData = False, onlySolidState = False):
    """Includes solution and solid state NMR if onlyNMR is chosen
    """
#    if True: # Default False; used for not bothering sites.
#        return ['1a4d', '2d6p', '2e7r', '3ejo']

    dir_name = os.path.join(cingPythonDir, 'cing', 'NRG', DATA_STR)
    if onlySolidState:
        inputFile = os.path.join(dir_name, 'RESTqueryPDB_NMR_solid.xml')
    elif onlyNmr:
        if mustHaveExperimentalNmrData:
            inputFile = os.path.join(dir_name, 'RESTqueryPDB_NMR_exp.xml')
        else:
            inputFile = os.path.join(dir_name, 'RESTqueryPDB_NMR.xml')
    else:
        if mustHaveExperimentalNmrData:
            inputFile = os.path.join(dir_name, 'RESTqueryPDB_exp.xml')
#            NTcodeerror("Can't query for onlyNmr = True AND mustHaveExperimentalNmrData = True")
#            return
        else:
            inputFile = os.path.join(dir_name, 'RESTqueryPDB.xml')

    rpcUrl = 'http://www.rcsb.org/pdb/rest/search'
    queryText = open(inputFile, 'r').read()
#    NTdebug("queryText:\n%s" % queryText)
#    NTdebug("querying...")
    req = urllib2.Request(url=rpcUrl, data=queryText)
    f = urllib2.urlopen(req)
    result = []
    for record in f.readlines():
        result.append(record.rstrip().lower())

    if not result:
        NTerror("Failed to read file from server")
        return
#    NTdebug("Done successfully.")
    return result


def getPdbEntriesOca(onlyNmr = False):
  """Not really used anymore"""
  result = []
  urlLocation = ocaUrl + "?dat=dep&ex=any&m=du"
  if testingLocally:
      urlLocation = ocaUrl + "/ocaidsPDB"
  if onlyNmr:
      urlLocation = ocaUrl + "?dat=dep&ex=nmr&m=du"
      if testingLocally:
          urlLocation = ocaUrl + "/ocaidsPDB-NMR"

## OCA database search on: Wed Dec  3 10:18:07 2008
## Query: ex=any&m=du
## Hits: 55841 (search time 0 sec)
#100D     Crystal The Highly Distorted Chimeric Deca... Ban                1.90
#101D     Refinement Of Netropsin Bound To DNA: Bias... Goodsell           2.25
  r1 = urllib.urlopen(urlLocation)
  data = r1.read()
  r1.close()

  dataLines = data.split("\n")
  for dataLine in dataLines:
    if dataLine:
        if not dataLine[0].isdigit():
             # skipping html and header.
            continue
        items = dataLine.split()
        if items:
            pdbCode = items[0]
            pdbCode = pdbCode.lower()
            result.append(pdbCode)
  result.sort()
  return result

