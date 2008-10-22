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
from cing.main import project
from cing.Libs.NTutils import NTmessage

#===========================================================================
# parameters 
#===========================================================================

# Adjust to generate different output
resonances =[ (0,'HN'),(0,'N'),( 0,'CA'),(0,'CB'),( -1,'CA'), (-1,'CB')]
             
#===========================================================================
# No need to edit below here (I think)
#===========================================================================
NTmessage('%-8s  ',  ' ')
for index,name in resonances:
    NTmessage('%-8s  ', name+'i'+str(index) )
#end for
NTmessage('')

# Generate peaks for all residues
for residue in project.molecule.allResidues(): #@UndefinedVariable
    atoms = translateTopology( residue, resonances )
    NTmessage('%-8s  ', residue.name)
    for atm in atoms:
        if not atm:
            NTmessage('%-8s  ', '-X-')
        elif atm.isAssigned():
            NTmessage('%-8.3f  ', atm.shift() )
        else:
            NTmessage('%-8s  ', '-?-' )
        #end if
    #end for
    NTmessage('')
#end for

