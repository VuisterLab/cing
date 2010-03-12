"""
Unit test execute as:
python $CINGROOT/python/cing/Scripts/cingProfile.py
"""
import cProfile
import pstats

def run():
    print "hello"
    import cing
    from cing.Libs.NTutils import NTdebug
    from cing import verbosityDebug
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