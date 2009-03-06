"""
Author: Jurgen F. Doreleijers, BMRB, June 2006

python -u $CINGROOT/python/cing/NRG/PDBEntryLists.py
"""
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import toCsv
from cing.Libs.NTutils import writeTextToFile
import cing
import urllib

urlDB2 = "http://restraintsgrid.bmrb.wisc.edu/servlet_data/viavia/mr_mysql_backup/" # Gets Denial of Service sometimes.
#ocaUrl = "http://oca.ebi.ac.uk/oca-bin/ocaids"
ocaUrl = "http://www.ebi.ac.uk/msd-srv/oca/oca-bin/ocaids" 

testingLocally = True
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
    

def getPdbEntries(onlyNmr = False):
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

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug    
#    entry_list_pdb = getPdbEntries() 
#    NTdebug( "entries pdb: %d %40s" % (len(entry_list_pdb), entry_list_pdb ))
#    entry_list_pdb_nmr = getPdbEntries(onlyNmr=True)
#    NTdebug( "entries nmr: %d %s" % (len(entry_list_pdb_nmr), entry_list_pdb_nmr ))
    entry_list_nrg_docr = getBmrbNmrGridEntriesDOCRfREDDone()
    NTdebug("entries nrg docr: %d %s" % (len(entry_list_nrg_docr), entry_list_nrg_docr))
