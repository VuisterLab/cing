"""
Script to compare the shifts of two projects
Adapted from CompareResonances2.py, written for Lieke PDZ analysis

GWV; 19Feb 2014
First used for CaM analysis JBC paper
"""

import cing
from cing import constants
from cing.core import pid
from cing.core import project
from cing.Libs import io
from cing.Libs import fpconst
import math
from cing.Libs.NTutils import fprintf, sprintf, NTlist, nTmessage
from math import fabs

#------------------------------------------------------------------------------------------
# Parameters
#------------------------------------------------------------------------------------------
hydrogenFactor = 7.0 # weight of 1H delta shift relative to 13C/15N

#------------------------------------------------------------------------------------------
# Routines
#------------------------------------------------------------------------------------------
def compareAtms(atm1, atm2):
    """Compare the shifts of two atoms, store in delta attribute
    """
    #print '>>', atm1, atm2
    if (atm1 and atm1.isAssigned() and atm2 and atm2.isAssigned()):
        delta = atm2.shift()-atm1.shift()
        delta = fabs( delta )
        if (atm1.db.spinType == '1H'):
            delta *= hydrogenFactor
        #end if

        #expand the delta shift to real atoms
        if atm1.isPseudoAtom():
            atms = atm1.realAtoms()
        else:
            atms = NTlist(atm1)
        #end if
        for atm in atms:
            atm.delta = delta
        #end for
#        print '>>', atms.format(), delta
    #end if
#end def


def mkYasaraMacro(mol, attr, path):
    """Create a Yasara macro using attr
    """
    nTmessage('==> Creating macro %s\n', path)
    yasara = open(path, 'w')

    fprintf(yasara, 'Console off\n')
    fprintf(yasara, 'ColorAtom All,Gray\n')
    fprintf(yasara, 'PropAtom All,-999\n')

    for atm in mol.allAtoms():
        an = atm.translate('PDB')
        # tmp hack, convert to YASARA format since PDB HB3 does not work
        if an and an[0:1].isdigit():
            an = an[1:]
        #end if
#        print atm, an
        if an and atm.has_key(attr):
#            print '>',atm[attr]
            a = 1.0 - atm[attr]
            a = max( a, 0.0 )
            fprintf(yasara, 'PropAtom residue %d atom %s,%.2f\n', atm.residue.resNum, an, a)
        #end if
    #end for

    fprintf(yasara, 'Console off\n')
    fprintf(yasara, 'ColorAll Property\n')
    fprintf(yasara, 'Console on\n')
    yasara.close()
#end def


def average(atm):
    """Average value of atom with those of assigned neighbors"""
    if atm.has_key('deltaAverage'): del(atm['deltaAverage'])
    values = NTlist()
    for a in [atm] + atm.topology():
        if 'delta' in a and not fpconst.isNaN(a['delta']):
            #print '>>', a, a.delta
            values.append(a.delta)
        #end if
    #end for
    #print '>>', atm, values
    if len(values) > 0:
        atm.deltaAverage, sd, n = values.average()
        #print atm.deltaAverage, sd, n
#end def


def mapMolecule(molA, molB):
    """
    Map mol, chains, residues and atoms instances between molA and molB.
    set a map attribute for all of these: None indicates no map found.
    """
    molA.map = molB
    molB.map = molA
    #
    for objA in molA.allChains() + molA.allResidues() + molA.allAtoms():
        objA.map = None
    for objB in molB.allChains() + molB.allResidues() + molB.allAtoms():
        objB.map = None

    for objA in molA.allChains() + molA.allResidues() + molA.allAtoms():
        pidA = objA.asPid()
        # create the corresponding pid for objB
        pidB = pidA.modify(0,molB.name)
        if pidA.type == 'Atom':
            # change residue to include matching atoms; to deal with mutations in the sequence
            # CaM: GLU67   CaM10: GLN67; resnum's are the same
            resNum = objA._parent.resNum
            pidB = pid.new('Atom', molB.name, 'A', molB.A[resNum].name, objA.name)
        #end if
        # see if objB exists
        objB = molB.project.getByPid(pidB)
        if objB is not None:
            objA.map = objB
            objB.map = objA
        #end if
    #end for
#end def


def compare( project1, project2 ):
    """Compare the shifts of all equivalent atoms.
    """
    if project1 is None or project1.molecule is None:
        return True
    if project2 is None or project2.molecule is None:
        return True

    mol1 = project1.molecule
    mol2 = project2.molecule

    nTmessage('==> comparing %s and %s\n', mol1, mol2)

    mapMolecule(mol1, mol2)

    for atm1 in mol1.allAtoms():
        if atm1.has_key('delta'): del(atm1['delta'])
    #end for
    for atm1 in mol1.allAtoms():
        compareAtms(atm1, atm1.map)
    #end for

    # average; taken the values of directly bonded atoms into account
    for atm in mol1.allAtoms():
        average(atm)
    #end for

    # generate scripts
    mkYasaraMacro(mol1, 'delta', sprintf('yasara-%s-%s.mcr', project1.name, project2.name))
    mkYasaraMacro(mol1, 'deltaAverage', sprintf('yasara-%s-%s-averaged.mcr', project1.name, project2.name))
#end def


def printShifts(project):
    """
    Print delta shifts after mapping and averaging
    """
    fname = 'shifts-{0}-{1}.txt'.format(project.name, project.molecule.map.project.name)
    with open(fname,'w') as fp:
        fp.write('# atom  resNum shift(%s)  shift(%s)  delta  deltaAverage\n' %
                 (project.name, project.molecule.map.project.name))
        for atm in project.molecule.allAtoms():
            delta = atm.setdefault('delta', fpconst.NaN)
            deltaAverage = atm.setdefault('deltaAverage', fpconst.NaN)
            if atm.map is None:
                shift2 = fpconst.NaN
            else:
                shift2 = atm.map.shift()
            msg = '{0:20s} {1:4d}  {2:7.3f}  {3:7.3f}  {4:7.3f}  {5:7.3f}\n'.format(
                        atm, atm.residue.resNum, atm.shift(), shift2, delta, deltaAverage)
            #io.message(msg)
            fp.write(msg)
        #end for
    #end with
#end def


def openProject(path, status):
    p = project.open(path, status)
    if p is None:
        return None
    if p.molecule is None:
        return None
    p.molecule.mergeResonances(append=False)
    return p
#end def


def calibrateShifts(project):
    """
    Idea: use dCa, dCb
    dCa:  H: +3.5  S: -1.5 (centre: 1.0, spread 5.0 ppm)
    dCb:  S: +3.0  H: -0.5 (centre: 1.25 spread 3.5 ppm)

    0.7(dCa-1.0) + (dCb-1.25) should be zero
    0.7dCa + dCb - 1.95 should be zero

    """
    diffs = NTlist()
    for res in project.molecule.allResidues():
        if 'CA' in res and res.CA.isAssigned() and \
           'CB' in res and res.CB.isAssigned():
            dCa = res.CA.shift() - res.CA.db.shift.average
            dCb = res.CB.shift() - res.CB.db.shift.average
            diff = 0.7*dCa+dCb-1.95
            diffs.append(diff)
    #end for
    return diffs
#end def


#------------------------------------------------------------------------------------------
# End routines
#------------------------------------------------------------------------------------------

# pCaM10V514 = openProject(CaM10V514[0], CaM10V514[1])
# pCaM10 = openProject(CaM10[0], CaM10[1])
# # correct 13C CaM10:
# for atm in pCaM10.molecule.allAtoms():
#     if atm.isCarbon and atm.isAssigned():
#         atm.resonances[0].value -= 0.975
# #pCaMWTV514 = openProject(CaMWTV514[0], CaMWTV514[1])
#
# compare(pCaM10V514, pCaM10)
# printShifts(pCaM10V514)

#switch on or off
if True:
    #fedir
    cam10v5 = openProject('20140327CaM10V514',constants.PROJECT_NEWFROMCCPN)
    cam1v5 = openProject('20140401CaM1V514',constants.PROJECT_NEWFROMCCPN)
    # deassign cam1v5 Arg37.C
    cam1v5.molecule.A[37].C.resonances().value = fpconst.NaN
    #ben
    cam10 = openProject('20140407Cam10',constants.PROJECT_NEWFROMCCPN)
    cam1 = openProject('20140407Cam1',constants.PROJECT_NEWFROMCCPN)

    cam10v6 = openProject('20140403Cam10V611',constants.PROJECT_NEWFROMCCPN)
    cam1v6 = openProject('20140403CaM1V611',constants.PROJECT_NEWFROMCCPN)

#end if

#switch on or off
if True:
    #CaM10 V5
    compare(cam10v5,cam10)
    printShifts(cam10v5)

    #CaM1 V5
    compare(cam1v5,cam1)
    printShifts(cam1v5)

    #Fedir
    compare(cam1v5,cam10v5)
    printShifts(cam1v5)

    #Ben
    compare(cam1, cam10)
    printShifts(cam1)

    #CaM10 V6
    compare(cam10v6,cam10)
    printShifts(cam10v6)

    #CaM1 V6
    compare(cam1v6,cam1)
    printShifts(cam1v6)

    #CaM1 V5/V6
    compare(cam1v5,cam1v6)
    printShifts(cam1v5)

    #CaM1 V5/V6
    compare(cam10v5,cam10v6)
    printShifts(cam10v5)

#end if

