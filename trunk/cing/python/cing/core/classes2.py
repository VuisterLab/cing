'''
Created on Aug 30, 2010

@author: jd
'''
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqVasco import * #@UnusedWildImport
from cing.core.ROGscore import ROGscore

class RestraintList(NTlist):
    """
    Super class for DistanceRestraintList etc..
    Moving functionality to here gradually.
    """
    # use the same spelling through out.
    def __init__(self, name, status = 'keep'):
        NTlist.__init__(self)
        self.__CLASS__ = 'RestraintList'
        self.name = name        # Name of the list
        self.status = status    # Status of the list; 'keep' indicates storage required
        self.currentId = 0      # Id for each element of list
        self._idDict = {}       # dictionary to look up id in case the list is sorted differently
        self._byItem = None     # if not None: list was sorted _byItem.

        self.rmsd = None        # rmsd per model, None indicate no analysis done
        self.rmsdAv = 0.0
        self.rmsdSd = 0.0
        self.violCount1 = 0       # Total violations over 0.1 A (1 degree)
        self.violCount3 = 0       # Total violations over 0.3 A (3 degrees)
        self.violCount5 = 0       # Total violations over 0.5 A (5 degrees)

        self.rogScore = ROGscore()
    #end def
    def __str__(self):
        return sprintf('<%s "%s" (%s,%d)>' % (self.__CLASS__, self.name, self.status, len(self)))
    #end def
    def __repr__(self):
        return self.__str__()
    #end def
    def rename(self, newName):
        return self.projectList.rename(self.name, newName)
    #end def
    def renameToXplorCompatible(self):
        l = len(self.name)
        if l < MAX_SIZE_XPLOR_RESTRAINT_LIST_NAME:
             NTdebug("Kept the original xplor compatible drl name: %s" % self.name)
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
            NTerror("Failed renameToXplorCompatible for %s" % self)
            return
        self.rename(newName)
    #end def

    def append(self, restraint):
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

        if not path: path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            NTerror('%s.save: failed creating "%s"' % (self.__CLASS__, self. path))
            return None
        #end if

        # restore original sorting
        if self._byItem:
            NTsort( self, byItem=self._byItem, inplace=True)

        NTdetail('==> Saved %s to "%s"', self, path)
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
            NTerror('RestraintList.getId: invalid id (%d)', id)
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
        MAX_RESTRAINTS_TO_TEST = 10 # disable feature after testing.
        for i, restraint in enumerate(self):
            modelCount = restraint.getModelCount()
            if modelCount != None:
                return modelCount
            if i == MAX_RESTRAINTS_TO_TEST:
#                NTwarning("getModelCount returned None for the first %d restraints; giving up." % i)
                return None
#        NTwarning("getModelCount returned None for all %d restraints; giving up." % len(self))
        return None
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

class ResonanceList(NTlist):
    """
    Contains ResonanceList meta data.
    NB the name is not necessarily unique within even the molecule. 
    I.e. for PDB entry 1cjg and from NMR-STAR entry 4813 will get the resonance list name bmr4813_21.str twice from CCPN. 
    """
    SML_SAVE_ATTRIBUTE_LIST = 'name status vascoApplied vascoResults'.split() # Used in cing.core.sml.SMLNTListWithAttrHandler
    # use the same spelling through out.
    
    # NB the unusual init. Differs in that arguments aren't added to the list.
    def __init__(self, name, status = 'keep'):
        NTlist.__init__(self)
        self.__CLASS__ = 'ResonanceList'
        self.name = name        # Name of the list
        self.status = status    # Status of the list; 'keep' indicates storage required
        self.currentId = 0      # Id for each element of list
        self._idDict = {}       # dictionary to look up id in case the list is sorted differently
        self._byItem = None     # if not None: list was sorted _byItem.
        self.vascoResults  = NTdict() # See applyVascoChemicalShiftCorrections # NB match with VASCO_RESULTS_STR
        self.vascoApplied  = False # VASCO_APPLIED_STR
        self.rogScore = ROGscore()
        self.SMLhandler.SML_SAVE_ATTRIBUTE_LIST = self.SML_SAVE_ATTRIBUTE_LIST
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
        self.name = newName
#        return self.projectList.rename(self.name, newName)
        return self
    #end def
    def append(self, item):
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

        if not path: path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            NTerror('%s.save: failed creating "%s"' % (self.__CLASS__, self. path))
            return None
        #end if

        # restore original sorting
        if self._byItem:
            NTsort( self, byItem=self._byItem, inplace=True)

        NTdetail('==> Saved %s to "%s"', self, path)
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
            NTerror('ResonanceList.getId: invalid id (%d)', id)
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

def resonanceListGetIndexFirstObjectWithRealValue(resonanceList):
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
