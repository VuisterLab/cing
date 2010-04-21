from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage

# Run and parse/Only parse the results
parseOnly = False
# Do/do not generate images
htmlOnly  = False

project = project #@UndefinedVariable for Pydev extensions.
options = options #@UndefinedVariable
#==================================================
# Check for molecule
#==================================================
if project.molecule == None:
    NTerror('script doValidate.py: no molecule defined')
    exit(1)
#end if

project.validate( parseOnly=parseOnly, htmlOnly=htmlOnly)

NTmessage("Done with overall validation")

