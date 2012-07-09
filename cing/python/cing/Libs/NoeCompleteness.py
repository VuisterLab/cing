'''
Created on May 30, 2011

@author: jd
'''
from cing import cingDirLibs
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import * #@UnusedWildImport

OVER_NUMBER_OF_SIGMAS_STR    = ">sigma"
NO_MULTIMER_STR              = "no multimer"
NO_INTRAS_STR                = "no intras"

#/** The eight is used for overflow */
MAX_SHELLS_OBSERVED = 9

# pylint: disable=R0902
class NoeCompleteness( NTdict ):
    'Simple class for getting artificial distance restraints and in the future to get the NOE completeness'
    def __init__(self, project, **kwds):
        NTdict.__init__(self, **kwds)        
        self.project = project
        self.lib = NoeCompletenessAtomLib()
        self.modelCount = self.project.molecule.modelCount
        self.resList = NTlist()        
        self.atomList = NTlist() # only observables.
        self.atomHash = NTdict() # hash of atomList
        self.resDistanceHoH = {}  # only up to self.max_dist_expectedOverall
        self.resRadiusHash = {}   # don't pollute our data model but store locally. Key residue, value: radius float
        self.atomDistanceHoH = {} # only up to self.max_dist_expectedOverall

        self.max_dist_expectedOverall       = None
        self.min_dist_expected              = None
        self.max_dist_expected              = None
        self.numb_shells_expected           = None
        self.min_dist_observed              = None
        self.max_dist_observed              = None
        self.numb_shells_observed           = None
        self.avg_power_models               = None
        self.avg_method                     = None
        self.monomers                       = None
        self.use_intra                      = None
        self.ob_file_name                   = None
        self.summaryFileNameCompleteness    = None
        self.write_dc_lists                 = None
        self.file_name_base_dc              = None
        self.hbOnly                         = None
        self.excludeBonded                  = None
        self.resList                        = None
        self.isPerShellRun                  = None
        self.vSet = None
        self.xSet = None
        
    def doCompletenessCheck( self, 
             max_dist_expectedOverall = 4.0,
             min_dist_observed = 2.0,
             max_dist_observed = 4.0,
             numb_shells_observed = 2,
             min_dist_expected = 2.0,
             max_dist_expected = 10.0,
             numb_shells_expected = 16,
             avg_power_models = 1.0, # unused
             avg_method = 1,# unused
             monomers = 1,# unused
             use_intra = False,
             ob_file_name = None,
             summaryFileNameCompleteness = "tmp_dir/XXXX_compl_sum",
             write_dc_lists = True,
             file_name_base_dc  = "tmp_dir/XXXX_compl",
             hbOnly=False,             
             resList = None, # Subset of residues                                  
             ):
        'Convenience method.    Return None on error or completeness on success. '
        
        self.max_dist_expectedOverall       = max_dist_expectedOverall
        self.min_dist_expected              = min_dist_expected
        self.max_dist_expected              = max_dist_expected
        self.numb_shells_expected           = numb_shells_expected
        self.min_dist_observed              = min_dist_observed
        self.max_dist_observed              = max_dist_observed
        self.numb_shells_observed           = numb_shells_observed
        self.avg_power_models               = avg_power_models # Unused as of yet.
        self.avg_method                     = avg_method
        self.monomers                       = monomers
        self.use_intra                      = use_intra                  
        self.ob_file_name                   = ob_file_name               
        self.summaryFileNameCompleteness    = summaryFileNameCompleteness
        self.write_dc_lists                 = write_dc_lists             
        self.file_name_base_dc              = file_name_base_dc
        self.hbOnly                         = hbOnly  
        self.excludeBonded                  = True
        self.resList                        = resList        
        self.isPerShellRun                  = False
        
        nTmessage("max_dist_expectedOverall     : %8.3f" % self.max_dist_expectedOverall   )
        nTmessage("min_dist_expected            : %8.3f" % self.min_dist_expected          )
        nTmessage("max_dist_expected            : %8.3f" % self.max_dist_expected          )
        nTmessage("numb_shells_expected         : %d   " % self.numb_shells_expected       )
        nTmessage("min_dist_observed            : %8.3f" % self.min_dist_observed          )
        nTmessage("max_dist_observed            : %8.3f" % self.max_dist_observed          )
        nTmessage("numb_shells_observed         : %d   " % self.numb_shells_observed       )
        nTmessage("avg_power_models             : %s   " % self.avg_power_models           )
        nTmessage("avg_method                   : %s   " % self.avg_method                 )
        nTmessage("monomers                     : %s   " % self.monomers                   )
        nTmessage("use_intra                    : %s   " % self.use_intra                  )
        nTmessage("ob_file_name                 : %s   " % self.ob_file_name               )
        nTmessage("summaryFileNameCompleteness  : %s   " % self.summaryFileNameCompleteness)
        nTmessage("write_dc_lists               : %s   " % self.write_dc_lists             )
        nTmessage("file_name_base_dc            : %s   " % self.file_name_base_dc          )
        nTmessage("resList                      : %s   " % str(self.resList)               )
        nTmessage("hbOnly                       : %s   " % self.hbOnly                     )               
        nTmessage("excludeBonded                : %s   " % self.excludeBonded              )               
        nTmessage("isPerShellRun                : %s   " % self.isPerShellRun              )
        
        if ob_file_name:
            self.lib.readStarFile(ob_file_name)
            
        if self.cacheDistanceInformation():
            nTerror("Failed to cacheDistanceInformation")
            return
        for i in range(2):
            if i:
                self.isPerShellRun = True
            if not self.doCompletenessCheckInnerLoop():
                nTerror("Failed to run %d of completeness check." % i)
                return
            # end if
        # end for
        return True
    # end def
    
    def cacheDistanceInformation(self):
        'Fills below distance sets for later use. Return True on error.'
        
        nTdebug("Now in %s" % getCallerName())        
        
        resListNew = NTlist()
        for residue in self.resList:
            if not self.lib.obsHoH.has_key(residue.resName):
                nTdebug("Skipping %s" % residue)            
                continue
            # end if
            resListNew.append(residue)
        # end for
        self.resList = resListNew
        
        if not self.getAtomList():
            nTerror("Failed getAtomList")
            return True
        
        self.resDistanceHoH = {}  # only up to self.max_dist_expectedOverall
        self.resRadiusHash = {}   # don't pollute our data model but store locally. Key residue, value: radius float
        self.atomDistanceHoH = {} # only up to self.max_dist_expectedOverall
        # Partition by residue for efficiency
        n = len(self.resList)
#        m = len(self.atomList)
        for r in range(n): # rows by columns; rc
            residue = self.resList[r]
            if not self.lib.obsHoH.has_key(residue.resName):
                nTdebug("Skipping %s" % residue)            
                continue
#            nTdebug("Doing radius of %s" % residue)            
            radiusList = residue.radius()
#            nTdebug("Found radii: %s" % str(radiusList))
            if not radiusList:
                nTdebug("Failed to get radius for %s" % residue)
                continue
            radius = max(radiusList)
            setDeepByKeys(self.resRadiusHash, radius, residue)
        # end for
    
        for r in range(n): # rows by columns; rc
            residue1 = self.resList[r]
            nTdebug("Caching distances starting from %s" % residue1)            
            residue1Radius = getDeepByKeysOrAttributes(self.resRadiusHash, residue1)
            if not residue1Radius:
                residue1Radius = 0.0
            rStart = r + 1
            if self.use_intra:
                rStart = r            
            for c in range(rStart, n): # Just do above the diagonal
                residue2 = self.resList[c]
                residue2Radius = getDeepByKeysOrAttributes(self.resRadiusHash, residue2)
                if not residue2Radius:
                    residue2Radius = 0.0
                distanceList = residue1.distance( residue2 ) # center to center
                if not distanceList:
                    nTerror("Failed to get distance between %s and %s. Skipping pair" % (residue1, residue2))
                    continue
                distance = min(distanceList)
                cutoff = self.max_dist_expectedOverall + residue1Radius + residue2Radius
                valueTuple = (residue1, residue2, distance, residue1Radius, residue2Radius,cutoff)
                if distance > cutoff:
#                    nTdebug("Skipping distant residue pair %20s/%20s at %8.3f with radii %8.3f, %8.3f and cutoff %8.3f" % valueTuple)
                    continue
                # end if
#                nTdebug("Adding residue pair           %20s/%20s at %8.3f with radii %8.3f, %8.3f and cutoff %8.3f" % valueTuple)
                setDeepByKeys(self.resDistanceHoH, distance, residue1, residue2)
                # end if
            # end for
        # end for
                
        key1List = self.resDistanceHoH.keys()
        key1List.sort()
        for r,residue1 in enumerate(key1List):
#            atom1 = self.atomList[r]
#            residue1 = self.resList[r]
#            atom1._parent
#            nTdebug("Getting precise distances starting from residue1 %s" % residue1)
            atom1List = NTlist()
            for atom1 in residue1.allAtoms():
                if self.atomHash.has_key(atom1):
                    atom1List.append(atom1)
                # end if  
            # end for  
#            nTdebug("Working on atom1 %s" % atom1)
#            presenceResidue1 = getDeepByKeysOrAttributes( self.resDistanceHoH, residue1 )
#            if not presenceResidue1:
#                nTdebug("Skipping completely missing residue1 %s" % (residue1)) # Will occur for last residue since matrix is sparse.
#                continue
            resDistanceHash = self.resDistanceHoH[residue1]
            key2List = resDistanceHash.keys()
            key2List.sort()
            for c,residue2 in enumerate(key2List):
#                nTdebug("Getting precise distances starting from residue2 %s" % residue2)                                
                
#                distanceResidue1and2 = getDeepByKeysOrAttributes( self.resDistanceHoH, residue1, residue2 )
#                if distanceResidue1and2 == None: # Watch out zero is allowed for the distance
##                    nTdebug("Skipping missing combo residue1/2 %s/%s for atom1/2 %s/%s" % ( residue1, residue2, atom1, atom2))
#                    continue

#                if not self.use_intra:
#                    if residue1 == residue2:
#                        nTcodeerror("Combo with self for %s should not occur here." % residue1)
#                        return True
#                    # end if
#                # end if

                # Only here do we loop over possible atom combos
                atom2List = NTlist()
                for atom2 in residue2.allAtoms():
                    if self.atomHash.has_key(atom2):
                        atom2List.append(atom2)
                    # end if  
                # end for  

                for atom1 in atom1List:
#                    nTdebug("Working on atom1 %s" % atom1)
#                    atom1topology = atom1.topology()
#                    if atom1topology == None:
#                        nTerror("Failed to get atom1's topology; skipping %s" % atom1)
#                        continue
                    for atom2 in atom2List:
                        if atom1 == atom2:
                            continue
                        # end if
                              
#                        nTdebug("Working on atom2 %s" % atom2)
                        if self.hbOnly and not atom1.canFormHydrogenBondWith( atom2 ):
                            continue
                        if self.excludeBonded and atom1.isBondedTo( atom2 ):
#                            nTdebug("Skipping bonded pair")
                            continue
                        # end if
                        atomPairs = NTlist()
                        atomPairs.append((atom1,atom2))
                        dr = DistanceRestraint(atomPairs=atomPairs)
                #        dr.upper = self.max_dist_expectedOverall # Not really used but nice.
                        distance, _sd, _min, _max = dr.calculateAverage()
                        valueTuple = (atom1, atom2, distance)
                        if distance == None:
                            nTwarning("Failed to get distance for %s" % str(valueTuple))
                            continue
                        valueTuple = (atom1, atom2, distance)
                        if distance > self.max_dist_expectedOverall:
                            pass
#                            nTdebug("Skipping distant atom pair %20s/%20s with distance %8.3f" % valueTuple)
                        else:
#                            nTdebug("Adding atom pair           %20s/%20s with distance %8.3f" % valueTuple)
                            setDeepByKeys(self.atomDistanceHoH, distance, atom1, atom2)
                        # end if
                    # end for
                # end for
            # end for
        # end for
        nTdebug("resList          count: %s" % len(self.resList))            
        nTdebug("atomList         count: %s" % len(self.atomList))            
        nTdebug("resDistanceHoH   count: %s" % lenRecursive( self.resDistanceHoH ))
        nTdebug("resRadiusHash    count: %s" % lenRecursive( self.resRadiusHash ))
        nTdebug("atomDistanceHoH  count: %s" % lenRecursive( self.atomDistanceHoH ))
    # end def
        
    
    def addTheoreticalConstraints(self):
        'Using the prehashed info getting the actual precise distances.'
        result = DistanceRestraintList('Vset')
        key1List = self.atomDistanceHoH.keys()
        key1List.sort()
        for atom1 in key1List:
            atomDistanceHash = self.atomDistanceHoH[ atom1 ]
            key2List = atomDistanceHash.keys()
            key2List.sort()
            for atom2 in key2List:
                atomDistance = atomDistanceHash[ atom2 ]
                if atomDistance == None:
                    nTerror("No atom distance found for %s/%s" % (atom1,atom2))
                    continue
                if atomDistance >= self.max_dist_expected: # non-inclusive bound.
                    continue
                if atomDistance < (MIN_DISTANCE_ANY_ATOM_PAIR - 0.4):
                    nTdebug("Small distance %8.3f found for %s/%s" % (atomDistance, atom1,atom2))
#                nTmessage("Looking at distance %8.3f for %s/%s" % (atomDistance, atom1,atom2))
                atomPairsTuple = (atom1, atom2)
                atomPairs = NTlist(atomPairsTuple)
                dr = DistanceRestraint(atomPairs=atomPairs, lower = atomDistance, upper = atomDistance) # Looks weird in xplor otherwise.
                result.append(dr)
            # end for 
        # end for 
        return result
    # end def
         
    def doCompletenessCheckInnerLoop( self ):
        """
    Analyzes the completeness of selected residues.
    Reset the completeness lib first in the ui if needed to change from standard.
    If there are no observable atoms in the coordinate list (e.g. entry 8drh) no
    results will be generated but the return status will still be True for success.
    The same if no restraints were observed.
    
   Return None on error or completeness on success. 
     """

        if self.numb_shells_observed > MAX_SHELLS_OBSERVED:
            self.numb_shells_observed = MAX_SHELLS_OBSERVED
        # end def

        if not self.isPerShellRun:
            self.max_dist_expected = self.max_dist_expectedOverall
        # end def
        

#        Create the sets anew
        dcSetNameList = [
            "USet", # universe of experimental constraints
            "vSet", # universe of theoretical constraints
            "WSet", # union of U and V
            "xSet", # ((U - (E u O)) u V but keeps shrinking on removal of (I u S). Internal to Wattos.
            "ESet", # exceptional
            "OSet", # not observable
            "ISet", # intra residual not to be analyzed
            "SSet", # surplus
            "ASet", # set of observable experimental distance constraints
            "BSet", # set of observable theoretical ...
            "MSet", # A n B
            "CSet", # A - M
            "DSet", # B - M
            "LSet", # contributions with lower bounds
            "PSet"  # contributions with upper bounds
        ]
        for dcSetName in dcSetNameList:
            setDeepByKeys(self, NTlist(), dcSetName)

#        // Find constraints
#        BitSet dcInEntry = SQLSelect.selectBitSet( dc.dbms,
#                dc.mainRelation,
#                Gumbo.DEFAULT_ATTRIBUTE_SET_ENTRY[ RelationSet.RELATION_ID_COLUMN_NAME ],
#                SQLSelect.OPERATION_TYPE_EQUALS, currentEntryRidInt, false );
#        BitSet dcSelectedInEntry = (BitSet) dcInEntry.clone();
#        dcSelectedInEntry.and( dc.selected );
#        int dcSelectedInEntryCount = dcSelectedInEntry.cardinality();
#        if ( dcSelectedInEntryCount < 1 ) {
#            General.showWarning("No selected dcs in first selected entry.");
#            return true;
#        }                

        _doc = """
        if self.getAtomsObservableObjects(resList)) {
            General.showError("Failed to get the observable atoms within the first model");
            return false;
        }
        if ( atomsObservableCombos == null ) {
            General.showCodeBug("atomsObservableCombos is null");
            return false;
        }
        if ( atomsObservableCombos.size() == 0 ) {
            General.showWarning("No observables.");
            return true;
        }


        // Set the newDCListId class attribute
        if ( ! splitDCs( dcSelectedInEntry )) { // input dcs may be spread over multiple dclists.
            General.showError("Failed to split the selected DCs in entry to a new list with one potentially observable contribution per constraint.");
            return false;
        }


        /** Create the sets anew */
        String[] dcSetNames = {
            "USet", // universe of experimental constraints
            "vSet", // universe of theoretical constraints
            "WSet", // union of U and V
            "xSet", // ((U - (E u O)) u V but keeps shrinking on removal of (I u S). Internal to Wattos.
            "ESet", // exceptional
            "OSet", // not observable
            "ISet", // intra residual not to be analyzed
            "SSet", // surplus
            "ASet", // set of observable experimental distance constraints
            "BSet", // set of observable theoretical ...
            "MSet", // A n B
            "CSet", // A - M
            "DSet", // B - M
            "LSet", // contributions with lower bounds
            "PSet"  // contributions with upper bounds
        };
        for (int c=0;c< dcSetNames.length;c++) {
            if ( dc.mainRelation.containsColumn( dcSetNames[ c ] ) ) {
                if ( dc.mainRelation.getColumnDataType( dcSetNames[ c ]  ) != Relation.DATA_TYPE_BIT ) {
                    General.showWarning("Existing column isn't of type BitSet from dc main relation with name: " + dcSetNames[ c ] );
                }
                Object tmpObject = dc.mainRelation.removeColumn( dcSetNames[ c ] );
                if ( tmpObject == null ) {
                    General.showError("Failed to remove existing column from dc main relation with name: " + dcSetNames[ c ] );
                    return false;
                }
            }
            if ( ! dc.mainRelation.insertColumn( dcSetNames[ c ], Relation.DATA_TYPE_BIT, null )) {
                General.showError("Failed to insert bitset column to dc main relation with name: " + dcSetNames[ c ] );
                return false;
            }
        }
        BitSet[] setsToWrite    = {  USet,   vSet,   WSet,   ESet,   OSet,   ISet,   SSet,   ASet,   BSet,   MSet,   CSet,   DSet };
"""
        
        
#        setsToWriteStrList =  'USet vSet WSet ESet OSet ISet SSet ASet BSet MSet CSet DSet'.split() # for future
        setsToWriteStrList =  'vSet '.split()

        _doc = """
        BitSet splitDcs = SQLSelect.selectBitSet( dc.dbms,
                dc.mainRelation,
                Constr.DEFAULT_ATTRIBUTE_SET_DC_LIST[ RelationSet.RELATION_ID_COLUMN_NAME ],
                SQLSelect.OPERATION_TYPE_EQUALS, new Integer(newDCListId), false );
        USet.or( splitDcs ); // All to be checked.
        ASet.clear();
        ASet.or( USet ); // keeps shrinking
// EXCEPTIONAL
        ESet.clear();
        ESet.or( ASet );
        ESet.and( dc.hasUnLinkedAtom ); // Exceptional constraints should be removed.
        General.showDebug("Constraints (E): " + PrimitiveArray.toString( ESet, showValues ));
        ASet.andNot( ESet ); // keeps shrinking
// UNOBSERVABLE
        boolean status = setSelectionObscured(ASet); // will work on OSet
        if ( ! status ) {
            General.showError("Failed to setSelectionObscured");
            return false;
        }
        General.showDebug("Constraints (O): " + PrimitiveArray.toString( OSet, showValues ));
        ASet.andNot( OSet ); // keeps shrinking
"""
#// THEO
    
        result = self.addTheoreticalConstraints()
        if not result:
            nTerror("Failed to addTheoreticalConstraints")
            return
        # end if
        nTmessage("Found number of theo constraints: %s" % len(result))
        self.vSet =  result
        self.xSet.union( self.vSet )    # keeps shrinking
#        xSet.or( ASet);
        
        _doc = """
// INTRAS
        status = dc.classify(xSet);
        if ( ! status ) {
            General.showError("Failed to dc.classify");
            return false;
        }
        if ( ! use_intra ) {
            ISet.or( dc.mainRelation.getColumnBit( DistConstr.DEFAULT_CLASS_NAMES[ DistConstr.DEFAULT_CLASS_INTRA]));
        }
        General.showDebug("Constraints (I): " + PrimitiveArray.toString( ISet, showValues  ));
        xSet.andNot( ISet ); // keeps shrinking
// SURPLUS
        /** Mark the surplus */
        Surplus surplus = new Surplus(ui);
        boolean updateOriginalConstraints = false;
        boolean onlyFilterFixed = false;
//        boolean append = true;

        result = surplus.getSelectionSurplus(
                xSet,
                Surplus.THRESHOLD_REDUNDANCY_DEFAULT,
                updateOriginalConstraints,
                onlyFilterFixed,
                avg_method,
                monomers,
                file_name_base_dc,              // for summary etc.
                true,                           // append
                false,                          // writeNonRedundant,
                false,                          // writeRedundant,
                false                           // removeSurplus
                );
        if ( result == null ) {
            General.showError( "Failed to get surplus.");
            return false;
        }

        SSet.or( result );
        General.showDebug("Constraints (S): " + PrimitiveArray.toString( SSet, showValues  ));
        xSet.andNot( SSet ); // keeps shrinking

        // DO THE LOGIC AGAIN.
        BitSet cleared = (BitSet) ESet.clone();
        cleared.or( OSet );
        cleared.or( ISet );
        cleared.or( SSet );
        ASet.clear();
        ASet.or(USet);
        ASet.andNot( cleared );

        cleared = (BitSet) ISet.clone();
        cleared.or( SSet );
        BSet.clear();
        BSet.or(vSet);
        BSet.andNot( cleared );

        MSet.or( ASet );
        MSet.and( BSet );
        CSet.or(ASet);
        CSet.andNot(MSet);
        DSet.or(BSet);
        DSet.andNot(MSet);

        WSet.clear();
        WSet.or( USet );
        WSet.or( vSet );

        int USetCount = USet.cardinality();
        int VSetCount = vSet.cardinality();
        int ESetCount = ESet.cardinality();
        int OSetCount = OSet.cardinality();
        int ISetCount = ISet.cardinality();
        int SSetCount = SSet.cardinality();
        int ASetCount = ASet.cardinality();
        int BSetCount = BSet.cardinality();
        int MSetCount = MSet.cardinality();
        int CSetCount = CSet.cardinality();
        int DSetCount = DSet.cardinality();

        float overall_completeness_factor = Defs.NULL_FLOAT;
        if ( !isPerShellRun ) {
            if ( BSetCount != 0 ) {
                overall_completeness_factor = 100f * MSetCount / BSetCount;
            } else {
                General.showWarning("The completeness is undefined because there aren't any expected constraints.");
            }

            if ( Defs.isNull( overall_completeness_factor )) {
                General.showWarning("Failed to calculate the completeness");
            } else {
                General.showOutput( "Overal completeness is " + overall_completeness_factor );
            }
        }

        gumbo.entry.selected.clear();
        gumbo.entry.selected.set(currentEntryId);   // only use the current entry
        gumbo.mol.selected.clear();  // clearing the molecules will disable writing them
        gumbo.atom.selected.clear(); // clearing the atoms     will disable writing them
        """
        if self.write_dc_lists and not self.isPerShellRun:                        
            for i,setName in enumerate(setsToWriteStrList):
                drl = getDeepByKeysOrAttributes(self, setName)
                if drl == None:
                    nTerror("Failed to get set %d by name [%s]" % (i, setName))
                    continue
                if not drl:
                    nTdebug("Found empty set %s" % setName)
                fileNameBase = self.file_name_base_dc+"_"+setName
                nTmessage("Writing the set: " + setName + " to file name base: " + fileNameBase
                        + " with number of dcs: %s" % len(drl))
                drl.export2cyana( fileNameBase, convention=CYANA2)
                drl.export2xplor( fileNameBase + '.tbl' )
            #end for
        # end if

        _doc = """
        if ( ! isPerShellRun ) {
            // Create star nodes
            db = new DataBlock();
            if ( db == null ) {
                General.showError( "Failed to init datablock.");
                return false;
            }
            db.title = gumbo.entry.nameList[entryId];
            SaveFrame sF = getSFTemplate();
            if ( sF == null ) {
                General.showError( "Failed to getSFTemplate.");
                return false;
            }
            db.add(sF);
            int rowIdx = 0;
            // INTRO

            TagTable tT = (TagTable) sF.get(0);
            tT.setValue(rowIdx, Relation.DEFAULT_ATTRIBUTE_ORDER_ID , 0);
            tT.setValue(rowIdx, tagNameNOE_compl_listModel_count,     modelCount);
            tT.setValue(rowIdx, tagNameNOE_compl_listResidue_count,   resInModel.cardinality());
            tT.setValue(rowIdx, tagNameNOE_compl_listTot_atom_count,  atomSelectedInModel.cardinality());
            tT.setValue(rowIdx, tagNameNOE_compl_listObserv_atoms,    InOut.getFilenameBase(ob_file_name));
            tT.setValue(rowIdx, tagNameNOE_compl_listObs_atom_count,  atomsObservableCombos.size());
            tT.setValue(rowIdx, tagNameNOE_compl_listUse_intra_resid, use_intra);
            tT.setValue(rowIdx, tagNameNOE_compl_listThreshold_redun, Surplus.THRESHOLD_REDUNDANCY_DEFAULT);
            tT.setValue(rowIdx, tagNameNOE_compl_listAveraging_power, avg_power_models);
            tT.setValue(rowIdx, tagNameNOE_compl_listCompl_cutoff,    max_dist_expected);
            tT.setValue(rowIdx, tagNameNOE_compl_listCompl_cumul,     overall_completeness_factor);
            tT.setValue(rowIdx, tagNameNOE_compl_listRst_unexp_count, dcSelectedInEntry.cardinality());

            tT.setValue(rowIdx, tagNameNOE_compl_listRestraint_count, USetCount);
            tT.setValue(rowIdx, tagNameNOE_compl_listPair_count,      VSetCount);
            tT.setValue(rowIdx, tagNameNOE_compl_listRst_excep_count, ESetCount);
            tT.setValue(rowIdx, tagNameNOE_compl_listRst_nonob_count, OSetCount);
            tT.setValue(rowIdx, tagNameNOE_compl_listRst_intra_count, ISetCount);
            tT.setValue(rowIdx, tagNameNOE_compl_listRst_surpl_count, SSetCount);
            tT.setValue(rowIdx, tagNameNOE_compl_listRst_obser_count, ASetCount);
            tT.setValue(rowIdx, tagNameNOE_compl_listRst_expec_count, BSetCount);
            tT.setValue(rowIdx, tagNameNOE_compl_listRst_match_count, MSetCount);
            tT.setValue(rowIdx, tagNameNOE_compl_listRst_unmat_count, CSetCount);
            tT.setValue(rowIdx, tagNameNOE_compl_listRst_exnob_count, DSetCount);

            tT.setValue(rowIdx, tagNameNOE_compl_listDetails,         explanation);

            // CLASSES
            if ( ! setTagTableClasses( sF )) {
                General.showError("Failed setTagTableClasses");
                return false;
            }
            // RESIDUE
            if ( ! setTagTableRes( sF, file_name_base_dc )) {
                General.showError("Failed setTagTableRes");
                return false;
            }
        } else {
            SaveFrame sF = (SaveFrame) db.get(0);
            if ( sF == null ) {
                General.showError( "Failed to get old SF.");
                return false;
            }
            // SHELL
            if ( ! setTagTableShell( sF )) {
                General.showError("Failed setTagTableClasses");
                return false;
            }
            General.showDebug("Reformat the columns by dictionary defs");
            if ( ! sF.toStarTextFormatting(starDict)) {
                General.showWarning("Failed to format all columns as per dictionary this is not fatal however.");
            }
            General.showOutput("Writing completeness results to STAR file: " + summaryFileNameCompleteness);
            if ( ! db.toSTAR(summaryFileNameCompleteness)) {
                General.showError("Failed to write the file.");
                return false;
            }
        }

        // Restore the selections that can get changed by this code.
        gumbo.atom.selected.clear();
        gumbo.mol.selected.clear();
        gumbo.entry.selected.clear();
        dc.selected.clear();
        dcList.selected.clear();

        gumbo.atom.selected.or(     atomSelectedSave);
        gumbo.mol.selected.or(      molSelectedSave);
        gumbo.entry.selected.or(    entrySelectedSave);
        dc.selected.or(             dcSelectedSave);
        dcList.selected.or(         dcListSelectedSave);

        return true;
    }
    """
        return True
    # end def        
    
    def getAtomList( self ):
        'Return list or None on error.'
        nTdebug("Now in %s" % getCallerName())        
        self.atomList = NTlist()
        if not self.resList:
            nTdebug("Setting resList to all residues")
            self.resList =  self.project.molecule.allResidues()
        for res in self.resList:
            for atom in res.allAtoms():
                if not atom.hasCoordinates(allRealAtomCoordinatesNeeded=True):
                    continue
                parent = atom.getParent()                
                if self.lib.inLib(parent.resName, atom.name):
#                    nTdebug("Found observable atom: %s" % atom)
                    self.atomList.append(atom)
                # end if
#                nTdebug("Found non-observable atom: %s" % atom)
            # end for
        # end for
        nTdebug("Found observable atoms: %s\n%s" % (len(self.atomList), str(self.atomList)))
        self.atomHash = NTdict()
        self.atomHash.appendFromList(self.atomList)
        return self.atomList
    # end def    
# end class

            
def doCompleteness( project,
             max_dist_expectedOverall = 4.0,
             min_dist_observed = 2.0,
             max_dist_observed = 4.0,
             numb_shells_observed = 2,
             min_dist_expected = 2.0,
             max_dist_expected = 10.0,
             numb_shells_expected = 16.0,
             avg_power_models = 1.0,
             avg_method = 1,
             monomers = 1,
             use_intra = False,
             ob_file_name = None,
             summaryFileNameCompleteness = "tmp_dir/XXXX_compl_sum",
             write_dc_lists = True,
             file_name_base_dc  = "tmp_dir/XXXX_compl",
             hbOnly = False,             
             resList = None, # Subset of residues
             ):    
    """
        NB it will not yet do a full completeness check it's just framed this way for future work.
        
       max_dist_expectedOverall  = Maximum distance expected (4.0 suggested)

       min_dist_observed         = Minimum distance observed for per shell listing (2.0 suggested)
       max_dist_observed         = Maximum distance observed for per shell listing (4.0 suggested)
       numb_shells_observed      = Number of shells observed for per shell listing (2 suggested; max is 9)

       min_dist_expected         = Minimum distance expected for per shell listing (2.0 suggested)
       max_dist_expected         = Maximum distance expected for per shell listing (10.0 suggested)
       numb_shells_expected      = Number of shells expected for per shell listing (16 suggested; no max)

       avg_power_models          = Averaging power over models (1.0 suggested)
       avg_method                = Averaging method id. Center,Sum,R6 are 0,1, and 2 respectively : (1 suggested)
       monomers                  = Number of monomers but only relevant when Sum averaging is selected: (1 suggested)
       ob_file_name              = Enter file name of a standard set of observable atoms (fullPath/ob_standard.str or None suggested)
       use_intra                 = Should intraresiduals be considered (n suggested)
       summaryFileNameCompleteness = Enter file name base (with path) for output of completeness check summary
       write_dc_lists            = Should distance constraints be written (y suggested)
       file_name_base_dc         = Enter file name base (with path) for surplus analysis and distance constraints (if selected) to be written
       resList                   = CING residue list or None for all residues with coordinates
       
       Return None on error or completeness on success. 
"""
    nTdebug("Now in %s" % getCallerName())        
    nc = NoeCompleteness(project)
    return nc.doCompletenessCheck(
             max_dist_expectedOverall   = max_dist_expectedOverall   ,
             min_dist_observed          = min_dist_observed          ,
             max_dist_observed          = max_dist_observed          ,
             numb_shells_observed       = numb_shells_observed       ,
             min_dist_expected          = min_dist_expected          ,
             max_dist_expected          = max_dist_expected          ,
             numb_shells_expected       = numb_shells_expected       ,
             avg_power_models           = avg_power_models           ,
             avg_method                 = avg_method                 ,
             monomers                   = monomers                   ,
             use_intra                  = use_intra                  ,
             ob_file_name               = ob_file_name               ,
             summaryFileNameCompleteness= summaryFileNameCompleteness,
             write_dc_lists             = write_dc_lists             ,
             file_name_base_dc          = file_name_base_dc          ,
             hbOnly = hbOnly,             
             resList = resList           
            )
# end def

class NoeCompletenessAtomLib:
    'Info and read methods for STAR library.'
#    /** Local resource */
    STR_FILE_DIR = "Data"
    STR_FILE_NAME = "ob_standard.str"

    saveframeNodeCategoryName      = "completeness_observable_info"
    tagNameCompID                  = "_Comp_ID"
    tagNameAtomID                  = "_Atom_ID"
    fileName = None
        
        
#    /** Creates a new instance of AtomMap */
    def __init__(self, fn = None):  
        self.obsHoH = NTdict() # Set in readStarFile.
        self.obs = None #  Set in readStarFile.  # table of 2 columns
        if not self.readStarFile(fn=fn):
            nTerror("Failed to readStarFile")
        
    def toHoH(self):
        'Create the observable Hash of Hash'
        self.obsHoH = NTdict()
        idxColumnKeyList = [] # indicates all.
        self.obsHoH.appendFromTableGeneric(self.obs, *idxColumnKeyList, invertFirst=True, appendBogusColumn=True)
#        nTdebug("self.obs: %s" % str(self.obs))
        nTdebug("self.obsHoH: %r" % self.obsHoH)
        return self.obsHoH 
        
    def inLib(self, k1, k2):
        'Convenience method.'
        v = getDeepByKeysOrAttributes( self.obsHoH, k1, k2 )
#        nTdebug('In %s atom._parent.resName, atom.name: [%s] [%s] [%s]' % ( getCallerName(), atom._parent.resName, atom.name, v ))
        return v
    
    def readStarFile( self, fn = None):
        'Get the STAR info'
        if not fn:
            fn = os.path.join( cingDirLibs, self.STR_FILE_DIR, self.STR_FILE_NAME)
        nTdebug("Now in %s reading from fn: [%s]" % (getCallerName(), fn))              
        starFile = File(filename=fn)
        starFile.read()

        if starFile.check_integrity():
            nTerror( "In %s STAR text failed integrity check." % getCallerName() )
            return
        sfList = starFile.getSaveFrames(category = self.saveframeNodeCategoryName)
        if not sfList or len(sfList) != 1:
            nTerror("In %s failed to get single saveframe but got list of: [%s]" % ( getCallerName(), sfList))
            return
        saveFrame = sfList[0]
        tT = saveFrame.tagtables[1]
        if not tT:
            nTerror("Expected to find the appropriate tagtable but apparently not." )
            return
        # end if

        varCompID      = tT.getStringListByColumnName(self.tagNameCompID)
        varAtomID      = tT.getStringListByColumnName(self.tagNameAtomID)
        self.obs = [varCompID, varAtomID]
        atomCount = tT.getRowCount()
        nTdebug("Found number of elements in obs : %s" % atomCount)
        self.obsHoH = self.toHoH() # Hashed by resName and atomName/dihedralName          
        return self.obs 
# end class

class TheoreticalDihedralLib(NoeCompletenessAtomLib):
    'Small class with info on STAR library.'
    STR_FILE_NAME                  = "dih_standard.str"
    saveframeNodeCategoryName      = "theoretical_dihedral_observable_info"
    tagNameAtomID                  = "_Dih_ID" # overloaded for simplicity
# end class
                        
class TheoreticalDihedral( NoeCompleteness ):
    'Small class akin to NoeCompleteness super class.'
    def __init__(self, project, **kwds):
        NoeCompleteness.__init__(self, project, **kwds)        
        self.project = project
        self.lib = TheoreticalDihedralLib()
        self.variance                = None         
        self.write_ac_lists          = None   
        self.file_name_base_ac       = None

    def doTheoreticalDihedral( self, 
             variance           = 10.0, 
             ob_file_name       = None,
             write_ac_lists     = True,
             file_name_base_ac  = THEORETICAL_RESTRAINT_LIST_STR,
             resList            = None, # Subset of residues
             ):
        'Convenience method.    Return None on error or completeness on success. '
        
        self.variance                = variance         
        self.ob_file_name            = ob_file_name         
        self.write_ac_lists          = write_ac_lists   
        self.file_name_base_ac       = file_name_base_ac
        self.resList                 = resList          
        
        nTmessage("variance          : %8.3f" % self.variance            )
        nTmessage("write_ac_lists    : %s"    % self.write_ac_lists      )
        nTmessage("file_name_base_ac : %s"    % self.file_name_base_ac   )
        nTmessage("resList           : %s   " % str(self.resList)        )
        
        if ob_file_name:
            self.lib.readStarFile(ob_file_name)
            
            
        result = DihedralRestraintList('Vset')
        for residue in self.resList:
            residueDef = residue.db
            for dihedralDef in residueDef.dihedrals:
                comboStr = "%s %s" % (residue, dihedralDef)
                if not self.lib.inLib(residue.resName, dihedralDef.name):
                    nTdebug("Skipping unwelcome " + comboStr)
                    continue
                dihedral = getDeepByKeysOrAttributes(residue, dihedralDef.name )
                if not dihedral:
                    nTdebug("No dihedral for " + comboStr)
                    continue
                atoms = getDeepByKeysOrAttributes(dihedral, ATOMS_STR)
                if not atoms:
                    nTerror("Failed to find atoms for " + comboStr)
                    continue
                dihedralAverage = dihedral.calculateValues()
                if not dihedralAverage or isNaN(dihedralAverage[0]):
                    nTerror("Failed to find dihedralAverage for " + comboStr)
                    continue                    
                cav, _cv = dihedralAverage
                lower = cav - variance
                upper = cav + variance
                dihedralRestraint = DihedralRestraint(atoms=atoms, lower=lower, upper=upper)
                result.append(dihedralRestraint)
            # end for 
        # end for 
        if self.write_ac_lists:                        
            if not result:
                nTdebug("Found empty result list")
                return result
        # end if 
        nTmessage("Writing the list to file name base: " + self.file_name_base_ac
                + " with number of restraints: %s" % len(result))
        result.export2cyana( self.file_name_base_ac + '.aco', convention=CYANA2)    # pylint: disable=E1101
        result.export2xplor( self.file_name_base_ac + '.tbl' )                      # pylint: disable=E1101
        return result
    # end def
# end class
           
           
def doTheoreticalDihedral( project,
             variance           = 10.0, 
             ob_file_name       = None,
             write_ac_lists     = True,
             file_name_base_ac  = THEORETICAL_RESTRAINT_LIST_STR,
             resList            = None, # Subset of residues
             ):    
    """        
       variance  = Plus and minus deviation from target allowed (10.0 suggested)
       write_ac_lists            = Should constraints be written (y suggested)
       file_name_base_ac         = Enter file name base (with path) for output
       resList                   = CING residue list or None for all residues with coordinates
       
       Return None on error or completeness on success. 
    """
    nTdebug("Now in %s" % getCallerName())        
    td = TheoreticalDihedral(project)
    return td.doTheoreticalDihedral(
             variance           = variance           ,
             ob_file_name       = ob_file_name       ,
             write_ac_lists     = write_ac_lists     ,
             file_name_base_ac  = file_name_base_ac  ,
             resList            = resList           
            )
# end def