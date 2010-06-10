from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Whatif import runWhatif
from cing.core.classes import Project

"""
Usage: define the set of files below and the atom nomenclature of the input
then run as: "python WhatIfSeries.py"
Paths have to be relative to cingDirTmp
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
if os.chdir(cingDirTmp):
    raise SetupError("Failed to change to directory for temporary test files: "+cingDirTmp)

for pdbFilePath in fileSet:
    pdbFileName = os.path.split(os.path.abspath(pdbFilePath))[0]
    _dir,entryId,_ext = NTpath( pdbFilePath )
    project = Project.open( entryId, status='new' )
    project.initPDB( pdbFile=pdbFilePath, convention = pdbFileAtomNomenclatureConvention )
    status = runWhatif(project)
