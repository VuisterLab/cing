# run as:
# > python compare3.3.2.py
#
#  compare three CYANA runs;
#  generate C13/N15 peak lists corresponding to all NOEs not present in the other-upl,
#  Consider only mapped atoms; i.e. atoms which exist in both A and B forms. 
#
#  Append peaks to existing C13, aro and n15
#
#  Does not handle ambigious NOEs properly (yet).
# 
#  Version 3 :  for cing_70
#  Version 3.1: Output filtering in chemical shift comparison
#  Version 3.2: Include stereoAssignment check
#  Version 3.3: Optional swap back of stereoAssignments
#  Version 3.3.2: Fix error when swapping resonances (alose need to include 
#                 swaps of atom pointers.
#

import math

from cing    import *
from cing.Libs.NTutils import NTlist, printf, fprintf, sprintf, NTerror, NTmessage
from cing.Libs.AwkLike import AwkLike
from cing.core.molecule import Atom


#------------------------------------------------------------------------------------
# PARAMETERS ed.
#------------------------------------------------------------------------------------
ADCadef     = range(501,658)+[800,850]
ADedtadef   = range(501,658)+[None,None]
BDdef       = range(501,603)+[None]+range(603,657)+[None,None]

defsA     = ('H2_2Ca_53',   'CYANA2', ADCadef)     # AD with calcium
defsB     = ('H2_AD_EDTA_58', 'CYANA2', ADedtadef) # AD EDTA
defsC     = ('H2_BD_41',      'CYANA2', BDdef)     # BD

peakColor    = 2
verbose      = False 
removeStereo = True # Remove the stereoAssignments for all but VaL, Leu
                    # and switch back to Hilge conventions (lower_ppm, higher_ppm)
minNOE       = 4    # minimum difference in residue id's; i.e. allows for selection of
                    # long-range
limits       = [0.1, 0.4, 0.4] # limits for chemical shift differences reporting
                               # 1H, 13C, 15N

#------------------------------------------------------------------------------------
# ROUTINES
#------------------------------------------------------------------------------------

def parseCyanaStereoFile( project, stereoFileName, convention, verbose=True ):
    """
var info echo
echo:=off
info:=none
atom stereo "HB2  HB3   509"   # GLU-
atom stereo "QG1  QG2   511"   # VAL
atom stereo "HB2  HB3   513"   # HIS
atom stereo "QG1  QG2   514"   # VAL
atom stereo "HG2  HG3   516"   # GLU-
atom stereo "HA1  HA2   519"   # GLY

    """
    for line in AwkLike( stereoFileName, minNF=5 ):
        if line.dollar[1] == 'atom' and line.dollar[2] == 'stereo':
            resnum = int (line.dollar[5].strip('"') )
            for i in [3,4]:
                atm = project.molecule.decodeNameTuple( (convention, 'A', resnum, line.dollar[i].strip('"')) )
                #print atm
                if atm == None:
                    NTerror(' parseCyanaStereoFile: line %d (%s)\n', line.NR, line.dollar[0] )
                else:
                    atm.stereoAssigned = True
                    if atm.isMethylProton():        # Val, Ile methyls: Carbon implicit in CYANA defs
                        atm.heavyAtom().stereoAssigned = True
                    #end if
                #end if
            #end for
        #end if
    #end for
    if verbose:
        NTmessage('==> Imported stereo assignments from "%s"\n', stereoFileName )
#end def

def isStereoAssigned( atm ):
    """
    Return True if stereoAssigned flag present and True
    """
    atm.setdefault( 'stereoAssigned', False )
    return atm.stereoAssigned
#end def
Atom.isStereoAssigned = isStereoAssigned

def isProChiral( atm ):
    """
    Return True if atm is pro-chiral and thus can have stereo assignment
    Should be in in database
    """
    LVdict = dict( CD1 = 'CD2', CD2 = 'CD1', QD1 = 'QD2', QD2 = 'QD1',
                   CG1 = 'CG2', CG2 = 'CG1', QG1 = 'QG2', QG2 = 'QG1' 
                 )
    atm.db.proChiralPartnerAtom = None
    if atm.residue.db.name in ['LEU', 'VAL'] and atm.db.name in LVdict:
        # patch database
        atm.db.proChiralPartnerAtom = LVdict[ atm.db.name ]
        return True
    #end if
    if atm.isProton():
        p = atm.pseudoAtom()
        if p != None:
            r = p.realAtoms()
            if len(r) == 2:
                if atm == r[0]:
                    atm.db.proChiralPartnerAtom = r[1].db.name
                else:
                    atm.db.proChiralPartnerAtom = r[0].db.name
                return True
            #end if
        #end if
    #end if
    return False
#end def
Atom.isProChiral = isProChiral

def proChiralPartner( atm ):
    """
    Return proChiral partner Atom instance of atm or None if this does not exist
    should be in database
    """
    
    if atm.isProChiral():
        return atm.residue[atm.db.proChiralPartnerAtom]
    #end if
    return None
#end def
Atom.proChiralPartner = proChiralPartner

def heavyAtom( atm ):
    """
    For protons return heavyAtom of atm,
    None otherwise
    """
    if not atm.isProton(): return None
    return atm.topology()[0]
#end def
Atom.heavyAtom = heavyAtom

def cyana2cing( name, convention ):
    """Read the data from the cyana directory and store in new project
    """
    
    printf("\n==> Opening Project %s\n", name )
    
    project = Project.open(name, 'new', verbose=False )
    from cing.Libs.disk import matchfilelist
    seqfile = matchfilelist( project.name +'/*.seq')[0]
    
    project.newMolecule( project.name, seqfile, convention, verbose=False )
    project.importXeasy( seqfile, project.name + '/all-final.prot', convention )
    parseCyanaStereoFile( project, project.name + '/finalstereo.cya', convention )
    
    project.c13peaks = project.importXeasyPeaks( seqfile, project.name + '/all-final.prot', project.name + '/c13.peaks', convention )
    project.aropeaks = project.importXeasyPeaks( seqfile, project.name + '/all-final.prot', project.name + '/aro.peaks', convention )
    project.n15peaks = project.importXeasyPeaks( seqfile, project.name + '/all-final.prot', project.name + '/n15.peaks', convention )
    project.upl      = project.importUpl( project.name +'/final.upl', convention )
# comment because of crash in export and not needed anyway
#    project.aco      = project.importAco( project.name +'/talos.aco', convention )
    
    print project.format()
    return project
#end def

def mapMolecules( mol1, mol2, molMap ):
    """Give residues and atoms a 'map' attribute
       that points to the corresponding residue/atom in the other molecule
    """
    # Initialize (should not be neccessary! but alas)
    for atm in mol1.allAtoms(): atm.map = None
    for atm in mol2.allAtoms(): atm.map = None
    
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

def checkAssignments( project ):
    """
    Check assignments for potential trivial errors
    """
    if project == None: return
    
    printf("==> Assignment check Project %s\n", project )
    
    for atm in project.molecule.allAtoms():
        if atm.isAssigned():
            # Check database
            av = atm.db.shift.average
            sd = atm.db.shift.sd
        
            #print atm, atm.db.pseudo
            
            # Check the shift against the database
            if (math.fabs(atm.resonances().value - av) > 3.0*sd):
                printf('SHIFT                         %s: more than 3*sd away from average\n', atm )
            #end if
        
            # Check if not both realAtom and pseudoAtom are assigned
            if atm.hasPseudoAtom() and atm.pseudoAtom().isAssigned():
                printf('MULTIPLE_ASSIGNMENT           %s: also has %s assigned\n', atm, atm.pseudoAtom() )
            #end if
            
            # Check if not pseudoAtom and realAtom are assigned
            if atm.isPseudoAtom():
                for a in atm.realAtoms():
                    if a.isAssigned():
                        printf('MULTIPLE_ASSIGNMENT          %s: also has %s assigned\n', atm, a )
                    #end if
                #end for
            #end if
            
            # Check if all realAtoms are assigned in case there is a pseudoatom
            if atm.hasPseudoAtom():
                ratms = atm.pseudoAtom().realAtoms()
                allAssigned = True
                for a in ratms:
                    if not a.isAssigned():
                        printf('MISSING_PROTON_ASSIGNMENT     %s: expected also %s to be assigned\n', atm, a )
                        allAssigned = False
                    #end if
                #end for
                
#                 if len( ratms ) == 2 and allAssigned and ratms[0].resonances().value > ratms[1].resonances().value:
#                         printf('SWAPPED_PROTON_ASSIGNMENTS    %s: and %s\n', ratms[0], ratms[1] )
#                 #end if                    
            #end if
            
            # Check for protons with unassigned heavy atoms
            if atm.db.spinType == '1H':
                heavyAtm = atm.topology()[0]
                if not heavyAtm.isAssigned():
                    printf('MISSING_HEAVY_ATOM_ASSIGNMENT %s: expected %s to be assigned\n', atm, heavyAtm )
                #end if
            #end if
            
            pc = atm.proChiralPartner()
            if removeStereo and pc and not (atm.hasProperties('isMethyl') or atm.hasProperties('isMethylProton')):
                # check the order and the value of resonances; i.e. HB2 < HB3
                if ( (atm < pc and atm.resonances().value > pc.resonances().value) or
                     (atm > pc and atm.resonances().value < pc.resonances().value)
                   ):
                    swapAssignments(tmp,pc)
                    printf( 'SWAPPED assignments           %s and %s\n',atm, pc)
                #end if
                atm.stereoAssigned = False
                pc.stereoAssigned = False
            #end if
        #end if
    #end for
#end def

def swapAssignments( atm1, atm2 ):
    """
    Swap the assignments of atm1 and atm2
    """
    for r in atm1.resonances:
        r.atom = atm2
    for r in atm2.resonances:
        r.atom = atm1
    tmp = atm1.resonances
    atm1.resonances = atm2.resonances
    atm2.resonances = tmp
#end def

def printatom( atm ):
    if atm.isStereoAssigned():
        ss = '(stereo)'
    else:
        ss = '()      '
    #end if
    return sprintf('%-12s %10.3f  %s', atm._Cname(1), atm.resonances().value, ss )
#end def

def compareShifts( projectA, projectB ):
    """Compare the shifts of the two molecules of both projects
    """
    # Loop through all the residues
    for res1 in projectA.molecule.allResidues():
        res2=res1.map
        #compare the two residues
        if res2 != None:
            # check if they are the same type
            if (res1.db.name == res2.db.name):
                identity = "(S)"
            else:
                identity = '(D)'
            #end if

            printf("\n==== %s %s ==== %s\n", res1.name, res2.name, identity)

            # loop through all the atoms of res1
            for a1 in res1.atoms:
                a2=a1.map #check if this atom exists in res2
                a1.delta   = None
                if a2 and (a1.isAssigned() and a2.isAssigned()):
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
                if pc2 and (a1.isAssigned() and pc2.isAssigned()):
                    a1.deltaPC = a1.resonances().value - pc2.resonances().value
                #end if
            #end for
            
            for a1 in res1.atoms:
                a2=a1.map #check if this atom exists in res2
                doPrint = False
                swapText = ''
                if a1.delta:
                    if ((a1.isProton() and math.fabs( a1.delta ) >= limits[0]) or
                        (a1.isCarbon() and math.fabs( a1.delta ) >= limits[1]) or
                        (a1.isNitrogen() and math.fabs( a1.delta ) >= limits[2]) 
                       ):
                       doPrint = True
                       swapText = sprintf('%7.3f ', a1.delta)
                    #end if
                # check for altered assignment
                if a1.delta and a1.deltaPC and a1.pc.delta and a1.pc.deltaPC:
                    if (math.fabs( a1.deltaPC ) + math.fabs( a1.pc.deltaPC ) <  
                        math.fabs( a1.delta ) + math.fabs( a1.pc.delta )
                       ):
                       doPrint = True
                       swapText = sprintf("%7.3f >> Potential Swapped assignment %s and %s", a1.deltaPC, a1.map, a1.pc.map)
                #end if       
                if doPrint:
                    printf('%s  %s    %s    %7.3f  %s\n', identity, printatom( a1 ), printatom( a2 ), a1.delta, swapText)
                #end if
            #end for
        #end if
    #end for
#end def

def prepareNOEs( project ):
    # List Noes of project.upl on 'both' sides (X->Y and Y->X) for the molecule
    # Only take them when there is a map for both atoms and
    # when there is an assignment: the latter filters out NOEs generated by
    # Cyana from pseudoatoms
    for atm in project.molecule.allAtoms():
        atm.NOEs = NTset()      # NTset: list of objects; sets are equal if they share a common object
        atm.s    = atm.set()    # NTset instance with self, real/pseudo atom instances
    #end for
    for r in project.upl:
        for atm1,atm2 in r.atomPairs:
            if (atm1.map != None and atm1.isAssigned() and 
                atm2.map != None and atm2.isAssigned() and
                int(math.fabs(atm1.residue.resNum - atm2.residue.resNum)) >= minNOE
               ):
                atm1.NOEs.append( atm2 )
                atm2.NOEs.append( atm1 )
            #end if
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
    NTmessage('==> comparing NOEs %s with %s\n', projectA, projectB )

    prepareNOEs( projectA )
    prepareNOEs( projectB )
    
    count = 0

    for atmA1 in projectA.molecule.allAtoms():
        # check all the NOEs for this atom
        for atmA2 in atmA1.NOEs:

            if verbose:
                printf('Checking NOE %-40s : ', sprintf('(%s,%s)', atmA1, atmA2) )
            #end if
            
            atmB1 = atmA1.map
            atmB2 = atmA2.map
            found = False
            atmB1.setdefault('newNOEs', NTlist() )
            
            if atmB2 in atmB1.newNOEs:
                if verbose:  printf('Peak has been generated previously\n')
            else:
                # check all the possibilities of the set of atomB1
                for b1 in atmB1.s:
                    # A set comparison yields true if there is one or more common elements
                    if b1.NOEs == atmB2.s:
                        count += 1
                        found = True
                        if verbose: printf('Found NOE %s\n', sprintf('(%s,%s)', b1, atmB2.s) )
                        break
                    else:
                        pass
                    #end if
                #end for
            
                if (not found):
                    # generate an atmB1-atmB2 peak since this NOE (atmA1,atmA2) was not found in the B-set
                    # the reverse peak is accounted for by the (atmA2-atmA1) Noe
                    peak = atoms2peak( atmB1, atmB2, projectB.c13peaks, projectB.aropeaks, projectB.n15peaks )
                    if peak:
                        peak.xeasyColor = peakColor
                        count          += 1
                        atmB1.newNOEs.append( atmB2 )
                        if verbose:  printf('New %s\n', peak)
                    else: 
                        if verbose:  printf('Skipped because of lacking assignments\n')
                    #end if
                #end if
            #end if
        #end for
    #end for

    if verbose:
        NTmessage('==> Appended %d peaks\n', count )
    #end if
#end def

#------------------------------------------------------------------------------------
# START
#------------------------------------------------------------------------------------

# define, open, read the files
projectA = cyana2cing( defsA[0], defsA[1])
checkAssignments( projectA )
projectB = cyana2cing( defsB[0], defsB[1])
checkAssignments( projectB )
projectC = cyana2cing( defsC[0], defsC[1])
checkAssignments( projectC )

# compare A,B
mapMolecules( projectA.molecule, projectB.molecule, zip(defsA[2],defsB[2]) )
compareShifts( projectA, projectB )
compareNoeNetWork( projectA, projectB, verbose )
compareNoeNetWork( projectB, projectA, verbose )

# compare A, C
peakColor += 1
mapMolecules( projectA.molecule, projectC.molecule, zip(defsA[2],defsC[2]) )
compareShifts( projectA, projectC )
compareNoeNetWork( projectA, projectC, verbose )
compareNoeNetWork( projectC, projectA, verbose )

# compare B, C
peakColor += 1
mapMolecules( projectB.molecule, projectC.molecule, zip(defsB[2],defsC[2]) )
compareShifts( projectB, projectC )
compareNoeNetWork( projectB, projectC, verbose )
compareNoeNetWork( projectC, projectB, verbose )

# export and save by closing projects
projectA.export()
projectA.close()
projectB.export()
projectB.close()
projectC.export()
projectC.close()

