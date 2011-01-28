"""
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
Skipped: 18 obsolete PDB entries from score_many2one ['1lnp', '1bqv', '1bxj', '1ymj', '1ym6', '1ck9', '1cn9', '1cn8', '1ck8', '1ck5', '2new', '1jyp', '1n4t', '1n9d', '1uw2', '1xo9', '1xaq', '1yl2']
Skipped: 0 obsolete BMRB entries from score_many2one []
Accepted from old list 1690 matches
Skipped: 60 double entries from pdbIdAditList ['1joo', '1a5j', '1cqb', '7hsc', '1cl4', '1g03', '1f6u', '1e91', '1qqy', '1ps2', '1jbh', '1ayg', '1ji8', '1gm1', '1jru', '1uwo', '1bpb', '1qum', '1dxg', '1kka', '1bta', '2pld', '1hrh', '1lud', '1sxd', '1m8b', '1ma2', '5fx2', '1mzk', '1mv1', '1j0t', '1nwb', '1axh', '1k8j', '4ake', '1fgu', '1sap', '1b40', '1qvm', '1qxq', '1unc', '1i04', '1tn3', '1erq', '1adn', '2aiz', '1mmc', '2igz', '2jqr', '2jxy', '2k0k', '2k61', '2k8v', '351c', '2o32', '2jpo', '2k05', '2kcb', '2kh9', '2kmp']
Skipped: 187 obsolete PDB entries from adit ['1spz', '1alp', '1bqv', '1bxj', '1l2v', '1m4o', '1d5k', '1hzr', '1hzq', '1fio', '1j9d', '1a3k', '1lks', '1omp', '3mbp', '1qot', '1g6l', '1jjl', '1kdd', '1jsb', '1jyp', '1uea', '1k16', '1hg6', '1n4t', '1ezk', '1vie', '2cth', '2end', '1krk', '1kjo', '1pin', '2om4', '1ayf', '1laz', '1z3b', '1hur', '1lsk', '1qaw', '1gaj', '1d8c', '2hnp', '1iya', '1mh1', '1mms', '1b9c', '1f5w', '1h40', '1dki', '1mjf', '1oqj', '1n9d', '1irn', '1bq8', '1n3v', '1nzt', '1k04', '1xyf', '1nvh', '1o0z', '1oob', '1uav', '1aox', '1mu4', '1gyu', '1iwo', '1abj', '1ew4', '1ehk', '1igd', '1ird', '1oun', '1khc', '1ril', '1m2y', '1ass', '1fbt', '1e0r', '1q8e', '1r40', '1yzo', '2aic', '1p67', '1upo', '1h0x', '1x6k', '1b9k', '3paz', '1r83', '1uec', '1emv', '1rp6', '1h70', '1dpj', '1sv7', '2hnm', '1tgq', '1hco', '1uv0', '1sfc', '1vk7', '4azu', '1kil', '1jiw', '1dqe', '1utx', '1xo4', '1xo9', '1xaq', '1e96', '1uiu', '1p38', '1yl2', '2bar', '2f2y', '1ywz', '2a4y', '1zs1', '2b2m', '1zwq', '2a2h', '2b0n', '2p7w', '2auf', '2non', '2fjj', '2gpg', '2di1', '2g8p', '2h33', '2gx3', '2h7u', '1i45', '2hc6', '1plq', '2nyo', '2p60', '2dhw', '1wjh', '1iof', '2rls', '2rnc', '2rn6', '2rof', '2rpg', '2rq3', '2jmt', '1naq', '2kao', '2jp4', '2uz7', '2jrn', '2js8', '2jur', '2jus', '2qkz', '2jsu', '2jth', '2jut', '2juq', '2jux', '2jud', '2jvp', '2jw3', '2jy3', '2jy4', '2jzu', '2k0h', '2k0i', '2kp5', '2k82', '2k83', '2kab', '2kci', '2kpy', '2ki1', '2km7', '2kna', '2knw', '2koo', '2kql', '2ks8', '2ks7', '2ksx', '2kwm', '2kwa', '1jjq']
Skipped: 0 obsolete BMRB entries from adit []
Accepted from adit list   1648 for a total of 3338 matches
Accepted from manual list 1 for a total of 3339 matches
Accepted unique 3339 PDB and 2993 BMRB entries
Will write 3339 nrows and 2 ncols to newMany2OneTable.csv
"""
from cing.Libs.DBMS import Relation
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.PDBEntryLists import * #@UnusedWildImport
from cing.NRG.nrgCing import nrgCing
from glob import glob

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
    n = nrgCing()
    csvFileDir = os.path.join(cingRoot, matchBmrbPdbDataDir)
    NTmessage("Reading csv files in %s" % csvFileDir)
    os.chdir(csvFileDir)
    relationNames = glob("*.csv")
    relationNames = [ relationName[:-4] for relationName in relationNames]
    dbms = DBMS()
    dbms.readCsvRelationList(relationNames, csvFileDir)
    if 1: # Only do once a week.
        dbms2 = DBMS()
        pdbList = getPdbEntries(onlyNmr = True)
        pdbNmrTable = Relation('pdbNmr', dbms2, columnList=['pdb_id'])
        pdbIdColumn = pdbNmrTable.getColumnByIdx(0)
        pdbIdColumn += pdbList
        pdbNmrTable.writeCsvFile('pdbNmrTable.csv')
    if 0: # Only do once a week.
        bmrbIdList = getBmrbEntries()
        bmrbSttIdList = [ str(bmrbId) for bmrbId in bmrbIdList ]
        writeTextToFile('bmrb.csv', 'bmrb_id\n' + '\n'.join(bmrbSttIdList))
    if False:
        newMany2OneTable =dbms.tables['newMany2OneTable']

    newMany2OneTable = Relation('newMany2OneTable', dbms, columnList=['pdb_id', 'bmrb_id'])
    bmrbIdNewMany2OneList = newMany2OneTable.getColumn('bmrb_id')
    pdbIdNewMany2OneList = newMany2OneTable.getColumn('pdb_id')

    tableScore_many2one = dbms.tables['score_many2one']
    bmrbIdOldMany2OneList = tableScore_many2one.getColumn('bmrb_id')
    pdbIdOldMany2OneList = tableScore_many2one.getColumn('pdb_id')

    # Not that this table is a one 2 many unlike what I need.
    tableAdit = dbms.tables['adit_nmr_matched_pdb_bmrb_entry_ids']
    bmrbIdAditList = tableAdit.getColumn('bmrb_id')
    pdbIdAditList = tableAdit.getColumn('pdb_id')
    pdbIdAditNmrHash = list2dict( pdbIdAditList )

    # New table from Dmitri
    tableAdit2 = dbms.tables['BMRB_PDB_match']
    bmrbIdAdit2List = tableAdit2.getColumn('BMRB_ID')
    pdbIdAdit2List = tableAdit2.getColumn('PDB_ID')
    pdbIdAdit2NmrHash = list2dict( pdbIdAdit2List )


    tableManual = dbms.tables['manualMatches']
    bmrbIdManualList = tableManual.getColumn('bmrb_id')
    pdbIdManualList = tableManual.getColumn('pdb_id')
    pdbIdManualNmrHash = list2dict( pdbIdManualList )

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
    NTmessage("Skipped: %s obsolete PDB entries from score_many2one %s" % (len(pdbIdListAbsent),str(pdbIdListAbsent)))
    NTmessage("Skipped: %s obsolete BMRB entries from score_many2one %s" % (len(bmrbIdListAbsent),str(bmrbIdListAbsent)))
    NTmessage("Accepted from old list %s matches" % l1)



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
            NTerror("Failed to find %s in PDB; update the manual list." % pdb_id)
            continue
        if not bmrbIdHash.has_key(bmrb_id):
            NTerror("Failed to find %s in BMRB; update the manual list." % bmrb_id)
            continue
        if pdb_id in pdbIdNewMany2OneList:
            NTdebug("Already found %s in PDB; consider updating the manual list." % pdb_id)
            continue
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

    NTmessage("Skipped: %s double entries from pdbIdAditList %s" % (len(pdbIdListDouble),str(pdbIdListDouble)))
    for aditIdx in range(nadit):
        pdbIdLoLObsolete[aditIdx].sort()
        bmrbIdLoLObsolete[aditIdx].sort()
        NTmessage("Skipped: %s obsolete  PDB entries from adit%s %s" % (len( pdbIdLoLObsolete[aditIdx]), aditIdx,  str(pdbIdLoLObsolete[aditIdx])))
        NTmessage("Skipped: %s obsolete BMRB entries from adit%s %s" % (len(bmrbIdLoLObsolete[aditIdx]), aditIdx, str(bmrbIdLoLObsolete[aditIdx])))
        NTmessage("Accepted from adit%s %s for a total of %s matches" %(aditIdx, l2[aditIdx], ltotal1[aditIdx]))
    NTmessage("Accepted from manual list %s for a total of %s matches" %( l3, ltotal2))
    NTmessage("Accepted unique %d PDB and %d BMRB entries" %( uniquePdbCount, uniqueBmrbCount))

    newMany2OneTable.writeCsvFile()

