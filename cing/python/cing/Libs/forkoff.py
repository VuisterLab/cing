"""
Useful for starting multiple independent processes given a function and list
of arguments when the process might hang or crash and leave zombies around.
Convenient clean up provided. See test code for examples. Only runs on systems
supporting os.fork() call; Unix.

kill -2 PID (sending a INT (interrupt) to this parent python process)
will signal the parent to not start any more subprocesses but finish nicely
otherwise.


Author: Jurgen F. Doreleijers, BMRB, September 2001
"""
from cing.Libs.NTutils import * #@UnusedWildImport
import signal
import types

__author__    = "$Author$"
___revision__ = "$Revision$"
___date__     = "$Date$"


def do_cmd( cmd ):
    """
    Returns False for success.
    """
    NTmessage( "Doing command: %s" % cmd )

    ##  Try command and check for non-zero exit status
#    pipe = os.popen( cmd )
    pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
    output = pipe.read()

    ##  The program exit status is available by the following construct
    ##  The status will be the exit number unless the program executed
    ##  successfully in which case it will be None.
    status = pipe.close()

    if output:
        NTmessage( output )

    ## Success
    if status == None:
        return

    NTerror("Failed shell command:")
    NTerror( cmd )
    NTerror("Output: %s" % output)
    NTerror("Status: %s" % status)
    return True
# end def

def get_cmd_output( cmd ):
#    NTdebug( "Doing command: %s" % cmd )

    ##  Try command and check for non-zero exit status
#    pipe = os.popen( cmd )
    pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
    output = pipe.read()

    ##  The program exit status is available by the following construct
    ##  The status will be the exit number unless the program executed
    ##  successfully in which case it will be None.
    status = pipe.close()

    ## Success
    if ( status != None ):
        NTerror("Failed shell command:")
        NTerror( cmd )
        NTerror("Output: %s" % output)
        NTerror("Status: %s" % status)
    return output

class ForkOff:

    def __init__( self,
            ## Number of processes that will be spawned/forked off. This could
            ## usually be set to the number of processors
            processes_max               = 1,
            ## Time in seconds a single function may take to complete execution
            ## and return.
            max_time_to_wait            = 60,
            ## After a killing signal how long do we wait for it to die, and
            ## perhaps try killing it again.
            max_time_to_wait_kill       = 5,
            ## Time to wait in parent by sleeping if no process finished
            time_to_wait                = 1,
            ## Verbosity of output
            verbosity                   = 2
            ):

        ## Parallel processing options:
        ## Maximum number of simultanuous subprocesses
        self.processes_max          = processes_max
        ## Currently open subprocesses
        self.processes_open         = 0
        ## Total number of started subprocesses
        self.processes_started      = 0
        ## Total number of finished subprocesses
        self.processes_finished     = 0
        ## Total number of subprocesses to be done if all scheduled to be done
        ## are indeed to be done. This is set later on and perhaps adjusted
        ## when the user interrupts the process by ctrl-c.
        self.processes_todo         = 0
        ## List of jobs fids that were done correctly (jobs are numbered as in
        ## array (0..n-1)
        self.done_jobs_list         = []
        ## Dictionary with pid:fid info on running subprocesses
        ## fid is forkoff id.
        self.process_d              = {}
        ## Dictionary with pid:seconds info on running subprocesses
        self.process_t              = {}
        ## Maximume number of seconds to wait for a subprocesses
        self.max_time_to_wait       = max_time_to_wait
        ## See above
        self.time_to_wait           = time_to_wait
        ## See above
        self.verbosity              = verbosity
        ## Use methods provided by Process class
        ## Maximume number of seconds to wait after killing a subprocesses
        self.max_time_to_wait_kill  = max_time_to_wait_kill

        ## Initialize an instance of the Process class
        self.p                      = Process(
            max_time_to_wait_kill   = self.max_time_to_wait_kill,
            verbosity               = self.verbosity
            )

    """
    Main loop
    job_list should be of a list of tuples. The tuple should contain
    a function and a tuple with one or more arguments.
    E.g. [( my_sleep, (990.1,) ), ( my_sleep, (990.1,) )]
    Returns a list of ids of processes (id is the index of the job in the list
    of jobs) that were done AND done successfully.
    Empty lists will be returned if nothing gets done successfully or an error occurs.
    """
    def forkoff_start( self, job_list, delay_between_submitting_jobs=5 ):

        if self.processes_max == None or self.processes_max < 1: # double but just to be clear.
            NTerror("Can't do jobs without having processes_max; processes_max: %s" % self.processes_max )
            return []

        ## Check job list for variable type errors
        for job in job_list:
            func = job[0]
            args = job[1]
            if type(args) != types.TupleType:
                NTerror("given argument not of type Tuple for job: %s", job)
                return []
            if not ( type(func) == types.FunctionType or
                     type(func) == types.BuiltinFunctionType or
                     type(func) == types.MethodType ) :
                NTerror("given function not of types:")
                NTmessage("(Function, BuiltinFunctionType, or MethodType) for job:")
                print job
                NTmessage("In stead type is : %s", type(func))
                return []

        ## Maximum number of processes to do
        self.processes_todo = len( job_list )
        if self.processes_todo == 0:
            if self.verbosity:
                NTwarning("No new processes to do so none to start")
            return []

        if self.verbosity > 1:
            NTmessage("Doing %s new process(es)" % self.processes_todo)

        ## Keep making processes until an uncaught Exception occurs
        ## That would be a ctrl-c or so. The ctrl-c is also caught by
        ## subprocesses within python at least.
        ## I have not found a way to use this mechanism for jobs
        ## running in the background of a now killed terminal.
        ## When I read up, I got indications that the signal handlers
        ## for INTerrupt and QUIT might be rerouted and not available
        ## anymore. A hard kill is then needed.
        ##
        try:
            self.do_jobs( job_list, delay_between_submitting_jobs )
        except KeyboardInterrupt:
            if self.verbosity:
                NTwarning("Caught interrupt in parent.")
                NTwarning("Trying to finish up by waiting for subprocess(es)")

        ## Finish waiting for subprocesses
        ## Don't make any new!
        self.processes_todo = self.processes_started
        try:
            self.do_jobs( job_list, delay_between_submitting_jobs )
        except KeyboardInterrupt:
            if self.verbosity:
                NTwarning("Again caught interrupt in parent. Will start to kill running jobs.")
                if self.hard_kill_started_jobs():
                    NTerror("Failed hard killing running jobs")
            raise KeyboardInterrupt

        ## Any subprocesses left
        if self.process_d:
            key_list = self.process_d.keys()
            key_list.sort()
            for pid in key_list:
                NTerror("subprocesses with fid [%s] was left behind with pid [%d]" \
                      % ( self.process_d[ pid ], pid ))

        ## Check all were done
        if self.processes_finished != len( job_list ):
            if self.verbosity > 1:
                NTwarning("only %s out of %s jobs were started (not all successfully finished perhaps)" \
                      % ( self.processes_finished, len( job_list ) ))

        ## Check if all finished correctly
        if self.processes_finished != self.processes_started:
            str = "ERROR: Number of processes finished and started do not match"
            str += `self.processes_finished` + " " + `self.processes_started`
            raise str

        if self.verbosity > 1:
            NTmessage("Finished %s out of the %s processes successfully" \
                  % ( len( self.done_jobs_list), self.processes_todo ))

        ## List of job numbers that were done.
        return self.done_jobs_list

    def hard_kill_started_jobs( self ):
        """
        Kill kill kill
        """
        keys = self.process_t.keys()
        NTmessage("Killing jobs: %s" % str(keys))
        ## Check to see if time's done for any
        for pid in keys:
            ## Pop pid/args from dictionary
            fid = self.process_d[ pid ]
            del self.process_d[ pid ]
            del self.process_t[ pid ]
            self.processes_open     -= 1
            self.processes_finished += 1
            if self.verbosity:
                NTwarning("Process pid [%s] and fid [%s] will be killed" % (pid, fid))
                NTwarning("Process is not considered done")
            _exit_pid, _exit_status = self.p.process_kill( pid )
        # end for
    # end def

    def do_jobs( self, job_list, delay_between_submitting_jobs ):
        """
        Starting independent processes given a list of function with
        list of arguments.

        Return True on error.
        """

        if self.processes_max == None or self.processes_max < 1: # double but just to be clear.
            NTerror("Can't do jobs without having processes_max; processes_max: %s" % self.processes_max )
            return True

        while ( self.processes_started  < self.processes_todo or
                self.processes_open     > 0 ):
            sys.stdout.flush()
            sys.stderr.flush()
            ## Start new or wait for old process
            if ( self.processes_open    < self.processes_max  and
                 self.processes_started < self.processes_todo ):
                func = job_list[ self.processes_started ][0]
                args = job_list[ self.processes_started ][1]
                self.processes_open     += 1
                self.processes_started  += 1
                pid = self.p.process_fork( func, args )
#                NTmessage("Process with pid [%s] exited with status [%s]" % \

                ## Push pid/fid onto dictionary of things running
                self.process_d[ pid ] = self.processes_started - 1
                self.process_t[ pid ] = time.time()
                time.sleep(delay_between_submitting_jobs)
            elif self.processes_open:
                keys = self.process_d.keys()
                for pid in keys:
                    exit_pid, exit_status = self.p.process_wait( pid, os.WNOHANG )
                    if exit_pid:
                        if self.verbosity > 3:
                            NTmessage("Process with pid [%s] exited with status [%s]" % \
                              (exit_pid, exit_status))
                        ## Pop pid/args from dictionary
                        fid = self.process_d[ exit_pid ]
                        del self.process_d[ exit_pid ]
                        del self.process_t[ exit_pid ]
                        self.processes_open     -= 1
                        self.processes_finished += 1
                        ## Only consider things done if done correctly
                        if exit_status:
                            if self.verbosity:
                                NTwarning("Process with fid: [%s] considered NOT done" % fid)
                        else:
                            if self.verbosity > 3:
                                NTmessage("Process with fid: [%s] considered done" % fid)
                            self.done_jobs_list.append( fid )
                ## Give the cpu 1 second rest in between the checks
                ## if no process has exited
                time.sleep ( self.time_to_wait )

            ## Check to see if time's done for any
            keys = self.process_t.keys()
            for pid in (keys):
                if ( time.time() - self.process_t[ pid ] >
                     self.max_time_to_wait ):
                    ## Pop pid/args from dictionary
                    fid = self.process_d[ pid ]
                    del self.process_d[ pid ]
                    del self.process_t[ pid ]
                    self.processes_open     -= 1
                    self.processes_finished += 1
                    if self.verbosity:
                        NTwarning("Process with fid [%s] was not done within time limits" % fid)
                        NTwarning("Process is not considered done")
                    _exit_pid, _exit_status = self.p.process_kill( pid )
                    ## If a process needed to be killed then
                    ## don't check for others in this iteration.
                    ## This is to prevent processes being killed that might
                    ## already be finished but didn't get a chance to be reaped
                    ## because the process_kill takes quite some time.
                    break




class Process:
    """
    Class for process oriented functions used by ForkOff.
    """

    def __init__( self,
            ## After sending a killing signal how long do we wait for it to die (and perhaps
            ## try killing it again.
            max_time_to_wait_kill       = 5,
            ## Time to wait in parent by sleeping if no process finished
            verbosity                   = 2
            ):

        ## Maximum number of seconds to wait after killing a subprocesses
        self.max_time_to_wait_kill  = max_time_to_wait_kill

        ## See ForkOff class
        self.verbosity              = verbosity

        ## Number for the exit status as returned by pipe.close() normally
        ## corresponding to exit status 1
        self.exit_status_failure    = 256


    def process_fork( self, function, arguments ):

        pid = os.fork()

        if pid:
            ## Parent here
            if self.verbosity > 3:
                NTmessage("Forked an independent process with pid: %s" % pid)
            return pid

        if pid == None:
            NTerror("pid is None after fork, unknown error to coder")
            NTerror("child returns")
            return pid

        ## Subprocess here
        ## Define exit status is an error for child if not changed
        exit_status = 1

        if pid != 0:
            str = "ERROR: code error in Fork, process_start, pid =" + `os.getpid()`
            raise str
        if self.verbosity > 2:
            NTmessage("Starting subprocess with pid: %s" % os.getpid())
#        if self.verbosity > 8:
#            NTdebug("Setting gpid from [%s] to current pid" % os.getpgrp())

        os.setpgid(0,0)
#        if self.verbosity > 8:
#            NTdebug("After setgpid: Current gpid: [%s], pid: [%s]" % (
#                os.getpgrp(), os.getpid() ))

        try:
            exit_status = apply( function, arguments )
        except KeyboardInterrupt:
            if self.verbosity:
                NTwarning("Caught KeyboardInterrupt in subprocess, subprocess will exit(1)")
            os._exit(1)
##        except:
##            NTerror("Caught exception other than KeyboardInterrupt, subprocess will exit(1)"
##            os._exit(1)

        if exit_status:
            if self.verbosity > 1:
                NTmessage("Subprocess will do error exit with exit code 1")
            os._exit(1)
        else:
            if self.verbosity > 2:
                NTdebug("Subprocess will do normal exit with exit code 0")
            os._exit(0)



    def process_wait( self, pid=0, options=0 ):
#        if self.verbosity > 8:
#            NTdebug("Wait for process: [%s] with options: [%s] " % ( pid, options ))

        ## Indicating failure
        exit_pid, exit_status = 0, self.exit_status_failure

        if os.getpid() == pid:
            if self.verbosity:
                NTwarning("given pid is for current process, giving up")
            return exit_pid, exit_status

        try:
            exit_pid, exit_status = os.waitpid(pid, options)
        except OSError, info:
            if self.verbosity:
                NTwarning("caught an OSError with info: %s" % info)

        return exit_pid, exit_status


    def process_signal( self, pid, sig ):
        if self.verbosity > 1:
            NTmessage("Signal process: [%s] with signal [%s]" % ( pid, sig ))
        if os.getpid() == pid:
            if self.verbosity:
                NTwarning("given pid is for current process, giving up")
            return 1

        try:
            os.kill( pid, sig )
        except OSError, info:
            if self.verbosity:
                NTwarning("caught an OSError with info: %s" % info)
            return 0


    def process_kill( self, pid ):
        if self.verbosity > 1:
            NTmessage("Signaling process: [%s] for a kill" % pid)
        if os.getpid() == pid:
            if self.verbosity:
                NTwarning("given pid is for current process, giving up")
            return 0, self.exit_status_failure

        if self.verbosity > 2:
            NTmessage("Process and subprocesses will be signaled by a TERM signal")
        ## On my linux box urchin:
        ## HUP  1    TERM 15
        ## INT  2    KILL  9
        ## Please note that the minus sign in front of the pid which tells kill to
        ## kill all processes with that pid for its **group process id**
        ## Took 2 days to figure out...
        self.process_signal( -pid, signal.SIGTERM )
        if self.verbosity > 2:
            NTmessage("Sleeping %s" % self.max_time_to_wait_kill)
        time.sleep(self.max_time_to_wait_kill)
        exit_pid, exit_status = self.process_wait( pid, os.WNOHANG )
        if exit_pid:
            if self.verbosity > 1:
                NTmessage("Process with pid [%s] was killed by TERM signal" % exit_pid)
        else:
            if self.verbosity > 2:
                NTmessage("Process was not killed, now it will be signaled a KILL signal")
            self.process_signal( -pid, signal.SIGKILL )
            if self.verbosity > 2:
                NTdebug("Sleeping %s" % self.max_time_to_wait_kill)
            time.sleep(self.max_time_to_wait_kill)
            exit_pid, exit_status = self.process_wait( pid, os.WNOHANG )
            if exit_pid > 1:
                NTmessage("Process with pid [%s] was killed by KILL signal" % exit_pid)
            else:
                NTerror("  Process could NOT be killed by HUP or KILL signal")
                NTerror("  Process has turned into zombie")
        if self.verbosity >= 9:
            NTmessage("Got exit_pid, exit_status: %s, %s" % (exit_pid, exit_status))

        return exit_pid, exit_status


