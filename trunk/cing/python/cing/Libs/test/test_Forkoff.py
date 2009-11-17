from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.forkoff import ForkOff
from cing.Libs.forkoff import do_cmd
from unittest import TestCase
import cing
import os
import time
import types
import unittest

def my_sleep( arg ):
    ## Check types
    if type(arg) == types.TupleType:
        NTerror("Type of args [%s] is tuple" % arg)
        NTerror("This can happen when supplied with more than 1 argument")
        return 1

    ## Take first argument
    NTmessage("Sleeping for %s", arg)
    time.sleep ( arg )
    NTmessage("Going back to caller")
    return 0

class AllChecks(TestCase):

    def tttestRun(self):
        # important to switch to temp space before starting to generate files for the project.
        os.chdir(cingDirTmp)
        ## Test takes 5 seconds to run.
        ## Initializing f will also initialize an instance of class Process
        ## Can be interrupted by doing kill -2 pid which will be caught and dealt with.
        f = ForkOff(
                processes_max       = 3,
                max_time_to_wait    = 5,
                verbosity           = 2
                )

        ## Sleep long
        job_0       = ( my_sleep, (9999,) )
        ## Sleep
        job_1       = ( my_sleep, (3.1,) )
        ## Sleep short
        job_2       = ( my_sleep, (1.2,) )
        job_list    = [ job_0, job_1, job_2 ]

        done_list   = f.forkoff_start( job_list, 0 )
        NTmessage("Finished ids: %s", done_list)

    def ttttttttttestRun2(self):
        ## Initializing f will also initialize an instance of class Process
        ## Can be interrupted by doing kill -2 pid which will be caught and dealt with.
        f = ForkOff(
                processes_max       = 3,
                max_time_to_wait    = 10,
                verbosity           = 2
                )

        ## Sleep long
#        job_1       = ( do_cmd, ('date',) )
#        job_2       = ( do_cmd, ('echo "hello world"',) )
        job_3       = ( do_cmd, ('echo "hello world two"   > helloWorld2.txt',) )
#        job_4       = ( do_cmd, ('ls helloWorld3xxx > helloWorld3.txt 2>&1 ',) )
        # disabled jobs because it will show up when unit testing and we don't want that.
#        job_4 = job_0
        job_list    = [ job_3 ]

        done_list   = f.forkoff_start( job_list, 0 )
        NTmessage("Finished ids: %s", done_list)


if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
