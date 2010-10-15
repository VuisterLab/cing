"""
Unit test execute as:
python -u $CINGROOT/python/cing/Scripts/test/testiCingRobot.py
"""
from cing import cingDirTestsData #@UnusedImport
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Scripts.iCingRobot import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testvCingMaster(self):
        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
#        url = 'http://restraintsgrid.bmrb.wisc.edu/servlet_data/NRG_ccpn_tmp'
    #    NTwarning("Expect errors without a server up and running.")
        NTmessage("Querying the vCingMaster; aka token server for vCingSlave")

        ## queries possible; do one at a time going down the list.
        ## After the run is started the status will let you know if the run is finished
        ## The log will show what the server is doing at any one time.
#        doSave  = 0 # Upload to iCing and show derived urls
        doRun   = 0 # Start the run in Nijmegen
        doStatus= 1 # Find out if the run finished
        doLog   = 0 # Get the next piece of log file (may be empty)
        doPname = 0 # Get the project name back. This is the entryId below.
        doPurge = 0 # Remove data from server again.

        # User id should be a short id (<without any special chars.)
    #    user_id = os.getenv("USER", "UnknownUser")
        user_id = "vCingSlave"
        access_key = "iLoveVc"
#        access_key = getRandomKey() # Use a different one in a production setup.

#        entryId = '1brv' # 68K, smallest for quick testing.
    #    entryId = 'gb1' # only included in xplor variant as single model.

        # Select one of the types by uncommenting it
#        inputFileType = 'CCPN'
    #    inputFileType = 'PDB'
    #    inputFileType = 'XPLOR'

#        ccpnFile = os.path.join(cingDirTestsData, "ccpn", entryId + ".tgz")
#        pdbFile = os.path.join(cingDirTestsData, "pdb", entryId, 'pdb' + entryId + ".ent")
#        xplorFile = os.path.join(cingDirTestsData, "xplor", entryId, entryId + ".pdb")

#        inputFile = ccpnFile
#        if inputFileType == 'PDB':
#            inputFile = pdbFile
#        elif inputFileType == 'XPLOR':
#            inputFile = xplorFile


    #    rpcUrl=DEFAULT_URL+"icing/serv/iCingServlet"
        rpcUrl=DEFAULT_URL+DEFAULT_RPC_PORT+'/'+DEFAULT_URL_PATH+"/serv/vCingMasterServlet"
        NTdebug("Using rpc at: %s" % rpcUrl )
        credentials = [(FORM_USER_ID, user_id), (FORM_ACCESS_KEY, access_key)]
        NTdebug("With credentials: %s" % credentials )

    ##############################################################################################################

    ##############################################################################################################
        files = None

        if doRun:
            data = credentials + [(FORM_ACTION,FORM_ACTION_RUN),]
            print  sendRequest(rpcUrl, data, files)

        if doStatus:
            data = credentials + [(FORM_ACTION,FORM_ACTION_STATUS),]
            print  sendRequest(rpcUrl, data, files)

        if doLog:
            data = credentials + [(FORM_ACTION,FORM_ACTION_LOG),]
            print  sendRequest(rpcUrl, data, files)

        if doPname:
            data = credentials + [(FORM_ACTION,FORM_ACTION_PROJECT_NAME),]
            print  sendRequest(rpcUrl, data, files)

        if doPurge:
            data = credentials + [(FORM_ACTION,FORM_ACTION_PURGE),]
            print  sendRequest(rpcUrl, data, files)

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
