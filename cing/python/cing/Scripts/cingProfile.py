"""
Unit test execute as:
python $CINGROOT/python/cing/Scripts/cingProfile.py
"""
from cing.Libs.NTutils import * #@UnusedWildImport
import cProfile
import pstats

def run():
    print "hello"
    cing.verbosity = verbosityDebug
    NTdebug( "hello again" )

if True:
    # Commented out because profiling isn't part of unit testing.
    fn = 'fooprof'
    cProfile.run('run()', fn)
    p = pstats.Stats(fn)
    #p.sort_stats('time').print_stats(100)
    p.sort_stats('cumulative').print_stats(20)
else:
    run()