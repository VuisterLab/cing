from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage

# Run and parse/Only parse the results
parseOnly = False

fastestTest = False

htmlOnly = False # default is False but enable it for faster runs without some actual data.
doWhatif = True # disables whatif actual run
doProcheck = True
if fastestTest:
    htmlOnly = True 
    doWhatif = False
    doProcheck = False

project = project #@UndefinedVariable for Pydev extensions.
options = options #@UndefinedVariable


if options.noImagery:
    NTmessage( "Setting to htmlOnly because noImagery option was set." )
    htmlOnly = True
else:
    NTdebug( "noImagery option was not found." )
    
#==================================================
# Check for molecule
#==================================================
if project.molecule == None: 
    NTerror('script doValidate.py: no molecule defined')
    exit(1)
#end if

## TODO: disable after done debugging.
exit(0)
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

