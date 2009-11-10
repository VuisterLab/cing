"""
Author: Jurgen F. Doreleijers, BMRB, June 2006

python -u $CINGROOT/python/cing/NRG/PDBEntryLists.py
"""
from cing import cingPythonDir
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import toCsv
from cing.Libs.NTutils import writeTextToFile
from cing.Scripts.iCingRobot import encodeForm
from cing.Scripts.iCingRobot import urlOpen
from cing.Libs.NTutils import NTcodeerror
import os
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


def getBmrbNmrGridEntries():
  result = []
  urlLocation = urlDB2 + "/entry.txt"
##4583	\N	108d	\N	\N
##4584	\N	149d	\N	\N
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

def writeEntryListToFile(fileName, entryList):
    "Returns True on failure"
    csvText = toCsv(entryList)
    if not csvText:
        NTerror("Failed to get CSV for %s" % entryList)
        return True
    writeTextToFile(fileName, csvText)

def getPdbEntries(onlyNmr = False, mustHaveExperimentalNmrData = False, onlySolidState = False):
    """Includes solution and solid state NMR if onlyNMR is chosen
    """
    dir_name = os.path.join(cingPythonDir, 'cing', 'NRG', 'data')
    if onlySolidState:
        inputFile = os.path.join(dir_name, 'RESTqueryPDB_NMR_solid.xml')
    elif onlyNmr:
        if mustHaveExperimentalNmrData:
            inputFile = os.path.join(dir_name, 'RESTqueryPDB_NMR_exp.xml')
        else:
            inputFile = os.path.join(dir_name, 'RESTqueryPDB_NMR.xml')
    else:
        if mustHaveExperimentalNmrData:
            NTcodeerror("Can't query for onlyNmr = True AND mustHaveExperimentalNmrData = True")
            return
        else:
            inputFile = os.path.join(dir_name, 'RESTqueryPDB.xml')

    rpcUrl = 'http://www.rcsb.org/pdb/rest/search'
    queryText = open(inputFile, 'r').read()
    NTdebug("queryText:\n%s" % queryText)
    NTdebug("querying...")
    req = urllib2.Request(url=rpcUrl, data=queryText)
    f = urllib2.urlopen(req)
    result = f.readlines()

    if not result:
        NTerror("Failed to save file to server")
        return
    NTdebug("Done successfully.")
    return result


def getPdbEntriesOca(onlyNmr = False):
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

