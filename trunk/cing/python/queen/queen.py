#!/usr/bin/env python
#@PydevCodeAnalysisIgnore
"""
QUEEN   : QUantitative Evaluation of Experimental Nmr restraints

Author  : Sander Nabuurs & Geerten Vuister

E-mail  : s.nabuurs@cmbi.ru.nl or g.vuister@science.ru.nl

Homepage and servers: http://nmr.cmbi.ru.nl/QUEEN


When using QUEEN please cite:

  Sander B. Nabuurs, Chris A.E.M. Spronk, Elmar Krieger, Hans Maassen,
  Gert Vriend and Geerten W. Vuister (2003). Quantitative evaluation of
  experimental NMR restraints. J. Am. Chem. Soc. 125 (39), 12026-12034.

No warranty implied or expressed. All rights reserved.


"""
import sys,os

sys.path += [os.path.join(sys.path[0],'src/py'),
             os.path.join(sys.path[0],'src/c'),
             os.path.join(sys.path[0],'src/3rd-party')]

# DO IMPORTS
import optparse
from qn import *

programName         = 'QUEEN'
queenVersion        = 1.2

__version__         = queenVersion # for pydoc
__date__            = '9 April 2009'
__copyright_years__ = '2004-' + __date__.split()[-1] # Never have to update this again...

authorList          = [  ('Geerten W. Vuister',          'g.vuister@science.ru.nl'),
                         ('Jurgen F. Doreleijers',       'jurgend@cmbi.ru.nl'),
                         ('Sander Nabuurs',              's.nabuurs@cmbi.ru.nl'),
                      ]
__author__          = '' # for pydoc
for _a in authorList:
    __author__ = __author__ + _a[0] + ' (' + _a[1] + ')    '

__copyright__       = "Copyright (c) Protein Biophysics (IMM)/CMBI, Radboud University Nijmegen, The Netherlands"
__credits__         = """More info at http://nmr.cmbi.ru.nl/QUEEN

""" + __copyright__ # TODO: misusing credits for pydoc

versionStr = "%s" % queenVersion

header = """
======================================================================================================
| QUEEN: QUantitative Evaluation of Experimental Nmr restraints      Version %-10s   %-10s |
|                                                                                                    |
| %-98s |
======================================================================================================
""" % (versionStr, __copyright_years__, __copyright__)

# READ THE QUEEN CONFIGURATION FILE and adjust Q_PATH
nmvconf = dct_read(os.path.join(sys.path[0],'queen.conf'))
nmvconf["Q_PATH"] = os.path.abspath(os.sys.path[0])


if __name__ == '__main__':
    # CHECK PYTHON VERSION
    version = nmv_checkpython()

    # OPTION PARSER
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage,version=versionStr)

    parser.add_option("--project", dest="projectName", default=None,
                       help="name of the project (required, except in case of --example, --test, --pydoc)",
                       metavar="PROJECTNAME"
                     )
    parser.add_option("--cing",action="store_true",dest='cing', default=False,
                      help="defines PROJECTNAME to be a CING project")

    parser.add_option("--init",action="store_true",dest='init', default=None,
                      help="initialize QUEEN project PROJECTNAME")

    parser.add_option("--initCing",action="store_true",dest='initCing', default=False,
                      help="initialize from CING project PROJECTNAME (equivalent to --cing --init)")

    parser.add_option("--overwrite",action="store_true",dest='overwrite', default=False,
                      help="flag to overwrite existing project directory")

    parser.add_option("--pdb2seq",dest="pdb2seq",default=None,
                      help="generate sequence file from PDBFILE",
                      metavar="PDBFILE"
                     )
    parser.add_option("--seq2psf",dest="seq2psf",default=None,
                      help="generate psf file from SEQUENCEFILE",
                      metavar="SEQUENCEFILE"
                     )
    parser.add_option("--psf2tem",dest="psf2tem",default=None,
                      help="generate template file from PSFFILE",
                      metavar="PSFFILE"
                     )
    parser.add_option("--pdb2all",dest="pdb2all",default=None,
                      help="generate sequence, psf and template from PDBFILE",
                      metavar="PDBFILE"
                     )
    parser.add_option("--xplor",action="store_true",dest="xplor",default=False,
                      default=0,help="xplor PDBFILE flag")


    parser.add_option("--dataset",dest='dataset', default=None,
                      help="defines dataset (required for subsequent options)",
                      metavar="DATASET"
                     )

    parser.add_option("--check",action="store_true",dest='check',
                      help="check validity of DATASET")
    parser.add_option("--icheck",action="store_true",dest='icheck',
                      help="iteratively check validity of DATASET")
    parser.add_option("--Iset",action="store_true",dest="iset",
                      help="calculate DATASET information")
    parser.add_option("--Iuni",action="store_true",dest="iuni",
                      help="calculate DATASET unique information")
    parser.add_option("--Iave",action="store_true",dest="iave",
                      help="calculate DATASET average information")
    parser.add_option("--Iavef",action="store_true",dest="iavef",
                      help="calculate DATASET average restraint information\
                      (faster, but less accurate algorithm)")
    parser.add_option("--Isort",action="store_true",dest="sort",
                      help="sort DATASET by information")
    parser.add_option("--plot",action="store_true",dest="plot",
                      help="plot DATASET Iave versus Iuni")
    parser.add_option("--mpi",action="store_true",dest="mpi",
                      default=0,help="mpi flag")


    parser.add_option("--example",action="store_true",dest='example', default=False,
                      help="use example QUEEN project")
    parser.add_option("--test",action="store_true",dest='test', default=False,
                      help="test QUEEN installation")
    parser.add_option("--pydoc",
                        action="store_true",
                        dest="pydoc",
                        help="start pydoc server and browse documentation"
                      )
    (options,args) = parser.parse_args()

    #------------------------------------------------------------------------------
    # MPI and other stuff
    #------------------------------------------------------------------------------
    # CHECK IF WE NEED TO IMPORT PYPAR
    if options.mpi:
        import pypar
        numproc = pypar.size()
        myid = pypar.rank()
        sys.stdout.flush()
    else:
        numproc,myid = 1,0

    # PRINT WARNING FOR Iave CALCULATIONS not done on cluster
    if (options.iave or options.iavef) and numproc == 1:
        print "WARNING: You are running an Iave calculation on 1 processor."
        print "         This can be very time consuming, we suggest to run"
        print "         these calculations on a (Linux) cluster or multi-processor CPU.\n"
    #end if

    # SHOW TEXT HEADER
    if myid==0: print header


    #------------------------------------------------------------------------------
    # testing installation
    #------------------------------------------------------------------------------
    if options.test:
        qn_test(nmvconf)
        sys.exit(0)
    #end if

    #------------------------------------------------------------------------------
    # pydoc documentation
    #------------------------------------------------------------------------------
    if options.pydoc:
        import pydoc
        import webbrowser
        print '==> Serving documentation at http://localhost:9998'
        print '    Type <control-c> to quit'
        webbrowser.open('http://localhost:9998/queen.html')
        pydoc.serve(port=9998)
        sys.exit(0)
    #end if


    #------------------------------------------------------------------------------
    # Initialize queenbase instances and optionally use the CING API
    #------------------------------------------------------------------------------

    # Check if we need CING IMPORTS and patch the nmvconf file
    cingProject = None
    queen = None

    if options.example:
        queen = ExampleQueen(nmvconf)
        xplr  = qn_setupxplor(nmvconf,'example')
        print '==> Using data in QUEEN example directory %s' % (queen.projectpath)

    elif options.cing or options.initCing:
        # check the projectName
        if not options.projectName:
            error("Please supply the --project argument; type queen --help for more help")
            exit(1)
        #end if
#        try:
#            from cing import *
#            from cing.core.parameters import directories
#            from cing.Libs.NTutils import removedir
#            from initFromCING import initFromCING
#        except ImportError:
#            error("You do not seem to have the CING API installed")
#            exit(1)
#
#        cingProject = Project.open( options.projectName, status='old', restore=False)
#        if cingProject == None:
#            NTerror('initFromCING: Opening project "%s"\n', options.projectName )
#            exit(1)
#        #end if
#
#        # patch the nmrconf file to point to CING project and CING source code
#        nmvconf["Q_PROJECT"] = os.path.abspath(cingProject.path())
#
#        # patch the project to point to cingProject/Queen directory
#        queen = qn_setup(nmvconf, directories.queen, myid, numproc)
#        xplr  = qn_setupxplor(nmvconf,directories.queen)
        from initFromCING import CingBasedQueen
        queen = CingBasedQueen( nmvconf, options.projectName, numproc=numproc, myid=myid )
        print '==> Data in CING project directory %s' % (queen.projectpath)

    # default
    else:
        # check the projectName
        if not options.projectName:
            error("Please supply the --project argument; type queen --help for more help")
            exit(1)
        #end if
        queen = qn_setup(nmrconf, options.projectName, myid, numproc)
        xplr  = qn_setupxplor(nmvconf,options.projectName)
        print '==> Data in QUEEN project directory %s' % (queen.projectpath)
    #end if

    if numproc==1:
        print "==> Starting QUEEN ..."
    else:
        print "==> Starting QUEEN on processor %i of %i ..." %(myid+1,numproc)


    #------------------------------------------------------------------------------
    # Inits (< version 1.1 in generate.py)
    #------------------------------------------------------------------------------

    # create regular QUEEN project
    if options.init and not options.cing:
        queen.createproject(options.overwrite)
        exit(0)
    #end if

    # create QUEEN project using CING data structures
    if options.initCing or (options.init and options.cing):
        queen.createproject(options.overwrite)
        queen.exportFromCING()
        #initFromCING( queen, cingProject)
        exit(0)
    #end if

    #------------------------------------------------------------------------------
    # Generation of template files (< version 1.1 in generate.py)
    #------------------------------------------------------------------------------
    # GV wonders why not passing the xplor option directly?
    if options.xplor: xplorflag = 1
    else: xplorflag = 0

    if options.pdb2seq:
        qn_pdb2seq(options.pdb2seq, queen.seqfile, xplorflag)
        exit(0)
    #end if
    if options.seq2psf:
        qn_seq2psf( queen, options.seq2psf )
        exit(0)
    #end if
    if options.psf2tem:
        qn_psf2tem( queen, options.psf2tem )
        exit(0)
    #end if
    if options.pdb2all:
        qn_pdb2all( queen, options.pdb2all, xplorflag )
        exit(0)
    #end if

    #------------------------------------------------------------------------------
    # Dataset actions
    #------------------------------------------------------------------------------

    # check of dataset option
    if not options.dataset:
        error("Please supply the --dataset argument; type queen --help for more help")
        exit(1)
    else:
        dataset = options.dataset
    #end if


    # TAKE THE SELECTED OPTION
    if options.check:
      # CHECK VALIDITY OF DATASET
      qn_checkdata(queen,xplr,dataset)
    if options.icheck:
      # ITERATIVELY CHECK VALIDITY OF RESTRAINTS
      qn_checkdata(queen,xplr,dataset,iterate=1)
    if options.iset:
      # CALCULATE SET INFORMATION
      qn_setinformation(queen,xplr,dataset)
    elif options.iuni:
      # CALCULATE Iuni
      qn_infuni(queen,xplr,dataset)
    elif options.iave:
      # CALCULATE Iave
      convcutoff = float(nmvconf["IAVE_CUTOFF"])
      qn_infave(queen,xplr,dataset,convcutoff=convcutoff)
    elif options.iavef:
      # CALCULATE Iavef
      ncycles = int(nmvconf["IAVEF_NCYCLES"])
      qn_infave_fast(queen,xplr,dataset,ncycles=ncycles)
    elif options.sort:
      # SORT RESTRAINTS WITH MOST INFORMATIVE FIRST
      qn_infsort(queen,xplr,dataset)
    elif options.plot:
      # PLOT Iave VS Iuni
      qn_avevsuni(queen,xplr,dataset)
      # WRITE SORTED RESTRAINTTABLE
      qn_sorttbl(queen,xplr,dataset)
    #end if
#end main
