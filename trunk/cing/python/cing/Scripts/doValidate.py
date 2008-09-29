#==================================================
# some variables
#==================================================

# Run and parse/Only parse the results
parseOnly = False
# Do/do not generate images
htmlOnly  = False

#==================================================
# Check for molecule
#==================================================
if project.molecule == None:
    cing.NTerror('script doValidate.py: no molecule defined')
    exit(1)
#end if
#==================================================
# Run the tests
#==================================================
project.runShiftx()
project.runDssp(parseOnly=parseOnly)
project.runProcheck(ranges=options.ranges, parseOnly=parseOnly)
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

