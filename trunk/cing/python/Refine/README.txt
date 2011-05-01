# Refinement setup

set x = 1brv
set stage = rA
set ranges = 171-188

set x = H2_2Ca_64_100
set stage = rT
set ranges = 501-850


-----------------------------------------------------------------------------------------------------------------------------------------
   Import into cing
-----------------------------------------------------------------------------------------------------------------------------------------

# From CCPN:
cing -v 9 --name $x --initCcpn $x.tgz --ipython



Usage: cyana2cing.py [options] cyanaDirectory Use -h or --help for full options.

Options:
  -h, --help            show this help message and exit
  -o, --overwrite       Overwrite existing cing output directory (default: no-
                        overwrite).
  -c CONVENTION, --convention=CONVENTION
                        Set convention: CYANA,CYANA2 (default=CYANA2).
  --seqFile=SEQFILE     Define seqFile (no .seq extension).
  --protFile=PROTFILE   Define protFile (no .prot extension).
  --stereoFile=STEREOFILE
                        Define stereoFile (no .cya extension).
  --pdbFile=PDBFILE     Define pdbFile (no .pdb extension).
  --nmodels=NMODELS     Define number of models to extract from PDBFILE
                        (default=20).
  --peakFiles=PEAKFILES
                        Define peakFiles (no .peaks extension; separate by
                        comma's:e.g. c13,n15).
  --uplFiles=UPLFILES   Define uplFiles (no .upl extension; separate by
                        comma's:e.g. final,manual).
  --acoFiles=ACOFILES   Define acoFiles (no .aco extension; separate by
                        comma's:e.g. talos, hnha).
  --export              Export to different formats (default: no-export).
  -v VERBOSITY, --verbosity=VERBOSITY
                        verbosity: [0(nothing)-9(debug)] no/less messages to
                        stdout/stderr (default: 3)

# Create a new project from a CYANA directory (called LdCof) with all required files in.
cyana2cing -v 9 --pdbFile $x --peakFiles $x"n15",$x"c13" --uplFiles $x --acoFiles $x --seqFile $x --protFile $x -o $x

-----------------------------------------------------------------------------------------------------------------------------------------
  setup for refine using XPLOR-NIH
-----------------------------------------------------------------------------------------------------------------------------------------

Usage: refine.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --doc                 print extended documentation to stdout
  --project=PROJECT     Cing project name (required); data will be in
                        PROJECT.cing/Refine/NAME
  --name=NAME           NAME of the refinement run (required)
  -s, --setup           Generate directory structure, parameter file, export
                        project data
  -f, --psf             Generate PSF file (default: no PSF)
  -a, --analyze         Initial analysis (default: no analysis)
  -r, --refine          Refine the structures (default: no refine)
  -p, --print           Print script before running (default: no print)
  --models=MODELS       Model indices (e.g. 0,2-5,7,10-13)
  --parse               Parse the output of the refine run (default: no parse)
  --sort=SORTFIELD      sort field for parse option
  --best=BESTMODELS     Number of best models for parse option
  --import              Import the refined structures of the refine run
                        (default: no import)
  --superpose=SUPERPOSE
                        superpose ranges; e.g. 503-547,550-598,800,801
  -v VERBOSITY, --verbosity=VERBOSITY
                        verbosity: [0(nothing)-9(debug)] no/less messages to
                        stdout/stderr (default: 3)


refine --project $x --name $stage --setup --overwrite --superpose $ranges


==> Generated setup under "./$x.cing/Refine/$stage"
-----------------------------------------------------------------------------------------------------------------------------------------
  Edit parameters.py file
-----------------------------------------------------------------------------------------------------------------------------------------
Edit "./$x.cing/Refine/$stage/parameters.py" before continuing


-----------------------------------------------------------------------------------------------------------------------------------------
  Manually edit the Ca.tbl file to the following format
-----------------------------------------------------------------------------------------------------------------------------------------
XPLOR: d dminus dplus
assi (resid 578 and name OD1)       (resid 800 and name "CA+2")         2.800     2.800     0.000
assi (resid 578 and name OD2)       (resid 850 and name "CA+2")         2.800     2.800     0.000
assi (resid 580 and name O)         (resid 800 and name "CA+2")         2.800     2.800     0.000
assi (resid 648 and name OE1)       (resid 800 and name "CA+2")         2.800     2.800     0.000
assi (resid 648 and name OE2)       (resid 800 and name "CA+2")         2.800     2.800     0.000
assi (resid 552 and name OD1)       (resid 850 and name "CA+2")         2.800     2.800     0.000
assi (resid 516 and name OE2)       (resid 800 and name "CA+2")         2.800     2.800     0.000
assi (resid 516 and name OE1)       (resid 800 and name "CA+2")         2.800     2.800     0.000

# Then create the psf etc.
refine --project $x --name $stage --superpose $ranges --psf

-----------------------------------------------------------------------------------------------------------------------------------------
  PSF file
-----------------------------------------------------------------------------------------------------------------------------------------
Manually copy the appropriate .psf file to the $x.cing/Refine/$stage/PSF subdirectory if not there yet.

Be sure to have the right name in parameter.py for the psfFile field
PERHAPS: edit the generatePSF.inp to include better topology description:
        patch DISN
            reference=1=( resid 173 )  reference=2=( resid 186 )
        end
        patch DISN
            reference=1=( resid 176 )  reference=2=( resid 182 )
        end
        and run again:
        $x.cing/Refine/$stage/Jobs/generatePSF.csh

-----------------------------------------------------------------------------------------------------------------------------------------
  Analyze
-----------------------------------------------------------------------------------------------------------------------------------------
refine --project $x --name $stage --analyze --overwrite --ipython

Examine at least one log file in the Jobs directory for errors.
JFD: - fixed bug with too long file name: @@1brv_cs_pk_2mdl.cing/Refine/refine1/Tables/dihedral_constraint_list.tbl
        The same for the other files. Easiest fix is to rename the lists to be no more than 10 chars.

-----------------------------------------------------------------------------------------------------------------------------------------
  Refine
-----------------------------------------------------------------------------------------------------------------------------------------
refine --project $x --name $stage --refine

or to start multiple jobs consider multipleRefineJobs.csh

-----------------------------------------------------------------------------------------------------------------------------------------
  Parse result, select 10? best, based on Enoe
-----------------------------------------------------------------------------------------------------------------------------------------
refine --project $x --name $stage --parse --best 10 --sort Enoe

-----------------------------------------------------------------------------------------------------------------------------------------
  Import into project using $stage as the name for the new molecule
  JFD: consider renaming the stage at this point?
-----------------------------------------------------------------------------------------------------------------------------------------
refine --project $x --name $stage --import

-----------------------------------------------------------------------------------------------------------------------------------------
  Open in CING
-----------------------------------------------------------------------------------------------------------------------------------------

cing --project $x --ipython --nosave






