from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing.core.classes import Project
from cing.Libs.NTutils import printDebug
from cing.core.constants import CYANA
import os

entryId = "2hgh" # Small much studied PDB NMR entry 
pdbFileName = entryId+"_small.pdb"
pdbFilePath = os.path.join( cingDirTestsData, pdbFileName)
os.chdir(cingDirTestsTmp)
# does it matter to import it just now?
project = Project.open( entryId, status='new' )
project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )
printDebug("Reading files from directory: " + cingDirTestsData)
project.cyana2cing(cyanaDirectory=cingDirTestsData, convention=CYANA,
            uplFiles  = [ entryId ],
            acoFiles  = [ entryId],
            copy2sources = True
)
project.validate()
#        project.save( )
