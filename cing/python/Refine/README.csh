# Follow other readme for the original refine protocol.
# However, the new code is not automatically tested for that protocol.
# This is due to too many complications going from cing to xplor coordinates.

#WORKFLOW marked ORG for originally used.

set x = 1brv
set stage = $x"_redo"
set ranges = auto
# Derived but may be overriden.
#set modelsAnneal     = 0-3 # selected by modelCountAnneal
#set models           = 0-2 # selected by bestAnneal                                        ORG
#set bestModels       = 0-1 # selected by best                                              ORG
set modelCountAnneal = 4    
set bestAnneal = 3          
set best = 2                
@ minmodels = $modelCountAnneal - 1
set modelsAnneal = "0-$minmodels"

set standardOptions = "--modelsAnneal $modelsAnneal --modelCountAnneal $modelCountAnneal --bestAnneal $bestAnneal --best $best -v 9 --superpose $ranges --overwrite"

# Prepare a CING project
\rm -rf $x.cing
cing                -n $x --initCcpn $x.tgz

# -Choose the terseness of the commands you like from the below 3 options
# -1-
refine --project $x -n $stage --fullAnnealAndRefine         $standardOptions
# or -2-
refine --project $x -n $stage --fullAnneal                  $standardOptions
refine --project $x -n $stage --fullRefine #TODO: check this.
# or -3-
refine --project $x -n $stage --setup                       $standardOptions 
refine --project $x -n $stage --psf                     
refine --project $x -n $stage --generateTemplate        
refine --project $x -n $stage --anneal                  
refine --project $x -n $stage --analyze --useAnnealed   
refine --project $x -n $stage --parse   --useAnnealed   
# and then WORKFLOW refine
refine --project $x -n $stage --refine                  
refine --project $x -n $stage --parse                   
refine --project $x -n $stage --import  

    