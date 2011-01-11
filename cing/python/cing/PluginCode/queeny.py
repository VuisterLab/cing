"""
Basic QUEEN implementation for restraint information calculation

project.runQueeny() executes the queeny routine.
Atoms obtain attribute 'information' (defined in QUEENY_INFORMATION_STR) with information value.
Residues obtain attribute 'information' with information value that is averaged over a three residue window

"""

from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.cython.superpose import Rm6dist
from cing.PluginCode.required.reqQueeny import * #@UnusedWildImport
from cing.core.sml import SML2obj
from cing.core.sml import obj2SML


class dmElement():
    "Distance Matrix element for Queeny"
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
        self.upperChange = 0.0 # change after using last iteration of setLU()
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

class Queeny( odict ):
    """
    Class to run a queen-like analysis

    """

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
        self.setUncertainty(QUEENY_UNCERTAINTY1_STR)
        # do the restraints
        self.initRestraints()
        self.triangulateAll( cutoff=cutoff, maxDepth = 3 )
        self.setUncertainty(QUEENY_UNCERTAINTY2_STR)
        # calculate the information content for each atom, residue
        self.setInformation(QUEENY_UNCERTAINTY1_STR, QUEENY_UNCERTAINTY2_STR, QUEENY_INFORMATION_STR)
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
        NTdebug('Queeny.initTopology: initializing topology')
        for atm in self.molecule.allAtoms():
            for atmN in atm.topology():

                if self.has_key((atm.atomIndex,atmN.atomIndex)):
                    continue

                dme = dmElement(atm, atmN)
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


#        NTdebug('Queeny._calculateAverage: %s')
        error = False    # Indicates if an error was encountered when analyzing restraint @UnusedVariable

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

        NTdebug('Queeny.initRestraints: adding restraints (# elements = %d)', len(self))

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
                    # ambiguous restraints
                    Rm6distances = self._calculateAverage( dr )
                    if Rm6distances == None:
                        NTwarning('Queeny.initRestraints: failure to analyze %s', dr)
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

        NTdebug('Queeny.initRestraints: %d restraints added (# elements = %d)', count, len(self))

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

        NTdebug('Queeny.triangulateAll: starting')
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
#                    NTdebug('Queeny.triangulateAll: depth: %d nkeys %4d  key %4d  len %6d  count %4d %7.3f',
#                            depth, nkeys, key, len(self), count, dme12.upperChange)


                if dme12.upperChange < cutoff:
                    NTdebug('Queeny.triangulateAll: depth: %d nkeys %4d  key %4d  len %6d  count %4d %7.3f  BREAK',
                            depth, nkeys, key, len(self), count, dme12.upperChange)
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

            NTdebug('Queeny.triangulateAll: depth: %d nkeys %4d  key %4d  len %6d  count %4d', depth, nkeys, key, len(self), count)
            depth += 1
        #end while
    #end def

    def setUncertainty(self, key):
        """set the uncertainty for:
        - each atom[key] of molecule
        - each residue[key] of molecule
        """
        NTdebug('Queeny.setUncertainty: starting')

        for dme in self.itervalues():
            if dme.upper > dme.lower:
                dme.uncertainty = max(dmElement.uncertaintyMinvalue, math.log(dme.upper-dme.lower))
            else:
                NTdebug('Queeny.setUncertainty: problem with %s', dme.format())
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
        fls = float(l-1)
        for atm in atms:
            atm[key] /= fls

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
        NTdebug('Queeny.setInformation: starting')
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
#        # average
#        for chain in self.molecule.allChains():
#            for res in chain.allResidues()[1:-1]:
#                res.information = (res.sibling(-1).information+res.information+res.sibling(1).information)*0.333
#            #end for
#        #end for
    #end def

    def zap(self, byItem):
        return NTzap(self.values(), byItem)

    def sortKeys(self):
        'Sorts the dme list by upperChange'
        a = zip(self._keys,NTzap(self.values(),'upperChange'))
        NTsort(a, 1, inplace=True)
        a.reverse()
        self._keys = NTzap(a,0)
    #end def

#end class

def queenyDefaults():
    d = NTdict( directory  = 'Queeny',
                smlFile    = 'queeny.sml',
                molecule   = None,
                completed  = False,
              )
    d.keysformat()
    return d
#end def


def runQueeny( project, tmp=None ):
    """Perform a queeny analysis and save the results.

    Returns True on error.
    Returns False when all is fine.
    """
    if project == None:
        NTerror("runQueeny: No project defined")
        return True

    if project.molecule == None:
        NTerror("runQueeny: No molecule defined")
        return True

    if len(project.distances) == 0:
        NTmessage("==> runQueeny: No distance restraints defined.")
        return True

    project.status.queeny = queenyDefaults()
    queenyDefs = project.status.queeny # temp variable for shorter typing
    queenyDefs.molecule = project.molecule.nameTuple()


    path = project.validationPath( queenyDefs.directory )
    if not path:
        NTmessage("==> runQueeny: error creating '%s'", path)
        return True

    q = Queeny( project )
    q.execute()
    project.saveQueeny()

    queenyDefs.completed = True

    del(q)

    return False
#end def


def saveQueeny( project, tmp=None ):
    """
    Save queeny results to sml file
    Returns True on error.
    Returns False on success.
    """
    if project == None:
        NTmessage("saveQueeny: No project defined")
        return True

    if 'queeny' not in project.status:
#        NTdebug("saveQueeny: No talos+ was run")
        return False # just no data, not an error

    queenyDefs = project.status.queeny

    path = project.validationPath( queenyDefs.directory )
    if not path:
        NTerror('saveQueeny: directory "%s" with talosPlus data not found', path)
        return True

    if project.molecule == None:
        NTmessage("saveQueeny: No molecule defined")
        return True

    l = NTlist()
    for res in project.molecule.allResidues():
        if res.has_key(QUEENY_INFORMATION_STR):
            l.append( (res.nameTuple(), res[QUEENY_INFORMATION_STR])
                    )
        for atm in res:
            if atm.has_key(QUEENY_INFORMATION_STR):
                l.append( (atm.nameTuple(), atm[QUEENY_INFORMATION_STR])
                          )
        #end for
    #end for
    smlFile = os.path.join(path, queenyDefs.smlFile )
    obj2SML( l, smlFile)
    NTdetail('==> Saved queeny results to "%s"', smlFile)
    return False
#end def


def restoreQueeny( project, tmp=None ):
    """
    Restore queeny results from sml file.

    Return True on error
    """
    if project == None:
        NTmessage("restoreQueeny: No project defined")
        return True

    if project.molecule == None:
        return False # Gracefully returns
    for res in project.molecule.allResidues():
        res[QUEENY_INFORMATION_STR] = 0.0
    for atm in project.molecule.allAtoms():
        atm[QUEENY_INFORMATION_STR] = 0.0

    project.status.setdefault('queeny',queenyDefaults())
    project.status.keysformat()

    if not project.status.queeny.completed:
        return # Return gracefully

    queenyDefs = project.status.queeny # short cur for less typing
    path = project.validationPath( queenyDefs.directory)
    if not path:
        NTerror('restoreQueeny: directory "%s" with queeny data not found', path)
        return True

    smlFile = os.path.join(path, queenyDefs.smlFile )
    if not os.path.exists(smlFile):
        NTerror('restoreQueeny: file "%s" with queeny data not found', path)
        return True

   # Restore the data
    NTmessage('==> Restoring queeny results from "%s"', smlFile)
    l=SML2obj( smlFile, project.molecule)
    if l==None:
        return True
    for nameTuple,info in l:
        obj = project.molecule.decodeNameTuple(nameTuple)
        if not obj:
            NTerror('restoreQueeny: error decoding "%s"', nameTuple)
        else:
            obj[QUEENY_INFORMATION_STR] = info
    #end for
    return False
#end def
#-----------------------------------------------------------------------------

# register the functions
methods  = [(runQueeny,None)]
saves    = [(saveQueeny, None)]
restores = [(restoreQueeny, None)]
