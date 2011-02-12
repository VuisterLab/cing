# Execute like:
# python -u $CINGROOT/python/cing/Libs/test/test_Forkoff.py
# In order to test killing capabilities try (replacing 9999 by pid):
# kill -2 9999 (twice)
from cing import cingDirTmp
from cing import header
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import * #@UnusedWildImport
from cing.main import getStartMessage
from cing.main import getStopMessage
from unittest import TestCase
import unittest

def my_sleep(arg):
    ## Check types
    if type(arg) == types.TupleType:
        NTerror("Type of args [%s] is tuple" % arg)
        NTerror("This can happen when supplied with more than 1 argument")
        return 1

    ## Take first argument
    NTmessage("Sleeping for %s", arg)
    time.sleep (arg)
    NTmessage("Going back to caller")
    return 0

class AllChecks(TestCase):

    def ttttestRun(self):
        # important to switch to temp space before starting to generate files for the project.
        os.chdir(cingDirTmp)
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
        NTmessage("Finished ids: %s", done_list)

    def ttttttttttestRun2(self):
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
        NTmessage("Finished ids: %s", done_list)


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    NTmessage(header)
    NTmessage(getStartMessage())
    try:
        unittest.main()
    finally:
        NTmessage(getStopMessage(cing.starttime))

