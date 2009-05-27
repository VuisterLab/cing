# Executed from iCingServlet.java#processRun:
# String cing_options = "--name " + projectName + " --script doValidateiCing.py " + possibleInit;
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage

# Run and parse/Only parse the results
parseOnly = False

fastestTest = False

htmlOnly = False # default is False but enable it for faster runs without some actual data.
doWhatif = True # disables whatif actual run
doProcheck = True
doWattos = True
if fastestTest:
    htmlOnly = True
    doWhatif = False
    doProcheck = False
    doWattos = False

project = project #@UndefinedVariable for Pydev extensions.
options = options #@UndefinedVariable


#if options.noImagery:
#    NTmessage( "Setting to htmlOnly because noImagery option was set." )
#    htmlOnly = True
#else:
#    NTdebug( "noImagery option was not set so doing all images." )

#==================================================
# Check for molecule
#==================================================
if project.molecule == None:
    NTerror('script doValidate.py: no molecule defined')
    exit(1)
#end if

## TODO: disable after done debugging.
#exit(0)

# KEEP THIS BLOCK SYNC-ED or unify WITH THE FOLLOWING FILES:
# python/cing/Scripts/doValidate.py
# python/cing/Scripts/doValidateiCing.py
# python/cing/PluginCod/validate.py#validate
#project.runShiftx()
#project.runDssp(parseOnly=parseOnly)
#if doProcheck:
#    project.runProcheck(ranges=options.ranges, parseOnly=parseOnly)
#if doWhatif:
#    project.runWhatif(parseOnly=parseOnly)
#project.runWattos()
#project.runCingChecks(ranges=options.ranges)
#project.setupHtml()
#project.generateHtml(htmlOnly = htmlOnly)

# Moved to:
project.validate( ranges=options.ranges, parseOnly=parseOnly,  htmlOnly=htmlOnly,
                  doProcheck = doProcheck, doWhatif=doWhatif, doWattos=doWattos)

NTmessage("Done with overall validation")

