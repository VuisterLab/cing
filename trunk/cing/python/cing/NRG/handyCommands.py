# python -u $CINGROOT/python/cing/NRG/handyCommands.py

"""
Commands that are more like a loose script utilizing/testing the CING api.
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import CASD_DB_NAME
from cing.NRG import CASD_DB_USER_NAME
from cing.NRG.CasdNmrMassageCcpnProject import colorByLab
from cing.NRG.CasdNmrMassageCcpnProject import labList
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from pylab import * #@UnusedWildImport # imports plt too now.
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import select #@Reimport

cing.verbosity = verbosityDebug

csql = csqlAlchemy(user=CASD_DB_USER_NAME, db=CASD_DB_NAME)
csql.connect()
csql.autoload()

execute = csql.conn.execute
session = csql.session
query = session.query
engine = csql.engine
centry = csql.entry
cchain = csql.chain
cresidue = csql.residue

e1 = centry.alias()
c1 = cchain.alias()
r1 = cresidue.alias()
r2 = cresidue.alias()

#SQL: select count(*) from entry e;
s = select([func.count(centry.c.entry_id)])
m = execute(s).fetchall()
NTdebug("Entry count: %s" % m)

#SQL: select entry_id from entry e where e.casd_id='AR3436ACheshire';
s = select([centry.c.entry_id, centry.c.casd_id], centry.c.casd_id == 'AR3436ACheshire')
m = execute(s).fetchall()
NTdebug("Data: %s" % m)

#result = csql.conn.execute(centry.insert().values(casd_id='testje'))
#print result.last_inserted_ids() # fails for postgres version I have.
#
#result = csql.session.execute(select([centry.c.entry_id]).where(centry.c.casd_id == 'testje'))
#m = result.fetchall()
#NTdebug("Entry count: %s" % m)
#
#s = select([centry.c.entry_id],and_(centry.c.casd_id == 'testje', centry.c.entry_id > 0))
#result = csql.session.execute(s)
#m = result.fetchall()
#NTdebug("Entry count: %s" % m)

#SQL: select r.rog, count(*) from residue r group by r.rog;
#s = select([cresidue.c.rog, func.count(cresidue.c.rog)]).group_by(cresidue.c.rog)
#m = execute(s).fetchall()
#NTdebug("ROG distribution: %s" % m)

#SQL: to get percentages of rog scores.
# select r.entry_id, r.rog, count(*)/(
#            select count(*) from residue rr where rr.entry_id = r.entry_id)
# from residue r group by r.entry_id,r.rog order by r.entry_id, r.rog;
#s = select([r1.c.entry_id, r1.c.rog, 100*func.count(r1.c.rog)/
#            select([func.count(r2.c.entry_id)], r2.c.entry_id==r1.c.entry_id)
#             ]).group_by(r1.c.entry_id, r1.c.rog)
#NTdebug( "SQL: %s" % s)
#m = execute(s).fetchall()
#NTdebug("ROG percentage per entry: %s" % m)

# My first join with sqlAlchemy
#s = select([e1.c.pdb_id, e1.c.res_count, r1.c.name, r1.c.rog], from_obj=[e1.join(r1)])
#m = execute(s).fetchone()
#NTdebug("Residues per entry: %s" % m)

# START BLOCK
s = select([e1.c.casd_id, e1.c.rog])
NTdebug("SQL: %s" % s)
m = execute(s).fetchall()
NTdebug("ROG per entry: %s" % m)

# below works in MySql but not in Postgresql
#s = select([e1.c.casd_id, r1.c.rog, 100.0 * func.count(r1.c.rog) / e1.c.res_count
#             ], from_obj=[e1.join(r1)]
#             ).group_by(e1.c.casd_id, r1.c.rog)
s = select([e1.c.casd_id, r1.c.rog, 100.0 * func.count(r1.c.rog) / e1.c.res_count
             ], from_obj=[e1.join(r1)]
             ).group_by(e1.c.casd_id, r1.c.rog, e1.c.res_count).order_by(e1.c.casd_id,r1.c.rog)
NTdebug("SQL: %s" % s)
m = execute(s).fetchall()
NTdebug("ROG per residue: %s" % m)

perEntryRog = NTdict()
for row in m:
#    print row[0]
    k = row[0]
    if not perEntryRog.has_key(k):
        perEntryRog[k] = NTfill(0.0, 3)
    perEntryRog[k][int(row[1])] = float(row[2])

casd_id_list = perEntryRog.keys()
color = NTfill(0.0, 3)
color[0] = NTlist() # green
color[1] = NTlist()
color[2] = NTlist()

for casd_id in casd_id_list:
    l = perEntryRog[ casd_id ]
    for i in range(3):
        color[i].append(l[i])

#result = engine.execute("select count(*) from ENTRY")
#for u in session.query(e1).instances(result):
#    print u
#query(e1).from_statement("SELECT COUNT(*) FROM ENTRY WHERE pdb_id=:pdb_id").params(pdb_id='1brv').all()

# start plotting.

#color[0] = [ 1,2,3]
#color[2] = [ 2,3,4]
cla() # clear all.
# scatter plot red (x) versus green (y)
for lab in labList:
    lineColor = colorByLab[lab]
    p = plt.plot(color[2], color[0], '+', colorXXXX=lineColor, label = lab)
    xlim(0, 100)
    ylim(0, 100)
    xlabel('% residues green')
    ylabel('% residues red')

    legend( ('label1', 'label2', 'label3'), loc='upper left')
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

savefig('rog.png')
