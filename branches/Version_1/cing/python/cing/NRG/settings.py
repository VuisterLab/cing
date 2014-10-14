"""
Settings for the NRG-CING

Test by:
python $CINGROOT/python/cing/NRG/settings.py
"""
from cing.Libs.NTutils import nTdebug
import os

PLOT_STR = 'plot'
PLOT_TREND_STR = 'plotTrend'
PPLOT_STR = 'pplot'
PPLOT_TREND_STR = 'pplotTrend'

# If on production machine then
# -1- the urls will differ from localhost to nmr.cmbi.ru.nl or so.
# -2- results base is tmpNRG-CING
# -3- db schema is tmpnrgcing

#: override for development in localConstants.py @UnusedVariable Disables some operations for need for speed.
isProduction        = 1 # DEFAULT: 1  @UnusedVariable
#: when assumed all are done. Disables some messaging in case not all are done.
assumeAllAreDone    = 1 # DEFAULT: 1  @UnusedVariable

UJ                  = '/Users/wim'
WS                  = os.path.join(UJ,'workspace')
dDir                = '/Library/WebServer/Documents'            # Web dir.
VCsecret            = 'a/b/c' # Overriden locally. @UnusedVariable Only used in publishVC.py

try:
    from cing.NRG.localConstants import * #@UnusedWildImport # pylint: disable=E0611
    nTdebug("NRG/settings: Loaded NRG localConstants.py.")
except:
    nTdebug("NRG/settings: Consider creating a localConstants.py file with a different 'user' location.")

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

# Url part of http://nmr.cmbi.ru.nl/NRG-CING
# Is also used to derived in validateEntry.py the archive id from the input dir.
results_base         = 'NRG-CING'
results_base_redo    = 'NMR_REDO'
results_base_recoord = 'RECOORD'
results_baseList = [ results_base, results_base_redo, results_base_recoord ]

#if not isProduction:
#    results_base    = 'dev' + results_base
results_dir     = os.path.join(dDir, results_base)
big_dir         = results_dir                           # NRG data large in size.
dir_star        = os.path.join(big_dir,'star')
dir_link        = os.path.join(big_dir,'link')

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

# Replace % b with BMRB id.
#           s with PDB id.
#           a with archive id.
bmrb_link_template = 'http://www.bmrb.wisc.edu/cgi-bin/explore.cgi?bmrbId=%b'
pdb_link_template  = 'http://www.rcsb.org/pdb/explore/explore.do?structureId=%s'
archive_link_template = 'http://nmr.cmbi.ru.nl/%a'

# Front page
entry_list_summary_file_name_base = 'entry_list_summary'
#rev_first becomes an image column
#summaryHeaderList = 'rev_first name bmrb_id rog distance_count cs_count chothia_class chain_count res_count'.split()
#summaryHeader2List = 'img. PDB BMRB ROG distances chem.s. Chothia chains residues'.split()
PDB_ID_IDX = 2
summaryHeaderList  = 'rev_first  name   pdb_id bmrb_id rog_str distance_count cs_count chothia_class_str chain_count res_count'.split()
summaryHeader2List = 'tgz        report PDB    BMRB    ROG     distances      chem.s.  Chothia           chains      residues'.split()
summaryHeaderTitleList = [
    'Complete NRG-CING report (click on icon to download)',
    'NRG-CING report (click on to go to NRG-CING report.)',
    'PDB entry code (click on to go to RCSB-PDB for original data.)',
    'BMRB entry code (click on to go to BMRB for original data.)',
    'CING Red Orange Green scores',
    'Number of distance restraints',
    'Number of chemical shifts',
    'Chothia definition for alpha,beta,alpha/beta,coil,None',
    'Number of chains including water',
    'Total number of residues'
]
