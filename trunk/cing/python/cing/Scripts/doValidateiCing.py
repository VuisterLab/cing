"""
Executed from iCingServlet.java#processRun:
String cing_options = "--name " + projectName + " --script doValidateiCing.py " + possibleInit;
"""
from cing.Libs.NTutils import * #@UnusedWildImport

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

# pylint: disable=E0601
project = project #@UndefinedVariable for Pydev extensions.
# pylint: disable=E0601
options = options #@UndefinedVariable

#==================================================
# Check for molecule
#==================================================
if project.molecule == None:
    nTerror('script doValidateiCing.py: no molecule defined')
    exit(1)
#end if

project.validate( ranges=options.ranges, parseOnly=parseOnly,  htmlOnly=htmlOnly,
                  doProcheck = doProcheck, doWhatif=doWhatif, doWattos=doWattos, doTalos=doTalos)

nTmessage("Done with overall validation")

