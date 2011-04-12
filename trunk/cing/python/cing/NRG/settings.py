"""
Settings for the NRG-CING

Test by:
python $CINGROOT/python/cing/NRG/settings.py
"""

from cing.Libs.NTutils import * #@UnusedWildImport

# If on production machine then
# -1- the urls will differ from localhost to nmr.cmbi.ru.nl or so.
# -2- results base is tmpNRG-CING
# -3- db schema is tmpnrgcing

isProduction = 1 # DEFAULT: 1 override for development in localConstants.py @UnusedVariable

UJ              = '/Users/wim'
WS              = os.path.join(UJ,'workspace')
dDir            = '/Library/WebServer/Documents'            # Web dir.

try:
    from localConstants import * #@UnusedWildImport
    NTdebug("Loaded NRG localConstants.py.")
except:
    NTdebug("Consider creating a localConstants.py file with a different 'user' location.")

platform_dir    = os.path.join(UJ,'wattosTestingPlatform')  # For BMRB, and PDB and mmCIF formatted entries data. @UnusedVariable
pdbbase_dir     = os.path.join(platform_dir,'pdb')          # For PDB and mmCIF formatted entries data. @UnusedVariable
baseDir         = os.path.join(UJ,'CASD-NMR-CING') #@UnusedVariable
baseCaspDir     = os.path.join(UJ, 'CASP-NMR-CING') #@UnusedVariable
nrg_project     = 'nmrrestrntsgrid'
nrg_dir         = os.path.join(WS,nrg_project)              # For NRG project code.

scripts_dir     = os.path.join(nrg_dir,'scripts')
wcf_dir         = os.path.join(scripts_dir,'wcf') #@UnusedVariable
divDir          = os.path.join(pdbbase_dir,'data/structures/divided')

PDBZ2           = os.path.join(divDir,'pdb')
CIFZ2           = os.path.join(divDir,'mmCIF')
PDBNMR2         = os.path.join(divDir,'nmr_restraints')


results_base    = 'NRG-CING'
#if not isProduction:
#    results_base    = 'dev' + results_base
results_dir     = os.path.join(dDir, results_base)
big_dir         = results_dir                           # NRG data large in size.
dir_star        = os.path.join(big_dir,'star')
dir_link        = os.path.join(big_dir,'link')
dir_plot        = os.path.join(big_dir,'plot')
dir_plotTrending= os.path.join(big_dir,'plotTrend')


dir_prep        = os.path.join(big_dir, 'prep')
dir_C           = os.path.join(dir_prep, 'C')
#dir_R           = os.path.join(dir_prep, 'R')
dir_S           = os.path.join(dir_prep, 'S')
dir_F           = os.path.join(dir_prep, 'F')
dir_vCing       = os.path.join(dir_prep, 'vCing')

bmrbbase_dir    = os.path.join(platform_dir,'bmrb')
#bmrbDir         = os.path.join(bmrbbase_dir,'ftp.bmrb.wisc.edu/pub/bmrb/entry_directories')
bmrbDir         = os.path.join(bmrbbase_dir,'rsync') # Switching to 3 later.
#bmrbDir         = os.path.join(bmrbbase_dir,'2.1.1') # Switching to 3 later.
#bmrbDir         = os.path.join(bmrbbase_dir,'3.0.8.34')
matchBmrbPdbDir = os.path.join(bmrbbase_dir,'matchBmrbPdb') # Switching to 3 later.
