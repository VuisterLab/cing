'''
Created on Oct 20, 2010
'''

from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Scripts.vCing.vCing import Vcing
from unittest import TestCase
import unittest

max_time_to_wait = 365 * 24 * 60 * 60 # a year in seconds
time_sleep_when_no_token = 1 * 1 * 5 * 60 # 5 minutes
lockTimeOut = 1 * 1 * 5 * 60 # 5 minutes

vc = Vcing()

class AllChecks(TestCase):
    # important to switch to temp space before starting to generate files for the project.
    cingDirTmpTest = os.path.join( cingDirTmp, 'testToposCmd' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def _testAll(self): ###  TODO: fails in current setup.
#        exitCode, token, tokenLock = vcMaster.nextTokenWithLock(lockTimeOut)
#        if exitCode:
#            nTdebug("Failed to vcMaster.nextTokenWithLock(). Was the token deleted?")
#        nTdebug("Got exitCode, token, tokenLock: %s %s %s" % (exitCode, token, tokenLock))
#        vcMaster.toposCmd.token = token
#        pid = p.process_fork( vcMaster.refreshLock, [tokenLock, lockTimeOut] )
#        nTdebug("create a background process [%s] keeping the lock" % pid)
#        time.sleep(sleepTimeSimulatingWork)
#        nTdebug("get_num_tokens:")
#        vc.toposCmd.get_num_tokens()
#        nTdebug("get_token:")
#        vc.toposCmd.get_token()

#        vcMaster.toposCmd.token = token
#        vcMaster.toposCmd.remove_token()

#        p.process_kill( pid )
        pass

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
