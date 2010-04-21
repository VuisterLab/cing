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
doTalos = True
if fastestTest:
    htmlOnly = True
    doWhatif = False
    doProcheck = False
    doWattos = False
    doTalos = False

project = project #@UndefinedVariable for Pydev extensions.
options = options #@UndefinedVariable

#==================================================
# Check for molecule
#==================================================
if project.molecule == None:
    NTerror('script doValidateiCing.py: no molecule defined')
    exit(1)
#end if

project.validate( ranges=options.ranges, parseOnly=parseOnly,  htmlOnly=htmlOnly,
                  doProcheck = doProcheck, doWhatif=doWhatif, doWattos=doWattos, doTalos=doTalos)

NTmessage("Done with overall validation")

