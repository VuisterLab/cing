"""
Commands that are more like a loose script utilizing/testing the CING api.
"""
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTlist
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from cing.core.sml import NTdict
from pylab import * #@UnusedWildImport must be before below so 'select' gets overwritten.
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import select #@Reimport
import cing

cing.verbosity = verbosityDebug

csql = csqlAlchemy()
csql.connect()
csql.autoload()

execute = csql.conn.execute
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
s = select([cresidue.c.rog, func.count(cresidue.c.rog)]).group_by(cresidue.c.rog)
m = execute(s).fetchall()
NTdebug("ROG distribution: %s" % m)

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
s = select([e1.c.pdb_id, e1.c.res_count, r1.c.name, r1.c.rog], from_obj=[e1.join(r1)])
m = execute(s).fetchall()
NTdebug("Residues per entry: %s" % m)

s = select([e1.c.pdb_id, r1.c.rog, 100.0*func.count(r1.c.rog)/e1.c.res_count
             ], from_obj=[e1.join(r1)]
             ).group_by(e1.c.pdb_id, r1.c.rog)
NTdebug( "SQL: %s" % s)
m = execute(s).fetchall()
NTdebug("ROG percentage per entry: %s" % m)

perEntryRog = NTdict()
for row in m:
    perEntryRog[ row[0] ] = NTfill(0.0,3)

for row in m:
    perEntryRog[ row[0] ][row[1]] = float(row[2])

green = NTlist()
orange = NTlist()
red = NTlist()
for entry_id in perEntryRog.keys():
    green.append(perEntryRog[ entry_id ][0])
    orange.append(perEntryRog[ entry_id ][1])
    red.append(perEntryRog[ entry_id ][2])


sort(green)
plot(green)
plot(orange)
plot(red)
