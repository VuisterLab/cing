"""
   printResonances.py
   Initial version for Mark, 7 Nov 2006
   
   For a 'cold-start' from a SEQFILE,PROTFILE in cyana format:
        cing.py -n PROJECTNAME --init SEQFILE,CYANA --xeasy SEQFILE,PROFILE,CYANA --script printResonances.py
   
    For an existing project PROJECTNAME
        cing.py -n PROJECTNAME --script printResonances.py

   Can be easily adapted
   
"""
from cing.core.molecule import translateTopology
from cing.Libs.NTutils import printf
from cing.main import project

#===========================================================================
# parameters
#===========================================================================

# Adjust to generate different output
resonances =[ (0,'HN'),(0,'N'),( 0,'CA'),(0,'CB'),( -1,'CA'), (-1,'CB')]
             
#===========================================================================
# No need to edit below here (I think)
#===========================================================================
printf('%-8s  ',  ' ')
for index,name in resonances:
    printf('%-8s  ', name+'i'+str(index) )
#end for
printf('\n')

# Generate peaks for all residues
for residue in project.molecule.allResidues(): 
    atoms = translateTopology( residue, resonances )
    printf('%-8s  ', residue.name)
    for atm in atoms:
        if not atm:
            printf('%-8s  ', '-X-')
        elif atm.isAssigned():
            printf('%-8.3f  ', atm.shift() )
        else:
            printf('%-8s  ', '-?-' )
        #end if
    #end for
    printf('\n')
#end for

