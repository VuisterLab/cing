"""
Basic QUEEN implementation for restraint information calculation

project.runQueeny() executes the queeny routine.
Atoms obtain attribute 'information' (defined in QUEENY_INFORMATION_STR) with information value.
Residues obtain attribute 'information' with information value that is averaged over all atoms

"""
import math

import cing
from cing import constants
from cing.core import validation
from cing.core import molecule
#from cing. import sml
from cing.Libs import io
from cing.Libs import jsonTools

from cing.Libs.Adict import Adict
from cing.Libs.NTutils import NTsort
from cing.Libs.NTutils import nTerror
from cing.Libs.NTutils import nTtracebackError
from cing.Libs.NTutils import nTwarning
from cing.Libs.NTutils import nTmessage
from cing.Libs.NTutils import nTdebug
from cing.Libs.NTutils import nTfill
from cing.Libs.NTutils import nTzap
from cing.Libs.NTutils import Odict

from cing.Libs.io import sprintf

try:
    import pyximport
    pyximport.install()
    import cing.Libs.cython.superpose as superpose
# GWV 20140501: changed calls
#    from cing.Libs.cython.superpose import NTcMatrix
#    from cing.Libs.cython.superpose import NTcVector
#    from cing.Libs.cython.superpose import calculateRMSD
#    from cing.Libs.cython.superpose import superposeVectors
#    from cing.Libs.cython.superpose import Rm6dist #@UnresolvedImport
except ImportError:
    io.error('Importing cython routines  for queeny\n')
    raise ImportError


# versions < 0.95 not logged with version number
# cing versions >1.0 first ones to include this
__version__ = cing.__version__


# defaults for the talosPlus status dict
def queenyDefaults():
    d = Adict(
               completed  = False,
               parsed     = False,
               version    = __version__,
               directory  = constants.QUEENY_KEY,
               molecule   = None,
              )
    return d
#end def


class QueenyResult(validation.ValidationResult):
    """Class to store queeny results
    """
    KEY = constants.QUEENY_KEY
    UNCERTAINTY1 = constants.QUEENY_UNCERTAINTY1_STR
    UNCERTAINTY2 = constants.QUEENY_UNCERTAINTY2_STR
    INFORMATION  = constants.QUEENY_INFORMATION_STR

    def __init__(self):
        validation.ValidationResult.__init__(self)
        self.setdefault(QueenyResult.UNCERTAINTY1, 0.0)
        self.setdefault(QueenyResult.UNCERTAINTY2, 0.0)
        self.setdefault(QueenyResult.INFORMATION, 0.0)
    #end def
#end class


class QueenyResultJsonHandler(jsonTools.handlers.SimpleDictHandler):
    """Handler for the QueenyResult class
    """
    namespace = constants.QUEENY_KEY
    cls = QueenyResult
    encodedKeys = [constants.OBJECT_KEY]

    def restore(self, data):
        result = QueenyResult()
        self._restore(data, result)
        #LEGACY:
        if isinstance(result.object, molecule.Residue) or \
           isinstance(result.object, molecule.Atom):
            for storedProp in [QueenyResult.UNCERTAINTY1, QueenyResult.UNCERTAINTY2, QueenyResult.INFORMATION]:
                result.object[storedProp] = result[storedProp]
        #end if
        return result
    #end def
#end class
QueenyResultJsonHandler.handles(QueenyResult)


class DmElement():
    """Distance Matrix element for Queeny"""
    upperDefault = 256.0
    lowerDefault =   0.0
    uncertaintyDefault  =  5.545177 # log(256.0-0.0)
    uncertaintyMinvalue = -5.545177 # lowest value: log(1.0/256.0)

    def __init__(self, atm1, atm2 ):
        #NTdict.__init__( self, __CLASS__ = 'DmElement'  )
        self.atm1 = atm1
        self.atm2 = atm2
        self.upper  = DmElement.upperDefault
        self.lower  = DmElement.lowerDefault
        self.upperChange = 0.0 # change after using last iteration of setLU()
        self.uncertainty = DmElement.uncertaintyDefault
        self.flagged = False
    #end def

    def __str__(self):
        return '<DmElement>'

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


class Queeny( Odict ):
    """
    Class to run a queen-like analysis

    """

    def __init__(self, project ):
        Odict.__init__( self )
        self.project  = project
        self.molecule = project.molecule
        for atm in self.molecule.allAtoms():
            atm.neighbors = {}
    #end def

    def __setitem__(self, key, value):
        if key[0] > key[1]:
            key = (key[1],key[0])
        Odict.__setitem__(self, key, value)
    #end def

    def __getitem__(self, key):
        if key[0] > key[1]:
            key = (key[1],key[0])
        return Odict.__getitem__(self, key)
    #end def

    # W0222 Signature differs from overridden method
    # pylint: disable=W0222
    def setdefault(self, key, defaultValue):
        if key[0] > key[1]:
            key = (key[1],key[0])
        return Odict.setdefault( self, key, defaultValue)
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
        if self.project is None:
            io.error('Queeny.execute: undefined project')
            return True
        if self.molecule is None:
            io.error('Queeny.execute: undefined molecule')
            return True
        self.reset()

        # do the topology
        self.initTopology()
        self.triangulateAll( cutoff=cutoff, maxDepth = 4 )
        self.setUncertainty(constants.QUEENY_UNCERTAINTY1_STR)
        # do the restraints
        self.initRestraints()
        self.triangulateAll( cutoff=cutoff, maxDepth = 3 )
        self.setUncertainty(constants.QUEENY_UNCERTAINTY2_STR)
        # calculate the information content for each atom, residue
        self.setInformation(constants.QUEENY_UNCERTAINTY1_STR, constants.QUEENY_UNCERTAINTY2_STR, constants.QUEENY_INFORMATION_STR)
        return False
    #end def

    def reset(self):
        """
        Reset all Queeny values and and results dicts
        """
        for obj in self.molecule.allResidues() + self.molecule.allAtoms():
            self.project.validationData.setResult(obj, constants.QUEENY_KEY, None)
            #LEGACY
            for storedProp in [QueenyResult.UNCERTAINTY1, QueenyResult.UNCERTAINTY2, QueenyResult.INFORMATION]:
                obj[storedProp] = 0.0
            #end for
        #end for
    #end def


    def initDmElement(self, atm1, atm2, lower=None, upper=None):
        """Initialize a DmElement entry for atm1, atm2
        optionally set lower and upper
        return dme
        """
        if not self.has_key((atm1.atomIndex,atm2.atomIndex)):
            dme = DmElement(atm1, atm2)
            self[(atm1.atomIndex,atm2.atomIndex)] = dme
        else:
            dme = self[(atm1.atomIndex,atm2.atomIndex)]
        #end if
        if lower is not None and upper is not None:
            dme.setLU(lower, upper)
        #end if
        return dme
    #end def

    def initTopology(self):
#        nTdebug('Queeny.initTopology: initializing topology')
        for atm in self.molecule.allAtoms():
            for atmN in atm.topology():

                if self.has_key((atm.atomIndex,atmN.atomIndex)):
                    continue

                dme = DmElement(atm, atmN)
                self[(atm.atomIndex,atmN.atomIndex)] = dme

                # approximate values
                if (atm.isProton() and atmN.isCarbon()) or (atmN.isProton() and atm.isCarbon()):
                    dme.setLU( 0.0, 1.08)
                elif atm.isCarbon() and atmN.isCarbon():
                    dme.setLU( 0.0, 1.52) # alphatic C-C
                elif (atm.isNitrogen() and atmN.isCarbon()) or (atmN.isNitrogen() and atm.isCarbon()):
                    dme.setLU( 0.0, 1.33) #N-C'; (N-CA) = 1.45
                elif (atm.isNitrogen() and atmN.isProton()) or (atmN.isNitrogen() and atm.isProton()):
                    dme.setLU( 0.0, 0.98)
                else:
                    dme.setLU( 0.0, 1.0)
                #end if
            #end for
        #end for
        for atm in self.molecule.atomsWithProperties('isMethyl','isCarbon'):
            #patch methyls
            protons = atm.attachedProtons()
            if protons is None or len(protons) == 0: # fixes 2ca7
                continue
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
            if protons is None or len(protons) == 0: # fixes ??
                continue
            pseudo = protons[0].pseudoAtom()
            self.initDmElement(protons[0],protons[1], 0.0, 1.764)
            self.initDmElement(protons[0],pseudo, 0.0, 0.882) # geometric centre: 0.5*1.764
            self.initDmElement(protons[1],pseudo, 0.0, 0.882)
        #end if

        for res in self.molecule.residuesWithProperties('TYR'):
            HD1 = res.getAtom('HD1',constants.INTERNAL_0) # pylint: disable=C0103
            HD2 = res.getAtom('HD2',constants.INTERNAL_0) # pylint: disable=C0103
            QD  = res.getAtom('QD',constants.INTERNAL_0)  # pylint: disable=C0103
            HE1 = res.getAtom('HE1',constants.INTERNAL_0) # pylint: disable=C0103
            HE2 = res.getAtom('HE2',constants.INTERNAL_0) # pylint: disable=C0103
            QE  = res.getAtom('QE',constants.INTERNAL_0)  # pylint: disable=C0103

            if None in [ HD1, HD2, QD, HE1, HE2, QE]:
                continue
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
            HD1 = res.getAtom('HD1',constants.INTERNAL_0)   # pylint: disable=C0103
            HD2 = res.getAtom('HD2',constants.INTERNAL_0)   # pylint: disable=C0103
            QD  = res.getAtom('QD',constants.INTERNAL_0)    # pylint: disable=C0103
            HE1 = res.getAtom('HE1',constants.INTERNAL_0)   # pylint: disable=C0103
            HE2 = res.getAtom('HE2',constants.INTERNAL_0)   # pylint: disable=C0103
            QE  = res.getAtom('QE',constants.INTERNAL_0)    # pylint: disable=C0103
            HZ  = res.getAtom('HZ',constants.INTERNAL_0)    # pylint: disable=C0103

            if None in [ HD1, HD2, QD, HE1, HE2, QE, HZ]:
                continue

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
#        nTdebug('Queeny._calculateAverage: %s')
#        error = False    # Indicates if an error was encountered when analyzing restraint @UnusedVariable

        modelCount = dr.getModelCount()
        if not modelCount:
#            nTdebug('DistanceRestraint.calculateAverage: No structure models (%s)', self)
            return None
        #end if

        if len(dr.atomPairs) == 0:
            return None
        #end if

        models = range(modelCount)
        pair = 0
        rm6distances = nTfill(0.0, len(dr.atomPairs))

        for atm1, atm2 in dr.atomPairs:

            # GV says: Check are done to prevent crashes upon rereading
            # datasets with floating/adhoc residues/atoms

            # skip trivial cases
            if atm1 == atm2:
                continue
            if atm1 is None or atm2 is None:
                continue
            #expand pseudoatoms
            atms1 = atm1.realAtoms()
            if atms1 is None:
                #nTdebug('DistanceRestraint.calculateAverage: %s.realAtoms() None (%s)', atm1, self)
                continue
            atms2 = atm2.realAtoms()
            if atms2 is None:
                #nTdebug('DistanceRestraint.calculateAverage: %s.realAtoms() None (%s)', atm2, self)
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
                        rm6distances[pair] += superpose.Rm6dist(a1.coordinates[i].e, a2.coordinates[i].e)
                    #end for models
                #end for a2
            #end for a1
            pair += 1
        #end for

#        if self.distances[i] > 0.0:
#                self.distances[i] = math.pow(self.distances[i], -0.166666666666666667)
#        #end if

        psum = sum(rm6distances)
        for i,value in enumerate(rm6distances):
            rm6distances[i] = value/psum
        #end for

        return rm6distances
    #end def

    def initRestraints( self ):
        """
        Initialize restraints from restraint lists
        Only distances for now
        """

        nTmessage('==> Queeny adding restraints (# elements = %d)', len(self))

        for dme in self.itervalues():
            dme.upperChange = 0.0
        #end for

        nkeys = len(self)
        #print '>', nkeys
#        count = 0
        for drl in self.project.distances:
            for dr in drl:
                if len(dr.atomPairs) == 1:
                    atm1,atm2 = dr.atomPairs[0]
                    upper = dr.upper
                    if dr.upper is None: # sometimes happens; i.e. entry 1but
                        upper = DmElement.upperDefault
                    lower = dr.lower
                    if dr.lower is None: # lower values sometimes set to None
                        lower = DmElement.lowerDefault
                    self.initDmElement(atm1, atm2, lower, upper)
                else:
                    # ambiguous restraints
                    rm6distances = self._calculateAverage( dr )
                    if rm6distances is None:
                        nTwarning('Queeny.initRestraints: failure to analyze %s', dr)
                        break
                    #endif

                    upper = dr.upper
                    if dr.upper is None: # sometimes happens; i.e. entry 1but
                        upper = DmElement.upperDefault
                    lower = dr.lower
                    if dr.lower is None: # lower values sometimes set to None
                        lower = DmElement.lowerDefault

                    # hr: total uncertainty change associated with this restraint
                    # dH = hmax - hr : change in uncertainty
                    # hi = hmax - dH*frac : relative R-6 contribution of atom pair: sum(hi) = hr
                    hmax = DmElement.uncertaintyDefault
                    hr = math.log(upper-lower)
                    dH = hmax - hr
                    pair = 0
                    for atm1,atm2 in dr.atomPairs:
                        hi = hmax - rm6distances[pair]*dH
                        self.initDmElement(atm1, atm2, lower, lower+math.exp(hi))
                        pair += 1
                    #end for
                #end if
#                count += 1
            #end for
        #end for

#        nTdebug('Queeny.initRestraints: %d restraints added (# elements = %d)', count, len(self))

        self.setNeighbors(nkeys) # update the neighbors for newly added
        #print '>>',len(self)
    #end def

    def initFlagged(self):
        for dme in self.itervalues():
            dme.flagged = False
        self.nflagged = 0
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
            dme13 = DmElement(atm1, atm3)
            self[(atm1.atomIndex,atm3.atomIndex)] = dme13

        if dme12 is None:
            dme12 = self[(atm1.atomIndex,atm2.atomIndex)]
        if dme23 is None:
            dme23 = self[(atm2.atomIndex,atm3.atomIndex)]

        upper12 = dme12.upper
        upper23 = dme23.upper
        lower12 = dme12.lower
        lower23 = dme23.lower
        dme13.setLU( max(lower12-upper23, lower23-upper12), upper12+upper23)
        dme13.flagged = True
    #end def

    def setNeighbors(self, keyIndex):
        """Set the neighbors from dme, starting at keyIndex"""
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

#        nTdebug('Queeny.triangulateAll: starting')
        count = 1
        depth = 0

        while depth < maxDepth and count>0:

            self.sortKeys()
            self.initFlagged()

            nkeys = len(self._keys)
            key = 0
            count = 0

            while key < nkeys:

                dme12 = self(key)

#                if key%100==0:
#                    nTdebug('Queeny.triangulateAll: depth: %d nkeys %4d  key %4d  len %6d  count %4d %7.3f',
#                            depth, nkeys, key, len(self), count, dme12.upperChange)


                if dme12.upperChange < cutoff:
#                    nTdebug('Queeny.triangulateAll: depth: %d nkeys %4d  key %4d  len %6d  count %4d %7.3f  BREAK',
#                            depth, nkeys, key, len(self), count, dme12.upperChange)
                    break
                #end if

                atm1  = dme12.atm1
                atm2  = dme12.atm2

                for atmN1,dme in atm1.neighbors.iteritems(): # duplicate, because gets added onto original
                    self.triangulate(atmN1, atm1, atm2, dme, dme12)
                for atmN2,dme in atm2.neighbors.iteritems():
                    self.triangulate(atm1, atm2, atmN2, dme12, dme)
                dme12.upperChange=0.0
                dme12.flagged=True
                count += 1
                key += 1
            #end while
            self.setNeighbors(nkeys) # Update neighbor lists for newly added elements (starting at nkeys)

#            nTdebug('Queeny.triangulateAll: depth: %d nkeys %4d  key %4d  len %6d  count %4d', depth, nkeys, key, len(self), count)
            depth += 1
        #end while
    #end def

    def setUncertainty(self, key):
        """set the uncertainty for:
        - each atom[key] of molecule
        - each residue[key] of molecule
        """
#        nTdebug('Queeny.setUncertainty: starting')

        for dme in self.itervalues():
            if dme.upper > dme.lower:
                dme.uncertainty = max(DmElement.uncertaintyMinvalue, math.log(dme.upper-dme.lower))
            else:
                nTdebug('Queeny.setUncertainty: problem with %s', dme.format())
                dme.uncertainty = DmElement.uncertaintyMinvalue
        #end for

        atms = self.molecule.allAtoms()
        n = len(atms)

        for atm in atms:
            atm[key] = 0.0

        for i in range(n):
            atm1 = atms[i]
            for j in range(i+1,n):
                atm2 = atms[j]
                if self.has_key((atm1.atomIndex,atm2.atomIndex)):
                    dme = self[(atm1.atomIndex,atm2.atomIndex)]
                    atm1[key] += dme.uncertainty
                    atm2[key] += dme.uncertainty
                else:
                    atm1[key] += DmElement.uncertaintyDefault
                    atm2[key] += DmElement.uncertaintyDefault
                #end if
            #end for
        #end for
        fls = float(n-1)
        for atm in atms:
            atm[key] /= fls
        #end for

        # residues
        for res in self.molecule.allResidues():
            res[key] = 0.0
        for atm in atms:
            atm.residue[key] += atm[key]
        for res in self.molecule.allResidues():
            resAtomCount = len(res.atoms)
            if resAtomCount:
                res[key] /= resAtomCount
            #end if
        #end for
    #end def

    def setInformation(self, key1, key2, informationKey):
        """set the information and QueenyResult dicts for:
        - each atom of molecule
        - each residue of molecule
        using key1 and key2
        """
#        nTdebug('Queeny.setInformation: starting')
        for atm in self.molecule.allAtoms():
            if atm.has_key(key1) and atm.has_key(key2):
                atm[informationKey] = atm[key1]-atm[key2]
            else:
                atm[informationKey] = 0.0
            #end for
            qresult = QueenyResult()
            qresult[key1] = atm[key1]
            qresult[key2] = atm[key2]
            qresult[informationKey] = atm[informationKey]
            qresult[constants.OBJECT_KEY] = atm
            self.project.validationData.setResult(atm, constants.QUEENY_KEY, qresult)
        #end for
        for res in self.molecule.allResidues():
            if res.has_key(key1) and res.has_key(key2):
                res[informationKey] = res[key1]-res[key2]
            else:
                res[informationKey] = 0.0
            #end for
            qresult = QueenyResult()
            qresult[key1] = res[key1]
            qresult[key2] = res[key2]
            qresult[informationKey] = res[informationKey]
            self.project.validationData.setResult(res, constants.QUEENY_KEY, qresult)
        #end for
#        # average
#        for chain in self.molecule.allChains():
#            for res in chain.allResidues()[1:-1]:
#                res.information = (res.sibling(-1).information+res.information+res.sibling(1).information)*0.333
#            #end for
#        #end for
    #end def

    def zap(self, byItem):
        return nTzap(self.values(), byItem)

    def sortKeys(self):
        """Sorts the dme list by upperChange"""
        a = zip(self._keys,nTzap(self.values(),'upperChange'))
        NTsort(a, 1, inplace=True)
        a.reverse()
        self._keys = nTzap(a,0)
    #end def
#end class


def runQueeny( project, tmp=None ):
    try: # Fixes 2l4g
        return _runQueeny( project, tmp=tmp )
    except:
        nTerror("Queeny failed as per below.")
        nTtracebackError()
        return True

def _runQueeny( project, tmp=None ):
    """Perform a queeny analysis and save the results.

    Returns True on error.
    Returns False when all is fine.
    """
    nTmessage("==> Calculating restraint information by Queeny")
    if project is None:
        nTerror("runQueeny: No project defined")
        return True

    if project.molecule is None:
        nTerror("runQueeny: No molecule defined")
        return True

    if len(project.distances) == 0:
        nTmessage("==> runQueeny: No distance restraints defined.")
        return True

    queenyDefs = project.getStatusDict(constants.QUEENY_KEY, **queenyDefaults())
    queenyDefs.molecule = project.molecule.asPid

    path = project.validationPath( queenyDefs.directory )
    if not path:
        nTmessage("==> runQueeny: error creating '%s'", path)
        return True

    q = Queeny( project )
    q.execute()
    queenyDefs.date = io.now()
    queenyDefs.completed = True
    queenyDefs.parsed = True
    queenyDefs.version = __version__

    del(q)

    return False
#end def

#-----------------------------------------------------------------------------

# register the functions
methods  = [(runQueeny,None)]
#saves    = []
#restores = []
