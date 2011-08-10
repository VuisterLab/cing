#!/usr/bin/env python

"""
Execute as weekly cron job like:

$CINGROOT/python/cing/NRG/matchBmrbPdb.py

-0- The result is to be a many-to-one table. A BMRB entry can be matched to multiple PDB entries.
-1- For now I limit the BMRB entries to just those that have 2.1 files available.
-2- If there are multiple BMRB entries in ADIT-NMR for the same PDB entry (e.g. 1joo) I rather not match any.
-3- If a PDB entry was already present in my old match it is not used for any match in ADIT-NMR.

Output:
DEBUG: Read     2902 rows  2 cols to adit_nmr_matched_pdb_bmrb_entry_ids
DEBUG: Read     6353 rows  1 cols to bmrb
DEBUG: Read        1 rows  2 cols to manualMatches
DEBUG: Read     3339 rows  2 cols to newMany2OneTable
DEBUG: Read     8462 rows  1 cols to pdbNmrTable
DEBUG: Read     1708 rows  3 cols to score_many2one
Skipped: 18 obsolete PDB entries from score_many2one ['1lnp', '1bqv', '1bxj', '1ymj', '1ym6', '1ck9', '1cn9', '1cn8', '1ck8', '1ck5', ...
Skipped: 0 obsolete BMRB entries from score_many2one []
Accepted from old list 1690 matches
Skipped: 60 double entries from pdbIdAditList ['1joo', '1a5j', '1cqb', '7hsc', '1cl4', '1g03', '1f6u', '1e91', '1qqy', '1ps2', '...
Skipped: 187 obsolete PDB entries from adit ['1spz', '1alp', '1bqv', '1bxj', '1l2v', '1m4o', '1d5k', '1hzr', '1hzq', ...
Skipped: 0 obsolete BMRB entries from adit []
Accepted from adit list   1648 for a total of 3338 matches
Accepted from manual list 1 for a total of 3339 matches
Accepted unique 3339 PDB and 2993 BMRB entries
Will write 3339 nrows and 2 ncols to newMany2OneTable.csv
"""
from cing import cingRoot
from cing.Libs.DBMS import Relation
from cing.Libs.DBMS import addColumnHeaderRowToCsvFile
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import rmdir
from cing.NRG.PDBEntryLists import * #@UnusedWildImport
from cing.NRG.settings import * #@UnusedWildImport
from glob import glob
from shutil import copytree

class MatchBmrbPdb(Lister):
    def __init__(self):
        Lister.__init__(self)
        self.adit_fn = 'adit_nmr_matched_pdb_bmrb_entry_ids.csv'
        self.adit_url = 'ftp://ftp.bmrb.wisc.edu/pub/bmrb/nmr_pdb_integrated_data/' + self.adit_fn
        self.restartFromScratch = 1

    def prepare(self):
        if self.restartFromScratch:
            rmdir(matchBmrbPdbDir)
        if not os.path.exists(matchBmrbPdbDir):
            csvFileDir = os.path.join(cingRoot, matchBmrbPdbDataDir)
            nTmessage("Recreating data dir %s from SVN %s" % (matchBmrbPdbDir, csvFileDir))
#            mkdirs( matchBmrbPdbDir )
            copytree(csvFileDir, matchBmrbPdbDir)
        else:
            nTmessage("Reusing existing data dir " + matchBmrbPdbDir)
        os.chdir(matchBmrbPdbDir)
        if 1: # DEFAULT: 1
            if os.path.exists(self.adit_fn):
                os.unlink(self.adit_fn) # prevent buildup of endless copies.
            wgetProgram = ExecuteProgram('wget --no-verbose %s' % self.adit_url, redirectOutputToFile ='getAdit.log' )
            exitCode = wgetProgram()
            if exitCode:
                nTerror("Failed to download file %s" % self.adit_url)
                return True
            if not os.path.exists(self.adit_fn):
                nTerror("Failed to find downloaded file %s" % self.adit_url)
                return True
            columnOrder = 'bmrb_id pdb_id'.split()
            if addColumnHeaderRowToCsvFile(self.adit_fn, columnOrder):
                nTerror("Failed to add header row to " + self.adit_fn)
                return True
        if 1: # DEFAULT: 1
            bmrbFileList = findFiles("bmr*_21.str", bmrbDir)
            bmrbIdList = []
            for bmrbFile in bmrbFileList:
                _directory, basename, _extension = nTpath(bmrbFile)
                bmrbId = int(basename[3:-3]) # bmr970_21 -> 970
                bmrbIdList.append(bmrbId)
            bmrbIdList.sort()
            bmrbId2List = getBmrbEntries()
            bmrbIdNTList = NTlist(*bmrbIdList)
            bmrbId2NTList = NTlist(*bmrbId2List)
            bmrbIdNTmissingList = bmrbIdNTList.difference(bmrbId2NTList)
            if bmrbIdNTmissingList:
                nTmessage("Found %d entries on file but not in DB: %s" % (len(bmrbIdNTmissingList), str(bmrbIdNTmissingList)))
            bmrbId2NTmissingList = bmrbId2NTList.difference(bmrbIdNTList)
            if bmrbId2NTmissingList:
                nTmessage("Found %d entries in DB but not on file: %s" % (len(bmrbId2NTmissingList), str(bmrbId2NTmissingList)))
            if len( bmrbIdNTmissingList + bmrbId2NTmissingList ) > 40: # was 18 + 3=21 on April 11, 2011.
                nTwarning("More than one hundred inconsistencies between BMRB DB and on file.")
            bmrbIdStrList = ['bmrb_id']  + [ str(x) for x in bmrbIdList] # add header for CSV reader.
            fileName = os.path.join( matchBmrbPdbDir, 'bmrb.csv')
            txt = '\n'.join(bmrbIdStrList)
            if writeTextToFile(fileName, txt):
                return True
        if 1: # DEFAULT: 1
            dbms2 = DBMS()
            pdbList = getPdbEntries(onlyNmr = True)
            pdbNmrTable = Relation('pdbNmr', dbms2, columnList=['pdb_id'])
            pdbIdColumn = pdbNmrTable.getColumnByIdx(0)
            pdbIdColumn += pdbList
            pdbNmrTable.writeCsvFile('pdbNmrTable.csv')
#        if False:
#            newMany2OneTable =dbms.tables['newMany2OneTable'] #@UnusedVariable

    def run(self):
        if self.prepare():
            nTerrorT("Failed to prepare")
            return True
#        return

        relationNames = glob("*.csv")
        relationNames = [ relationName[:-4] for relationName in relationNames]
        dbms = DBMS()
        dbms.readCsvRelationList(relationNames, '.')

        # This will overwrite the just read newMany2OneTable
        newMany2OneTable = Relation('newMany2OneTable', dbms, columnList=['pdb_id', 'bmrb_id'])
        bmrbIdNewMany2OneList = newMany2OneTable.getColumn('bmrb_id')
        pdbIdNewMany2OneList = newMany2OneTable.getColumn('pdb_id')

        tableScore_many2one = dbms.tables['score_many2one']
        bmrbIdOldMany2OneList = tableScore_many2one.getColumn('bmrb_id')
        pdbIdOldMany2OneList = tableScore_many2one.getColumn('pdb_id')

        # NB that this table is a one 2 many unlike what I need.
        tableAdit = dbms.tables['adit_nmr_matched_pdb_bmrb_entry_ids']
        bmrbIdAditList = tableAdit.getColumn('bmrb_id')
        pdbIdAditList = tableAdit.getColumn('pdb_id')
        pdbIdAditList = [x.lower() for x in pdbIdAditList]
        pdbIdAditNmrHash = list2dict( pdbIdAditList )

        # New table from Dmitri with 655 matches.
        # With corrections for invalids:
#15591,2k0b,1,SOLUTION NMR,        15591 should be matched to 2jy7
        tableAdit2 = dbms.tables['BMRB_PDB_match']
        bmrbIdAdit2List = tableAdit2.getColumn('BMRB_ID')
        pdbIdAdit2List = tableAdit2.getColumn('PDB_ID')
        pdbIdAdit2NmrHash = list2dict( pdbIdAdit2List )


        # Manual corrections to Dmitri's table etc.
        tableManual = dbms.tables['manualMatches'] # Maintain this list in SVN control.
        bmrbIdManualList = tableManual.getColumn('bmrb_id')
        pdbIdManualList = tableManual.getColumn('pdb_id')
        pdbIdManualNmrHash = list2dict( pdbIdManualList ) #@UnusedVariable

        tablePdbNmrTable = dbms.tables['pdbNmrTable']
        pdbIdPdbNmrList = tablePdbNmrTable.getColumn('pdb_id')
        pdbIdPdbNmrHash = list2dict( pdbIdPdbNmrList )

        bmrbTable = dbms.tables['bmrb']
        bmrbIdList = bmrbTable.getColumn('bmrb_id')
        bmrbIdHash = list2dict( bmrbIdList )

        pdbIdListAbsent =[]
        bmrbIdListAbsent =[]
        for idx, pdb_id in enumerate(pdbIdOldMany2OneList):
            bmrb_id = bmrbIdOldMany2OneList[idx]
            if not pdbIdPdbNmrHash.has_key(pdb_id):
                pdbIdListAbsent.append(pdb_id)
                continue
            if not bmrbIdHash.has_key(bmrb_id):
                bmrbIdListAbsent.append(bmrb_id)
                continue
            bmrbIdNewMany2OneList.append(bmrb_id)
            pdbIdNewMany2OneList.append(pdb_id)

        l1 = len(pdbIdNewMany2OneList)
        nTmessage("Skipped: %s obsolete PDB entries from score_many2one %s" % (len(pdbIdListAbsent),str(pdbIdListAbsent)))
        nTmessage("Skipped: %s obsolete BMRB entries from score_many2one %s" % (len(bmrbIdListAbsent),str(bmrbIdListAbsent)))
        nTmessage("Accepted from old list %s matches" % l1)



        # Do both adit lists
        pdbIdLoLDouble = [[],[]]
        pdbIdLoLObsolete = [[],[]]
        bmrbIdLoLObsolete =[[],[]]
        ltotal1 = [ -1, -1]
        l2 = [ -1, -1]
        nadit = 2
        for aditIdx, pdbIdAditXList in enumerate( [pdbIdAditList, pdbIdAdit2List] ):
            bmrbIdAditXList = (bmrbIdAditList, bmrbIdAdit2List )[aditIdx]
            pdbIdAditXNmrHash = (pdbIdAditNmrHash, pdbIdAdit2NmrHash )[aditIdx]
            pdbIdListDouble = pdbIdLoLDouble[aditIdx]
            pdbIdListObsolete = pdbIdLoLObsolete[aditIdx]
            bmrbIdListObsolete = bmrbIdLoLObsolete[aditIdx]
            for idx, pdb_id in enumerate(pdbIdAditXList):
                bmrb_id = bmrbIdAditXList[idx]
                if pdbIdAditXNmrHash[pdb_id] > 1:
                    if pdb_id not in pdbIdListDouble:
                        pdbIdListDouble.append(pdb_id)
                    continue
                if not pdbIdPdbNmrHash.has_key(pdb_id):
                    pdbIdListObsolete.append(pdb_id)
                    continue
                if not bmrbIdHash.has_key(bmrb_id):
                    bmrbIdListObsolete.append(bmrb_id)
                    continue
                if pdb_id in pdbIdNewMany2OneList:
                    continue
            #    if bmrb_id in bmrbIdNewMany2OneList: allow this.
            #        continue
                bmrbIdNewMany2OneList.append(bmrb_id)
                pdbIdNewMany2OneList.append(pdb_id)
            ltotal1[aditIdx] = len(pdbIdNewMany2OneList)
            if aditIdx == 0:
                l2[aditIdx] = ltotal1[aditIdx] - l1
            else:
                l2[aditIdx] = ltotal1[aditIdx] - ltotal1[aditIdx-1]


        for idx, pdb_id in enumerate(pdbIdManualList):
            bmrb_id = bmrbIdManualList[idx]
            if not pdbIdPdbNmrHash.has_key(pdb_id):
                nTerror("Failed to find %s in PDB; update the manual list." % pdb_id)
                continue
            if not bmrbIdHash.has_key(bmrb_id):
                nTerror("Failed to find %s in BMRB; update the manual list." % bmrb_id)
                continue
            if pdb_id in pdbIdNewMany2OneList:
                idx = pdbIdNewMany2OneList.index(pdb_id)
                bmrb_id_current = bmrbIdNewMany2OneList[idx]
                if bmrb_id_current == bmrb_id:
                    nTmessage("Already found %s in PDB with BMRB %s in manual and current list; consider updating the manual list." % (
                        pdb_id, bmrb_id))
                    continue
                nTmessage("Using manual mapping of %s in PDB with BMRB %s in manual list instead of BMRB %s in current list." % (
                        pdb_id, bmrb_id, bmrb_id_current))
                nTmessage("First removing match at idx %s in current list." % idx)
                del bmrbIdNewMany2OneList[idx]
                del pdbIdNewMany2OneList[idx]
        #    if bmrb_id in bmrbIdNewMany2OneList: allow this.
        #        continue
            bmrbIdNewMany2OneList.append(bmrb_id)
            pdbIdNewMany2OneList.append(pdb_id)

        ltotal2 = len(pdbIdNewMany2OneList)
        l3 = ltotal2 - ltotal1[nadit-1]

        pdbIdNewHash = list2dict( pdbIdNewMany2OneList )
        bmrbIdNewHash = list2dict( bmrbIdNewMany2OneList )
        uniquePdbCount = len(pdbIdNewHash)
        uniqueBmrbCount = len(bmrbIdNewHash)

        nTmessage("Skipped: %s double entries from pdbIdAditList %s" % (len(pdbIdListDouble),str(pdbIdListDouble)))
        for aditIdx in range(nadit):
            pdbIdLoLObsolete[aditIdx].sort()
            bmrbIdLoLObsolete[aditIdx].sort()
            nTmessage("Skipped: %s obsolete  PDB entries from adit%s %s" % (len( pdbIdLoLObsolete[aditIdx]), aditIdx,  
                                                                            str(pdbIdLoLObsolete[aditIdx])))
            nTmessage("Skipped: %s obsolete BMRB entries from adit%s %s" % (len(bmrbIdLoLObsolete[aditIdx]), aditIdx, 
                                                                            str(bmrbIdLoLObsolete[aditIdx])))
            nTmessage("Accepted from adit%s %s for a total of %s matches" %(aditIdx, l2[aditIdx], ltotal1[aditIdx]))
        nTmessage("Accepted from manual list %s for a total of %s matches" %( l3, ltotal2))
        nTmessage("Accepted unique %d PDB and %d BMRB entries" %( uniquePdbCount, uniqueBmrbCount))

        pdbIdNewMany2OneNTList = NTlist(*pdbIdNewMany2OneList)
        pdbIdDuplicateList = pdbIdNewMany2OneNTList.removeDuplicates()
        if pdbIdDuplicateList:
            nTerror("Got %s duplicate PDB entries in result: %s" % (len(pdbIdDuplicateList), str(pdbIdDuplicateList) ))
            return True

        bmrbIdNewMany2OneNTList = NTlist(*bmrbIdNewMany2OneList)
        bmrbIdDuplicateList = bmrbIdNewMany2OneNTList.removeDuplicates()
        bmrbIdDuplicateList = bmrbIdDuplicateList.removeDuplicates()
        if bmrbIdDuplicateList:
            nTmessage("Using %s BMRB entries that match two or more PDB entries." % len(bmrbIdDuplicateList) )

        if newMany2OneTable.sortRelationByColumnIdx([0,1]):
            nTerror("Failed to sort table: %s")
            return True
        newMany2OneTable.writeCsvFile()


if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
    m = MatchBmrbPdb()
    if m.run():
        nTerrorT("Failed to match BMRB to PDB")
        sys.exit(1)