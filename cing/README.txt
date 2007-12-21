#------------------------------------------------------------------------------
 CING
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
Go to your CING installations directory. This directory will be identified by the
CINGROOT environment variable once the below setup is done. Type:

python python/cing/setup.py

This generates cing.csh or cing.sh in the current directory that you need to check 
and adjust if needed. Then source it in your .cshrc or .bashrc file
 
The setup.py script uses 'which xplor' etc. to determine the various locations for
executables; make sure it is in your path when you run setup. 

Setup instructions for working with CING in Eclipse/PyDev are available in:
Documentation/setupEclipse/development_installation_eclipse.html

#------------------------------------------------------------------------------
To get help:
> cing -h

usage: cing [options]       use -h or --help for listing

options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --doc                 Print more documentation to stdout
  --docdoc              Print full documentation to stdout
  -n PROJECTNAME, --name=PROJECTNAME
                        NAME of the project (required)
  --new                 Start new project
  --old                 Open a old project
  --init=SEQUENCEFILE[,CONVENTION]
                        Initialise from SEQUENCEFILE[,CONVENTION]
  --initPDB=PDBFILE[,CONVENTION]
                        Initialise from PDBFILE[,CONVENTION]
  --initCcpn=CCPNFILE
                        Initialise from CCPNFILE	
  --xeasy=SEQFILE,PROTFILE,CONVENTION
                        Import shifts from xeasy SEQFILE,PROTFILE,CONVENTION
  --xeasyPeaks=SEQFILE,PROTFILE,PEAKFILE,CONVENTION
                        Import peaks from xeasy
                        SEQFILE,PROTFILE,PEAKFILE,CONVENTION
  --merge               Merge resonances
  --generatePeaks=EXP_NAME,AXIS_ORDER
                        Generate EXP_NAME peaks with AXIS_ORDER from the
                        resonance data
  --script=SCRIPTFILE   Run script from SCRIPTFILE
  --ipython             Start ipython interpreter
  -q, --quiet           quiet: no/less messages to stdout (default: not quiet)
  --nosave              Don't save on exit (default: save)

  
#------------------------------------------------------------------------------
to get more help:
> cing -doc

to test the installation type:
> cing --test

--------------------------------------------------------------------------------
cing: command line interface to the cing utilities:
--------------------------------------------------------------------------------

Some examples; all assume a project named 'test':

- To start a new Project:
cing --name test --new

- To start a new Project from a xeasy seq file:
cing --name test --init AD.seq,CYANA 

- To start a new Project from a xeasy seq file and load an xeasy prot file:
cing --name test --init AD.seq,CYANA --xeasy AD.seq,AD.prot,CYANA

- To start a new Project from a CCPN project:
cing --name test --initCCPN ccpn_project.xml

- To start a new Project from a xeasy seq file via CCPN formatConverter CCPN project:
cing -name test --initXEASY_FC AD.seq,CYANA

- To open an existing Project:
cing --name test 

- To open an existing Project and load an xeasy prot file:
cing --name test --xeasy AD.seq,AD.prot,CYANA

- To open an existing Project and start an interactive python interpreter:
cing --name test --ipython

- To open an existing Project and run a script MYSCRIPT.py:
cing --name test --script MYSCRIPT.py

--------------------------------------------------------------------------------
Some simple script examples:
--------------------------------------------------------------------------------

== merging several prot files ==
project.initResonances()      # removes all resonances from the project
project.importXeasy( 'N15.seq', 'N15.prot', 'CYANA' )
project.importXeasy( 'C15.seq', 'C15.prot', 'CYANA' )
project.importXeasy( 'aro.seq', 'aro.prot', 'CYANA' )
project.mergeResonances( status='reduce'  )

== Generating a peak file from shifts ==
project.listPredefinedExperiments() # list all predefined experiments
peaks = project.generatePeaks('hncaha','HN:HA:N')
format(peaks)

== Print list of parameters:
    formatall( project.molecule.A.residues[0].procheck ) # Adjust for your mols
    formatall( project.molecule.A.VAL171.C )
