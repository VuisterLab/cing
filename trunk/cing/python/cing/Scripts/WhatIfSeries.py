from cing import cingDirTestsTmp
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import SetupError
from cing.PluginCode.Whatif import runWhatif
from cing.core.classes import Project
import os

"""
Usage: define the set of files below and the atom nomenclature of the input
then run as: "python WhatIfSeries.py"
Paths have to be relative to cingDirTestsTmp
"""

fileSet = [ 
#            "NCX_pdb_files/after/H2_AD_Ca_28.pdb",
#            "NCX_pdb_files/after/H2_AD_EDTA_37.pdb",
#            "NCX_pdb_files/after/H2_BD_35.pdb",
#            "NCX_pdb_files/before/H2_AD_EDTA_28.pdb",
#            "NCX_pdb_files/before/H2_BD_27.pdb",
            "NCX_pdb_files/before/H2_Ca_17.pdb",
            ]
pdbFileAtomNomenclatureConvention = "CYANA2"


# NO CHANGES BELOW THIS LINE
###############################################################################
if os.chdir(cingDirTestsTmp):
    raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)

for pdbFilePath in fileSet:
    pdbFileName = os.path.split(os.path.abspath(pdbFilePath))[0]
    dummy_dir,entryId,dummy_ext = NTpath( pdbFilePath )
    project = Project.open( entryId, status='new' )
    project.initPDB( pdbFile=pdbFilePath, convention = pdbFileAtomNomenclatureConvention )
    status = runWhatif(project)
