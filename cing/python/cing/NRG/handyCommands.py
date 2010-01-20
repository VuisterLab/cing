# python -u $CINGROOT/python/cing/NRG/handyCommands.py

"""
Commands that are more like a loose script utilizing/testing the CING api.
"""
#if False:
#    from matplotlib import interactive
#    from matplotlib import use #@UnusedImport
#    use('TkAgg') # Instead of agg
#    interactive(True)
# block to start interactive plotting. Do not alter the sequence of the blocked commands!
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTlist
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from cing.core.sml import NTdict
from pylab import * #@UnusedWildImport # imports plt too now.
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import select #@Reimport
import cing


cing.verbosity = verbosityDebug

csql = csqlAlchemy()
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
s = select([e1.c.pdb_id, r1.c.rog, 100.0*func.count(r1.c.rog)/e1.c.res_count
             ], from_obj=[e1.join(r1)]
             ).group_by(e1.c.pdb_id, r1.c.rog)
NTdebug( "SQL: %s" % s)
m = execute(s).fetchall()
#NTdebug("ROG percentage per entry: %s" % m)

perEntryRog = NTdict()
for row in m:
#    print row[0]
    k = row[0]
    if not perEntryRog.has_key(k):
        perEntryRog[k] = NTfill(0.0,3)
    perEntryRog[k][int(row[1])] = float(row[2])

pdb_id_list = perEntryRog.keys()
color = NTfill(0.0,3)
color[0] = NTlist() # green
color[1] = NTlist()
color[2] = NTlist()

for entry_id in pdb_id_list:
    l = perEntryRog[ entry_id ]
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
p = plt.plot( color[2], color[0], 'b+' )
xlim(0,100)
ylim(0,100)
a = gca()
attributesMatLibPlot = {'linewidth' :5}
xOffset = 20
line2D = Line2D([0,100-xOffset], [xOffset, 100])
line2D.set( **attributesMatLibPlot )
line2D.set_c('g')
a.add_line(line2D)
line2D = Line2D([xOffset,100], [0, 100-xOffset])
line2D.set( **attributesMatLibPlot )
line2D.set_c('r')
a.add_line(line2D)