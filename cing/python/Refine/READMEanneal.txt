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



WORKFLOW just ANNEAL -- should work --

cd
set x = 1brv
set stage = annealed
set ranges = 171-188
set models = 0-1
set x = 2fwu
set ranges = 500-850


cing                -n $x --initCcpn $x.tgz --ensemble $models

refine --project $x -n $stage --setup --fullAnneal --useAnnealed --overwrite --models $models --superpose $ranges --sort Enoe
# or
refine --project $x -n $stage --setup                   --overwrite --superpose $ranges
refine --project $x -n $stage --psf                     --overwrite
refine --project $x -n $stage --generateTemplate        --overwrite
refine --project $x -n $stage --anneal                  --overwrite
refine --project $x -n $stage --analyze --useAnnealed   --overwrite
refine --project $x -n $stage --parse   --useAnnealed   --sort Enoe
refine --project $x -n $stage --import  --useAnnealed   --superpose $ranges


WORKFLOW ANNEAL plus REFINE --todo--

set x = 1brv
set stage = waterRefined
set ranges = 171-188

cing                -n $x --initCcpn $x.tgz
refine --project $x -n $stage --setup                   --overwrite --superpose $ranges
refine --project $x -n $stage --psf                     --overwrite
refine --project $x -n $stage --generateTemplate        --overwrite
refine --project $x -n $stage --anneal                  --overwrite
refine --project $x -n $stage --analyze --useAnnealed   --overwrite
refine --project $x -n $stage --parse   --useAnnealed   --sort Enoe
refine --project $x -n $stage --import  --useAnnealed   --superpose $ranges
