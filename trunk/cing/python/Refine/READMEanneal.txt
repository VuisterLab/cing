# Follow other readme until --refine target.

-----------------------------------------------------------------------------------------------------------------------------------------
  Generate template PDB coordinate file of extended strand.
-----------------------------------------------------------------------------------------------------------------------------------------
refine --project $x -n $stage --generateTemplate --overwrite

-----------------------------------------------------------------------------------------------------------------------------------------
  Anneal to a reasonably good ensemble.
-----------------------------------------------------------------------------------------------------------------------------------------
refine --project $x -n $stage --anneal

refine --project $x -n $stage --parse --useAnnealed --sort Enoe

# Follow original README.txt again.

NOTES TO CHECK
- How does the SS bond finally get in? DISN is without actual bond.
- Dihedrals set to 100 force constant in anneal?



WORKFLOW

set x = H2_2Ca_64_100
set stage = $x"_redo"
set ranges = all
set models = 0-19

cing                -n $x --initCcpn $x.tgz --ensemble $models

# -Choose the terseness of the commands you like from the below 3 options
# -1-
refine --project $x -n $stage --setup --fullAnnealAndRefine --overwrite --models $models --superpose $ranges --sort Enoe
# or -2-
refine --project $x -n $stage --setup --fullAnneal --overwrite --models $models --superpose $ranges --sort Enoe
refine --project $x -n $stage         --fullRefine --overwrite --models $models --superpose $ranges --sort Enoe
# or -3-
refine --project $x -n $stage --setup                   --overwrite --superpose $ranges
refine --project $x -n $stage --psf                     --overwrite
refine --project $x -n $stage --generateTemplate        --overwrite
refine --project $x -n $stage --anneal                  --overwrite
refine --project $x -n $stage --analyze --useAnnealed   --overwrite
# and then WORKFLOW refine
refine --project $x -n $stage --refine  --overwrite         --models $models
refine --project $x -n $stage --parse   --sort Enoe         --models $models
refine --project $x -n $stage --import  --superpose $ranges --models $models
