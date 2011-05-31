'''
Created on May 30, 2011

@author: jd
'''
from cing import cingDirLibs
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.STAR.File import File
from cing.core.classes2 import AtomList
from cing.core.classes import DistanceRestraint

OVER_NUMBER_OF_SIGMAS_STR    = ">sigma"
NO_MULTIMER_STR              = "no multimer"
NO_INTRAS_STR                = "no intras"

#/** The eight is used for overflow */
MAX_SHELLS_OBSERVED = 9

class NoeCompleteness( NTdict ):
    def __init__(self, project, **kwds):
        NTdict.__init__(self, **kwds)        
        self.project = project
        self.completenessLib = NoeCompletenessAtomLib()
        self.modelCount = self.project.molecule.modelCount
        self.atomList = AtomList()
        self.resDistanceHoH = {}  # only up to self.max_dist_expectedOverall
        self.resRadiusHash = {}   # don't pollute our data model but store locally. Key residue, value: radius float
        self.atomDistanceHoH = {} # only up to self.max_dist_expectedOverall
        
    def doCompletenessCheck( self, 
             max_dist_expectedOverall = 4.0,
             min_dist_observed = 2.0,
             max_dist_observed = 4.0,
             numb_shells_observed = 2,
             min_dist_expected = 2.0,
             max_dist_expected = 10.0,
             numb_shells_expected = 16.0,
             avg_power_models = 1.0, # unused
             avg_method = 1,# unused
             monomers = 1,# unused
             use_intra = False,
             ob_file_name = None,
             summaryFileNameCompleteness = "tmp_dir/XXXX_DOCR_compl_sum",
             write_dc_lists = True,
             file_name_base_dc  = "tmp_dir/XXXX_DOCR_compl",
             resList = None, # Subset of residues                                  
             ):
        'Convenience method.    Return None on error or completeness on success. '

        
        self.max_dist_expectedOverall = max_dist_expectedOverall
        self.min_dist_expected      = min_dist_expected
        self.max_dist_expected      = max_dist_expected
        self.numb_shells_expected   = numb_shells_expected

        self.min_dist_observed      = min_dist_observed
        self.max_dist_observed      = max_dist_observed
        self.numb_shells_observed   = numb_shells_observed

        self.avg_power_models       = avg_power_models # Unused as of yet.
        self.avg_method             = avg_method
        self.monomers               = monomers
        
        self.use_intra                      = use_intra                  
        self.ob_file_name                   = ob_file_name               
        self.summaryFileNameCompleteness    = summaryFileNameCompleteness
        self.write_dc_lists                 = write_dc_lists             
        self.file_name_base_dc              = file_name_base_dc          
        self.resList                        = resList
        
        self.isPerShellRun = False
        
        if self.cacheDistanceInformation():
            NTerror("Failed to cacheDistanceInformation")
            return
        for i in range(2):
            if i:
                self.isPerShellRun = True
            if not self.doCompletenessCheckInnerLoop():
                NTerror("Failed to run %d of completeness check." % i);
                return
            # end if
        # end for
        return True
    # end def
    
    def cacheDistanceInformation(self):
        'Fills below distance sets for later use. Return True on error.'
        
        NTdebug("Now in %s" % getCallerName())        
        
        if not self.getAtomList():
            NTerror("Failed getAtomList")
            return True
        
        self.resDistanceHoH = {}  # only up to self.max_dist_expectedOverall
        self.resRadiusHash = {}   # don't pollute our data model but store locally. Key residue, value: radius float
        self.atomDistanceHoH = {} # only up to self.max_dist_expectedOverall
        # Partition by residue for efficiency
        n = len(self.resList)
        m = len(self.atomList)
        for r in range(n): # rows by columns; rc            
            residue = self.resList[r]
            radiusList = residue.radius()
#            NTdebug("Found radii: %s" % str(radiusList))
            if not radiusList:
                NTdebug("Failed to get radius for %s" % residue)
                continue
            radius = max(radiusList)
            setDeepByKeys(self.resRadiusHash, radius, residue)
        # end for
    
        for r in range(n): # rows by columns; rc
            residue1 = self.resList[r]
            NTdebug("Working on residue1 %s" % residue1)
            residue1Radius = getDeepByKeysOrAttributes(self.resRadiusHash, residue1)
            if not residue1Radius:
                NTdebug("Skipping radiusLess residue1 %s" % residue1)
                continue
            rStart = r + 1
            if self.use_intra:
                rStart = r            
            for c in range(rStart, n): # Just do above the diagonal
                residue2 = self.resList[c]
                NTdebug("Working on residue2 %s" % residue2)
                residue2Radius = getDeepByKeysOrAttributes(self.resRadiusHash, residue2)
                if not residue2Radius:
                    NTdebug("Skipping radiusLess residue2 %s" % residue2)
                    continue
                distanceList = residue1.distance( residue2 )
                if not distanceList:
                    NTerror("Failed to get distance between %s and %s. Skipping pair" % (residue1, residue2))
                    continue
                distance = min(distanceList)
                cutoff = self.max_dist_expectedOverall + residue1Radius + residue2Radius
                valueTuple = (residue1, residue2, distance, residue1Radius, residue2Radius,cutoff)
                if distance > cutoff:
                    NTdebug("Skipping distant residue pair %20s/%20s at %8.3f with radii %8.3f, %8.3f and cutoff %8.3f" % valueTuple)
                else:
                    NTdebug("Adding residue pair           %20s/%20s at %8.3f with radii %8.3f, %8.3f and cutoff %8.3f" % valueTuple)
                    setDeepByKeys(self.resDistanceHoH, distance, residue1, residue2)
                # end if
            # end for
        # end for
                
        for r in range(m): # rows by columns; rc
            atom1 = self.atomList[r]
            residue1 = atom1._parent
#            NTdebug("Working on atom1 %s" % atom1)
            presenceResidue1 = getDeepByKeysOrAttributes( self.resDistanceHoH, residue1 )
            if not presenceResidue1:
                NTdebug("Skipping completely missing residue1 %s for %s" % (residue1, atom1)) # Will occur for last residue since matrix is sparse.
                continue
            rStart = r + 1
            if self.use_intra:
                rStart = r
            for c in range(rStart, m): # Just do above the diagonal
                atom2 = self.atomList[c]
                if atom2 == atom1: # may occur when including intra residuals.
                    continue 
                residue2 = atom2._parent
#                NTdebug("Working on atom2 %s" % atom2)
                distanceResidue1and2 = getDeepByKeysOrAttributes( self.resDistanceHoH, residue1, residue2 )
                if distanceResidue1and2 == None: # Watch out zero is allowed for the distance
                    NTdebug("Skipping missing combo residue1/2 %s/%s for atom1/2 %s/%s" % ( residue1, residue2, atom1, atom2))
                    continue
                atomPairs = NTlist()
                atomPairs.append((atom1,atom2))
                dr = DistanceRestraint(atomPairs=atomPairs)
        #        dr.upper = self.max_dist_expectedOverall # Not really used but nice.
                distance, _sd, _min, _max = dr.calculateAverage()
                valueTuple = (atom1, atom2, distance)
                if distance == None:
                    NTwarning("Failed to get distance for %s" % str(valueTuple))
                    continue
                valueTuple = (atom1, atom2, distance)
                if distance > self.max_dist_expectedOverall:
                    NTdebug("Skipping distant atom pair %20s/%20s with distance %8.3f" % valueTuple)
                else:
                    NTdebug("Adding atom pair           %20s/%20s with distance %8.3f" % valueTuple)
                    setDeepByKeys(self.atomDistanceHoH, distance, atom1, atom2)
                # end if
            # end for
        # end for
        NTdebug("resList          count: %s" % len(self.resList))            
        NTdebug("atomList         count: %s" % len(self.atomList))            
        NTdebug("resDistanceHoH   count: %s" % lenRecursive( self.resDistanceHoH ))
        NTdebug("resRadiusHash    count: %s" % lenRecursive( self.resRadiusHash ))
        NTdebug("atomDistanceHoH  count: %s" % lenRecursive( self.atomDistanceHoH ))
    # end def
        
    
    def addTheoreticalConstraints(self):
        return
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
            "VSet", # universe of theoretical constraints
            "WSet", # union of U and V
            "XSet", # ((U - (E u O)) u V but keeps shrinking on removal of (I u S). Internal to Wattos.
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

        """
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
            "VSet", // universe of theoretical constraints
            "WSet", // union of U and V
            "XSet", // ((U - (E u O)) u V but keeps shrinking on removal of (I u S). Internal to Wattos.
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

        BitSet[] setsToWrite    = {  USet,   VSet,   WSet,   ESet,   OSet,   ISet,   SSet,   ASet,   BSet,   MSet,   CSet,   DSet };
        String[] setsToWriteStr = { "USet", "VSet", "WSet", "ESet", "OSet", "ISet", "SSet", "ASet", "BSet", "MSet", "CSet", "DSet" }; // stupid

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

        return True # TODO: pick up from here.
    
        result = self.addTheoreticalConstraints()
        if not result:
            NTerror("Failed to addTheoreticalConstraints");
            return
        # end if
        NTmessage("Found number of theo constraints: %s" % len(result));
        self.VSet =  result
        self.XSet.union( self.VSet )    # keeps shrinking
#        XSet.or( ASet);
        
        """
// INTRAS
        status = dc.classify(XSet);
        if ( ! status ) {
            General.showError("Failed to dc.classify");
            return false;
        }
        if ( ! use_intra ) {
            ISet.or( dc.mainRelation.getColumnBit( DistConstr.DEFAULT_CLASS_NAMES[ DistConstr.DEFAULT_CLASS_INTRA]));
        }
        General.showDebug("Constraints (I): " + PrimitiveArray.toString( ISet, showValues  ));
        XSet.andNot( ISet ); // keeps shrinking
// SURPLUS
        /** Mark the surplus */
        Surplus surplus = new Surplus(ui);
        boolean updateOriginalConstraints = false;
        boolean onlyFilterFixed = false;
//        boolean append = true;

        result = surplus.getSelectionSurplus(
                XSet,
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
        XSet.andNot( SSet ); // keeps shrinking

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
        BSet.or(VSet);
        BSet.andNot( cleared );

        MSet.or( ASet );
        MSet.and( BSet );
        CSet.or(ASet);
        CSet.andNot(MSet);
        DSet.or(BSet);
        DSet.andNot(MSet);

        WSet.clear();
        WSet.or( USet );
        WSet.or( VSet );

        int USetCount = USet.cardinality();
        int VSetCount = VSet.cardinality();
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
        if ( write_dc_lists && (!isPerShellRun)) {
            for (int setId=0;setId<setsToWrite.length;setId++) {
                BitSet setToWrite = setsToWrite[setId];
                String setName = setsToWriteStr[setId];
                String fileName = file_name_base_dc+"_"+setName+".str";
                dc.selected.clear();
                dc.selected.or(setToWrite);
                if ( dc.selected.cardinality() > 0 ) {
                    General.showOutput("Writing the set: " + setName + " to file: " + fileName
                            + " with number of dcs: " + dc.selected.cardinality());
                    gumbo.entry.writeNmrStarFormattedFileSet(fileName,null,ui);
                } else {
                    General.showOutput("Not writing set: " + setName + " to file: " + fileName
                            + " because there are no dcs in it");
                    File oldDump = new File( fileName );
                    if ( oldDump.exists() && oldDump.isFile() && oldDump.canRead() ) {
                        General.showDebug("Removing old dump.");
                        if ( ! oldDump.delete() ) {
                            General.showWarning("Failed to remove old dump");
                        }
                    }
                }
            }
        }
        int entryId = gumbo.entry.getEntryId();

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
        NTdebug("Now in %s" % getCallerName())        
        self.atomList = AtomList()
        if not self.resList:
            NTdebug("Setting resList to all residues")
            self.resList =  self.project.molecule.allResidues()
        for res in self.resList:
            for atom in res.allAtoms():
                if not atom.hasCoordinates(allRealAtomCoordinatesNeeded=True):
                    continue
                if self.completenessLib.inAtomLib(atom):
#                    NTdebug("Found observable atom: %s" % atom)
                    self.atomList.append(atom)
                # end if
#                NTdebug("Found non-observable atom: %s" % atom)
            # end for
        # end for
        NTdebug("Found observable atoms: %s\n%s" % (len(self.atomList), str(self.atomList)))
        return self.atomList
    # end def    
# end class

            
def doCompletenessCheck( project,
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
             summaryFileNameCompleteness = "tmp_dir/XXXX_DOCR_compl_sum",
             write_dc_lists = True,
             file_name_base_dc  = "tmp_dir/XXXX_DOCR_compl",
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
    NTdebug("Now in %s" % getCallerName())        
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
             resList = resList           
            )
# end def

class NoeCompletenessAtomLib:
#    /** Local resource */
    STR_FILE_DIR = "Data"
    STR_FILE_NAME = "ob_standard.str"

    saveframeNodeCategoryName      = "completeness_observable_info"
    tagNameCompID                  = "_Comp_ID"
    tagNameAtomID                  = "_Atom_ID"
    fileName = None
        
        
#    /** Creates a new instance of AtomMap */
    def __init__(self):  
        self.obs = self.readStarFile() # table of 2 columns
        self.obsHoH = self.toHoH() # Hashed by resName and atomName
        
    def toHoH(self):
        self.obsHoH = NTdict()
        idxColumnKeyList = [] # indicates all.
        self.obsHoH.appendFromTableGeneric(self.obs, *idxColumnKeyList, invertFirst=True, appendBogusColumn=True)
#        NTdebug("self.obs: %s" % str(self.obs))
        NTdebug("self.obsHoH: %r" % self.obsHoH)
        return self.obsHoH 
        
    def inAtomLib(self, atom):
        v = getDeepByKeysOrAttributes( self.obsHoH, atom._parent.resName, atom.name )
#        NTdebug('In %s atom._parent.resName, atom.name: [%s] [%s] [%s]' % ( getCallerName(), atom._parent.resName, atom.name, v ))
        return v
    
    def readStarFile( self, fn = None):
        NTdebug("Now in NoeCompletenessAtomLib#readStarFile" )              
        if not fn:
            fn = os.path.join( cingDirLibs, self.STR_FILE_DIR, self.STR_FILE_NAME)
        starFile = File(filename=fn)
        starFile.read()

        if starFile.check_integrity():
            NTerror( "In %s STAR text failed integrity check." % getCallerName() )
            return
        sfList = starFile.getSaveFrames(category = self.saveframeNodeCategoryName)
        if not sfList or len(sfList) != 1:
            NTerror("In %s failed to get single saveframe but got list of: [%s]" % ( getCallerName(), sfList))
            return
        saveFrame = sfList[0]
        tT = saveFrame.tagtables[1]
        if not tT:
            NTerror("Expected to find the appropriate tagtable but apparently not." )
            return
        # end if

        varCompID      = tT.getStringListByColumnName(self.tagNameCompID)
        varAtomID      = tT.getStringListByColumnName(self.tagNameAtomID)
        self.obs = [varCompID, varAtomID]
        atomCount = tT.getRowCount()
        NTdebug("Found number of elements in obs : %s" % atomCount)  
        return self.obs      