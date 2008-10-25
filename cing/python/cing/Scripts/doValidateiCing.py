#==================================================
# some variables
#==================================================
from cing.Libs.NTutils import NTerror, NTmessage

# Run and parse/Only parse the results
parseOnly = False
# Do/do not generate images
htmlOnly  = True
doProcheck = False
doWhatif = False

project = project #@UndefinedVariable for Pydev extensions.
options = options #@UndefinedVariable
#==================================================
# Check for molecule
#==================================================
if project.molecule == None: 
    NTerror('script doValidate.py: no molecule defined')
    exit(1)
#end if
#==================================================
# Run the tests
#==================================================
project.runShiftx()
project.runDssp(parseOnly=parseOnly)
if doProcheck:
    project.runProcheck(ranges=options.ranges, parseOnly=parseOnly)

if doWhatif:
    project.runWhatif(parseOnly=parseOnly)
project.runCingChecks(ranges=options.ranges)
#==================================================
# Initialize the HTML
#==================================================
project.setupHtml()

#==================================================
# Use code can go here
#==================================================



#==================================================
# Generate CING html code
#==================================================
project.generateHtml(htmlOnly = htmlOnly)

NTmessage("Done with overall validation")

