# python -u $CINGROOT/python/cing/NRG/makeNRGCINGplots.py
# reload cing.NRG.makeNRGCINGplots
# from cing.NRG.makeNRGCINGplots import *
"""
Create plots like the GreenVersusRed scatter by entry.
"""

from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotAttributes
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import fontAttributes
from cing.Libs.NTplot import fontVerticalAttributes
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from matplotlib import is_interactive
from pylab import * #@UnusedWildImport # imports plt too now.
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import select #@Reimport @UnusedImport

if False:
    from matplotlib import use #@UnusedImport
    use('TkAgg') # Instead of agg
    interactive(True)

# block to start interactive plotting. Do not alter the sequence of the blocked commands!

cing.verbosity = verbosityDebug

db_name = PDBJ_DB_NAME
user_name = PDBJ_DB_USER_NAME
schema = NRG_DB_NAME
#host = 'nmr'
host = 'localhost'
csql = csqlAlchemy(host=host, user=user_name, db=db_name, schema=schema)
csql.connect()
csql.autoload()
#csql.close()

csql.loadTable('cingsummary')
csql.loadTable('entry_list_selection')
csql.loadTable('tmppc')

execute = csql.conn.execute
session = csql.session
query = session.query
engine = csql.engine
centry = csql.cingentry
cchain = csql.cingchain
cresidue = csql.cingresidue
csummary = csql.cingsummary
centry_list_selection = csql.entry_list_selection
ctmppc = csql.tmppc

e1 = centry.alias()
c1 = cchain.alias()
r1 = cresidue.alias()
r2 = cresidue.alias()
cs = csummary.alias()
s1 = centry_list_selection.alias()
p1 = ctmppc.alias()



def createScatterPlotGreenVersusRed():
    """This routine is a duplicate of the one developed afterwards/below.
    """
    s = select([e1.c.pdb_id, r1.c.rog, 100.0 * func.count(r1.c.rog) / e1.c.res_count
                 ], from_obj=[e1.join(r1)]
                 ).group_by(e1.c.pdb_id, r1.c.rog)
    NTdebug("SQL: %s" % s)
    m = execute(s).fetchall()
    #NTdebug("ROG percentage per entry: %s" % m)

    for row in m:
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
    fn = 'nrgcingPlot1.png'
    ps.hardcopySize = (900,900)
    if is_interactive():
        ps.show()
    else:
        ps.hardcopy(fn)

    NTdebug("Done plotting %s" % fn)



def getAndPlotColorVsColor(perEntryRog, doPlot = True):
    # Plot the % red vs green for all in nrgcing
    s = select([e1.c.pdb_id, r1.c.rog, 100.0 * func.count(r1.c.rog) / e1.c.res_count
                 ], and_(e1.c.pdb_id==s1.c.pdb_id,
                         e1.c.entry_id==r1.c.entry_id
                         ),
                 ).group_by(e1.c.pdb_id, r1.c.rog, e1.c.res_count).order_by(e1.c.pdb_id,r1.c.rog)
    NTdebug("SQL: %s" % s)
    m = execute(s).fetchall()

    NTdebug("ROG per residue calculated for number of entry rog scores: %s" % len(m))
    for row in m:
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

def plotQualityVsColor(perEntryRog):
    elementNameList = ['WI_Backbone', 'WI_Rama', 'PC_Backbone']
    colorNameList = 'green orange red'.split()

    s = select([e1.c.pdb_id, e1.c.wi_bbcchk, e1.c.wi_ramchk, e1.c.pc_gf_phipsi,
                 ], and_(e1.c.pdb_id==s1.c.pdb_id,
                         e1.c.wi_bbcchk > -15.0,
                         e1.c.wi_bbcchk < 5.0,
                         )
                 ).order_by(e1.c.pdb_id)
    NTdebug("SQL: %s" % s)
    m = execute(s).fetchall()
    NTdebug("Entries returned: %s" % len(m))

#    elementIdx = 1
#    colorIdx = 0 # green is zero
    for elementIdx in range(len(elementNameList)):
        for colorIdx in range(len(colorNameList)):
            xSerie = []
            ySerie = []
            for row in m:
            #    print row[0]
                k = row[0]
                if not perEntryRog.has_key(k):
                    continue
                xSerie.append(row[elementIdx+1])
                ySerie.append(perEntryRog[k][colorIdx])

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

def plotQualityPcVsColor(perEntryRog):
    """
    pc_rama_core                      FLOAT DEFAULT NULL,
    pc_rama_allow                      FLOAT DEFAULT NULL,
    pc_rama_gener                      FLOAT DEFAULT NULL,
    pc_rama_disall                      FLOAT DEFAULT NULL
"""
    elementNameList = 'pc_rama_core pc_rama_allow pc_rama_gener pc_rama_disall'.split()
    colorNameList = 'green orange red'.split()

    s = select([e1.c.pdb_id, p1.c.pc_rama_core, p1.c.pc_rama_allow, p1.c.pc_rama_gener, p1.c.pc_rama_disall
                 ], and_(e1.c.pdb_id==s1.c.pdb_id,
                         e1.c.pdb_id==p1.c.pdb_id,
                         e1.c.wi_bbcchk > -15.0,
                         e1.c.wi_bbcchk < 5.0,
                         )
                 ).order_by(e1.c.pdb_id)
    NTdebug("SQL: %s" % s)
    m = execute(s).fetchall()
    NTdebug("Entries returned: %s" % len(m))

#    elementIdx = 1
#    colorIdx = 0 # green is zero
    for elementIdx in range(len(elementNameList)):
        for colorIdx in range(len(colorNameList)):
            xSerie = []
            ySerie = []
            for row in m:
            #    print row[0]
                k = row[0]
                if not perEntryRog.has_key(k):
                    continue
                xSerie.append(row[elementIdx+1])
                ySerie.append(perEntryRog[k][colorIdx])

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

            fn = strTitle + '.png'
            NTdebug("Writing " + fn)
            ps.hardcopy(fn)

if __name__ == '__main__':
    perEntryRog = NTdict()
    plotQualityVsColor(perEntryRog)
    plotQualityPcVsColor(perEntryRog)
    getAndPlotColorVsColor(perEntryRog, doPlot = True)
    if False:
        createScatterPlotGreenVersusRed()
