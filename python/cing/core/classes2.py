'''
Created on Aug 30, 2010

@author: jd
'''

from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqVasco import * #@UnusedWildImport
from cing.core.ROGscore import ROGscore

# pylint: disable=R0903
class ProjectListMember():
    """An element of ProjectList always has certain attributes to add.
    """
    def __init__(self):
        """
        Just add some properties.
        """
        self.project = None
        self.objectPath = None
        self.projectList = None
        self.rogScore = ROGscore()        
    # end def
    
    def decriticize(self):
#        nTdebug("Now in ProjectListMember#%s" % getCallerName())
        # Any list
        self.rogScore.reset()
        for obj in self:
#            nTdebug("Looking at object: %s [%r]" % (str(obj), repr(obj)))
            obj.decriticize()
        # end for
    #end def    
# end class


class RestraintList(NTlist, ProjectListMember):
    """
    Super class for DistanceRestraintList etc..
    Moving functionality to here gradually.
    """
    # use the same spelling through out.
    def __init__(self, name, status = 'keep'):
        NTlist.__init__(self)
        ProjectListMember.__init__(self)      # Initialized objectPath  
        self.__CLASS__ = 'RestraintList'
        self.name = name        # Name of the list
        self.status = status    # Status of the list; 'keep' indicates storage required
        self.currentId = 0      # Id for each element of list
        self._idDict = {}       # dictionary to look up id in case the list is sorted differently
        self._byItem = None     # if not None: list was sorted _byItem.

        self.projectList = None
        self.rmsd = None        # rmsd per model, None indicate no analysis done
        self.rmsdAv = 0.0
        self.rmsdSd = 0.0
        self.violAv = 0.0
        self.violMaxAll = 0.0        
        self.violCount1 = 0       # Total violations over 0.1 A (1 degree)
        self.violCount3 = 0       # Total violations over 0.3 A (3 degrees)
        self.violCount5 = 0       # Total violations over 0.5 A (5 degrees)

#        self.export2cyana = passThru # Explicite mention. Defaulting to passthru method.
#        self.export2xplor = passThru
#        self.path = None        
    #end def
    
    def __str__(self):
        return sprintf('<%s "%s" (%s,%d)>' % (self.__CLASS__, self.name, self.status, len(self)))
    #end def
    def __repr__(self):
        return self.__str__()
    #end def
    def rename(self, newName):
        'rename'
        return self.projectList.rename(self.name, newName)
    #end def
    
    def renameToXplorCompatible(self):
        'rename to Xplor Compatible'
        n = len(self.name)
        if n < MAX_SIZE_XPLOR_RESTRAINT_LIST_NAME:
#             nTdebug("Kept the original xplor compatible drl name: %s" % self.name)
            return
        prefix = 'pl'
        if self.__CLASS__ == DRL_LEVEL:
            prefix = DRL_STR
        elif self.__CLASS__ == ACL_LEVEL:
            prefix = ACL_STR
        elif self.__CLASS__ == RDCL_LEVEL:
            prefix = RDCL_STR
        prefix += '_'
        newName = self.projectList.getNextValidName(prefix = prefix)
        if newName == None:
            nTerror("Failed renameToXplorCompatible for %s" % self)
            return
        self.rename(newName)
    #end def

    def append(self, restraint):  # pylint: disable=W0221
        'Add a restraint to list.'
        restraint.id = self.currentId
        restraint.parent = self # being able to go from restraint to restraint list is important.
        NTlist.append(self, restraint)
        self._idDict[restraint.id] = restraint
        self.currentId += 1
    #end def
    def save(self, path = None):
        """
        Create a SML file
        Return self or None on error

        Sort the list on id before saving, to preserve (original) order from save to restore.
        """
        # sort the list on id number
        NTsort( self, byItem='id', inplace=True)

        if not path:
            # Should have come from ProjectListMember? TODO: check             
            path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            nTerror('%s.save: failed creating "%s"' % (self.__CLASS__, path))
            return None
        #end if

        # restore original sorting
        if self._byItem:
            NTsort( self, byItem=self._byItem, inplace=True)

        nTdetail('==> Saved %s to "%s"', self, path)
        return self
    #end def

    def sort(self, byItem='id' ):
        "Sort the list byItem; store the byItem "
        NTsort( self, byItem, inplace=True)
        self._byItem = byItem
        return self
    #end def

    def getId(self, id):
        """Return restraint instance with id
        Returns None on error
        """
        if not self._idDict.has_key(id):
            nTerror('RestraintList.getId: invalid id (%d)', id)
            return None
        #end if
        return self._idDict[id]
    #end def

    def getModelCount(self):
        """Iterate over the restraints until a restraint is found that returns not a None for getModelCount.
        Return 0 if it doesn't have any models or None on error.
        Never complain.
        """
        modelCount = None
        mAX_RESTRAINTS_TO_TEST = 10 # disable feature after testing.
        for i, restraint in enumerate(self):
            modelCount = restraint.getModelCount()
            if modelCount != None:
                return modelCount
            if i == mAX_RESTRAINTS_TO_TEST:
#                nTwarning("getModelCount returned None for the first %d restraints; giving up." % i)
                return None
#        nTwarning("getModelCount returned None for all %d restraints; giving up." % len(self))
        return None
    #end def

    def format(self, showAll = False):
#        nTdebug("Now in classes2.RestraintList#" + getCallerName())
        if not showAll:
            return ''
        rTxtList = []
        for r in self:
            rTxtList.append( r.format() )
        msg = '\n'
        msg += '\n'.join(rTxtList)
        return msg
    # end def
# end class

class ResonanceList(NTlist, ProjectListMember):
    """
    Contains ResonanceList meta data.
    NB the name is not necessarily unique within even the molecule.
    I.e. for PDB entry 1cjg and from NMR-STAR entry 4813 will get the resonance list name bmr4813_21.str twice from CCPN.
    """
    SML_SAVE_ATTRIBUTE_LIST = 'name status bmrb_id vascoApplied vascoResults'.split() # Used in cing.core.sml.SMLNTListWithAttrHandler
    # use the same spelling through out.

    # NB the unusual init. Differs in that arguments aren't added to the list.
    def __init__(self, name, status = 'keep'):
        NTlist.__init__(self)
        ProjectListMember.__init__(self)      # Initialized objectPath  
        self.__CLASS__ = 'ResonanceList'
        self.name = name        # Name of the list        
        self.status = status    # Status of the list; 'keep' indicates storage required
        self.currentId = 0      # Id for each element of list
        self._idDict = {}       # dictionary to look up id in case the list is sorted differently
        self._byItem = None     # if not None: list was sorted _byItem.
        self.vascoResults  = NTdict() # See applyVascoChemicalShiftCorrections # NB match with VASCO_RESULTS_STR
        self.vascoApplied  = False # VASCO_APPLIED_STR
        self.bmrb_id = None # Will be derived from name when calling rename.
        self.rogScore = ROGscore()
        self.SMLhandler.SML_SAVE_ATTRIBUTE_LIST = self.SML_SAVE_ATTRIBUTE_LIST
        self.rename(name) # Triggers setting self.bmrb_id
    #end def

    def decriticize(self):
#        nTdebug("Now in ResonanceList#decriticize")
        # Restraints lists
        self.rogScore.reset()
        for dr in self:
            dr.rogScore.reset()
        # end for
    #end def

    def hasVascoCorrectionsApplied(self):
        'A little bit more sophisticated routine to report no corrections of zero.'
        return self.vascoApplied and self.hasVascoCorrectionsApplicable()
    #end def

    def hasVascoCorrectionsApplicable(self):
        'A little bit more sophisticated routine to report no corrections of zero.'
        for atomId in self.vascoResults.keys():
            ntvalue =  self.vascoResults[ atomId ]
            rerefValue = ntvalue.value
            rerefError = ntvalue.error
            useCorrection = math.fabs(rerefValue) >= VASCO_CERTAINTY_FACTOR_CUTOFF * rerefError # sync with molecule code.
            if useCorrection:
                return True
            # end if
        # end for
        return False
    #end def

    def __str__(self):
        return sprintf('<%s "%s">' % (self.__CLASS__, self.name))
#        return self.toVascoHtmlList() # modify when needed.

    def toVascoHtmlList(self, showHeader = False):
        'If showIndividualApplication the output will be multiple lines.'
        s = ''
        if showHeader:
            s += '<h3>'
            s += self.name
            if self.vascoApplied:
                s += ' (applied)'
            else:
                s += ' (ignored)'
            s += '</h3>\n'
        s += '<ul>\n'
        for atomId in self.vascoResults.keys():
            ntvalue =  self.vascoResults[ atomId ]
            s += '<li>'
            atomClassId = getDeepByKeys(vascoMapAtomIdToHuman, atomId)
            if atomClassId == None:
                atomClassId = atomId
            s += '%s: %s' % ( atomClassId, ntvalue)
            rerefValue = ntvalue.value
            rerefError = ntvalue.error
            useCorrection = math.fabs(rerefValue) >= VASCO_CERTAINTY_FACTOR_CUTOFF * rerefError
            if useCorrection:
                s += ' applied'
            else:
                s += ' not applied'
            # end if
            s += '</li>\n'
        # end for
        s += '</ul>\n'
        return s
    #end def
    def __repr__(self):
        return self.__str__()
    #end def
    def rename(self, newName):
        'Please use this rename instead of directly renaming so BMRB ID detection can kick in.'        
        self.name = newName
        # Detect the id from strings like: bmr4020_21.str
        pattern = re.compile( '^.*(bmr\d+).*$' )
        match = pattern.match( self.name )
        if match:
            bmrb_idStr = match.group(1)[3:]            
            self.bmrb_id = int(bmrb_idStr)
            if is_bmrb_code(self.bmrb_id):
#                nTdebug("-0- Autodetected BMRB ID %s from new name: %s" % (self.bmrb_id, self.name))
                return self
            # end if
            nTerror("Did not detect valid BMRB ID from new name: %s." % self.name)
            return self
        # end if
#        nTdebug("-2- No BMRB ID was matched from new name: %s" % self.name)
#        return self.projectList.rename(self.name, newName)
        return self
    #end def
    def append(self, item):  # pylint: disable=W0221
        'Append'
#        if not hasattr(self, 'currentId'): # for deepcopy
#            self.currentId = 0
        item.id = self.currentId
        item.parent = self # being able to go from restraint to restraint list is important.
        NTlist.append(self, item)
        self._idDict[item.id] = item
        self.currentId += 1
    #end def
    def save(self, path = None):
        """
        Create a SML file
        Return self or None on error

        Sort the list on id before saving, to preserve (original) order from save to restore.
        """
        # sort the list on id number
        NTsort( self, byItem='id', inplace=True)

        if not path: 
            path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            nTerror('%s.save: failed creating "%s"' % (self.__CLASS__, path))
            return None
        #end if

        # restore original sorting
        if self._byItem:
            NTsort( self, byItem=self._byItem, inplace=True)

        nTdetail('==> Saved %s to "%s"', self, path)
        return self
    #end def

    def sort(self, byItem='id' ):
        "Sort the list byItem; store the byItem "
        NTsort( self, byItem, inplace=True)
        self._byItem = byItem
        return self
    #end def

    def getId(self, id):
        """Return restraint instance with id
        Returns None on error
        """
        if not self._idDict.has_key(id):
            nTerror('ResonanceList.getId: invalid id (%d)', id)
            return None
        #end if
        return self._idDict[id]
    #end def

    def format(self, showAll = False):
        if not showAll:
            return
        rTxtList = []
        for r in self:
            rTxtList.append( r.format() )
        msg = '\n'
        msg += '\n'.join(rTxtList)
        return msg
    # end def
# end class

def getIndexRealResList(resonanceList):
    """
    Return index of resonance that has an actual value or -1 if no such resonance exists in this list.
    Input can be a NTlist or a ResonanceList instance.
    """
    for i, resonance in enumerate(resonanceList):
        if isNoneorNaN(resonance.value):
            continue
        return i
    # end for
    return -1
# end def
        
class CoordinateList( NTlist ):
    def __init__(self, *args):
        NTlist.__init__(self, *args)
            