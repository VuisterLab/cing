"""

GVprocheck( ranges=None, verbose = True )

Molecule:
    procheck: <Procheck> object

Residue
    procheck: NTdict instance with procheck values for this residue



"""
#@PydevCodeAnalysisIgnore
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.svd import SVDfit
from cing.PluginCode.required.reqWhatif import *
from cing.core.molecule import dots
from cing.core.parameters import cingPaths
from math import cos, sin, pi, sqrt, fabs, log, exp
import math
from random import random
try:
    from cing.PluginCode.Whatif import Whatif # JFD: this statement causes this plugin to be skipped on systems without Whatif.
except:
    pass

def export2yasara( project, tmp=None ):
    """Export coordinates and restraints to yasara for further analysis; i.e. waterrefinement

    """

    yasara = 'Yasara'
    mol = project.molecule
    yasaraPath = project.mkdir( project.directories.export,  yasara )
    mol.export2xplor(project.path( project.directories.export, yasara, mol.name + '_%03d.pdb' ))

    for drl in project.distances:
        drl.export2xplor( project.path( project.directories.export, yasara, drl.name +'.tbl' ),
                        )
    #end for

    for drl in project.dihedrals:
        drl.export2xplor( project.path( project.directories.export, yasara, drl.name +'.tbl' ),

                        )
    #end for


    NTmessage('==> project.export2yasara: exported structure and restraints to "%s"', yasaraPath)
#end def


class dmElement():
    "Distance Matrix element for queeny"
    upperDefault = 256.0
    lowerDefault =   0.0
    uncertaintyDefault  =  5.545177 # log(256.0-0.0)
    uncertaintyMinvalue = -5.545177 # lowest value: log(1.0/256.0)

    def __init__(self, atm1, atm2 ):
        #NTdict.__init__( self, __CLASS__ = 'dmElement'  )
        self.atm1 = atm1
        self.atm2 = atm2
        self.upper  = dmElement.upperDefault
        self.lower  = dmElement.lowerDefault
        self.upperChange = 0.0
        self.uncertainty = dmElement.uncertaintyDefault
        self.flagged = False
    #end def

    def __str__(self):
        return '<dmElement>'

    def format(self):
        return sprintf('%s (%1s) %-20s %-20s  L: %7.3f  U: %7.3f  (%7.3f)  H: %7.3f',
                       self, str(self.flagged)[0:1], self.atm1, self.atm2, self.lower, self.upper, self.upperChange, self.uncertainty)

    def setLU(self, lower, upper ):
        """set self.upper if upper<self.upper
           set self.lower if lower >self.lower
           update self.upperChange
        """
        if upper < lower:
            return
        if upper < self.upper:
            self.upperChange = self.upper - upper
            self.upper = upper
        if lower > self.lower:
            self.lower = lower
        return
    #end def
#end class

class queeny( odict ):
    """
    Class to run a queen-like analysis

    """
    uncertainty1Key = 'uncertainty1'  # Key used for residue's and atom's uncertainty after topology triangulation
    uncertainty2Key = 'uncertainty2'  # Key used for residue's and atom's uncertainty after restraint triangulation
    informationKey  = 'information'   # Key used for residue's and atom's information, calculated from uncertainty1 and uncertainty2

    def __init__(self, project ):
        odict.__init__( self )
        self.project  = project
        self.molecule = project.molecule
        for atm in self.molecule.allAtoms():
            atm.neighbors = {}
    #end def

    def __setitem__(self, key, value):
        if key[0] > key[1]:
            key = (key[1],key[0])
        odict.__setitem__(self, key, value)
    #end def

    def __getitem__(self, key):
        if key[0] > key[1]:
            key = (key[1],key[0])
        return odict.__getitem__(self, key)
    #end def

    def setdefault(self, key, defaultValue):
        if key[0] > key[1]:
            key = (key[1],key[0])
        return odict.setdefault( self, key, defaultValue)
    #end def

    def has_key(self, key):
        if key[0] > key[1]:
            key = (key[1],key[0])
        return dict.has_key( self, key)
    #end def

    def __call__(self, index):
        return self[self._keys[index]]

    def execute(self, cutoff = 0.1):
        """Do the steps for a full analysis
        """
        # do the topology
        self.initTopology()
        self.triangulateAll( cutoff=cutoff, maxDepth = 4 )
        self.setUncertainty(queeny.uncertainty1Key)
        # do the restraints
        self.initRestraints()
        self.triangulateAll( cutoff=cutoff, maxDepth = 3 )
        self.setUncertainty(queeny.uncertainty2Key)
        # calculate the information content for each atom, residue
        self.setInformation(queeny.uncertainty1Key, queeny.uncertainty2Key, queeny.informationKey)
    #end def

    def initDmElement(self, atm1, atm2, lower=None, upper=None):
        """Initialize a dmElement entry for atm1, atm2
        optionally set lower and upper
        return dme
        """
        if not self.has_key((atm1.atomIndex,atm2.atomIndex)):
            dme = dmElement(atm1, atm2)
            self[(atm1.atomIndex,atm2.atomIndex)] = dme
        else:
            dme = self[(atm1.atomIndex,atm2.atomIndex)]
        #end if
        if lower != None and upper != None:
            dme.setLU(lower, upper)
        #end if
        return dme
    #end def

    def initTopology(self):
        NTdebug('queeny.initTopology: initializing topology')
        for atm in self.molecule.allAtoms():
            for n in atm.topology():

                if not self.has_key((atm.atomIndex,n.atomIndex)):

                    dme = dmElement(atm, n)
                    self[(atm.atomIndex,n.atomIndex)] = dme

                    # approximate values
                    if (atm.isProton() and n.isCarbon()) or (n.isProton() and atm.isCarbon()):
                        dme.setLU( 0.0, 1.08)
                    elif atm.isCarbon() and n.isCarbon():
                        dme.setLU( 0.0, 1.52) # alphatic C-C
                    elif (atm.isNitrogen() and n.isCarbon()) or (n.isNitrogen() and atm.isCarbon()):
                        dme.setLU( 0.0, 1.33) #N-C'; (N-CA) = 1.45
                    elif (atm.isNitrogen() and n.isProton()) or (n.isNitrogen() and atm.isProton()):
                        dme.setLU( 0.0, 0.98)
                    else:
                        dme.setLU( 0.0, 1.0)
                #end if
            #end for
        #end for
        for atm in self.molecule.atomsWithProperties('isMethyl','isCarbon'):
            #patch methyls
            protons = atm.attachedProtons()
            pseudo = protons[0].pseudoAtom()
            self.initDmElement(protons[0],protons[1], 0.0, 1.764)
            self.initDmElement(protons[0],protons[2], 0.0, 1.764)
            self.initDmElement(protons[1],protons[2], 0.0, 1.764)
            self.initDmElement(protons[0],pseudo, 0.0, 1.018) # geometric centre: 0.5*1.764/cos(30)
            self.initDmElement(protons[1],pseudo, 0.0, 1.018)
            self.initDmElement(protons[2],pseudo, 0.0, 1.018)
        #end if
        for atm in self.molecule.atomsWithProperties('isMethylene','isCarbon'):
            #patch methylenes
            protons = atm.attachedProtons()
            pseudo = protons[0].pseudoAtom()
            self.initDmElement(protons[0],protons[1], 0.0, 1.764)
            self.initDmElement(protons[0],pseudo, 0.0, 0.882) # geometric centre: 0.5*1.764
            self.initDmElement(protons[1],pseudo, 0.0, 0.882)
        #end if

        for res in self.molecule.residuesWithProperties('TYR'):
            HD1 = res.getAtom('HD1',INTERNAL_0)
            HD2 = res.getAtom('HD2',INTERNAL_0)
            QD  = res.getAtom('QD',INTERNAL_0)
            HE1 = res.getAtom('HE1',INTERNAL_0)
            HE2 = res.getAtom('HE2',INTERNAL_0)
            QE  = res.getAtom('QE',INTERNAL_0)

            self.initDmElement(HD1,HE1, 0.0, 2.46)
            self.initDmElement(HD2,HE2, 0.0, 2.46)

            self.initDmElement(HD1,HD2, 0.0, 4.27)
            self.initDmElement(HD1,QD, 0.0, 4.27/2.0) # geometric centre
            self.initDmElement(HD2,QD, 0.0, 4.27/2.0) # geometric centre
            self.initDmElement(HE1,HE2, 0.0, 4.27)
            self.initDmElement(HE1,QE, 0.0, 4.27/2.0) # geometric centre
            self.initDmElement(HE2,QE, 0.0, 4.27/2.0) # geometric centre
        #end if

        for res in self.molecule.residuesWithProperties('PHE'):
            HD1 = res.getAtom('HD1',INTERNAL_0)
            HD2 = res.getAtom('HD2',INTERNAL_0)
            QD  = res.getAtom('QD',INTERNAL_0)
            HE1 = res.getAtom('HE1',INTERNAL_0)
            HE2 = res.getAtom('HE2',INTERNAL_0)
            QE  = res.getAtom('QE',INTERNAL_0)
            HZ  = res.getAtom('HZ',INTERNAL_0)

            self.initDmElement(HD1,HE1, 0.0, 2.46)
            self.initDmElement(HD2,HE2, 0.0, 2.46)

            self.initDmElement(HD1,HD2, 0.0, 4.27)
            self.initDmElement(HD1,QD, 0.0, 4.27/2.0) # geometric centre
            self.initDmElement(HD2,QD, 0.0, 4.27/2.0) # geometric centre
            self.initDmElement(HE1,HE2, 0.0, 4.27)
            self.initDmElement(HE1,QE, 0.0, 4.27/2.0) # geometric centre
            self.initDmElement(HE2,QE, 0.0, 4.27/2.0) # geometric centre

            self.initDmElement(HD1,HZ, 0.0, 4.27)
            self.initDmElement(HD2,HZ, 0.0, 4.27)
            self.initDmElement(HE1,HZ, 0.0, 2.46)
            self.initDmElement(HE2,HZ, 0.0, 2.46)
            self.initDmElement(QE, HZ, 0.0, 0.5*2.46) # cos(alfa) = 4.27/2 / 2.46 => alfa=30; upper=sin(alfa)*2.46
            self.initDmElement(QD, HZ, 0.0, 3.70)     # cos(alfa) = 4.27/2 / 4.27 => alfa=60; upper=sin(alfa)*4.27
        #end if

        # update the neighbor lists
        self.setNeighbors(0)
    #end def

    def _calculateAverage(self, dr):
        """
        Calculate relative R-6 averaged distance contributions of dr
        Adapted from DistanceRestraint.calculateAverage

        returns None on error or list with relative contributions for each pair on success.
        """

        from cing.Libs.cython.superpose import Rm6dist #@UnresolvedImport

#        NTdebug('queeny._calculateAverage: %s')
        error = False    # Indicates if an error was encountered when analyzing restraint

        modelCount = dr.getModelCount()
        if not modelCount:
#            NTdebug('DistanceRestraint.calculateAverage: No structure models (%s)', self)
            return None
        #end if

        if len(dr.atomPairs) == 0:
            return None
        #end if

        models = range(modelCount)
        pair = 0
        Rm6distances = NTfill(0.0, len(dr.atomPairs))

        for atm1, atm2 in dr.atomPairs:

            # GV says: Check are done to prevent crashes upon rereading
            # datasets with floating/adhoc residues/atoms

            # skip trivial cases
            if atm1 == atm2:
                continue
            if atm1 == None or atm2 == None:
                continue
            #expand pseudoatoms
            atms1 = atm1.realAtoms()
            if atms1 == None:
                #NTdebug('DistanceRestraint.calculateAverage: %s.realAtoms() None (%s)', atm1, self)
                continue
            atms2 = atm2.realAtoms()
            if atms2 == None:
                #NTdebug('DistanceRestraint.calculateAverage: %s.realAtoms() None (%s)', atm2, self)
                continue
            for a1 in atms1:
                #print '>>>', a1.format()

                if len(a1.coordinates) != modelCount:
                    return None
                #end if

                for a2 in atms2:
                    #print '>>', atm1, a1, atm2, a2
                    if len(a2.coordinates) != modelCount:
                        return None
                    #end if

                    for i in models:
                        Rm6distances[pair] += Rm6dist(a1.coordinates[i].e, a2.coordinates[i].e)
                    #end for models
                #end for a2
            #end for a1
            pair += 1
        #end for

#        if self.distances[i] > 0.0:
#                self.distances[i] = math.pow(self.distances[i], -0.166666666666666667)
#        #end if

        psum = sum(Rm6distances)
        for i,value in enumerate(Rm6distances):
            Rm6distances[i] = value/psum
        #end for

        return Rm6distances
    #end def

    def initRestraints( self ):
        """
        Initialize restraints from restraint lists
        Only distances for now
        """

        NTdebug('queeny.initRestraints: adding restraints (# elements = %d)', len(self))

        for dme in self.itervalues():
            dme.upperChange = 0.0
        #end for

        nkeys = len(self)
        #print '>', nkeys
        count = 0
        for drl in self.project.distances:
            for dr in drl:
                if len(dr.atomPairs) == 1:
                    atm1,atm2 = dr.atomPairs[0]
                    upper = dr.upper
                    if dr.upper == None: # sometimes happens; i.e. entry 1but
                        upper = dmElement.upperDefault
                    lower = dr.lower
                    if dr.lower == None: # lower values sometimes set to None
                        lower = dmElement.lowerDefault
                    self.initDmElement(atm1, atm2, lower, upper)
                else:
                    # ambigious restraints
                    Rm6distances = self._calculateAverage( dr )
                    if Rm6distances == None:
                        NTwarning('queeny.initRestraints: failure to analyze %s', dr)
                        break
                    #endif

                    upper = dr.upper
                    if dr.upper == None: # sometimes happens; i.e. entry 1but
                        upper = dmElement.upperDefault
                    lower = dr.lower
                    if dr.lower == None: # lower values sometimes set to None
                        lower = dmElement.lowerDefault

                    # Hr: total uncertainty change associated with this restraint
                    # dH = Hmax - Hr : change in uncertainty
                    # Hi = Hmax - dH*frac : relative R-6 contribution of atom pair: sum(Hi) = Hr
                    Hmax = dmElement.uncertaintyDefault
                    Hr = math.log(upper-lower)
                    dH = Hmax - Hr
                    pair = 0
                    for atm1,atm2 in dr.atomPairs:
                        Hi = Hmax - Rm6distances[pair]*dH
                        self.initDmElement(atm1, atm2, lower, lower+math.exp(Hi))
                        pair += 1
                    #end for
                #end if
                count += 1
            #end for
        #end for

        NTdebug('queeny.initRestraints: %d restraints added (# elements = %d)', count, len(self))

        self.setNeighbors(nkeys) # update the neighbors for newly added
        #print '>>',len(self)
    #end def

    def initFlagged(self):
        for dme in self.itervalues():
            dme.flagged = False
        self.Nflagged = 0
    #end def

    def triangulate(self, atm1, atm2, atm3, dme12=None, dme23=None):
        """Triangulate the distance (atm1, atm3) from upper and lower bounds
        atm1-atm2 and atm2-atm3
        """
        #print '>>', atm1, atm2, atm3
        if atm1==atm3 or atm1==atm2 or atm2==atm3:
            return

        #print '>', atm1, atm2, atm3
        if self.has_key((atm1.atomIndex,atm3.atomIndex)):
            dme13 = self[(atm1.atomIndex,atm3.atomIndex)]
            if dme13.flagged:
                return
        else:
            dme13 = dmElement(atm1, atm3)
            self[(atm1.atomIndex,atm3.atomIndex)] = dme13

        if dme12 == None:
            dme12 = self[(atm1.atomIndex,atm2.atomIndex)]
        if dme23 == None:
            dme23 = self[(atm2.atomIndex,atm3.atomIndex)]

        upper12 = dme12.upper
        upper23 = dme23.upper
        lower12 = dme12.lower
        lower23 = dme23.lower
        dme13.setLU( max(lower12-upper23, lower23-upper12), upper12+upper23)
        dme13.flagged = True
    #end def

    def setNeighbors(self, keyIndex):
        """Set the neighbors form dme, starting at keyIndex"""
        nkeys = len(self)
        while keyIndex < nkeys:
            dme = self(keyIndex)
            atm1 = dme.atm1
            atm2 = dme.atm2
            atm2.neighbors[atm1] = dme
            atm1.neighbors[atm2] = dme
            keyIndex += 1
        #end for
    #end def


    def triangulateAll(self, cutoff=0.1, maxDepth=4):

        NTdebug('queeny.triangulateAll: starting')
        count = 1
        depth = 0

        while depth < maxDepth and count>0:

            self.sortedKeys()
            self.initFlagged()

            nkeys = len(self._keys)
            key = 0
            count = 0

            while key < nkeys:

                dme12 = self(key)

#                if key%100==0:
#                    NTdebug('queeny.triangulateAll: depth: %d nkeys %4d  key %4d  len %6d  count %4d %7.3f',
#                            depth, nkeys, key, len(self), count, dme12.upperChange)


                if dme12.upperChange < cutoff:
                    NTdebug('queeny.triangulateAll: depth: %d nkeys %4d  key %4d  len %6d  count %4d %7.3f  BREAK',
                            depth, nkeys, key, len(self), count, dme12.upperChange)
                    break

                atm1  = dme12.atm1
                atm2  = dme12.atm2

                for n1,dme in atm1.neighbors.iteritems(): # duplicate, because gets added onto original
                    self.triangulate(n1, atm1, atm2, dme, dme12)
                for n2,dme in atm2.neighbors.iteritems():
                    self.triangulate(atm1, atm2, n2, dme12, dme)
                dme12.upperChange=0.0
                dme12.flagged=True
                count += 1
                #end if
                key += 1
            #end while
            self.setNeighbors(nkeys) # Update neighborlists for newly added elements (starting at nkeys)

            NTdebug('queeny.triangulateAll: depth: %d nkeys %4d  key %4d  len %6d  count %4d', depth, nkeys, key, len(self), count)
            depth += 1
        #end while
    #end def

    def setUncertainty(self, key):
        """set the uncertainty for:
        - each atom[key] of molecule
        - each residue[key] of molecule
        """
        NTdebug('queeny.setUncertainty: starting')

        for dme in self.itervalues():
            if dme.upper > dme.lower:
                dme.uncertainty = max(dmElement.uncertaintyMinvalue, log(dme.upper-dme.lower))
            else:
                NTdebug('queeny.setUncertainty: problem with %s', dme.format())
                dme.uncertainty = dmElement.uncertaintyMinvalue
        #end for

        atms = self.molecule.allAtoms()
        l = len(atms)

        for atm in atms:
            atm[key] = 0.0

        for i in range(l):
            atm1 = atms[i]
            for j in range(i+1,l):
                atm2 = atms[j]
                if self.has_key((atm1.atomIndex,atm2.atomIndex)):
                    dme = self[(atm1.atomIndex,atm2.atomIndex)]
                    atm1[key] += dme.uncertainty
                    atm2[key] += dme.uncertainty
                else:
                    atm1[key] += dmElement.uncertaintyDefault
                    atm2[key] += dmElement.uncertaintyDefault
                #end if
            #end for
        #end for
        fl = 1.0/float(l-1)
        for atm in atms:
            atm[key] *= fl

        # residues
        for res in self.molecule.allResidues():
            res[key] = 0.0
        for atm in atms:
            atm.residue[key] += atm[key]
        for res in self.molecule.allResidues():
            res[key] /= len(res.atoms)

    #end def

    def setInformation(self, key1, key2, informationKey):
        """set the information for:
        - each atom of molecule
        - each residue of molecule
        using key1 and key2
        """
        NTdebug('queeny.setInformation: starting')
        for atm in self.molecule.allAtoms():
            if atm.has_key(key1) and atm.has_key(key2):
                atm[informationKey] = atm[key1]-atm[key2]
            else:
                atm[informationKey] = 0.0
        #end for
        for res in self.molecule.allResidues():
            if res.has_key(key1) and res.has_key(key2):
                res[informationKey] = res[key1]-res[key2]
            else:
                res[informationKey] = 0.0
        #end for
    #end def

    def zap(self, byItem):
        return NTzap(self.values(), byItem)

    def sortedKeys(self):
        a = zip(self._keys,NTzap(self.values(),'upperChange'))
        NTsort(a, 1, inplace=True)
        a.reverse()
        self._keys = NTzap(a,0)
    #end def

#end class



class PseudoRotation( SVDfit ):
    """
    Class to calculate PseudoRotation and pucker amplitudes of sugars in oligonucleotides
    (Altona and Sundaraligam, JACS, 94, 8205 1972).

    Definition:

        tauJ = tauM * cos( P + 0.8*pi*J )           (eq. 1 Altona and Sundaraligam)

        J = 0,1,2,3,4
        P = phaseangle
        tauM = pucker amplitude

    rewrite:

        tauJ = tauM * cos(P) * cos(tetaJ)  - tauM * sin(P) * sin(tetaJ)

        tetaJ = 0.8*pi*J

    rewrite:

        tauJ = c0 * cos(tetaJ) + c1 * sin(tetaJ)

        c0 = tauM*cos(P)
        c1 = -tauM*sin(P)

    solve c0,c1 by svd, with tetaJ as running variable, calculate

        P = atan(-c1/c0)
        tauM = c0/cos(P)

    # map of tauJ onto IUPAC dihedral angle defs
    angleMap = [
                    (0, 'NU2'),
                    (1, 'NU3'),
                    (2, 'NU4'),
                    (3, 'NU0'),
                    (4, 'NU1')
                ]
    """

    # map of tauJ onto IUPAC dihedral angle defs
    angleMap = [
                 (0, 'NU2'),
                 (1, 'NU3'),
                 (2, 'NU4'),
                 (3, 'NU0'),
                 (4, 'NU1')
               ]

    def __init__(self):
        tetas = []
        for J,dihed in self.angleMap:
            tetaJ = 0.8*pi*(J)
            tetas.append( tetaJ )
        #end for

        SVDfit.__init__(self, tetas, None, self.cos_sin, 2)
    #end def

    def calculate( self, residue ):
        """Calculate the PseudoRotation angles and pucker amplitudes
           for all models of residue.

           return a (Ntlist,NTlist,ETclassification) tuple with the PseudoRotation angles
           and pucker amplitudes, or (None,None,None) on error.

        """
        from cing import printf, NTerror, NTlist
        from math import atan2

        if not residue.hasProperties('nucleic'):
            NTerror('PseudoRotation.calculate: residue %s is not nucleic acid', residue)
            return (None,None,None)
        #end if

        diheds = []
        for J,dihed in self.angleMap:
            if dihed not in residue:
                NTerror('PseudoRotation.calculate: dihedral "%s" not defined for residue %s', dihed, residue)
                return (None,None,None)
            #end if
            diheds.append( residue[dihed] )
        #end for
        #print diheds

        nmodels = len(diheds[0])
        Plist = NTlist()
        tauMlist = NTlist()
        for i in range(nmodels):
            taus = []
            for d in diheds:
                taus.append(d[i])
            #end for

            # Do fit and calculate P and pucker
            c = self.fit(taus)
            P = atan2(-c[1],c[0])
            tauM = c[0]/cos(P)
            P = P/pi*180.0 # convert to degrees

            Plist.append(P)
            tauMlist.append(tauM)

            #printf( '%1d %8.2f %8.2f\n',i, P, tauM )
        #end for

        Plist.cAverage()
        Plist.limit(Plist.cav-180.0,Plist.cav+180.0) # Center around circular average,
        Plist.average()                              # to calculate sd in this step
        Plist.limit(0.0,360.0)                       # and rescale to 0,360 range
        tauMlist.average()

        ETname = self.getETnomenclature(Plist.cav,Plist.sd)
        return Plist,tauMlist,ETname
    #end def

    # ET definitions from: http://www.chem.qmul.ac.uk/iupac/misc/pnuc2.html#200
    # encoding superscript-lowerscript-E/T; underscore denotes 'absence'
    angleDefs = [( -9,   9, '32T'),
                 (  9,  27, '3_E'), # C3'-endo
                 ( 27,  45, '34T'),
                 ( 45,  63, '_4E'), # C4'-exo
                 ( 63,  81, 'O4T'),
                 ( 81,  99, 'O_E'), # O4'-endo
                 ( 99, 117, 'O1T'),
                 (117, 135, '_1E'), # C1'-exo
                 (135, 153, '21T'),
                 (153, 171, '2_E'), # C2'-endo
                 (171, 189, '23T'),
                 (189, 207, '_3E'), # C3'-exo
                 (207, 225, '43T'),
                 (225, 243, '4_E'), # C4'-endo
                 (243, 261, '4OT'),
                 (261, 279, '_OE'), # O4'-exo
                 (279, 297, '1OT'),
                 (297, 315, '1_E'), # C1'-endo
                 (315, 333, '12T'),
                 (333, 351, '_2E')  # C2'-exo
                 ]

    def getETnomenclature(self, pseudoAngle, error=0.0 ):
        """
        Return the E/T nomenclature corresponding to pseudoAngle+-error
        """
        #transform the pseudoAngle to [-9,351] range
        while pseudoAngle > 351.0:
            pseudoAngle -= 360.0
        while pseudoAngle < -9.0:
            pseudoAngle += 360.0

        if error == 0.0:
            for lower,upper,ETname in self.angleDefs:
                if pseudoAngle > lower and pseudoAngle <= upper:
                    return ETname
            #end for
        else:
            low = self.getETnomenclature( pseudoAngle - error, 0.0 )
            high = self.getETnomenclature( pseudoAngle + error, 0.0 )
            if low==high:
                return low
            else:
                return low + '/' + high
            #endif
        #end if

        return None
    #end def

    def cos_sin( teta, na ):
        """Return cos and sin for teta; NB na==2
        """
        from math import cos, sin, pi
        return [cos(teta),sin(teta)]
    #end def
    cos_sin = staticmethod(cos_sin)

#end class


def procheckString2float( string ):
    """Convert a string to float, return None in case of value of 999.90
    """
    result = float( string )
    if result == 999.90:
        return None
    else:
        return result
    #end if
#end def


class gvProcheck:
    #TODO: subclass this from ExecuteProgram
    """
    From Jurgen:

    Column id
    ^ Fortran variable
    ^ ^        Explanation
    ##############################
    ###################################################
    1 NXRES    residue number in procheck
    2 AA3      residue name
    3 BRKSYM   chain id as in PDB file
    4 SEQBCD   resdiue id as in PDB file??
    5 SUMMPL   secondary structure classification (DSSP?)
    6 MCANGS 1 phi
    7 MCANGS 2 psi
    8 MCANGS 3 omega
    9 SCANGS 1 chi 1
    0 SCANGS 2 chi 2
    1 SCANGS 3 chi 3
    2 SCANGS 4 chi 4
    3 HBONDE   Hydrogen bond energy
    4 DSDSTS ? statistics?
    5 MCANGS ?
    6 BVALUE   Crystallographic B factor
    7 MCBVAL   Mainchain B value
    8 SCBVAL   Sidechain B value
    9 OOIS 1 ?
    0 OOIS 2 ?
    1 MCBSTD Main chain bond standard deviation?
    2 SCBSTD Side chain bond standard deviation?


    #0000000000000000000000000000000000000000000000000000000000000000000000
      55GLY A  62 T-147.73 -20.13-166.50 999.90 999.90 999.90 999.90  -0.87   0.00 999.90   0.00  0.000  0.000 11 38  0.000  0.000
      56ASP A  63 e -78.77 161.06-173.97 -56.24 -71.93 999.90 999.90  -0.76   0.00  34.42   0.00  0.000  0.000 13 50  0.000  0.000
      57ARG A  64 E-104.07 124.65 166.81 177.50-170.21 179.43-172.18  -2.12   0.00  37.30   0.00  0.000  0.000 12 56  0.000  0.000
      58VAL A  65 E -87.26 117.24 175.76-157.64 999.90 999.90 999.90  -3.33   0.00  33.46   0.00  0.000  0.000 14 67  0.000  0.000
      59LEU A  66 E -99.01 -36.19-179.02  50.71 149.42 999.90 999.90  -2.74   0.00  31.00   0.00  0.000  0.000 13 50  0.000  0.000
      95PRO!A 102   -69.35 999.90 999.90 -24.86 999.90 999.90 999.90   0.00   0.00  37.72   0.00  0.000  0.000  4 13  0.000  0.000
      96TYR!B 205   999.90 -55.02-171.34-143.34 -89.71 999.90 999.90   0.00   0.00  34.80   0.00  0.000  0.000  2  5  0.000  0.000
      97LEU B 206    61.37 179.80 171.30-145.66  66.98 999.90 999.90   0.00   0.00  31.07   0.00  0.000  0.000  3  5  0.000  0.000
    """
    procheckDefs = NTdict(
    #   field       (startChar, endChar, conversionFunction)
        line      = (  0,  4, int ),
        resName   = (  4,  7, str ),
        chain     = (  8,  9, str ),
        resNum    = ( 10, 13, int ),
        secStruct = ( 14, 15, str ),
        PHI       = ( 15, 22, procheckString2float ),
        PSI       = ( 22, 29, procheckString2float ),
        OMEGA     = ( 29, 36, procheckString2float ),
        CHI1      = ( 36, 43, procheckString2float ),
        CHI2      = ( 43, 50, procheckString2float ),
        CHI3      = ( 50, 57, procheckString2float ),
        CHI4      = ( 57, 64, procheckString2float )
    )

    def __init__(self, project ):
        """
        Procheck class allows running procheck_nmr and parsing of results
        """
        self.molecule     = project.molecule
        self.rootPath     = project.mkdir( project.molecule.name, project.moleculeDirectories.procheck  )
#        self.runProcheck  = ExecuteProgram( cing.paths.procheck_nmr,
#                                            rootPath = self.rootPath,
#                                            redirectOutput= False
#                                          )
        self.ranges  = None
        self.summary = None
    #end def

    def run(self, ranges=None ):
        NTmessage('==> Running procheck_nmr, ranges %s, results in "%s" ...', ranges, self.rootPath)

        # Convert the ranges and translate into procheck_nmr format
        selectedResidues = self.molecule.setResiduesFromRanges( ranges )
        NTsort(selectedResidues, 'resNum', inplace=True)
        # reduce this sorted list to pairs start, stop
        self.ranges = selectedResidues[0:1]
        for i in range(0,len(selectedResidues)-1):
            if ((selectedResidues[i].resNum < selectedResidues[i+1].resNum - 1) or
                (selectedResidues[i].chain != selectedResidues[i+1].chain)
               ):
                self.ranges.append(selectedResidues[i])
                self.ranges.append(selectedResidues[i+1])
            #end if
        #end for
        self.ranges.append(selectedResidues[-1])
#        NTdebug( 'Procheck ranges %d', self.ranges )
        #generate the ranges file
        path = os.path.join( self.rootPath, 'ranges')
        fp = open( path, 'w' )
        for i in range(0,len(self.ranges),2):
            fprintf( fp, 'RESIDUES %3d %2s  %3d %2s\n', self.ranges[i].resNum, self.ranges[i].chain.name,
                                                        self.ranges[i+1].resNum, self.ranges[i+1].chain.name
                   )
        #end for
        fp.close()

        #export a PDB file
        path = os.path.join( self.rootPath, self.molecule.name + '.pdb')
        #print path
        self.molecule.toPDBfile( path, convention=cing.PDB )

        # run procehck
        runProcheck  = ExecuteProgram( cingPaths.procheck_nmr,
                                       rootPath = self.rootPath,
                                       redirectOutput= True
                                    )
        runProcheck( self.molecule.name +'.pdb ranges' )
        del( runProcheck )

        # Parse results
        self.parseResult()
    #end def

    def _parseProcheckLine( self, line ):
        """
        Internal routine to parse a single line
        Return result, which is a dict type or None
        on error (i.e. too short line)
        """
    #    print ">>", line
        result = {}
        if (len(line) >= 64):
            for field,fieldDef in self.procheckDefs.iteritems():
                c1,c2,func = fieldDef
                result[ field ] = func(line[c1:c2])
            #end for
        else:
            return None
        #end if

    #    print result
        return result
    #end def

    def parseResult( self ):
        """
        Get summary

        Parse procheck .rin files and store result in procheck NTdict
        of each residue of mol

        """
        path = os.path.join( self.rootPath, sprintf('%s.sum', self.molecule.name) )
        fp = open( path, 'r' )
        if not fp:
            NTerror('gvProcheck.parseResult: %s not found', path)
        else:
            self.summary = ''.join(fp.readlines())
            fp.close()
        #end if

        for i in range(1,self.molecule.modelCount+1):
            path = os.path.join( self.rootPath, sprintf('%s_%03d.rin', self.molecule.name, i) )
            #print '> parsing >', path

            for line in AwkLike( path, minLength = 64, commentString = "#" ):
                result = self._parseProcheckLine( line.dollar[0] )
                chain   = result['chain']
                resNum  = result['resNum']
                residue = self.molecule.decodeNameTuple((cing.PDB,chain,resNum,None))
                if not residue:
                    NTerror('Procheck.parseResult: residue not found (%s,%d)', chain, resNum )
                else:

                    residue.setdefault( 'procheck', NTstruct() )
                    for field,value in result.iteritems():
                        residue.procheck.setdefault( field, NTlist() )
                        residue.procheck[field].append( value )
                    #end for
                #end if
                del( result )
            #end for
        #end for
    #end def
#end class



def procheck_old( project, ranges=None ):
    """
    Adds <Procheck> instance to molecule. Run procheck and parse result
    """
    if not project.molecule:
        NTerror('ERROR procheck: no molecule defined\n')
        return None
    #end if

    if project.molecule.has_key('procheck'):
        del(project.molecule.procheck)
    #end if

    pcheck = gvProcheck( project )
    if not pcheck: return None

    pcheck.run( ranges=ranges )
    project.molecule.procheck = pcheck

    return project.molecule.procheck
#end def



def mkJmolMacros( project ):
    """
    Generate the Jmol macros in the moleculeDirectories.Jmol dir.
    """
    if not project.molecule:
        NTerror('mkJmolMacros: no molecule defined')
        return
    #end if

    # save first model
    molName = project.molecule.name + '_0'
    path = project.moleculePath('jmol', molName + '.pdb')
    project.molecule.toPDBfile( path, model=0 )

#    mkYasaraByResidueMacro(project, ['procheck','gf'],
#                           minValue=-3.0,maxValue=1.0,
#                           reverseColorScheme=True,
#                           path=project.moleculePath('yasara','gf.mcr')
#                          )
#
#    mkYasaraByResidueMacro(project, ['Qshift','backbone'],
#                           minValue=0.0,maxValue=0.05,
#                           reverseColorScheme=False,
#                           path=project.moleculePath('yasara','Qshift.mcr')
#                          )

    mkJmolByResidueROGMacro(project, object=1, path=project.moleculePath('jmol','rog.spt'))
#end def

def mkJmolByResidueROGMacro( project, object=None, path=None, stream=None ):
    if path:
        stream = open( path, 'w')
    elif stream:
        pass
    else:
        stream = sys.stdout
    #end if

    if not stream:
        NTerror('mkJmolByResidueROGMacro: undefined output stream')
        return
    #endif

    if object==None:
        fprintf( stream, 'select *; color grey\n' )
    else:
        fprintf( stream, 'select */%d; color grey\n', object )


    for res in project.molecule.allResidues():
        if object==None:
            fprintf( stream, 'select %d:%s.*; ', res.resNum, res.chain.name )
        else:
            fprintf( stream, 'select %d:%s.*/%d; ', res.resNum, res.chain.name, object )
        fprintf( stream, 'color %s\n', res.rogScore.colorLabel )
    #end for

    if path:
        stream.close()
#end def



"""
======================COPYRIGHT/LICENSE START==========================

ValidationBasic.py: Part of the CcpNmr Analysis program

Copyright (C) 2004 Wayne Boucher and Tim Stevens (University of Cambridge)

=======================================================================

This file contains reserved and/or proprietary information
belonging to the author and/or organisation holding the copyright.
It may not be used, distributed, modified, transmitted, stored,
or in any way accessed, except by members or employees of the CCPN,
and by these people only until 31 December 2005 and in accordance with
the guidelines of the CCPN.

A copy of this license can be found in ../../../license/CCPN.license.

======================COPYRIGHT/LICENSE END============================

for further information, please contact :

- CCPN website (http://www.ccpn.ac.uk/)

- email: ccpn@bioc.cam.ac.uk

- contact the authors: wb104@bioc.cam.ac.uk, tjs23@cam.ac.uk
=======================================================================

If you are using this software for academic purposes, we suggest
quoting the following references:

===========================REFERENCE START=============================
R. Fogh, J. Ionides, E. Ulrich, W. Boucher, W. Vranken, J.P. Linge, M.
Habeck, W. Rieping, T.N. Bhat, J. Westbrook, K. Henrick, G. Gilliland,
H. Berman, J. Thornton, M. Nilges, J. Markley and E. Laue (2002). The
CCPN project: An interim report on a data model for the NMR community
(Progress report). Nature Struct. Biol. 9, 416-418.

Wim F. Vranken, Wayne Boucher, Tim J. Stevens, Rasmus
H. Fogh, Anne Pajon, Miguel Llinas, Eldon L. Ulrich, John L. Markley, John
Ionides and Ernest D. Laue. The CCPN Data Model for NMR Spectroscopy:
Development of a Software Pipeline. Accepted by Proteins (2004).

===========================REFERENCE END===============================

"""

#VALID_VALUE_TYPE_ATTRS = {type(0.0): 'floatValue',
#                          type(1): 'intValue',
#                          type('a'): 'textValue',
#                          type(True): 'booleanValue'}
#
#
## # # # # # #  C I N G  E X A M P L E  # # # # # # #
#
#def storeRogScores(ccpnEnsemble, scores, context='CING'):
#   # Assumes scores in same order as residues
#
#   keyword    = 'ROG'
#   definition = 'Overall per-residue validation score for display. ROG=Red/Orange/Green'
#   synonym    = 'Residue ROG Score'
#
#   validStore = getEnsembleValidationStore(ccpnEnsemble, context,
#                                           keywords=[keyword, ],
#                                           definitions=[definition, ],
#                                           synonyms=[synonym, ])
#
#   residues = []
#   for chain in ccpnEnsemble.sortedCoordChains():
#     residues.extend(chain.sortedResidues())
#
#   storeResidueValidations(validStore, context, keyword, residues, scores)
#
## # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
#
#def getEnsembleValidationStore(ensemble, context, keywords,
#                               definitions=None, synonyms=None):
#  """Descrn: Get a CCPN object to store validation results for an ensemble
#             in a given program context. Requires a list of keywords which will
#             be used in this context. Allows optional lists of definitions and
#             user-friendly synonyms for these keywords.
#     Inputs: MolStructure.StructureEnsemble, Word, List of Words,
#             List of Lines, List of Words
#     Output: StructureValidation.StructureValidationStore
#  """
#
#  memopsRoot = ensemble.root
#  eid = '%s_%s' % (context, ensemble.guid)
#  validStore = ensemble.findFirstStructureValidationStore(name=eid)
#
#  if validStore is None:
#    validStore = memopsRoot.newStructureValidationStore(name=eid,
#                                      structureEnsemble=ensemble)
#
#  validStore.nmrProject = memopsRoot.currentNmrProject
#
#  keywordStore = memopsRoot.findFirstKeywordDefinitionStore(context=context)
#
#  if not keywordStore:
#    keywordStore = memopsRoot.newKeywordDefinitionStore(context=context)
#
#  for i, keyword in enumerate(keywords):
#    keywordDefinition = keywordStore.findFirstKeywordDefinition(keyword=keyword)
#
#    if not keywordDefinition:
#      keywordDefinition = keywordStore.newKeywordDefinition(keyword=keyword)
#
#    if definitions and (i < len(definitions)):
#      keywordDefinition.explanation = definitions[i]
#
#    if synonyms and (i < len(synonyms)):
#      keywordDefinition.name = synonyms[i]
#
#  return validStore
#
#
#def getValidationObjects(validStore, className, context, keyword):
#  """Descrn: Find a given class of validation objects in a validation store
#             in a given (program) context, with a given keyword.
#     Inputs: StructureValidation.StructureValidationStore, Word, Word, Word
#     Output: List of StructureValidation.Validations
#  """
#  return validStore.findAllValidationResults(context=context,
#                                             keyword=keyword,
#                                             className=className)
#
#
#def replaceValidationObjects(validStore, className, keyword, context, dataList):
#  """Descrn: Store validation data as CCPN validation objects,
#             overwriting all previous records of such information
#             in the validation store object. Finds a given class of
#             validation objects a given keyword in a given context.
#             The input data list is a 2-tuple containing a list of the
#             CCPN objects validated and the value associated with that
#             validation. Note that the validated CCPN object types must
#             match the type required by the validation object className.
#             *NOTE* this is a slow function and should often be replaced
#             with a class-specific equivalent.
#     Inputs: StructureValidation.StructureValidationStore, Word, Word, Word,
#             List of 2-Tuples of (List of CCPN objects, )
#     Output: None
#  """
#
#  for validObj in getValidationObjects(validStore, className, keyword, context):
#    validObj.delete()
#
#  newObject = getattr(validStore, 'new%s' % className)
#
#  validatedObjAttr = None
#
#  for validatedObjects, value in dataList:
#    validObj = newObject(context=context, keyword=keyword)
#
#    if not validatedObjAttr:
#      for role in validObj.metaclass.roles:
#        if role.locard == 0:
#          validatedObjAttr = role.name
#
#    if validatedObjAttr:
#      setattr(validObj, validatedObjAttr, validatedObjects)
#
#    valueAttr = VALID_VALUE_TYPE_ATTRS.get(type(value), 'textValue')
#    setattr(validObj, valueAttr, value)
#
#
#def getResidueValidation(validStore, residue, context, keyword):
#  """Descrn: Get any existing residue validation results from a CCPN
#             validation store which have the given keywords in the
#             given (program) context.
#             *NOTE* This function may be quicker than using the generic
#             getValidationObjects() because the link is queried from the
#             validated object, not the validation store, which often
#             has fewer total validation objects.
#     Inputs: StructureValidation.StructureValidationStore,
#             MolStructure.Residue, Word, Word
#     Output: StructureValidation.ResidueValidation
#  """
#
#  # Define data model call to find existing result
#  findValidation = residue.findFirstResidueValidation
#
#  validObj = findValidation(structureValidationStore=validStore,
#                            context=context, keyword=keyword)
#
#  return validObj
#
#
#def storeResidueValidations(validStore, context, keyword, residues, scores):
#  """Descrn: Store the per-residue scores for a an ensemble within
#             CCPN validation objects.
#             *NOTE* This function may be quicker than using the generic
#             replaceValidationObjects() because it is class specific
#     Inputs: StructureValidation.StructureValidationStore,
#             List of MolStructure.Residues, List if Floats
#     Output: List of StructureValidation.ResidueValidations
#  """
#
#  validObjs = []
#
#  # Define data model call for new result
#  newValidation = validStore.newResidueValidation
#
#  for i, residue in enumerate(residues):
#
#    score = scores[i]
#
#    # Find any existing residue validation objects
#    validObj = getResidueValidation(validStore, residue, context, keyword)
#
#    # Validated object(s) must be in a list
#    residueObjs = [residue, ]
#
#    # Make a new validation object if none was found
#    if not validObj:
#      validObj = newValidation(context=context, keyword=keyword,
#                               residues=residueObjs)
#
#    # Set value of the score
#    validObj.floatValue = score
#
#    validObjs.append(validObj)
#
#  return validObjs

VALID_VALUE_TYPE_ATTRS = {type(0.0): 'floatValue',
                          type(1): 'intValue',
                          type('a'): 'textValue',
                          type(True): 'booleanValue'}


# # # # # # #  C I N G  E X A M P L E  # # # # # # #

def storeRogScores(ccpnEnsemble, scores, context='CING'):
   # Assumes scores in same order as residues

   keyword    = 'ROG'
   definition = 'Overall per-residue validation score for display. ROG=Red/Orange/Green'
   synonym    = 'Residue ROG Score'

   validStore = getEnsembleValidationStore(ccpnEnsemble, context,
                                           keywords=[keyword, ],
                                           definitions=[definition, ],
                                           synonyms=[synonym, ])

   residues = []
   for chain in ccpnEnsemble.sortedCoordChains():
     residues.extend(chain.sortedResidues())

   storeResidueValidations(validStore, context, keyword, residues, scores)

# # # # # # # # # # # # # # # # # # # # # # # # # # #



def getEnsembleValidationStore(ensemble, context, keywords=None,
                               definitions=None, synonyms=None,
                               software=None):
  """Descrn: Get a CCPN object to store validation results for an ensemble
             in a given program context. Requires a list of keywords which will
             be used in this context. Allows optional lists of definitions and
             user-friendly synonyms for these keywords.
             Optional argument for passing software specification (otherwise
             defaults to current CcpNmr Analysis)
     Inputs: MolStructure.StructureEnsemble, Word, List of Words,
             List of Lines, List of Words, Method.Software
     Output: Validation.ValidationStore
  """

  if not keywords:
    keywords = []

  memopsRoot = ensemble.root
  eid = '%s_%s' % (context, ensemble.guid)
  validStore = ensemble.findFirstValidationStore(name=eid)

  if validStore is None:
    software = getSoftware(memopsRoot)
    validStore = memopsRoot.newValidationStore(name=eid, software=software,
                                               structureEnsemble=ensemble)

  validStore.nmrProject = memopsRoot.currentNmrProject

  keywordStore = memopsRoot.findFirstKeywordDefinitionStore(context=context)

  if not keywordStore:
    keywordStore = memopsRoot.newKeywordDefinitionStore(context=context)

  for i, keyword in enumerate(keywords):
    keywordDefinition = keywordStore.findFirstKeywordDefinition(keyword=keyword)

    if not keywordDefinition:
      keywordDefinition = keywordStore.newKeywordDefinition(keyword=keyword)

    if definitions and (i < len(definitions)):
      keywordDefinition.explanation = definitions[i]

    if synonyms and (i < len(synonyms)):
      keywordDefinition.name = synonyms[i]

  return validStore


def getValidationObjects(validStore, className, context, keyword):
  """Descrn: Find a given class of validation objects in a validation store
             in a given (program) context, with a given keyword.
     Inputs: Validation.ValidationStore, Word, Word, Word
     Output: List of Validation.Validations
  """
  return validStore.findAllValidationResults(context=context,
                                             keyword=keyword,
                                             className=className)


def replaceValidationObjects(validStore, className, keyword, context, dataList):
  """Descrn: Store validation data as CCPN validation objects,
             overwriting all previous records of such information
             in the validation store object. Finds a given class of
             validation objects a given keyword in a given context.
             The input data list is a 2-tuple containing a list of the
             CCPN objects validated and the value associated with that
             validation. Note that the validated CCPN object types must
             match the type required by the validation object className.
             *NOTE* this is a slow function and should often be replaced
             with a class-specific equivalent.
     Inputs: Validation.ValidationStore, Word, Word, Word,
             List of 2-Tuples of (List of CCPN objects, )
     Output: None
  """

  for validObj in getValidationObjects(validStore, className, keyword, context):
    validObj.delete()

  newObject = getattr(validStore, 'new%s' % className)

  validatedObjAttr = None

  for validatedObjects, value in dataList:
    validObj = newObject(context=context, keyword=keyword)

    if not validatedObjAttr:
      for role in validObj.metaclass.roles:
        if role.locard == 0:
          validatedObjAttr = role.name

    if validatedObjAttr:
      setattr(validObj, validatedObjAttr, validatedObjects)

    valueAttr = VALID_VALUE_TYPE_ATTRS.get(type(value), 'textValue')
    setattr(validObj, valueAttr, value)


def getResidueValidation(validStore, residue, context, keyword):
  """Descrn: Get any existing residue validation results from a CCPN
             validation store which have the given keywords in the
             given (program) context.
             *NOTE* This function may be quicker than using the generic
             getValidationObjects() because the link is queried from the
             validated object, not the validation store, which often
             has fewer total validation objects.
     Inputs: Validation.ValidationStore,
             MolStructure.Residue, Word, Word
     Output: Validation.ResidueValidation
  """

  # Define data model call to find exiting result
  findValidation = residue.findFirstResidueValidation

  validObj = findValidation(validationStore=validStore,
                            context=context, keyword=keyword)

  return validObj


#def parseWhatifSummary( wiSummary ):
#    from cing import NaN
#    foundWHATIF = False
#    for line in wiSummary.splitlines():
#        if not foundWHATIF and 'Structure Z-scores' in line:
#            foundWHATIF = True
#            break
#    #end for
#
#    #print foundWHATIF
#    rama = NaN
#    chi12 = NaN
#    bb = NaN
#    if foundWHATIF:
#        for i,line in enumerate(wiSummary.splitlines()):
#            #print i,'>',line
#            if 'Ramachandran plot appearance' in line:
#                rama = float(line[35:min(42,len(line)-1)])
#            if 'chi-1/chi-2 rotamer normality' in line:
#                chi12 = float(line[35:min(42,len(line)-1)])
#            if 'Backbone conformation' in line:
#                bb = float( line[35:min(42,len(line)-1)])
#        #end for
#    #end if
#    return (rama, chi12, bb)
##end def


# register the functions
methods  = [(procheck_old, None),
            (mkJmolByResidueROGMacro,None),
            (mkJmolMacros,None)
           ]
#saves    = []
#restores = []
exports  = [
            (export2yasara,None)
           ]

