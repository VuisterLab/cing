# python -u $CINGROOT/python/cing/NRG/nrgCingRdb.py
# reload cing.NRG.nrgCingRdb
# from cing.NRG.nrgCingRdb import *
"""
Create plots like the GreenVersusRed scatter by entry.
"""

from cing import cingDirTmp
from cing.Libs.NTplot import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.NRG.settings import * #@UnusedWildImport
from cing.PluginCode.matplib import NTplot
from cing.PluginCode.matplib import NTplotSet
from cing.PluginCode.required.reqDssp import * #@UnusedWildImport
from cing.PluginCode.required.reqProcheck import * #@UnusedWildImport
from cing.PluginCode.required.reqQueeny import * #@UnusedWildImport
from cing.PluginCode.required.reqWattos import * #@UnusedWildImport
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.PluginCode.sqlAlchemy import cgenericSql
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from cing.PluginCode.sqlAlchemy import printResult
from matplotlib import is_interactive
from pylab import * #@UnusedWildImport # imports plt too now.
from scipy import * #@UnusedWildImport
from scipy import optimize
from sqlalchemy.schema import Table #@UnusedImport
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import select #@Reimport @UnusedImport
import numpy

PLOT_REGRESSION_LINE = 'plotRegressionLine'
REGRESSION_LINEAR = 'linear'
DIVIDE_BY_RESIDUE_COUNT = 'divideByResiduecount'
ONLY_PROTEIN = 'onlyProtein'
'Only protein means that no other polymer types than xxx may be present; ligands are fine.'
ONLY_SELECTION = 'onlySelection'
DO_TRENDING = 'doTrending'
ENTRY_SET_ID = 'entrySetId'
'Used to filter for different sets of selected entries.'
ONLY_NON_ZERO = 'onlyNonZero'
'Filter out entities that have a zero float/int value'
PDBJ_ENTRY_ID_STR = 'pdbid'
DEPOSITION_DATE_STR = 'deposition_date'
EMPTY_PROGID = ""
SYMBOL_BY_ENTRY = 'symbolByEntry'
IS_TRUE = 'isTrue'
IS_FALSE = 'isFalse'

if False:
    from matplotlib import use #@UnusedImport
    use('TkAgg') # Instead of agg
    interactive(True)


class nrgCingRdb():
    def __init__(self,host='localhost', user=PDBJ_DB_USER_NAME, db=PDBJ_DB_NAME, schema=NRG_DB_SCHEMA):
        self.schema = schema
        if True: # block the NRG-CING stuff away from other schema
            self.csql = csqlAlchemy(host=host, user=user, db=db, schema=schema)
            self.csql.connect()
            self.execute = self.csql.conn.execute
            if 0: # DEFAULT True but disable for quicker testing.
                self.createDepTables()
            self.csql.autoload()
            #csql.close()

            self.session = self.csql.session
            self.query = self.session.query
            self.engine = self.csql.engine
            self.centry = self.csql.cingentry
            self.cchain = self.csql.cingchain
            self.cresidue = self.csql.cingresidue
            self.catom = self.csql.cingatom

            self.csql.loadTable('cingsummary')
            self.csql.loadTable('entry_list_selection')

            self.csummary = self.csql.cingsummary
            self.centry_list_selection = self.csql.entry_list_selection

            self.cs = self.csummary.alias()
            self.e1 = self.centry.alias()
            self.c1 = self.cchain.alias()
            self.r1 = self.cresidue.alias()
            self.r2 = self.cresidue.alias()
            self.a1 = self.catom.alias()

            self.s1 = self.centry_list_selection.alias()
            self.perEntryRog = NTdict()

        if True:
            self.jsql = cgenericSql(host=host, user=PDBJ_DB_USER_NAME, db=PDBJ_DB_NAME, schema=PDBJ_DB_SCHEMA)
            self.jsql.connect()
            self.jsql.autoload()

            self.jsql.loadTable('brief_summary')

            self.jexecute = self.jsql.conn.execute
            self.jsession = self.jsql.session
            self.jquery = self.jsession.query
            self.engine = self.jsql.engine
            self.brief_summary = self.jsql.brief_summary
            self.bs = self.brief_summary.alias()

    def showCounts(self):
        m = self
        if False:
            tableList = [m.centry, m.cchain, m.cresidue, m.catom, m.brief_summary]
#            countList = [m.query(table).count() for table in tableList]

            countList = []
            for table in tableList:
                countList.append( m.query(table).count())

            countStrTuple = tuple([locale.format('%.0f', value, True) for value in countList])
            NTmessage(NRG_DB_SCHEMA + " schema contains: %s entries %s chains %s residues %s atoms\npdbj schema contains %s entries." % countStrTuple)

        if True:
            tableList = [m.csummary, m.centry_list_selection]
            countList = [m.query(table).count() for table in tableList]
            countStrTuple = tuple([locale.format('%.0f', value, True) for value in countList])
            NTmessage("There are %s entries in summary and %s entries in selection." % countStrTuple)


    def getPdbIdList(self, fromNrg=True):
        "Return None on error."
        table = self.centry
        columnName = PDB_ID_STR

        if not fromNrg:
            table = self.bs.c
            columnName =PDBJ_ENTRY_ID_STR

        try:
            s = select([table.c[columnName]])
    #        NTdebug("SQL: %s" % s)
            pdbIdTable = self.execute(s).fetchall()
        except:
            NTtracebackError()
            return

        if pdbIdTable == None:
            NTerror("Failed retrieval from NRG-CING rdb from table %s and column %s" % (table, columnName))
            return None

        if not pdbIdTable:
            NTwarning("Failed to retrieve any entries from NRG-CING rdb from table %s and column %s" % (table, columnName))
            return []

        pdbIdDateResultDict = NTdict() # hash by entry id
        pdbIdDateResultDict.appendFromTable(pdbIdTable, 0, 0)
        pdbIdList = pdbIdDateResultDict.keys()
        pdbIdList.sort()
        return pdbIdList
    # end def

    def createDepTables(self):
        NTmessage("creating temporary tables")


        stmt1 = 'drop table if exists %s.cingsummary cascade' % self.schema
        # The full molecular weight > 3.5 kDa,; not just the polymers
        stmt2 = """
CREATE table %s.cingsummary AS
SELECT s.pdbid AS pdb_id, SUM(p2.val * p3.val) AS weight
FROM pdbj.brief_summary s
JOIN pdbj."E://entity" e ON e.docid = s.docid
JOIN "//entity/pdbx_number_of_molecules" p2    ON p2.docid = e.docid AND p2.pos BETWEEN e.pstart AND e.pend
JOIN "//entity/formula_weight" p3              ON p3.docid = e.docid AND p3.pos BETWEEN e.pstart AND e.pend
GROUP BY s.pdbid;
""" % self.schema
        stmt3 = 'drop table if exists %s.entry_list_selection cascade;' % self.schema
        # The full molecular weight; not just the polymers
        stmt4 = """
CREATE table %s.entry_list_selection AS
SELECT e.pdb_id
FROM %s.CINGENTRY E,  pdbj.brief_summary s, %s.cingsummary cingsummary
WHERE e.pdb_id = S.pdbid
AND e.pdb_id = cingsummary.pdb_id
AND E.MODEL_COUNT > 9
and cingsummary.weight > 3500.0 -- about 30 residues
AND '{2}' <@ S.chain_type; -- contains at least one protein chain.
""" % tuple( [self.schema] *3 )
        for stmt in [ stmt1, stmt2, stmt3, stmt4]:
#            NTdebug("Executing: %s" % stmt)
            result = self.execute(stmt)
            printResult(result)


    def getDbTable( self, level ):
        m = self
        table = m.e1
        if level == RES_LEVEL:
            table = m.r1
        elif level == ATOM_LEVEL:
            table = m.a1
        return table

    def level2level_id(self, level):
        if level == ATOM_LEVEL:
            return ATOM_ID_STR
        if level == RES_LEVEL:
            return RESIDUE_ID_STR
        if level == CHAIN_LEVEL:
            return CHAIN_ID_STR
        if level == PROJECT_LEVEL:
            return ENTRY_ID_STR
        NTexit("Bad level: %s" % level)

    def getLevelNumber(self, level):
        if level == ATOM_LEVEL:
            return 0
        if level == RES_LEVEL:
            return 1
        if level == CHAIN_LEVEL:
            return 2
        if level == PROJECT_LEVEL:
            return 3
        NTexit("In getLevelNumber bad level: %s" % level)


    def getTitleFromStats(self, av, sd, n, minValue, maxValue):
        return "av/sd/n %.3f %.3f %d min/max %.3f %.3f" % (av, sd, n, minValue, maxValue )

    def getTitleFromDict(self, plotDict):
        titleStr = ''
        if getDeepByKeysOrAttributes( plotDict, DIVIDE_BY_RESIDUE_COUNT):
            titleStr += ' perRes'
#            if getDeepByKeysOrAttributes( plotDict, ONLY_PROTEIN): # TODO: here
#                titleStr += ' onlyAA'
        if getDeepByKeysOrAttributes( plotDict, ONLY_SELECTION):
            titleStr += ' onlySel'
        if getDeepByKeysOrAttributes( plotDict, SYMBOL_BY_ENTRY):
            titleStr += ' byEntry'
        if getDeepByKeysOrAttributes( plotDict, ONLY_NON_ZERO):
            titleStr += ' only!zero'
        filterForTruth = getDeepByKeysOrAttributes( plotDict, IS_TRUE) or getDeepByKeysOrAttributes( plotDict, IS_FALSE)
        if filterForTruth:
            trueAttribute = getDeepByKeysOrAttributes( plotDict, IS_TRUE)
            if trueAttribute != None:
                titleStr += ' T:' + trueAttribute
            falseAttribute = getDeepByKeysOrAttributes( plotDict, IS_FALSE)
            if falseAttribute != None:
                titleStr += ' F:' + falseAttribute

        if getDeepByKeysOrAttributes( plotDict, USE_MIN_VALUE_STR) and \
           getDeepByKeysOrAttributes( plotDict, USE_MAX_VALUE_STR):
            xmin = getDeepByKeysOrAttributes( plotDict, USE_MIN_VALUE_STR)
            xmax = getDeepByKeysOrAttributes( plotDict, USE_MAX_VALUE_STR)
            titleStr += ' [%.3f,%.3f]' % (xmin,xmax)
        return titleStr

    def getFloatLoLFromDb(self, level, progId, chk_id, **plotDict):
        '''Returns a LoL with the
        first element being a tuple with elements (entry_id, chain_id, res_num, atom_num) and
        second element being a float
        third optional element being the deposition date needed for trending.
        '''
        m = self
        columnName = getDbColumnName( level, progId, chk_id )
    #    NTdebug("Found column: %s for level, progId, chk_id: %s" % (columnName,str([level, progId, chk_id])))
        table = self.getDbTable(level)
        level_number = self.getLevelNumber(level)

        doDivideByResidueCount = getDeepByKeysOrAttributes( plotDict, DIVIDE_BY_RESIDUE_COUNT)
        _filterForProtein = getDeepByKeysOrAttributes( plotDict, ONLY_PROTEIN)
        filterForSelection = getDeepByKeysOrAttributes( plotDict, ONLY_SELECTION)
        filterZero = getDeepByKeysOrAttributes( plotDict, ONLY_NON_ZERO)
        doTrending = getDeepByKeysOrAttributes( plotDict, DO_TRENDING)
        filterForTruth = getDeepByKeysOrAttributes( plotDict, IS_TRUE) or getDeepByKeysOrAttributes( plotDict, IS_FALSE)

        if doTrending: # optimalization is to ignore the 'pure' X-ray,
            # First get the entry entry_name info
            try:
                s = select([m.bs.c[PDBJ_ENTRY_ID_STR], m.bs.c[DEPOSITION_DATE_STR]])
        #        NTdebug("SQL: %s" % s)
                pdbIdDateResultTable = m.execute(s).fetchall()
            except:
                NTtracebackError()
                return
            pdbIdDateResultDict = NTdict() # hash by entry filterId
            pdbIdDateResultDict.appendFromTable(pdbIdDateResultTable, 0, 1)
        # end trending.

        if filterForTruth:
            truth = True
            columnNameForTruth = getDeepByKeysOrAttributes( plotDict, IS_TRUE)
            if columnNameForTruth == None:
                columnNameForTruth = getDeepByKeysOrAttributes( plotDict, IS_FALSE)
                truth = False
            try:
                level_id = self.level2level_id(level)
                s = select([table.c[level_id],]).where(table.c[columnNameForTruth]==truth)
#                NTdebug("SQL:\n%s\n" % s)
                truthResultTable = m.execute(s).fetchall()
            except:
                NTtracebackError()
                return
            truthResultDict = NTdict() # hash by entry filterId
            truthResultDict.appendFromTable(truthResultTable)


        # First get the entry name info
        try:
            s = select([m.e1.c[ENTRY_ID_STR], m.e1.c[NAME_STR]])
    #        NTdebug("SQL: %s" % s)
            entryNameResultTable = m.execute(s).fetchall()
        except:
            NTtracebackError()
            return
        entryIdEntryNameResultDict = NTdict() # hash by entry filterId
        entryIdEntryNameResultDict.appendFromTable(entryNameResultTable, 0, 1)
        entryNameEntryIdResultDict = NTdict() # hash by entry name
        entryNameEntryIdResultDict.appendFromTable(entryNameResultTable, 1, 0)


        # Get actual value of interest together with attributes to filter on.
        try:
            # Filter and limit after select for speed in most cases.
            # I wonder if sqlalchemy could relay the burden of filtering out the None's to the db.

            # Stupid trick but it will do.
            if level == ATOM_LEVEL:
                s = select([table.c[ENTRY_ID_STR], table.c[CHAIN_ID_STR], table.c[RESIDUE_ID_STR], table.c[ATOM_ID_STR], table.c[columnName]])
            elif level == RES_LEVEL:
                s = select([table.c[ENTRY_ID_STR], table.c[CHAIN_ID_STR], table.c[RESIDUE_ID_STR], table.c[columnName]])
            elif level == CHAIN_LEVEL:
                s = select([table.c[ENTRY_ID_STR], table.c[CHAIN_ID_STR], table.c[columnName]])
            elif level == MOLECULE_LEVEL:
                s = select([table.c[ENTRY_ID_STR], table.c[columnName]])
            s = s.where(table.c[columnName]!=None)
            if filterZero:
                s = s.where(table.c[columnName]!=0.0)
#                s = s.where(table.c[columnName]!=0) # don't use this because truncation will be tried.
#            NTdebug("SQL:\n%s\n" % s)
            checkResultTable = m.execute(s).fetchall()
        except:
            NTtracebackError()
            return

        if doDivideByResidueCount:
            try:
                # Filter and limit after select for speed in most cases.
                s = select([table.c[ENTRY_ID_STR], table.c[RES_COUNT_STR]])
    #            NTdebug("SQL: %s" % s)
                resCountTable = m.execute(s).fetchall()
            except:
                NTtracebackError()
                return
    #        NTdebug("Found table: %s" % (resCountTable))
            resCountDict = NTdict()
            resCountDict.appendFromTable(resCountTable, 0, 1)
            if len(resCountTable) != len(resCountDict):
                NTcodeerror("len(resCountTable) != len(resCountDict): %d %d" % (len(resCountTable), len(resCountDict)))
                return

        if filterForSelection:
            try:
                # Filter and limit after select for speed in most cases.
                s = select([m.centry_list_selection.c[PDB_ID_STR]])
    #            NTdebug("SQL: %s" % s)
                pdbIdSelectionTable = m.execute(s).fetchall()
            except:
                NTtracebackError()
                return
            pdbidSelectionDict = NTdict()
            pdbidSelectionDict.appendFromTable(pdbIdSelectionTable, 0, 0)
            NTdebug("Found selection with count: %s" % len(pdbidSelectionDict))

    #    checkResultTable = checkResultTable[:10]
    #    NTdebug("checkResultTable: %s" % str(checkResultTable))
        result = []
        for i,element in enumerate(checkResultTable):
#            entry_id, chain_id, res_id, atom_id, v = element

            chain_id, res_id, atom_id = (-1,-1,-1)
            entry_id = element[0]
            v = element[4-level_number]
            v = float(v)
            if level_number < 3:
                chain_id = element[1]
                if level_number < 2:
                    res_id = element[2]
                    if level_number < 1:
                        atom_id = element[3]

            entry_name = entryIdEntryNameResultDict[entry_id]
            if v == None:
                NTdebug("Unexpected None found at entry_name %s" % entry_name)
                continue
            if isNaN(v): # this -DOES- happen; e.g. PROJECT.Whatif.BNDCHK
#                NTdebug("Unexpected nan instead of None found at entry_name %s" % entry_name)
                continue
            if filterForTruth:
                idList = [atom_id, res_id, chain_id, entry_id] # shorter code longer execution time...
                filterId = idList[level_number]
                if not truthResultDict.has_key(filterId):
                    continue

            if doDivideByResidueCount:
                resCount = resCountDict[entry_id]
                if isNaN(resCount) or resCount == None or resCount == 0:
                    NTerror("Found null for resCount for entry_name %s" % entry_name)
                    continue
                v /= resCount
            if filterForSelection:
                if not pdbidSelectionDict.has_key(entry_name):
                    continue
            if filterZero:
                # Works when v is integer or float
                if v == 0.0:
                    NTdebug("Unexpected zero value for %s %s" % (entry_id, entry_name))
                    continue
#            resultIdTuple = ( entry_name, chain_id, res_id, atom_id )
#            resultIdTuple = ( entry_name, )
            resultRecord = [ entry_name, chain_id, res_id, atom_id, v ]
            if doTrending:
                dateObject = getDeepByKeysOrAttributes( pdbIdDateResultDict, entry_name)
                if dateObject == None: # obsoleted entries
#                    NTmessage("Skipping obsoleted entry: %s" % entry_name)
                    continue
                # end if date
                resultRecord.append( dateObject )
            # end trending
            result.append(resultRecord)
    #    NTdebug("len(y): %s" % len(y))
    #    result = [float(y[i]) for i in range(len(x))]
#        NTdebug("result: %s" % str(result))
        return result


    def createScatterPlots(self):
        ''' The code below can use settings in the form of a dictionary that influences the
        plotting.

        '''
        m = self
        try:
            djaflsjlfjalskdjf #@UndefinedVariable
            from localPlotList import plotList
        except:
#            NTtracebackError()
            d5 = {IS_TRUE: SEL1_STR, USE_MIN_VALUE_STR: 0.0}
#            d5 = {ONLY_NON_ZERO:1 }
            plotList = [
#            [ PROJECT_LEVEL, CING_STR, DISTANCE_COUNT_STR,dict4 ],
#            [ PROJECT_LEVEL, WHATIF_STR, RAMCHK_STR, {ONLY_SELECTION:1} ],
            [ RES_LEVEL, ( ( CING_STR,   RDB_QUEENY_INFORMATION_STR,    d5),
                           ( WHATIF_STR, RAMCHK_STR,                    d5) ),
                           {SYMBOL_BY_ENTRY:1} ],
            [ RES_LEVEL, ( ( CING_STR,   RDB_QUEENY_INFORMATION_STR,    d5),
                           ( PROCHECK_STR, gf_STR,                    d5) ),
                           {SYMBOL_BY_ENTRY:1} ],
            [ RES_LEVEL, ( ( CING_STR,   RDB_QUEENY_INFORMATION_STR,    d5),
                           ( WHATIF_STR, BBCCHK_STR,                    d5) ),
                           {SYMBOL_BY_ENTRY:1} ],
            [ RES_LEVEL, ( ( CING_STR, RDB_QUEENY_INFORMATION_STR,    d5),
                           ( CING_STR, CV_SIDECHAIN_STR,              d5) ),
                           {SYMBOL_BY_ENTRY:1} ],
            [ RES_LEVEL, ( ( CING_STR, RDB_QUEENY_INFORMATION_STR,    d5),
                           ( CING_STR, CV_BACKBONE_STR,               d5) ),
                           {SYMBOL_BY_ENTRY:1} ],
            [ RES_LEVEL, ( ( CING_STR, RDB_QUEENY_INFORMATION_STR,    d5),
                           ( CING_STR, RMSD_BACKBONE_STR,             d5) ),
                           {SYMBOL_BY_ENTRY:1} ],
            [ RES_LEVEL, ( ( CING_STR, RDB_QUEENY_INFORMATION_STR,    d5),
                           ( CING_STR, RMSD_SIDECHAIN_STR,             d5) ),
                           {SYMBOL_BY_ENTRY:1} ],
            ]

        for p in plotList:
            level, pTuple, plotDict = p
            floatValueLoLoL = []
            progIdList = [0,0]
            chk_idList = [0,0]
            dicList = [0,0]
            chk_id_unique = level + "-"
            level_number = self.getLevelNumber(level)
            NTdebug("level_number %d" % level_number)
            labelList = []
            for dim in range(2):
                progIdList[dim], chk_idList[dim], dicList[dim] = pTuple[dim]
                floatValueLoL = m.getFloatLoLFromDb(level, progIdList[dim], chk_idList[dim], **dicList[dim])
                floatValueLoLoL.append( floatValueLoL )
                if dim:
                    chk_id_unique += '-'
                chk_id = '.'.join([progIdList[dim], chk_idList[dim]])
                chk_id_unique += chk_id
                labelList.append( chk_id )
                NTdebug("Starting with: %s found number of records: %s" % (chk_id, len(floatValueLoL)))

            for dim, floatValueLoL in enumerate(floatValueLoLoL):
                if len(floatValueLoL) == 0:
                    NTmessage("Got empty float LoL for %s from db for: %s skipping plot" % (dim, chk_id_unique))
                    continue
                if not floatValueLoL:
                    NTerror("Encountered and error while getting float LoL %s from db for: %s skipping plot" % (dim, chk_id_unique))
                    continue
            # Link the 2 dims by id via a map from dim x to dim y.
            dim_yDict = NTdict() # hash by entry filterId. E.g. for residue level this will map from res_id to row_idx in floatValueLoL
#            level_number zero is for atom and 3 for entry.
            level_pos = 3-level_number
#            NTdebug("level_pos %d" % level_pos)
#            NTdebug("dim_yDict: %r" % dim_yDict)
            floatValueLoL_x = floatValueLoLoL[0]
            floatValueLoL_y = floatValueLoLoL[1]
            dim_yDict.appendFromTable(floatValueLoL_y, level_pos, -1)
            floatValueLoL_x_size = len(floatValueLoL_x)
            for row_idx in range(floatValueLoL_x_size-1,-1,-1): # reversed makes it easier to delete elements.
                floatValueL_x = floatValueLoL_x[row_idx]
#                NTdebug("floatValueL_x: %s" % str(floatValueL_x))
                level_idx = floatValueL_x[level_pos]
#                NTdebug("Checking row_idx %s and level_idx %s " % (row_idx, level_idx))
                if not dim_yDict.has_key(level_idx):
#                    NTdebug("Removing row_idx %s" % row_idx)
                    del floatValueLoL_x[row_idx]
#                else:
#                    rowY_idx = dim_yDict.get(level_idx)
#                    NTdebug("Found matching row of y %s" % str(floatValueLoL_y[rowY_idx]))
#            dim_xDict = {} # map from valid x row
            floatValueLoL2 = [[],[]]
            for row_idx in range(len(floatValueLoL_x)):
                floatValueL_x = floatValueLoL_x[row_idx]
                level_idx = floatValueL_x[level_pos]
#                dim_xDict[ row_idx ] = dim_yDict.get(level_idx)
#                resultRecord = [ entry_name, chain_id, res_id, atom_id, v ]
                floatValueLoL2[0].append(floatValueL_x[-1])
                floatValueLoL2[1].append(floatValueLoL_y[dim_yDict.get(level_idx)][-1])
            avList = [None,None]
            sdList = [None,None]
            nList = [None,None]
            minValueList = [None,None]
            maxValueList = [None,None]
            minList = [None,None]
            maxList = [None,None]

            titleStr = ''
            for dim in range(2):
                floatValueL = floatValueLoL2[dim]
                floatNTlist = NTlist()
                for row_idx in range(len(floatValueL)):
                    floatNTlist.append(floatValueL[row_idx])
                avList[dim], sdList[dim], nList[dim] = floatNTlist.average()
                minValueList[dim] = floatNTlist.min()
                maxValueList[dim] = floatNTlist.max()
                if 1: # DEFAULT: True. Disable when testing.
                    if minValueList[dim]  == maxValueList[dim]:
                        NTwarning("Skipping plot were the min = max value (%s) for dim: %s." % ( minValueList[dim], dim))
                        continue
                if dim:
                    titleStr += '\n'
                titleStr += "Dim: %s" % dim
                titleStr += ' ' + self.getTitleFromStats( avList[dim], sdList[dim], nList[dim], minValueList[dim], maxValueList[dim] )
                if dicList[dim]:
                    titleStr += ' ' + self.getTitleFromDict(dicList[dim])
                minList[dim] = getDeepByKeysOrAttributes( dicList[dim], USE_MIN_VALUE_STR)
                maxList[dim] = getDeepByKeysOrAttributes( dicList[dim], USE_MAX_VALUE_STR)
                NTdebug("dim: %s lim: %s %s" % (dim, minList[dim], maxList[dim]))
            if plotDict:
                titleStr += '\n' + self.getTitleFromDict(plotDict)
            # end for

            clf()
            doSymbolByEntry = getDeepByKeysOrAttributes( plotDict, SYMBOL_BY_ENTRY)
            if not doSymbolByEntry:
                scatter(x=floatValueLoL2[0], y=floatValueLoL2[1], s=10, c='b', marker='o', cmap=None, norm=None, vmin=None, vmax=None, alpha=None, linewidths=None, faceted=False )
            else:
                floatValueLoLoL = []
                entry_name_map = {}
                colorList = 'b k y g r b k y g r b k y g r'.split()
                markerList = 's o ^ > v < d p h 8 + x'.split()
                NTdebug("Using colorList: %s" % str(colorList))
                NTdebug("Using markerList: %s" % str(markerList))
                for row_idx in range(len(floatValueLoL_x)):
                    floatValueL_x = floatValueLoL_x[row_idx]
                    entry_name = floatValueL_x[0]
                    entry_name = entry_name.replace('Piscataway2','')
                    entry_name = entry_name.replace('Piscataway','')
                    if not entry_name_map.has_key(entry_name):
                         entry_name_map[ entry_name ] = len( entry_name_map.keys())
                         floatValueLoLoL.append(([],[]))
                    entryIdx = entry_name_map.get( entry_name )
                    floatValueLoL = floatValueLoLoL[entryIdx]
                    level_idx = floatValueL_x[level_pos]
    #                dim_xDict[ row_idx ] = dim_yDict.get(level_idx)
    #                resultRecord = [ entry_name, chain_id, res_id, atom_id, v ]
                    floatValueLoL[0].append(floatValueL_x[-1])
                    floatValueLoL[1].append(floatValueLoL_y[dim_yDict.get(level_idx)][-1])
                # end for
                entry_name_list = entry_name_map.keys()
                NTdebug("Using entry_name_list: %s" % str(entry_name_list))
                NTdebug("Using len entry_name_list: %s" % len(entry_name_list))
                entry_name_list.sort()
                for entryIdx in range( len(entry_name_list) ):
                    floatValueLoL = floatValueLoLoL[entryIdx]
                    scatter(x=floatValueLoL[0], y=floatValueLoL[1], s=10, c=colorList[entryIdx], edgecolors=colorList[entryIdx],
                            marker=markerList[entryIdx], label=entry_name_list[entryIdx] )
                    plot()
                legend()
            # end if
            if minList[0] != None:
                xlim(xmin=minList[0])

            xlabel(labelList[0])
            ylabel(labelList[1])
            # end else normed
            grid(True)
            # end else trending
            NTdebug("Title:\n%s" % titleStr)
            title(titleStr, fontsize='small')
            for fmt in ['png' ]:
                fn = "plotHist_%s.%s" % (chk_id_unique, fmt)
                NTdebug("Writing " + fn)
                savefig(fn)
#~
        # end for plot
    # end def


    def createPlots(self, doTrending = False):
        ''' The code below can use settings in the form of a dictionary that influences the
        plotting.
        doTrending shows history on x-axis.
        '''
        m = self
        # NB The level of project is equivalent to the entry level in the database.
        # Sorted by project, program.

#        if doTrending:
#            os.chdir(dir_plotTrending)

        try:
            djaflsjlfjalskdjf #@UndefinedVariable
            from localPlotList import plotList
        except:
#            NTtracebackError()
            plotList = [
#            [ PROJECT_LEVEL, CING_STR, DISTANCE_COUNT_STR,dict4 ],
#            [ PROJECT_LEVEL, WHATIF_STR, RAMCHK_STR, {ONLY_SELECTION:1} ],
#            [ RES_LEVEL, CING_STR, RDB_QUEENY_INFORMATION_STR,  {IS_FALSE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, RDB_QUEENY_UNCERTAINTY1_STR, {IS_FALSE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, RDB_QUEENY_UNCERTAINTY2_STR, {IS_FALSE: SEL1_STR} ],
            [ RES_LEVEL, CING_STR, RDB_QUEENY_INFORMATION_STR,  {IS_TRUE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, RDB_QUEENY_UNCERTAINTY1_STR, {IS_TRUE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, RDB_QUEENY_UNCERTAINTY2_STR, {IS_TRUE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, RMSD_BACKBONE_STR, {IS_TRUE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, RMSD_SIDECHAIN_STR, {IS_TRUE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, RMSD_BACKBONE_STR, {IS_FALSE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, RMSD_SIDECHAIN_STR, {IS_FALSE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, CV_BACKBONE_STR, {IS_TRUE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, CV_SIDECHAIN_STR, {IS_TRUE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, CV_BACKBONE_STR, {IS_FALSE: SEL1_STR} ],
#            [ RES_LEVEL, CING_STR, CV_SIDECHAIN_STR, {IS_FALSE: SEL1_STR} ],
            ]


        for p in plotList:
            level, progId, chk_id, plotDict = p
            if doTrending:
                plotDict[DO_TRENDING] = 1
            chk_id_unique = '.'.join([level,progId,chk_id])
            NTdebug("Starting with: %s" % chk_id_unique)
            floatValueLoL = m.getFloatLoLFromDb(level, progId, chk_id, **plotDict)
#            resultRecord = [ entry_name, chain_id, res_id, atom_id, v ]
            if len(floatValueLoL) == 0:
                NTmessage("Got empty float LoL from db for: %s skipping plot" % chk_id_unique)
                continue
            if not floatValueLoL:
                NTerror("Encountered and error while getting float LoL from db for: %s skipping plot" % chk_id_unique)
                continue

            floatNTlist = NTlist()
            for i in range(len(floatValueLoL)):
                floatNTlist.append(floatValueLoL[i][4])
            av, sd, n = floatNTlist.average()
            minValue = floatNTlist.min()
            maxValue = floatNTlist.max()


            if False: # DEFAULT: True. Disable when testing.
                if minValue == maxValue:
                    NTwarning("Skipping plot were the min = max value.")
                    continue

            titleStr = self.getTitleFromStats( av, sd, n, minValue, maxValue )
            if plotDict:
                titleStr += '\n'
            titleStr += self.getTitleFromDict( plotDict )
            NTmessage("Plotting level/program/check: %10s %10s %15s with options: %s %s" % (level,progId,chk_id,titleStr,plotDict))
            clf()

            xmin = getDeepByKeysOrAttributes( plotDict, USE_MIN_VALUE_STR)
            xmax = getDeepByKeysOrAttributes( plotDict, USE_MAX_VALUE_STR)

            if doTrending:
                num_points_line = 100
                y = floatNTlist
                x = NTlist()
                xDate = NTlist()
                for i in range(len(floatNTlist)):
                    dateObject = floatValueLoL[i][5]
                    x.append(date2num(dateObject))
                    xDate.append(dateObject)
                # end list creation.
                scatter(xDate, y, s=0.1) # Plot of the data and the fit
                p = polyfit(x, y, 1)  # deg 1 means 2 parameters for a order 2 polynomial
                NTmessage("Fit with terms             : %s" % p)
                titleStr += ' trending %s per year' % (p[0]*365.25)

                t = [min(xDate), max(xDate)] # Only need 2 points for straight line!
                plot(t, fitDatefuncD2(p, t), "r--", linewidth=1) # Plot of the data and the fit
                # Now bin
                yearMin = 1990 # inclusive start
                yearMax = 2012 # exclusive end
                yearBinSize = 2
                nbins = ( yearMax - yearMin ) / yearBinSize  # should match above. last bin will start at 2010
                dateMin = datetime.date(yearMin, 1, 1)
                dateMax = datetime.date(yearMax, 1, 1)
                dateNumMin = date2num(dateMin)
                dateNumMax = date2num(dateMax)
#                dateNumSpan = dateNumMax - dateNumMin
                halfBinSize = datetime.timedelta(365*yearBinSize/2.)
                NTmessage("Date number min/max: %s %s" % (dateNumMin, dateNumMax))
                if False: # test positions
                    testX = [dateMin,dateMax]
                    testY = [-10.,0.]
                    plot(testX, testY)

#                nr = 100 # number of records
#                x = np.random.random(nr) * dateNumSpan + dateNumMin
                x = np.array(x)
#                y = np.random.random(nr) * 10
                y = np.array(y)
                print "x: %s" % x
                print "y: %s" % y
                binned_valueList, numBins = bin_by(y, x, nbins=nbins, ymin=dateNumMin, ymax=dateNumMax)
                bins = []
                widths = []
                dataAll = []
                for i,bin in enumerate(numBins):
                    bins.append(num2date(bin) + halfBinSize )
                    widths.append(datetime.timedelta(365)) # 1 year width for box
                    spread = binned_valueList[i]
                    spread.sort()
#                    aspread = asarray(spread)
                    dataAll.append(spread)
                    NTdebug("spread: %s" % spread)
                # end for
                NTdebug("numBins: %s" % numBins)
                sym = '' # no symbols
                sym = 'k.'
                wiskLoL = boxplot(dataAll, positions=bins, widths=widths, sym=sym)
#                scatter(x, y, s=0.1) # Plot of the data and the fit
                print 'wiskLoL: %s' % wiskLoL
                xlim(xmin=dateMin, xmax=dateMax)
            else:
                # Histogram the data
                normed = 0 # Default zero
                num_bins = 50
                num_points_line = num_bins * 10

                bins_input = num_bins
                if xmax != None and xmin != None:
#                    NTdebug("Creating the non-standard x-range.")
                    bins_input = numpy.linspace(xmin,xmax,num_bins,endpoint=True)

                n, bins, _patches = hist(floatNTlist, bins_input, normed=normed, facecolor='green', alpha=0.75)
                # Draw a line to fit.
                if normed:
                    y = mlab.normpdf( bins, av, sd) # would loose the y-axis count by a varying scale factor. Not desirable.
                    plot(bins, y, 'r--', linewidth=1)
                else:
                    halve_bin_size = (bins[1] - bins[0])/2.
                    x = numpy.linspace(min(bins)+halve_bin_size, max(bins)-halve_bin_size, num_bins)
                    y = array(n)
#                    NTdebug("x:    %s %s" % (len(x), x))
#                    NTdebug("y:    %s %s" % (len(y), y))

                    # NB different functions can easily be modeled here.
                    # http://en.wikipedia.org/wiki/Gaussian_distribution taken for now. Normal distribution still needs to be scaled to fit
                    # Non-normalized distributions fitted here.
                    # Clearly, the bins need to be at the integer boundaries for integer values such as PROJECT.CING.distance_count
                    # Otherwise the fits will be on centered around the largest small bin.
                    # For now, not using the fitted parameters but when non-analytical functions need to be modeled we should use a fit.
                    # Below code inspired by: http://www.scipy.org/Cookbook/FittingData
                    fitfunc = lambda p, x: p[0] * numpy.exp(-(x-p[1])**2/(2*p[2])) # exp is numpy.exp @UndefinedVariable
                    errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function
                    variance = sd**2 # variance
                    maxValueHist = max(y)
                    p0 = [maxValueHist, av, variance] # Initial guess for the parameters
                    if False: # actually do the fit or save some time.
                        msg = "Started fit with maxValueHist, mu, variance     : %8.3f %8.3f %8.3f" % tuple(p0)
                        NTmessage(msg)
                        # Use full output to get error estimates etc from Fortran library.
                        p1, success = optimize.leastsq(errfunc, p0[:], full_output=0, args=(x, y))
                        NTmessage("Success: %s" % success)
                        msg = "Fit with maxValueHist, mu, variance             : %8.3f %8.3f %8.3f" % tuple(p1)
                        NTmessage(msg)
                    t = numpy.linspace(min(bins), max(bins), num_points_line)
                    if False:
                        NTdebug("Plotting fit")
                        q = p1
                    else:
                        NTdebug("Plotting analytically parameterized function.")
                        q = p0
                    if 0:
                        plot(t, fitfunc(q, t), "r--", linewidth=1) # Plot of the data and the fit
                    ylabel('Frequency')
                # end else normed
                grid(True)
            # end else trending

            xlabel(chk_id_unique)
            title(titleStr)
            for fmt in ['png' ]:
                fn = "plotHist_%s.%s" % (chk_id_unique, fmt)
                NTdebug("Writing " + fn)
                savefig(fn)
        # end for plot
    # end def


    def createScatterPlotGreenVersusRed(self):
        """This routine is a duplicate of the one developed afterwards/below.
        """
        os.chdir(cingDirTmp)
        m = self
        perEntryRog = m.perEntryRog
        s = select([m.e1.c.pdb_id, m.r1.c.rog, 100.0 * func.count(m.r1.c.rog) / m.e1.c.res_count
                     ], from_obj=[m.e1.join(m.r1)]
                     ).group_by(m.e1.c.pdb_id, m.r1.c.rog, m.e1.c.res_count)
        NTdebug("SQL: %s" % s)
        result = m.execute(s).fetchall()
        #NTdebug("ROG percentage per entry: %s" % result)

        for row in result:
        #    print row[0]
            k = row[0]
            if not perEntryRog.has_key(k):
                perEntryRog[k] = NTfill(0.0, 3)
            perEntryRog[k][int(row[1])] = float(row[2])

        pdb_id_list = perEntryRog.keys()
        color = NTfill(0.0, 3)
        color[0] = NTlist() # green
        color[1] = NTlist()
        color[2] = NTlist()

        for entry_id in pdb_id_list:
            l = perEntryRog[ entry_id ]
            for i in range(3):
                color[i].append(l[i])

        ps = NTplotSet()
        p = ps.createSubplot(1, 1, 1)
        p.title = 'NRG-CING'
        p.xRange = (0, 100)
        p.yRange = (0, 100)
        p.setMinorTicks(5)
        attr = fontVerticalAttributes()
        attr.fontColor = 'green'
        p.labelAxes((-0.08, 0.5), 'green(%)', attributes=attr)
        attr = fontAttributes()
        attr.fontColor = 'red'
        p.labelAxes((0.45, -0.08), 'red(%)', attributes=attr)
        p.label( (61,89), 'fine' )
        p.label( (80,53), 'problematic' )
        symbolColor = 'g'
        symbolSize = 5
        p.scatter(color[2], color[0], symbolSize, symbolColor, marker = '+')

        offset = 15
        lineWidth = 10
        attributes = NTplotAttributes(lineWidth=lineWidth, color='green')
        p.line([0,offset],[100 - offset, 100], attributes)
        attributes = NTplotAttributes(lineWidth=lineWidth, color='red')
        p.line([offset, 0], [100, 100 - offset], attributes)
        fn = os.path.join(cingDirTmp, 'nrgcingPlot1.png')
        ps.hardcopySize = (900,900)
        if is_interactive():
            ps.show()
        else:
            ps.hardcopy(fn)

        NTdebug("Done plotting %s" % fn)


    def getAndPlotColorVsColor(self, doPlot = True):
        m = self
        perEntryRog = m.perEntryRog
        # Plot the % red vs green for all in nrgcing
        s = select([m.e1.c.pdb_id, m.r1.c.rog, 100.0 * func.count(m.r1.c.rog) / m.e1.c.res_count
                     ], and_(m.e1.c.pdb_id==m.s1.c.pdb_id,
                             m.e1.c.entry_id==m.r1.c.entry_id
                             ),
                     ).group_by(m.e1.c.pdb_id, m.r1.c.rog, m.e1.c.res_count).order_by(m.e1.c.pdb_id,m.r1.c.rog)
        NTdebug("SQL: %s" % s)
        result = m.execute(s).fetchall()

        NTdebug("ROG per residue calculated for number of entry rog scores: %s" % len(result))
        for row in result:
        #    print row[0]
            k = row[0]
            if not perEntryRog.has_key(k):
                perEntryRog[k] = NTfill(0.0, 3)
            perEntryRog[k][int(row[1])] = float(row[2])

        if not doPlot:
            return
        pdb_id_list = perEntryRog.keys()
        color = NTfill(0.0, 3)
        color[0] = NTlist() # green
        color[1] = NTlist()
        color[2] = NTlist()

        for pdb_id in pdb_id_list:
            l = perEntryRog[ pdb_id ]
            for i in range(3):
                color[i].append(l[i])

        entryList = perEntryRog.keys()
        entryList.sort()
        NTdebug("ROG per residue calculated for number of entries: %s" % len(entryList))
    #    NTdebug("ROG per residue: %s" % m)

        strTitle = 'rog'
        ps = NTplotSet() # closes any previous plots
        ps.hardcopySize = (1000, 1000)
        myplot = NTplot(title=strTitle)
        ps.addPlot(myplot)

        cla() # clear all.
        _p = plt.plot(color[2], color[0], '+', color='blue')
        xlim(0, 100)
        ylim(0, 100)
        xlabel('% residues red')
        ylabel('% residues green')

        a = gca()
        attributesMatLibPlot = {'linewidth' :2}
        xOffset = 20
        line2D = Line2D([0, 100 - xOffset], [xOffset, 100])
        line2D.set(**attributesMatLibPlot)
        line2D.set_c('g')
        a.add_line(line2D)
        line2D = Line2D([xOffset, 100], [0, 100 - xOffset])
        line2D.set(**attributesMatLibPlot)
        line2D.set_c('r')
        a.add_line(line2D)

        fn = strTitle + '.png'
        ps.hardcopy(fn)

    def plotQualityVsColor(self):
        m = self
        elementNameList = ['WI_Backbone', 'WI_Rama', 'PC_Backbone']
        colorNameList = 'green orange red'.split()

        s = select([m.e1.c.pdb_id, m.e1.c.wi_bbcchk, m.e1.c.wi_ramchk, m.e1.c.pc_gf_phipsi,
                     ], and_(m.e1.c.pdb_id==m.s1.c.pdb_id,
                             m.e1.c.wi_bbcchk > -15.0,
                             m.e1.c.wi_bbcchk < 5.0,
                             )
                     ).order_by(m.e1.c.pdb_id)
        NTdebug("SQL: %s" % s)
        result = m.execute(s).fetchall()
        NTdebug("Entries returned: %s" % len(result))

    #    elementIdx = 1
    #    colorIdx = 0 # green is zero
        for elementIdx in range(len(elementNameList)):
            for colorIdx in range(len(colorNameList)):
                xSerie = []
                ySerie = []
                for row in result:
                #    print row[0]
                    k = row[0]
                    if not m.perEntryRog.has_key(k):
                        continue
                    xSerie.append(row[elementIdx+1])
                    ySerie.append(m.perEntryRog[k][colorIdx])

                strTitle = 'plotQualityVsColor_%s_%s' % ( elementNameList[elementIdx], colorNameList[colorIdx])
                ps = NTplotSet() # closes any previous plots
                ps.hardcopySize = (1000, 1000)
                myplot = NTplot(title=strTitle)
                ps.addPlot(myplot)

                cla() # clear all.
                _p = plt.plot(xSerie, ySerie, '+', color='blue')
            #    xlim(0, 100)
                ylim(0, 100)
                xlabel(elementNameList[elementIdx])
                ylabel('perc. residues %s' % colorNameList[colorIdx])

                fn = strTitle + '.png'
                NTdebug("Writing " + fn)
                ps.hardcopy(fn)

    def plotQualityPcVsColor(self):
        m = self
        """
        pc_rama_core                      FLOAT DEFAULT NULL,
        pc_rama_allow                      FLOAT DEFAULT NULL,
        pc_rama_gener                      FLOAT DEFAULT NULL,
        pc_rama_disall                      FLOAT DEFAULT NULL
    """
        elementNameList = 'pc_rama_core pc_rama_allow pc_rama_gener pc_rama_disall'.split()
        colorNameList = 'green orange red'.split()

        s = select([m.e1.c.pdb_id, m.p1.c.pc_rama_core, m.p1.c.pc_rama_allow, m.p1.c.pc_rama_gener, m.p1.c.pc_rama_disall
                     ], and_(m.e1.c.pdb_id==m.s1.c.pdb_id,
                             m.e1.c.pdb_id==m.p1.c.pdb_id,
                             m.e1.c.wi_bbcchk > -15.0,
                             m.e1.c.wi_bbcchk < 5.0,
                             )
                     ).order_by(m.e1.c.pdb_id)
        NTdebug("SQL: %s" % s)
        result = m.execute(s).fetchall()
        NTdebug("Entries returned: %s" % len(result))

    #    elementIdx = 1
    #    colorIdx = 0 # green is zero
        for elementIdx in range(len(elementNameList)):
            for colorIdx in range(len(colorNameList)):
                xSerie = []
                ySerie = []
                for row in result:
                #    print row[0]
                    k = row[0]
                    if not m.perEntryRog.has_key(k):
                        continue
                    xSerie.append(row[elementIdx+1])
                    ySerie.append(m.perEntryRog[k][colorIdx])

                strTitle = 'plotQualityPcVsColor_%s_%s' % ( elementNameList[elementIdx], colorNameList[colorIdx])
                ps = NTplotSet() # closes any previous plots
                ps.hardcopySize = (1000, 1000)
                myplot = NTplot(title=strTitle)
                ps.addPlot(myplot)

                cla() # clear all.
                _p = plt.plot(xSerie, ySerie, '+', color='blue')
            #    xlim(0, 100)
                ylim(0, 100)
                xlabel(elementNameList[elementIdx])
                ylabel('perc. residues %s' % colorNameList[colorIdx])

                for fmt in ['.png', '.eps']:
                    fn = strTitle + fmt
                    NTdebug("Writing " + fn)
                    ps.hardcopy(fn)
                # end for
            # end for
        # end for
    # end def
# end class

def getDbColumnName( level, progId, chk_id ):
    columnName = ''
    if progId == WHATIF_STR:
        columnName = 'wi_'
    elif progId == PROCHECK_STR:
        columnName = 'pc_'
    columnName += chk_id
    columnName = columnName.lower()
    return columnName


def fitDatefuncD2 (p, xDate):
    return p[0] * date2num(xDate) + p[1]

def fitDatefuncD1 (p, xDate):
    return p[0]

def bin_by(y, x, nbins=None, ymin=None, ymax=None):
    """
    Bin y by x.

    Returns the binned "y",'x' values and the left edges of the bins
    """
    if nbins == None:
        nbins = 6
    if ymin == None:
        ymin = x.min()
    if ymax == None:
        ymax = x.max()
    bins = np.linspace(ymin, ymax, nbins + 1)
    # To avoid extra bin for the max value
    bins[-1] += 1
    indicies = np.digitize(x, bins)
    output = []
    for i in xrange(1, len(bins)):
        output.append(y[indicies == i])
    # Just return the left edges of the bins
    bins = bins[:-1]
    return output, bins

if __name__ == '__main__':
    cing.verbosity = verbosityDebug

#    schema = DEV_NRG_DB_SCHEMA
    schema = CASD_DB_NAME

    m = nrgCingRdb( schema=schema )

    if 0:
        m.createPlots(doTrending = False)
    if 1:
        m.createScatterPlots()
    if False:
#        m.plotQualityVsColor()
#        m.plotQualityPcVsColor()
        m.getAndPlotColorVsColor(doPlot = True)
    if False:
        m.createScatterPlotGreenVersusRed()
    if 0:
        pdbIdList = m.getPdbIdList()

    if 0:
        m.showCounts()

    NTmessage("done with nrgCingRdb")
