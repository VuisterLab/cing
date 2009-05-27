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


# KEEP THIS BLOCK SYNC-ED or unify WITH THE FOLLOWING FILES:
# python/cing/Scripts/doValidate.py
# python/cing/Scripts/doValidateiCing.py
# python/cing/PluginCod/validate.py#validate
#project.runShiftx(parseOnly=parseOnly)
#project.runDssp(parseOnly=parseOnly)
#project.runWhatif(parseOnly=parseOnly)
#project.runProcheck(ranges=options.ranges, parseOnly=parseOnly)
#project.runWattos()
#project.runCingChecks(ranges=options.ranges)
#project.setupHtml()
#project.generateHtml(htmlOnly = htmlOnly)

# Moved to:
project.validate( parseOnly=parseOnly, htmlOnly=htmlOnly)

NTmessage("Done with overall validation")

