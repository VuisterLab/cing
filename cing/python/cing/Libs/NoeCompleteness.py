#@PydevCodeAnalysisIgnore
'''
Created on May 30, 2011

@author: jd
'''
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.STAR.File import File

OVER_NUMBER_OF_SIGMAS_STR    = ">sigma"
NO_MULTIMER_STR              = "no multimer"
NO_INTRAS_STR                = "no intras"

#/** The eight is used for overflow */
MAX_SHELLS_OBSERVED = 9

class NoeCompleteness:
    def __init__(self, project):
        self.project = project
        self.completenessLib = CompletenessLib()
        
    def doCompletenessCheck( self, 
             max_dist_expectedOverall,
             min_dist_observed,
             max_dist_observed,
             numb_shells_observed,
             min_dist_expected,
             max_dist_expected,
             numb_shells_expected,
             avg_power_models,
             avg_method,
             monomers,
             use_intra,
             ob_file_name,
             summaryFileNameCompleteness,
             write_dc_lists,
             file_name_base_dc,
             resList = None, # Subset of residues             
             ):
        'Convenience method.'
        isPerShellRun = False
        for r in range(2):
            if r:
                isPerShellRun = True
            if not self._doCompletenessCheck(
                    max_dist_expectedOverall,
                    min_dist_observed,
                    max_dist_observed,
                    numb_shells_observed,
                    min_dist_expected,
                    max_dist_expected,
                    numb_shells_expected,
                    isPerShellRun,
                    avg_power_models,
                    avg_method,
                    monomers,
                    use_intra,
                    ob_file_name,
                    summaryFileNameCompleteness,
                    write_dc_lists,
                    file_name_base_dc,
                    resList = resList, # Subset of residues
                    ):
                NTerror("Failed to run " + r + " of completeness check.");
                return
            # end if
        # end for
        return True
    # end def
    
    
    def _doCompletenessCheck( self,
             max_dist_expectedOverall,
             min_dist_observed,
             max_dist_observed,
             numb_shells_observed,
             min_dist_expected,
             max_dist_expected,
             numb_shells_expected,
             isPerShellRun,
             avg_power_models,
             avg_method,
             monomers,
             use_intra,
             ob_file_name,
             summaryFileNameCompleteness,
             write_dc_lists,
             file_name_base_dc            ,
             resList = None, # Subset of residues
             ):
        """
    Analyzes the completeness of selected residues.
    Reset the completeness lib first in the ui if needed to change from standard.
    If there are no observable atoms in the coordinate list (e.g. entry 8drh) no
    results will be generated but the return status will still be true for success.
    The same if no restraints were observed.
     """

        if numb_shells_observed > MAX_SHELLS_OBSERVED:
            numb_shells_observed = MAX_SHELLS_OBSERVED
        # end def

        if not isPerShellRun:
            max_dist_expected = max_dist_expectedOverall
        # end def
        

        self.min_dist_expected      = min_dist_expected;
        self.max_dist_expected      = max_dist_expected;
        self.numb_shells_expected   = numb_shells_expected;

        self.min_dist_observed      = min_dist_observed;
        self.max_dist_observed      = max_dist_observed;
        self.numb_shells_observed   = numb_shells_observed;

        self.avg_power_models       = avg_power_models;
        self.avg_method             = avg_method;
        self.monomers               = monomers;

        showValues = False
#        // Store the selections that can get changed by this code.
#        BitSet atomSelectedSave     = (BitSet) gumbo.atom.selected.clone();
#        BitSet dcSelectedSave       = (BitSet) dc.selected.clone();
#        BitSet dcListSelectedSave   = (BitSet) dcList.selected.clone();


        modelCount = self.project.molecule.modelCount
        doFancyAveraging = avg_power_models != 1.0 # faster to do simpel averaging.
        NTdebug("doFancyAveraging: %s" % doFancyAveraging)

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
        USet =  dc.mainRelation.getColumnBit( "USet" );
        VSet =  dc.mainRelation.getColumnBit( "VSet" );
        WSet =  dc.mainRelation.getColumnBit( "WSet" );
        XSet =  dc.mainRelation.getColumnBit( "XSet" );
        ESet =  dc.mainRelation.getColumnBit( "ESet" );
        OSet =  dc.mainRelation.getColumnBit( "OSet" );
        ISet =  dc.mainRelation.getColumnBit( "ISet" );
        SSet =  dc.mainRelation.getColumnBit( "SSet" );
        ASet =  dc.mainRelation.getColumnBit( "ASet" );
        BSet =  dc.mainRelation.getColumnBit( "BSet" );
        MSet =  dc.mainRelation.getColumnBit( "MSet" );
        CSet =  dc.mainRelation.getColumnBit( "CSet" );
        DSet =  dc.mainRelation.getColumnBit( "DSet" );
        LSet =  dc.mainRelation.getColumnBit( "LSet" );
        PSet =  dc.mainRelation.getColumnBit( "PSet" );

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
// THEO
        BitSet result = addTheoreticalConstraints(ASet, max_dist_expected, use_intra); // Looking only in ASet to match
        if ( result == null  ) {
            General.showError("Failed to addTheoreticalConstraints");
            return false;
        }
        General.showDebug("Found number of theo constraints: " + result.cardinality());
        VSet.or( result );
        XSet.or( VSet );    // keeps shrinking
        XSet.or( ASet);
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
    
# end class
    
class CompletenessLib:
#    /** Local resource */
    STR_FILE_DIR = "Data"
    STR_FILE_NAME = "ob_standard.str"

    saveframeNodeCategoryName      = "completeness_observable_info"
    tagNameCompID                  = "_Comp_ID"
    tagNameAtomID                  = "_Atom_ID"
    fileName = None
        
        
#    /** Creates a new instance of AtomMap */
    def __init__(self):  
        self.obs = self.readStarFile()
        
        
    def readStarFile( self, fn = None):
        NTdebug("Now in %s" % getCallerName)              
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