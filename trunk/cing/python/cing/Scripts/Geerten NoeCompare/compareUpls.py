# run as:
# > python compareUpls.py
#
#  compare two upl files;
#  generate C13/N15 peak lists corresponding to all NOEs not present in the other-upl,
#  Consider only mapped atoms; i.e. atoms which exist in both A and B forms. 
# 
#

from cing import *


#------------------------------------------------------------------------------------
# PARAMETERS ed.
#------------------------------------------------------------------------------------
ADCadef     = range(501,658)+[800,850,900]
ADedtadef   = range(501,658)+[None,None, None]
BDdef       = range(501,658)+[None,None, None]

defsC     = ('H2_3Ca_49',   'CYANA2', ADCadef)     # AD-Calcium
defsA     = ('H2_EDTA_54',   'CYANA2', ADedtadef)  # AD edta
defsB     = ('H2_BD_38',     'CYANA2', BDdef)      # BD

peakColor = 2
verbose   = True 

#------------------------------------------------------------------------------------
# ROUTINES
#------------------------------------------------------------------------------------

def cyana2cing( name, convention ):
    """Read the data from the cyana directory
    """
    project = Project.open(name, 'new')
    from disk import matchfilelist
    seqfile = matchfilelist( project.name +'/*.seq')[0]
    mol = project.newMolecule( project.name, seqfile, convention )
    project.importXeasy( seqfile, project.name + '/all-final.prot', convention )
    project.importXeasyPeaks( seqfile, project.name + '/all-final.prot', project.name + '/c13.peaks', convention )
    project.importXeasyPeaks( seqfile, project.name + '/all-final.prot', project.name + '/aro.peaks', convention )
    project.importXeasyPeaks( seqfile, project.name + '/all-final.prot', project.name + '/n15.peaks', convention )
    upl = project.importUpl( project.name +'/final.upl', convention )
    project.importAco( project.name +'/talos.aco', convention )
    return project, mol, upl
#end def

def mapMolecules( mol1, mol2, molMap ):
    """Give residues and atoms a 'map' attribute
       that points to the corresponding residue/atom in the other molecule
    """
    for i1,i2 in molMap:
        res1 = mol1.getResidue( i1 )
        res2 = mol2.getResidue( i2 )
        if (res1 != None and res2 != None):
            res1.map = res2
            res2.map = res1
            for atm in res1.atoms:
                if atm.name in res2:
                    atm.map = res2[atm.name]
                else:
                    atm.map = None
                #end if
            #end for
            for atm in res2.atoms:
                if atm.name in res1:
                    atm.map = res1[atm.name]
                else:
                    atm.map = None
                #end if
            #end for
        elif (res1!=None and res2 == None):
            res1.map = res2
            for atm in res1.atoms:
                atm.map = None
            #end for
        elif (res1==None and res2 != None):
            res2.map = res1
            for atm in res2.atoms:
                atm.map = None
            #end for
    #end for
#end def

def atoms2peak( atm1, atm2, c13peaks, aropeaks, n15peaks ):
    """return 3D peak [heavyAtom, atm2, atm1]
       check for assignments, replacing for pseudo atoms if needed
    """
    # Order of coordinates (heavy, H, attached-H)
    # get the heavy atom from the topology def of atm1.
    heavyAtm = atm1.topology()[0]
    atoms = NTlist( heavyAtm, atm2, atm1 )
    # check for assignment, use the set to find a possible alternative
    # pseudo/real atom with an assignment; the original atom is always
    # at the start of the set, so no changes are made if it is assigned.
    for atm in atoms[1:]:
        for a in atm.s:
            if a.isAssigned():
                atoms.replace( atm, a)
                break
            #end if
        #end for
    #end for
    if (heavyAtm.isCarbon() and heavyAtm.isAromatic()):
        peak=aropeaks.peakFromAtoms( atoms )
    elif (heavyAtm.isCarbon()):
        peak=c13peaks.peakFromAtoms( atoms )
    elif (heavyAtm.isNitrogen()):
        peak=n15peaks.peakFromAtoms( atoms )
    else:
        NTerror("NOE: %s-%s: Strange spinType heavyAtom %s\n", atm1, atm2, heavyAtm )
        peak = None
    #end if
    
#    if peak: print peak
#    else: print atoms
    
    return peak
#end def

def compareNoeNetWork( projectA, projectB, verbose ):
    """
    Generate B-peakLists for NOEs of A not present in B.
    Mapping and NOE sorting should have been done before
    
    Expand the NOEs to/from pseudo atoms by using the set() method (already 
    present as the '.s' attribute).
    The sets should take care of the comparison of 'like' atoms;
    i.e. pseudo with real atoms
    """
    
    c13peaks = projectB.newPeakList('c13new', status='keep', verbose=False)
    c13peaks.xeasyColor = peakColor
    aropeaks = projectB.newPeakList('aronew', status='keep', verbose=False)
    aropeaks.xeasyColor = peakColor
    n15peaks = projectB.newPeakList('n15new', status='keep', verbose=False)
    n15peaks.xeasyColor = peakColor
    count = 0

    for atmA1 in projectA.molecule.allAtoms():
        # check all the NOEs for this atom
        for atmA2 in atmA1.NOEs:
            atmB1 = atmA1.map
            atmB2 = atmA2.map
            found = 0
            # check all the possibilities of the set of atomB1
            for b1 in atmB1.s:
                # A set comparison yields true if there is one or more common elements
                if b1.NOEs == atmB2.s:
                    count += 1
                    found = 1
                    #printf( '>>> Found (%3d)   %-10s - %-10s    %-10s - %-10s\n', count, atmA1, atmA2, b1, atmB2)
                    break
                else:
                    #printf( '>>> Not found     %-10s - %-10s    %-10s - %-10s\n', atmA1, atmA2, b1, atmB2)
                    pass
                #end if
            #end for
            if (not found):
                # generate a atmB1-atmB2 peak since this NOE (atmA1,atmA2) was not found in the B-set
                # the reverse peak is accounted for by the (atmA2-atmA1) Noe
                peak = atoms2peak( atmB1, atmB2, c13peaks, aropeaks, n15peaks )
            #end if
        #end for
    #end for

    if verbose:
        NTmessage('==> Created %s\n', c13peaks )
        NTmessage('==> Created %s\n', aropeaks )
        NTmessage('==> Created %s\n', n15peaks )  
    #end if
#end def

#------------------------------------------------------------------------------------
# START
#------------------------------------------------------------------------------------

# define, open, read the files
projectA, molA, uplA = cyana2cing( defsA[0], defsA[1])
projectB, molB, uplB = cyana2cing( defsB[0], defsB[1])


# Loop through all the atoms and initialize
for atm in projectA.molecule.allAtoms():
    atm.map  = None
    atm.NOEs = NTset()      # NTset: list of objects; sets are equal if they share a common object
    atm.s    = atm.set()    # NTset instance with self, real/pseudo atom instances
#end for
for atm in projectB.molecule.allAtoms():
    atm.map  = None
    atm.NOEs = NTset()      # NTset: list of objects; sets are equal if they share a common object
    atm.s    = atm.set()    # NTset instance with self, real/pseudo atom instances
#end for

# Map equivalent atoms
mapMolecules( projectA.molecule, projectB.molecule, zip(defsA[2],defsB[2]) )

# List Noes on 'both' sides (X->Y and Y->X) for the A-molecule
# Only take them when there is a map for both atoms
for r in uplA:
    for atm1,atm2 in r.atomPairs:
        if (atm1.map != None and atm2.map != None):
            atm1.NOEs.append( atm2 )
            atm2.NOEs.append( atm1 )
        #end if
    #end for
#end for

# List Noes on 'both' sides (X->Y and Y->X) for the B-molecule
# Only take them when there is a map for both atoms
for r in uplB:
    for atm1,atm2 in r.atomPairs:
        if (atm1.map != None and atm2.map != None):
            atm1.NOEs.append( atm2 )
            atm2.NOEs.append( atm1 )
        #end if
    #end for
#end for

# Now compare with the networks of the two molecules
NTmessage('==> comparing %s %s\n', uplA, uplB )
compareNoeNetWork( projectA, projectB, verbose )
NTmessage('==> comparing %s %s\n', uplB, uplA )
compareNoeNetWork( projectB, projectA, verbose )

# export and save by closing projects
projectA.close()
projectB.close()

