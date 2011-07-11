# run as:
# > python compareShifts.py
#
#  compare shifts of two projects
#
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.molecule import mapMolecules

#------------------------------------------------------------------------------------
# PARAMETERS ed.
#------------------------------------------------------------------------------------
ADCadef = range(501, 658) + [800, 850]
ADedtadef = range(501, 658) + [None, None]
BDdef = range(501, 603) + [None] + range(603, 657) + [None, None]

defsA = ('H2_2Ca_64_100C', 'CYANA', ADCadef)     # AD-Calcium
defsB = ('H2_AD_EDTA_63_100', 'CYANA2', ADedtadef)  # AD edta
#defsC = ('H2_BD_27', 'CYANA2', BDdef)      # BD

verbose = False
removeStereo = False # Remove the stereoAssignments for all but VaL, Leu
                    # and switch back to Hilge conventions (lower_ppm, higher_ppm)
limits = [0.0, 0.0, 0.0] # limits for chemical shift differences reporting
                               # 1H, 13C, 15N

#------------------------------------------------------------------------------------
# ROUTINES
#------------------------------------------------------------------------------------



def printatom(atm):
    if atm.isStereoAssigned():
        ss = '(stereo)'
    else:
        ss = '()      '
    #end if
    return sprintf('%-12s %10.3f  %s', atm.cName(1), atm.resonances().value, ss)
#end def

def compareShifts(projectA, projectB):
    """Compare the shifts of the two molecules of both projects
    """
    # Loop through all the residues
    for res1 in projectA.molecule.allResidues():
        res2 = res1.map
        #compare the two residues
        if not res2:
            continue

        # check if they are the same type
        if (res1.db.name == res2.db.name):
            identity = "(S)"
        else:
            identity = '(D)'
        #end if

        printf("\n==== %s %s ==== %s\n", res1.name, res2.name, identity)

        # loop through all the atoms of res1
        for a1 in res1.atoms:
            a2 = a1.map #check if this atom exists in res2
            a1.delta = None
            if a2 and a1.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY) and a2.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY):
                a1.delta = a1.resonances().value - a2.resonances().value
            #end if

            # calc differences with potential prochiral
            a1.pc = a1.proChiralPartner()
            if a1.pc:
                pc2 = a1.pc.map # atom of second set
            else:
                pc2 = None
            #end if
            a1.deltaPC = None # delta with prochiral atom
            if pc2 and a1.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY) and pc2.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY):
                a1.deltaPC = a1.resonances().value - pc2.resonances().value
            #end if
        #end for

        for a1 in res1.atoms:
            a2 = a1.map #check if this atom exists in res2
            doPrint = False
            swapText = ''
            if a1.delta:
                if ((a1.isProton() and math.fabs(a1.delta) >= limits[0]) or
                    (a1.isCarbon() and math.fabs(a1.delta) >= limits[1]) or
                    (a1.isNitrogen() and math.fabs(a1.delta) >= limits[2])
                   ):
                   doPrint = True
                   swapText = sprintf('%7.3f ', a1.delta)
                #end if
            # check for altered assignment
            if a1.delta and a1.deltaPC and a1.pc.delta and a1.pc.deltaPC:
                if (math.fabs(a1.deltaPC) + math.fabs(a1.pc.deltaPC) <
                    math.fabs(a1.delta) + math.fabs(a1.pc.delta)
                   ):
                   doPrint = True
                   swapText = sprintf("%7.3f >> Potential Swapped assignment %s and %s", a1.deltaPC, a1.map, a1.pc.map)
            #end if
            if doPrint:
                printf('%s  %s    %s    %7.3f  %s\n', identity, printatom(a1), printatom(a2), a1.delta, swapText)
            #end if
        #end for
    #end for
#end def


#------------------------------------------------------------------------------------
# START
#------------------------------------------------------------------------------------

# define, open, read the files
projectA = Project.open(defsA[0], 'old')
if not projectA: exit(1)
projectB = Project.open(defsB[0], 'old')
if not projectB: exit(1)

# compare A,B
mapMolecules(projectA.molecule, projectB.molecule, zip(defsA[2], defsB[2]))
compareShifts(projectA, projectB)

