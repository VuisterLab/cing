"""
Settings for the processNrgCing script
"""

import os
baseDir = '/Users/jd/CASD-NMR-CING' #@UnusedVariable

# If on production machine then
# -1- the urls will differ from localhost to nmr.cmbi.ru.nl or so.
isProduction = False #@UnusedVariable

UJ              = '/Users/jd'
WS              = os.path.join(UJ,'workspace35')
nrg_project     = 'nmrrestrntsgrid'
nrg_dir         = os.path.join(WS,nrg_project)                  # For NRG project code.
pdbbase_dir     = os.path.join(UJ,'wattosTestingPlatform','pdb')     # For PDB and mmCIF formatted entries data. @UnusedVariable
scripts_dir     = os.path.join(nrg_dir,'scripts')
wcf_dir         = os.path.join(scripts_dir,'wcf') #@UnusedVariable
divDir          = os.path.join(pdbbase_dir,'data/structures/divided')

PDBZ2           = os.path.join(divDir,'pdb')
CIFZ2           = os.path.join(divDir,'mmCIF')
PDBNMR2         = os.path.join(divDir,'nmr_restraints')

results_base = 'NRG-CING'
results_dir  = os.path.join('/Library/WebServer/Documents', results_base)
big_dir      = results_dir                           # NRG data large in size.
dir_star     = os.path.join(big_dir,'star')
dir_link     = os.path.join(big_dir,'link')

try:
    from localConstants import * #@UnusedWildImport
except:
    pass