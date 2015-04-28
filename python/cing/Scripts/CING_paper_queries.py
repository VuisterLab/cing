"""
Unit test execute as:
python $CINGROOT/python/cing/Scripts/cingProfile.py
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.html import hPlot

cing.verbosity = cing.verbosityDebug

#[PYTHON-001]
# Not used.
if True:
    hPlot.initHist()
    hist2d = hPlot.histRamaCombined
    result = sum( sum( hist2d ))
    nTmessage("histRamaCombined: %s" % hist2d)
    nTmessage("Sum: %s" % result)
    hist2d = hPlot.histRamaBySsAndResType
    nTmessage("histRamaBySsAndResType: %s" % hist2d)
    nTmessage("histRamaCombined: %s" % hist2d)
    nTmessage("Sum: %s" % result)

#[PYTHON-002]
# Not really python code but just a link for
# 1044392 residues in D1D2 plots from $C/data/PluginCode/WhatIf/README.txt 

#[PYTHON-003]
# set x = 1cjg
# cing -n $x -v 9 --initCcpn $D/NRG-CING/recoordSync/$x/$x.tgz --ipython
project = None

# Use %paste in ipython.
p = project
m = p.molecule

rl = p.molecule.allResidues()
distanceL = p.distances[0]
distanceL.analyze()
nTmessage("%s is:\n%s" % (distanceL, format(distanceL)))
i = 0
count_total = 0.
for r in rl:
    if r.resNum < 83 or r.resNum > 98:
        continue
    # end if
    drl = r.distanceRestraints
    n = len(drl)
    nTmessage("%s has %03d DRs" % (r, n))
    count_total += n
    i += 1
# end for 
averageCount = count_total / i
nTmessage("For this segment there are on average %s DRs per residue" % averageCount)
