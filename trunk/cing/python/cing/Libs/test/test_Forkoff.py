# Execute like:
# python -u $CINGROOT/python/cing/Libs/test/test_Forkoff.py
# In order to test killing capabilities try (replacing 9999 by pid):
# kill -2 9999 (twice)
import cing
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import * #@UnusedWildImport
from unittest import TestCase
import unittest

def my_sleep(arg):
    ## Check types
    if type(arg) == types.TupleType:
        nTerror("Type of args [%s] is tuple" % arg)
        nTerror("This can happen when supplied with more than 1 argument")
        return 1

    ## Take first argument
    nTmessage("Sleeping for %s", arg)
    time.sleep(arg)
    nTmessage("Going back to caller")
    return 0

class AllChecks(TestCase):

    def _test_sleep(self):
        cmd = ''
        for i in range(2):
            cmd += 'echo %s; sleep 1; ' % i
        do_cmd(cmd, bufferedOutput=0)

    def _test_Forkoff(self):
        # important to switch to temp space before starting to generate files for the project.
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)
        ## Test takes 5 seconds to run.
        ## Initializing f will also initialize an instance of class Process
        ## Can be interrupted by doing kill -2 pid which will be caught and dealt with.
        f = ForkOff(
                processes_max=3,
                max_time_to_wait=5,
                verbosity=cing.verbosity
                )

        ## Sleep long
        job_0 = (my_sleep, (9999,))
        ## Sleep
        job_1 = (my_sleep, (3.1,))
        ## Sleep short
        job_2 = (my_sleep, (1.2,))
        job_list = [ job_0, job_1, job_2 ]

        done_list = f.forkoff_start(job_list, 0)
        nTmessage("Finished ids: %s", done_list)

    def _testRun2(self):
        ## Initializing f will also initialize an instance of class Process
        ## Can be interrupted by doing kill -2 pid which will be caught and dealt with.
        f = ForkOff(
                processes_max=3,
                max_time_to_wait=10,
                verbosity=2
                )

        ## Sleep long
#        job_1       = ( do_cmd, ('date',) )
#        job_2       = ( do_cmd, ('echo "hello world"',) )
        job_3 = (do_cmd, ('echo "hello world two"   > helloWorld2.txt',))
#        job_4       = ( do_cmd, ('ls helloWorld3xxx > helloWorld3.txt 2>&1 ',) )
        # disabled jobs because it will show up when unit testing and we don't want that.
#        job_4 = job_0
        job_list = [ job_3 ]

        done_list = f.forkoff_start(job_list, 0)
        nTmessage("Finished ids: %s", done_list)


if __name__ == "__main__":
    cing.verbosity = cing.constants.verbosity.debug
    nTmessage(cing.constants.definitions.cingDefinitions.getHeaderString())
    nTmessage(cing.constants.definitions.systemDefinitions.getStopMessage())
    try:
        unittest.main()
    finally:
        nTmessage(cing.constants.definitions.systemDefinitions.getStopMessage())

