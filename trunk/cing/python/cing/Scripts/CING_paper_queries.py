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
