# python -u $CINGROOT/python/cing/Scripts/interactive/mouseBuffer6.py
from cing.Libs.NTutils import * #@UnusedWildImport
from pylab import * #@UnusedWildImport # imports plt too now.



# for 2kq3; for removing high violations in the DRs and talos dihedrals 
p = None # Just for misleading pylint and pydev.
# START
#p = project
m = p.molecule
p.validate(validateFastest=True)
drViolThreshold = 2.0

drL = p.distances[0]
for i,dr in enumerate(drL):
    if dr.violMax > drViolThreshold:
        nTmessage("%s" % format(dr))
    # end if
# end for dr

disList = p.distances[0]
dis1 = disList[1936]


