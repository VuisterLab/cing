# python -u $CINGROOT/python/cing/NRG/makeNRGCINGplots.py
"""
Create plots like the GreenVersusRed scatter by entry.
"""
if False:
    from matplotlib import interactive
    from matplotlib import use #@UnusedImport
    use('TkAgg') # Instead of agg
    interactive(True)

# block to start interactive plotting. Do not alter the sequence of the blocked commands!
from cing.Libs.NTplot import NTplotAttributes
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import fontAttributes
from cing.Libs.NTplot import fontVerticalAttributes
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from matplotlib import is_interactive
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import select #@Reimport

def createScatterPlotGreenVersusRed():
    cing.verbosity = verbosityDebug

    csql = csqlAlchemy()
    csql.connect()
    csql.autoload()

    execute = csql.conn.execute
    centry = csql.entry
    cchain = csql.chain #@UnusedVariable
    cresidue = csql.residue

    e1 = centry.alias()
    r1 = cresidue.alias()

    s = select([e1.c.pdb_id, r1.c.rog, 100.0 * func.count(r1.c.rog) / e1.c.res_count
                 ], from_obj=[e1.join(r1)]
                 ).group_by(e1.c.pdb_id, r1.c.rog)
    NTdebug("SQL: %s" % s)
    m = execute(s).fetchall()
    #NTdebug("ROG percentage per entry: %s" % m)

    perEntryRog = NTdict()
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

if __name__ == '__main__':
    createScatterPlotGreenVersusRed()