"""
Stores data into RDB for one entry

Execute like:
cd /Library/WebServer/Documents/CASD-NMR-CING/data/eR/NeR103ALyon2; \
python -u $CINGROOT/python/cing/NRG/storeCING2db.py NeR103ALyon2 ARCHIVE_CASD

cd /Library/WebServer/Documents/CASP-NMR-CING/data/05/T0538Org; \
python -u $CINGROOT/python/cing/NRG/storeCING2db.py T0538Org ARCHIVE_CASP

cd $D/NRG-CING/data/br/1brv; \
python -u $CINGROOT/python/cing/NRG/storeCING2db.py 1brv ARCHIVE_NRG

cd /Library/WebServer/Documents/NRG-CING/data/cj/1cjg; \
python -u $CINGROOT/python/cing/NRG/storeCING2db.py 1cjg ARCHIVE_NRG

cd /Library/WebServer/Documents/NMR_REDO/data/br/1brv; \
python -u $CINGROOT/python/cing/NRG/storeCING2db.py 1brv ARCHIVE_NMR_REDO

cd /Library/WebServer/Documents/RECOORD/data/br/1brv; \
python -u $CINGROOT/python/cing/NRG/storeCING2db.py 1brv ARCHIVE_RECOORD

NB this script fails if the Postgresql backend is not installed. Which is exactly why it's kept out of CING's core routines.
"""

import cing
from cing.constants import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.helper import getSvnRevision
from cing.NRG import * #@UnusedWildImport
from cing.PluginCode.required.reqDssp import * #@UnusedWildImport
from cing.PluginCode.required.reqProcheck import * #@UnusedWildImport
from cing.PluginCode.required.reqQueeny import * #@UnusedWildImport
from cing.PluginCode.required.reqWattos import * #@UnusedWildImport
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.PluginCode.sqlAlchemy import CsqlAlchemy
from cing.core.classes import Project
from cing.core.molecule import chothiaId2DbStr
from cing.core.molecule import getAssignmentCountMapForResList
from cing.core.parameters import directories
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import select

db_name = PDBJ_DB_NAME
user_name = PDBJ_DB_USER_NAME
maxNumberOfRdbConnectionTries = 5
rdbConnectionRetryDelaySeconds = 60
def doStoreCING2db( entry_code, archive_id, project = None):
    """Cwd should be where the project is located.
    Returns True on error.

    If project is given then use that instead of loading a different one.
    """
    doReadProject = True
    if project:
        doReadProject = False

    pdb_id = None
    casd_id = None
    schema = getDeepByKeysOrAttributes( mapArchive2Schema, archive_id)
    if not schema:
        nTerror("Expected valid schema for archive_id: %s" % archive_id)
        return True
    # end if

    if archive_id in  [ ARCHIVE_NRG_ID, ARCHIVE_DEV_NRG_ID, ARCHIVE_PDB_ID,
                        ARCHIVE_NMR_REDO_ID, ARCHIVE_NMR_REDOA_ID, ARCHIVE_RECOORD_ID, ARCHIVE_RECOORDA_ID]:
        pdb_id = entry_code
        if pdb_id == None:
            nTerror("Expected pdb_id argument")
            return True
        if not is_pdb_code(pdb_id):
            nTerror("Expected pdb_id argument and [%s] isn't recognized as such." % pdb_id)
            return True
        # end if
    elif archive_id in [ ARCHIVE_CASD_ID, ARCHIVE_CASP_ID]:
        casd_id = entry_code
        if casd_id == None:
            nTerror("Expected casd_id argument")
            return True
        entry_code = casd_id
    else:
        nTerror("Expected valid archive_id argument but got: %s" % archive_id)
        return True
    # end if


    nTdebug("Starting doStoreCING2db using:")
    nTdebug("entry_code:           %s" % entry_code)
    nTdebug("archive_id:           %s" % archive_id)
    nTdebug("user_name:            %s" % user_name)
    nTdebug("db_name:              %s" % db_name)
    nTdebug("schema:               %s" % schema)
    nTdebug("doReadProject:        %s" % doReadProject)

    # Read project before opening the database connection in order to save access time to RDB.
    # Storing is on same order of time as reading.
    if doReadProject:
        # presume the directory still needs to be created.
        cingEntryDir = entry_code + ".cing"
        cingEntryTgz = entry_code + ".cing.tgz"
        if not ( os.path.isdir(cingEntryDir) or os.path.exists(cingEntryTgz)):
            nTerror("Failed to find input directory: %s" % cingEntryDir)
            return
        # end if.
        # Needs to be copied because the open method doesn't take a directory argument..
        project = Project.open(entry_code, status='old')
        if not project:
            nTerror("Failed to init old project")
            return True
        # end if.
    # end if project


#    echo = 'debug'
    echo = False # Default no echo. Can be True or 'debug'
    csql = CsqlAlchemy(user=user_name, db=db_name,schema=schema, echo=echo)
    if csql.connect(maxTries=5, retryInitialDelaySeconds = 60., retryDelayFactor = 4. ):
        nTerror("Failed to connect to DB.")
        return True
    # end if
    csql.autoload()

    execute = csql.conn.execute
    centry = csql.cingentry
    cchain = csql.cingchain
    cresidue = csql.cingresidue
    catom = csql.cingatom
    cresonancelist = csql.cingresonancelist
    cresonancelistperatomclass = csql.cingresonancelistperatomclass
    cdrlist = csql.drlist
    cdr = csql.dr

    # shortcuts
    p = project
    molecule = project.molecule

#    p.runCingChecks() # need because otherwise the restraints aren't partitioned etc.
    if False: # TODO: enable when done testing overall strategy.
        p.validate(parseOnly=True, htmlOnly=True)

    if archive_id == ARCHIVE_CASD_ID or archive_id == ARCHIVE_CASP_ID:
        result = execute(centry.delete().where(centry.c.casd_id == casd_id))
    else:
        result = execute(centry.delete().where(centry.c.pdb_id == pdb_id))

    if result.rowcount:
        if result.rowcount != 1:
            nTdebug("Removed original entries numbering: %s" % result.rowcount)
        if result.rowcount > 1:
            nTerror("Removed more than the expected ONE entry; this could be serious.")
            return True
#    else:
#        nTdebug("No original entry present yet.")

    logFileNameList = project.getLogFileNameList(latestListedFirst = False) #sorted chronologically with latest latest.
    rev_first = None
    rev_last = getSvnRevision()
    timestamp_first = None
    timestamp_last = datetime.datetime.now()

    if not logFileNameList:
        nTerror("Failed to get log file name list; aborting.")
        return True

    firstIdx = 0
#    lastIdx = -1 # Just do first for now and take the last from the above defaults.
#    for logIdx in ( firstIdx, lastIdx):
    for logIdx in ( firstIdx, ):
        logFileName = logFileNameList[logIdx]
        logFilePath = os.path.join( project.path(directories.logs), logFileName)
        result = getRevDateCingLog( logFilePath )
        if not result:
            nTerror("In %s failed to getRevDateCingLog for: %s" % (getCallerName(), logFilePath))
            continue # with next log.
        # end if
        rev, datetime_seen = result
        if logIdx == firstIdx:
            rev_first = rev
            timestamp_first = datetime_seen
        else:
            if rev_last != rev:
                nTcodeerror("Mismatching rev %s with rev extracted from self log: %s" % ( rev_last, rev))
            # should be pretty close to now datetime set above.
            timestamp_last = datetime_seen # Better to use the start date of log than now time.
#            nTdebug("Modifying timestamp_last %s to %s" % (timestamp_last, datetime_seen) )
        # end if
    # end for
    bmrb_id = getDeepByKeysOrAttributes(molecule, BMRB_ENTRY_LIST_STR, 0)
    ranges = getDeepByKeysOrAttributes(molecule,RANGES_STR)
    p_rmsd_backbone = getDeepByKeysOrAttributes(molecule, RMSD_STR, BACKBONE_AVERAGE_STR, VALUE_STR)
    p_rmsd_sidechain = getDeepByKeysOrAttributes(molecule, RMSD_STR, HEAVY_ATOM_AVERAGE_STR, VALUE_STR)
    p_cv_backbone = getDeepByKeysOrAttributes(molecule, CV_BACKBONE_STR)
    p_cv_sidechain = getDeepByKeysOrAttributes(molecule, CV_SIDECHAIN_STR)

    chainList = molecule.allChains()
    is_multimeric = len(chainList) > 1
    symmetry, ncsSymmetry, drSymmetry = None, None, None
    symmetryResult = molecule.getSymmetry()
    if symmetryResult != None:
        symmetry, ncsSymmetry, drSymmetry = symmetryResult

    chothia_class = molecule.chothiaClassInt()
    chothia_class_str = chothiaId2DbStr(chothia_class) # Difference than string representation in CING api.
    molTypeCountList = molecule.getMolTypeCountList()
    p_protein_count = molTypeCountList[ mapMoltypeToInt[PROTEIN_STR] ]
    p_dna_count     = molTypeCountList[ mapMoltypeToInt[DNA_STR] ]
    p_rna_count     = molTypeCountList[ mapMoltypeToInt[RNA_STR] ]
    p_water_count   = molTypeCountList[ mapMoltypeToInt[WATER_STR] ]
    p_other_count   = molTypeCountList[ mapMoltypeToInt[OTHER_STR] ]

    molTypeResidueCountList = molecule.getMolTypeResidueCountList()
    p_res_protein_count = molTypeResidueCountList[ mapMoltypeToInt[PROTEIN_STR] ]
    p_res_dna_count     = molTypeResidueCountList[ mapMoltypeToInt[DNA_STR] ]
    p_res_rna_count     = molTypeResidueCountList[ mapMoltypeToInt[RNA_STR] ]
    p_res_water_count   = molTypeResidueCountList[ mapMoltypeToInt[WATER_STR] ]
    p_res_other_count   = molTypeResidueCountList[ mapMoltypeToInt[OTHER_STR] ]
    if sum(molTypeResidueCountList) != molecule.residueCount:
        nTerror("Count of residues doesn't add up to individual types of residues; ignored")
    # end if

    p_distance_count = project.distances.lenRecursive(max_depth = 1)
    p_distance_count_sequential      =  0
    p_distance_count_intra_residual  =  0
    p_distance_count_medium_range    =  0
    p_distance_count_long_range      =  0
    p_distance_count_ambiguous       =  0
    restraintList = project.allRestraints() # defaults to DRs
    lenRestraintList = 0
    if restraintList:
        lenRestraintList = len(restraintList)
    if p_distance_count != lenRestraintList:
        msg = ( "Expected the same numbers for project.distances.lenRecursive(max_depth = 1) " +
            "and the size of project.allRestraints() but found: %s and %s") % ( p_distance_count, len(restraintList))
        nTcodeerror(msg)
        p_distance_count = len(restraintList)
    # end if
    if p_distance_count:
        if restraintList.analyze():
            p_distance_count_sequential      =  len(restraintList.intraResidual)
            p_distance_count_intra_residual  =  len(restraintList.sequential)
            p_distance_count_medium_range    =  len(restraintList.mediumRange)
            p_distance_count_long_range      =  len(restraintList.longRange)
            p_distance_count_ambiguous       =  len(restraintList.ambiguous)
        else:
            nTerror("Failed to do restraintList.analyze()")
        # end if
#    else:
#        nTdebug("No restraints in %s" % getCallerName())
    # end if

#    p_dihedral_count = project.dihedrals.lenRecursive() # Note Talos derived would be counted this way.
    p_dihedral_count = 0
    for dihList in project.dihedrals:
        if dihList.isFromTalos():
            continue
        p_dihedral_count += len(dihList)
    # end for
    p_rdc_count = project.rdcs.lenRecursive(max_depth = 1)
    p_peak_count = project.peaks.lenRecursive(max_depth = 1)

    rL = project.distanceRestraintNTlist
    # None may exist.
    p_dis_max_all = getDeepByKeysOrAttributes(rL,VIOLMAXALL_STR)
    p_dis_rms_all = getDeepByKeysOrAttributes(rL,RMSD_STR      )
    p_dis_av_viol = getDeepByKeysOrAttributes(rL,VIOLAV_STR    )
    p_dis_av_all  = getDeepByKeysOrAttributes(rL,VIOLAVALL_STR )
    p_dis_c1_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT1_STR)
    p_dis_c3_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT3_STR)
    p_dis_c5_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT5_STR)
    rL = project.dihedralRestraintNTlist
    p_dih_max_all = getDeepByKeysOrAttributes(rL,VIOLMAXALL_STR)
    p_dih_rms_all = getDeepByKeysOrAttributes(rL,RMSD_STR      )
    p_dih_av_viol = getDeepByKeysOrAttributes(rL,VIOLAV_STR    )
    p_dih_av_all  = getDeepByKeysOrAttributes(rL,VIOLAVALL_STR )
    p_dih_c1_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT1_STR)
    p_dih_c3_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT3_STR)
    p_dih_c5_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT5_STR)

    p_assignmentCountMap = project.molecule.getAssignmentCountMap()
    p_cs_count = p_assignmentCountMap.overallCount()
    p_cs1H_count = p_assignmentCountMap['1H']
    p_cs13C_count = p_assignmentCountMap['13C']
    p_cs15N_count = p_assignmentCountMap['15N']
    p_cs31P_count = p_assignmentCountMap['31P']

    p_ssa_count, p_ssa_swap_count, p_ssa_deassign_count = None, None, None
    ssa_count_tuple = project.getSsaTripletCounts()
    if ssa_count_tuple:
        p_ssa_count, p_ssa_swap_count, p_ssa_deassign_count = ssa_count_tuple

    # Queen
    rdbItemList = [ 0, 0, 0]
    projectItemList = [ QUEENY_INFORMATION_STR, QUEENY_UNCERTAINTY1_STR, QUEENY_UNCERTAINTY2_STR]
    for r in project.molecule.allResidues():
        for i, rdbItemName in enumerate(projectItemList):
            v = r.getDeepByKeys(rdbItemName)
            if v != None:
                rdbItemList[i] += v
#    nTdebug("rdbItemList: %s (before potential nilling)" % str(rdbItemList))
    if rdbItemList[0] < 0.001:
        rdbItemList = [None, None, None]
    # end if
#    nTdebug("rdbItemList: %s" % str(rdbItemList))
    p_queen_information, p_queen_uncertainty1, p_queen_uncertainty2 = rdbItemList

    # WI
    p_wi_bbcchk = molecule.getDeepAvgByKeys(WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR)
    p_wi_bmpchk = molecule.getDeepAvgByKeys(WHATIF_STR, BMPCHK_STR, VALUE_LIST_STR) # not used
    p_wi_bndchk = molecule.getDeepAvgByKeys(WHATIF_STR, BNDCHK_STR, VALUE_LIST_STR)
    p_wi_c12chk = molecule.getDeepAvgByKeys(WHATIF_STR, C12CHK_STR, VALUE_LIST_STR)
    p_wi_chichk = molecule.getDeepAvgByKeys(WHATIF_STR, CHICHK_STR, VALUE_LIST_STR)
    p_wi_flpchk = molecule.getDeepAvgByKeys(WHATIF_STR, FLPCHK_STR, VALUE_LIST_STR)
    p_wi_hndchk = molecule.getDeepAvgByKeys(WHATIF_STR, HNDCHK_STR, VALUE_LIST_STR)
    p_wi_inochk = molecule.getDeepAvgByKeys(WHATIF_STR, INOCHK_STR, VALUE_LIST_STR)
    p_wi_nqachk = molecule.getDeepAvgByKeys(WHATIF_STR, NQACHK_STR, VALUE_LIST_STR)
    p_wi_omechk = molecule.getDeepAvgByKeys(WHATIF_STR, OMECHK_STR, VALUE_LIST_STR)
    p_wi_pl2chk = molecule.getDeepAvgByKeys(WHATIF_STR, PL2CHK_STR, VALUE_LIST_STR)
    p_wi_pl3chk = molecule.getDeepAvgByKeys(WHATIF_STR, PL3CHK_STR, VALUE_LIST_STR)
    p_wi_plnchk = molecule.getDeepAvgByKeys(WHATIF_STR, PLNCHK_STR, VALUE_LIST_STR)
    p_wi_quachk = molecule.getDeepAvgByKeys(WHATIF_STR, QUACHK_STR, VALUE_LIST_STR)
    p_wi_ramchk = molecule.getDeepAvgByKeys(WHATIF_STR, RAMCHK_STR, VALUE_LIST_STR)
    p_wi_rotchk = molecule.getDeepAvgByKeys(WHATIF_STR, ROTCHK_STR, VALUE_LIST_STR)

    # PC
    p_pc_gf = molecule.getDeepByKeys(PROCHECK_STR, gf_STR)
    p_pc_gf_chi12 = molecule.getDeepByKeys(PROCHECK_STR, gf_CHI12_STR)
    p_pc_gf_chi1 = molecule.getDeepByKeys(PROCHECK_STR, gf_CHI1_STR)
    p_pc_gf_phipsi = molecule.getDeepByKeys(PROCHECK_STR, gf_PHIPSI_STR)
    pc_summary = molecule.getDeepByKeys(PROCHECK_STR, SUMMARY_STR)
    p_pc_rama_core = getDeepByKeysOrAttributes(pc_summary,  core_STR)
    p_pc_rama_allow = getDeepByKeysOrAttributes(pc_summary, allowed_STR)
    p_pc_rama_gener = getDeepByKeysOrAttributes(pc_summary, generous_STR)
    p_pc_rama_disall = getDeepByKeysOrAttributes(pc_summary,disallowed_STR)

    # Wattos
    p_noe_compl4    = molecule.getDeepByKeys(WATTOS_STR, COMPLCHK_STR,  VALUE_LIST_STR)
    p_noe_compl_obs = molecule.getDeepByKeys(WATTOS_STR, OBS_COUNT_STR, VALUE_LIST_STR)
    p_noe_compl_exp = molecule.getDeepByKeys(WATTOS_STR, EXP_COUNT_STR, VALUE_LIST_STR)
    p_noe_compl_mat = molecule.getDeepByKeys(WATTOS_STR, MAT_COUNT_STR, VALUE_LIST_STR)

    # Overall rog
    rogC = molecule.rogScore.rogInt()
    rog_str = molecule.rogScore.colorLabel

    result = execute(centry.insert().values(
        pdb_id=pdb_id,
        bmrb_id=bmrb_id,
        casd_id=casd_id,
        name=entry_code,
        rev_first = rev_first,
        rev_last = rev_last,
        timestamp_first = timestamp_first,
        timestamp_last = timestamp_last,

        is_multimeric=is_multimeric,
        symmetry=symmetry,
        ncs_symmetry = ncsSymmetry,
        dr_symmetry  = drSymmetry ,
        chothia_class=chothia_class,
        chothia_class_str=chothia_class_str,

        protein_count        =  p_protein_count               ,
        dna_count            =  p_dna_count                   ,
        rna_count            =  p_rna_count                   ,
        water_count          =  p_water_count                 ,
        other_count          =  p_other_count                 ,

        res_protein_count  = p_res_protein_count,   # The sum should be the total number of residues; res_count
        res_dna_count      = p_res_dna_count    ,   # The chain property determines this classification.
        res_rna_count      = p_res_rna_count    ,
        res_water_count    = p_res_water_count  ,
        res_other_count    = p_res_other_count  ,

        ranges=ranges,
#        omega_dev_av_all = p_omega_dev_av_all,
        cv_backbone      = p_cv_backbone     ,
        cv_sidechain     = p_cv_sidechain    ,
        rmsd_backbone    = p_rmsd_backbone   ,
        rmsd_sidechain   = p_rmsd_sidechain  ,

        res_count   =molecule.residueCount,
        chain_count =molecule.chainCount,
        atom_count  =molecule.atomCount,
        model_count =molecule.modelCount,

        distance_count=p_distance_count,
        distance_count_sequential      = p_distance_count_sequential    ,
        distance_count_intra_residual  = p_distance_count_intra_residual,
        distance_count_medium_range    = p_distance_count_medium_range  ,
        distance_count_long_range      = p_distance_count_long_range    ,
        distance_count_ambiguous       = p_distance_count_ambiguous     ,

        dihedral_count=p_dihedral_count,
        rdc_count=p_rdc_count,
        peak_count=p_peak_count,
        cs_count=p_cs_count,
        cs1h_count=p_cs1H_count,
        cs13c_count=p_cs13C_count,
        cs15n_count=p_cs15N_count,
        cs31p_count=p_cs31P_count,

        ssa_count=p_ssa_count,
        ssa_swap_count=p_ssa_swap_count,
        ssa_deassign_count=p_ssa_deassign_count,

        dis_max_all = p_dis_max_all,
        dis_rms_all = p_dis_rms_all,
        dis_av_all  = p_dis_av_all,
        dis_av_viol = p_dis_av_viol,
        dis_c1_viol = p_dis_c1_viol,
        dis_c3_viol = p_dis_c3_viol,
        dis_c5_viol = p_dis_c5_viol,

        dih_max_all = p_dih_max_all,
        dih_rms_all = p_dih_rms_all,
        dih_av_all  = p_dih_av_all,
        dih_av_viol = p_dih_av_viol,
        dih_c1_viol = p_dih_c1_viol,
        dih_c3_viol = p_dih_c3_viol,
        dih_c5_viol = p_dih_c5_viol,

        # Queen
        queen_information  = p_queen_information,
        queen_uncertainty1 = p_queen_uncertainty1,
        queen_uncertainty2 = p_queen_uncertainty2,

        wi_bbcchk=p_wi_bbcchk,
        wi_bmpchk=p_wi_bmpchk,
        wi_bndchk=p_wi_bndchk,
        wi_c12chk=p_wi_c12chk,
        wi_chichk=p_wi_chichk,
        wi_flpchk=p_wi_flpchk,
        wi_hndchk=p_wi_hndchk,
        wi_inochk=p_wi_inochk,
        wi_nqachk=p_wi_nqachk,
        wi_omechk=p_wi_omechk,
        wi_pl2chk=p_wi_pl2chk,
        wi_pl3chk=p_wi_pl3chk,
        wi_plnchk=p_wi_plnchk,
        wi_quachk=p_wi_quachk,
        wi_ramchk=p_wi_ramchk,
        wi_rotchk=p_wi_rotchk,
        pc_gf=p_pc_gf,
        pc_gf_chi12=p_pc_gf_chi12,
        pc_gf_chi1=p_pc_gf_chi1,
        pc_gf_phipsi=p_pc_gf_phipsi,
        pc_rama_core                    =p_pc_rama_core,
        pc_rama_allow                   =p_pc_rama_allow,
        pc_rama_gener                   =p_pc_rama_gener,
        pc_rama_disall                  =p_pc_rama_disall,
        noe_compl4   =p_noe_compl4   ,
        noe_compl_obs=p_noe_compl_obs,
        noe_compl_exp=p_noe_compl_exp,
        noe_compl_mat=p_noe_compl_mat,
        rog_str=rog_str,
        rog=rogC
        )
    )
#    entry_id_list = result.last_inserted_ids() # fails for postgres version I have.
#    entry_id_list = result.inserted_primary_key() # wait for this new feature
    if archive_id == ARCHIVE_CASD_ID or archive_id == ARCHIVE_CASP_ID:
        entry_id_list = execute(select([centry.c.entry_id]).where(centry.c.casd_id==casd_id)).fetchall()
    else:
        entry_id_list = execute(select([centry.c.entry_id]).where(centry.c.pdb_id==pdb_id)).fetchall()
    if not entry_id_list:
        nTerror("Failed to get the id of the inserted entry but got: %s" % entry_id_list)
        return True
    if len( entry_id_list ) != 1:
        nTerror("Failed to get ONE id of the inserted entry but got: %s" % entry_id_list)
        return True
    entry_id = entry_id_list[0][0] # NB this is an integer and different from entry_code which is a string.
#    nTdebug("Inserted entry id %s" % entry_id)


#    for residue in csql.session.query(cresidue):
#        nTdebug("New residue number %s" % residue.number)
#
#    for instance in csql.session.query(centry):
#        nTdebug( "Retrieved entry instance: %s" % instance.entry_id )

    for resonanceList in project.molecule.resonanceSources:
        nameResoL = resonanceList.name # Name has got to be key
        appliedResoL = resonanceList.vascoApplied
        rogResoL = resonanceList.rogScore.rogInt()
        result = execute(cresonancelist.insert().values(
            entry_id=entry_id,
            name=nameResoL,
            applied=appliedResoL,
            rog=rogResoL
            )
        )
        s = select([cresonancelist.c.resonancelist_id],and_(cresonancelist.c.entry_id == entry_id, cresonancelist.c.name == nameResoL))
        resonancelist_id = execute(s).fetchall()[0][0]
        for atomId in resonanceList.vascoResults.keys():
            rerefNTvalue = resonanceList.vascoResults[ atomId ]
            result = execute(cresonancelistperatomclass.insert().values(
                entry_id = entry_id,
                resonancelist_id = resonancelist_id,
                atomclass= atomId,
                csd      = rerefNTvalue.value,
                csd_err  = rerefNTvalue.error
#                rog=rogResoL
                )
            )
            s = select([cresonancelistperatomclass.c.resonancelistperatomclass_id],
                       and_(cresonancelistperatomclass.c.entry_id == entry_id,
                            cresonancelistperatomclass.c.resonancelist_id == resonancelist_id,
                            cresonancelistperatomclass.c.atomclass == atomId,
                            ))
#            cingresonancelistperatomclass_id = execute(s).fetchall()[0][0]
#            nTdebug("Inserted cingresonancelistperatomclass_id %s" % cingresonancelistperatomclass_id)
        # end for
#        nTdebug("Inserted resonancelist_id %s with name %s and atoms %s" % (
#            resonancelist_id, nameResoL, str(resonanceList.vascoResults.keys())))
    # end for

    chainCommittedCount = 0
    residueCommittedCount = 0
    waterResidueCount = 0
    atomCommittedCount = 0
    atomIdHash = NTdict() # map to RDB entity id
    residueIdHash = NTdict()
    chainIdHash = NTdict()
    for chain in project.molecule.allChains():
        nameC = chain.name
        chothia_class = chain.chothiaClassInt()
        cIdxMolType = chain.getIdxMolType()
        rogC = chain.rogScore.rogInt()
        result = execute(cchain.insert().values(
            entry_id=entry_id,
            name=nameC,
            chothia_class=chothia_class,
            mol_type_idx = cIdxMolType,
            rog=rogC,
            )
        )
        s = select([cchain.c.chain_id],and_(cchain.c.entry_id == entry_id, cchain.c.name == nameC))
        chain_id = execute(s).fetchall()[0][0]
#        nTdebug("Inserted chain id %s" % chain_id)
        chainIdHash[ chain ] = chain_id
        chainCommittedCount += 1
        if cIdxMolType == mapMoltypeToInt[WATER_STR]:
            nTdebug("Not storing water residues for this water chain id %s" % chain_id)
            waterResidueCount += len( chain.allResidues())
            continue
        # end if
        for residue in chain.allResidues():
            if residue.hasProperties('HOH'): # In entry 1l0r the water had HOH but not water set.
                nTwarning("Water residue %s almost slipped into RDB because it was in a non-water chain. Skipping now." % residue)
                waterResidueCount += 1
                continue
#            if residue.resName == 'HOH':
#                waterResidueCount += 1
#                NTcodeerror("Water residue %s almost slipped into RDB because it doesn't have the water property set. Skipping." % residue)
#                continue

#            nTmessage("Residue: %s" % residue)
            # CING
    #        print m.C.ASN46.distanceRestraints
#            residue = m.C.ASN46
#            drOrgList = residue.distanceRestraints
#            drList = DistanceRestraintList('tmp')
#            drList.addList(drOrgList)
#            (rmsd, _sd, _viol1, _viol3, _viol5 ) = drList.analyze()
#            if rmsd:
#                n = len(drList)
#                valueMap[ 'dis_max_all' ] = drList.violMax
#                valueMap[ 'dis_rms_all' ] = drList.rmsdAv # average over all models
#                valueMap[ 'dis_av_all' ] = drList.zap('violAv').sum()/n # the average violation per restraint over all models.
#                valueMap[ 'dis_c1_viol' ] = drList.violCount1
#                valueMap[ 'dis_c3_viol' ] = drList.violCount3
#                valueMap[ 'dis_c5_viol' ] = drList.violCount5

            nameR = residue.resName
            numberR = residue.resNum
            sel_1R = molecule.rangesContainsResidue(residue)
            is_commonR = residue.isCommon()
            is_terminR  = residue.isNterminal() or residue.isCterminal()
            is_present_R = residue.hasCoordinates()
            dssp_id = getDsspSecStructConsensusId(residue)
            dssp_percent_list = getDsspPercentList(residue)

#            r_distance_count = residue.distanceRestraints.lenRecursive(max_depth = 1) # filled in partition restraints
#            r_dihedral_count = residue.dihedralRestraints.lenRecursive(max_depth = 1)
#            r_rdc_count = residue.rdcRestraints.lenRecursive(max_depth = 1)

            r_distance_count = len(residue.distanceRestraints)
            r_dihedral_count = len(residue.dihedralRestraints)
            r_rdc_count =      len(residue.rdcRestraints)

#            nTdebug("r_distance_count r_dihedral_count r_rdc_count %d %d %d" % (r_distance_count, r_dihedral_count, r_rdc_count))
            # TODO: test with cs present
            r_assignmentCountMap = getAssignmentCountMapForResList([residue])
            r_cs_count = r_assignmentCountMap.overallCount()
            r_cs1H_count = r_assignmentCountMap['1H']
            r_cs13C_count = r_assignmentCountMap['13C']
            r_cs15N_count = r_assignmentCountMap['15N']
            r_cs31P_count = r_assignmentCountMap['31P']

            rL = residue.distanceRestraints
            # None may exist.
            r_dis_max_all = getDeepByKeysOrAttributes(rL,VIOLMAXALL_STR)
            r_dis_rms_all = getDeepByKeysOrAttributes(rL,RMSD_STR      )
            r_dis_av_viol = getDeepByKeysOrAttributes(rL,VIOLAV_STR    )
            r_dis_av_all  = getDeepByKeysOrAttributes(rL,VIOLAVALL_STR )
            r_dis_c1_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT1_STR)
            r_dis_c3_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT3_STR)
            r_dis_c5_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT5_STR)
            rL = residue.dihedralRestraints
            r_dih_max_all = getDeepByKeysOrAttributes(rL,VIOLMAXALL_STR)
            r_dih_rms_all = getDeepByKeysOrAttributes(rL,RMSD_STR      )
            r_dih_av_viol = getDeepByKeysOrAttributes(rL,VIOLAV_STR    )
            r_dih_av_all  = getDeepByKeysOrAttributes(rL,VIOLAVALL_STR )
            r_dih_c1_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT1_STR)
            r_dih_c3_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT3_STR)
            r_dih_c5_viol = getDeepByKeysOrAttributes(rL,VIOLCOUNT5_STR)

            # WI
            r_wi_acclst = residue.getDeepAvgByKeys(WHATIF_STR, ACCLST_STR, VALUE_LIST_STR)
            r_wi_angchk = residue.getDeepAvgByKeys(WHATIF_STR, ANGCHK_STR, VALUE_LIST_STR)
            r_wi_bbcchk = residue.getDeepAvgByKeys(WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR)
            r_wi_bmpchk = residue.getDeepAvgByKeys(WHATIF_STR, BMPCHK_STR, VALUE_LIST_STR)
            r_wi_bndchk = residue.getDeepAvgByKeys(WHATIF_STR, BNDCHK_STR, VALUE_LIST_STR)
            r_wi_c12chk = residue.getDeepAvgByKeys(WHATIF_STR, C12CHK_STR, VALUE_LIST_STR)
            r_wi_flpchk = residue.getDeepAvgByKeys(WHATIF_STR, FLPCHK_STR, VALUE_LIST_STR)
            r_wi_inochk = residue.getDeepAvgByKeys(WHATIF_STR, INOCHK_STR, VALUE_LIST_STR)
            r_wi_omechk = residue.getDeepAvgByKeys(WHATIF_STR, OMECHK_STR, VALUE_LIST_STR)
            r_wi_pl2chk = residue.getDeepAvgByKeys(WHATIF_STR, PL2CHK_STR, VALUE_LIST_STR)
            r_wi_pl3chk = residue.getDeepAvgByKeys(WHATIF_STR, PL3CHK_STR, VALUE_LIST_STR)
            r_wi_plnchk = residue.getDeepAvgByKeys(WHATIF_STR, PLNCHK_STR, VALUE_LIST_STR)
            r_wi_quachk = residue.getDeepAvgByKeys(WHATIF_STR, QUACHK_STR, VALUE_LIST_STR)
            r_wi_ramchk = residue.getDeepAvgByKeys(WHATIF_STR, RAMCHK_STR, VALUE_LIST_STR)
            r_wi_rotchk = residue.getDeepAvgByKeys(WHATIF_STR, ROTCHK_STR, VALUE_LIST_STR)

            # PC
            r_pc_gf = residue.getDeepByKeys(PROCHECK_STR, gf_STR)
            r_pc_gf_chi12 = residue.getDeepByKeys(PROCHECK_STR, gf_CHI12_STR)
            r_pc_gf_chi1 = residue.getDeepByKeys(PROCHECK_STR, gf_CHI1_STR)
            r_pc_gf_phipsi = residue.getDeepByKeys(PROCHECK_STR, gf_PHIPSI_STR)

            # Wattos
            r_noe_compl4    = residue.getDeepByKeys(WATTOS_STR, COMPLCHK_STR,  VALUE_LIST_STR)
            r_noe_compl_obs = residue.getDeepByKeys(WATTOS_STR, OBS_COUNT_STR, VALUE_LIST_STR)
            r_noe_compl_exp = residue.getDeepByKeys(WATTOS_STR, EXP_COUNT_STR, VALUE_LIST_STR)
            r_noe_compl_mat = residue.getDeepByKeys(WATTOS_STR, MAT_COUNT_STR, VALUE_LIST_STR)

            # Queen
            r_queen_information = residue.getDeepByKeys(QUEENY_INFORMATION_STR)
            r_queen_uncertainty1 = residue.getDeepByKeys(QUEENY_UNCERTAINTY1_STR)
            r_queen_uncertainty2 = residue.getDeepByKeys(QUEENY_UNCERTAINTY2_STR)

            # Talos+
            r_qcs_all = residue.getDeepAvgByKeys(QSHIFT_STR, ALL_ATOMS_STR, VALUE_LIST_STR)
            r_qcs_bb = residue.getDeepAvgByKeys(QSHIFT_STR, BACKBONE_STR, VALUE_LIST_STR)
            r_qcs_hvy = residue.getDeepAvgByKeys(QSHIFT_STR, HEAVY_ATOMS_STR, VALUE_LIST_STR)
            r_qcs_prt = residue.getDeepAvgByKeys(QSHIFT_STR, PROTONS_STR, VALUE_LIST_STR)
            # Talos+ but from different location in data model.
            r_qcs_s2 = residue.getDeepByKeys(TALOSPLUS_STR, S2_STR)

            # CING
            r_chk_ramach = residue.getDeepAvgByKeys(CHK_STR, RAMACHANDRAN_CHK_STR, VALUE_LIST_STR)
            r_chk_janin = residue.getDeepAvgByKeys(CHK_STR, CHI1CHI2_CHK_STR, VALUE_LIST_STR)
            r_chk_d1d2 = residue.getDeepAvgByKeys(CHK_STR, D1D2_CHK_STR, VALUE_LIST_STR)
#            r_omega_dev_av_all = residue.getDeepAvgByKeys(CHK_STR, XXX_CHK_STR, VALUE_LIST_STR)
            r_rmsd_backbone    = residue.getDeepAvgByKeys(RMSD_STR, BACKBONE_STR)
            r_rmsd_sidechain   = residue.getDeepAvgByKeys(RMSD_STR, HEAVY_ATOMS_STR)
            r_cv_backbone = residue.getDeepByKeys(CV_BACKBONE_STR)
            r_cv_sidechain = residue.getDeepByKeys(CV_SIDECHAIN_STR)

            r_phi_avg = residue.getDeepByKeys(PHI_STR, CAV_STR)
            r_phi_cv = residue.getDeepByKeys(PHI_STR, CV_STR)
            r_psi_avg = residue.getDeepByKeys(PSI_STR, CAV_STR)
            r_psi_cv = residue.getDeepByKeys(PSI_STR, CV_STR)
            r_chi1_avg = residue.getDeepByKeys(CHI1_STR, CAV_STR)
            r_chi1_cv = residue.getDeepByKeys(CHI1_STR, CV_STR)
            r_chi2_avg = residue.getDeepByKeys(CHI2_STR, CAV_STR)
            r_chi2_cv = residue.getDeepByKeys(CHI2_STR, CV_STR)

            rogR = residue.rogScore.rogInt()

            result = execute(cresidue.insert().values(
                entry_id=entry_id,
                chain_id=chain_id,
                name=nameR,
                sel_1=sel_1R,
                is_common=is_commonR,
                is_termin=is_terminR,
                is_present=is_present_R,
                number=numberR,
                dssp_id=dssp_id,
                dssp_h_percent = dssp_percent_list[DSSP_ID_H],
                dssp_s_percent = dssp_percent_list[DSSP_ID_S],
                dssp_c_percent = dssp_percent_list[DSSP_ID_C],
                wi_acclst=r_wi_acclst,
                wi_angchk=r_wi_angchk,
                wi_bbcchk=r_wi_bbcchk,
                wi_bmpchk=r_wi_bmpchk,
                wi_bndchk=r_wi_bndchk,
                wi_c12chk=r_wi_c12chk,
                wi_flpchk=r_wi_flpchk,
                wi_inochk=r_wi_inochk,
                wi_omechk=r_wi_omechk,
                wi_pl2chk=r_wi_pl2chk,
                wi_pl3chk=r_wi_pl3chk,
                wi_plnchk=r_wi_plnchk,
                wi_quachk=r_wi_quachk,
                wi_ramchk=r_wi_ramchk,
                wi_rotchk=r_wi_rotchk,
                pc_gf=r_pc_gf,
                pc_gf_chi12=r_pc_gf_chi12,
                pc_gf_chi1=r_pc_gf_chi1,
                pc_gf_phipsi=r_pc_gf_phipsi,

                noe_compl4   =r_noe_compl4   ,
                noe_compl_obs=r_noe_compl_obs,
                noe_compl_exp=r_noe_compl_exp,
                noe_compl_mat=r_noe_compl_mat,

                queen_information = r_queen_information,
                queen_uncertainty1 = r_queen_uncertainty1,
                queen_uncertainty2 = r_queen_uncertainty2,

                distance_count  = r_distance_count,
                dihedral_count  = r_dihedral_count,
                rdc_count       = r_rdc_count,
                cs_count        = r_cs_count,
                cs1h_count      = r_cs1H_count,
                cs13c_count     = r_cs13C_count,
                cs15n_count     = r_cs15N_count,
                cs31p_count     = r_cs31P_count,

                dis_max_all = r_dis_max_all,
                dis_rms_all = r_dis_rms_all,
                dis_av_all  = r_dis_av_all,
                dis_av_viol = r_dis_av_viol,
                dis_c1_viol = r_dis_c1_viol,
                dis_c3_viol = r_dis_c3_viol,
                dis_c5_viol = r_dis_c5_viol,

                dih_max_all = r_dih_max_all,
                dih_rms_all = r_dih_rms_all,
                dih_av_all  = r_dih_av_all,
                dih_av_viol = r_dih_av_viol,
                dih_c1_viol = r_dih_c1_viol,
                dih_c3_viol = r_dih_c3_viol,
                dih_c5_viol = r_dih_c5_viol,

#                omega_dev_av_all= r_omega_dev_av_all,
                rmsd_backbone    = r_rmsd_backbone,
                rmsd_sidechain   = r_rmsd_sidechain,
                cv_backbone     = r_cv_backbone,
                cv_sidechain    = r_cv_sidechain,

                phi_avg =  r_phi_avg ,
                phi_cv  =  r_phi_cv  ,
                psi_avg =  r_psi_avg ,
                psi_cv  =  r_psi_cv  ,
                chi1_avg=  r_chi1_avg,
                chi1_cv =  r_chi1_cv ,
                chi2_avg=  r_chi2_avg,
                chi2_cv =  r_chi2_cv ,

                chk_ramach      = r_chk_ramach,
                chk_janin       = r_chk_janin,
                chk_d1d2        = r_chk_d1d2,

                qcs_all         = r_qcs_all,
                qcs_bb          = r_qcs_bb,
                qcs_hvy         = r_qcs_hvy,
                qcs_prt         = r_qcs_prt,
                qcs_s2          = r_qcs_s2,
#                is_pressssssent = True,         # bogus column for demonstration.
                rog=rogR
                )
            )

#            residue_id = result.last_inserted_ids()[0]
            s = select([cresidue.c.residue_id],and_(
                  cresidue.c.entry_id == entry_id,
                  cresidue.c.chain_id == chain_id,
                  cresidue.c.number == numberR
                  ))
            residue_id = execute(s).fetchall()[0][0]
            residueIdHash[ residue ] = residue_id
            residueCommittedCount += 1
#            nTdebug("Inserted residue %s" % residue_id)
            for atom in residue.allAtoms():
                a_name = atom.name
                a_spin_type = getDeepByKeysOrAttributes( atom, DB_STR, SPINTYPE_STR )
                # WI
#                    a_wi_ba2lst = atom.getDeepAvgByKeys(WHATIF_STR, BA2CHK_STR, VALUE_LIST_STR) # should have worked
#                    a_wi_bh2chk = atom.getDeepAvgByKeys(WHATIF_STR, BH2CHK_STR, VALUE_LIST_STR) # should have worked
                a_wi_chichk = atom.getDeepAvgByKeys(WHATIF_STR, CHICHK_STR, VALUE_LIST_STR)
                a_wi_dunchk = atom.getDeepAvgByKeys(WHATIF_STR, DUNCHK_STR, VALUE_LIST_STR)
                a_wi_hndchk = atom.getDeepAvgByKeys(WHATIF_STR, HNDCHK_STR, VALUE_LIST_STR)
#                    a_wi_mischk = atom.getDeepAvgByKeys(WHATIF_STR, MISCHK_STR, VALUE_LIST_STR)
#                    a_wi_mo2chk = atom.getDeepAvgByKeys(WHATIF_STR, MO2CHK_STR, VALUE_LIST_STR)
                a_wi_pl2chk = atom.getDeepAvgByKeys(WHATIF_STR, PL2CHK_STR, VALUE_LIST_STR)
                a_wi_wgtchk = atom.getDeepAvgByKeys(WHATIF_STR, WGTCHK_STR, VALUE_LIST_STR)
                a_wi_wsvacc = atom.getDeepAvgByKeys(WHATIF_STR, WSVACC_STR, VALUE_LIST_STR)
                a_queen_information  = getDeepByKeysOrAttributes(atom, QUEENY_UNCERTAINTY1_STR)
                a_queen_uncertainty1 = getDeepByKeysOrAttributes(atom, QUEENY_UNCERTAINTY2_STR)
                a_queen_uncertainty2 = getDeepByKeysOrAttributes(atom, QUEENY_INFORMATION_STR )
                a_cs = None
                a_cs_err = None
                a_cs_ssa = None
                a_first_resonance = getDeepByKeysOrAttributes(atom, RESONANCES_STR, 0)
                if a_first_resonance != None:
                    a_cs = getDeepWithNone(a_first_resonance, VALUE_STR)
                    if a_cs != None:
                        a_cs_err = getDeepWithNone(a_first_resonance, ERROR_STR)
                        a_cs_ssa = truthToInt( atom.isStereoAssigned() )
                # Store all atoms including pseudos.
#                    useFulColumns = [
##                        a_wi_ba2lst,
##                        a_wi_bh2chk,
#                        a_wi_chichk,
#                        a_wi_dunchk,
#                        a_wi_hndchk,
##                        a_wi_mischk,
##                        a_wi_mo2chk,
#                        a_wi_pl2chk,
#                        a_wi_wgtchk,
#                        a_cs,
#                        a_cs_err,
#                        a_cs_ssa
#                    ]
#                    hasUsefulColumn = False
#                    for _i,column in enumerate(useFulColumns):
#                        if column != None:
##                            nTdebug("Found useful column: %s %s" % ( i, column))
#                            hasUsefulColumn = True
#                    if not hasUsefulColumn:
#                        continue
                a_rog = atom.rogScore.rogInt()
                atomInfoList = [entry_id,chain_id,residue_id,
                    a_name,a_wi_chichk,a_wi_dunchk,a_wi_hndchk, a_wi_pl2chk, a_wi_wgtchk, a_cs,a_cs_err,a_cs_ssa,a_rog]
#                    nTdebug("Inserting atom: " + str(atomInfoList))
                try:
                    result = execute(catom.insert().values(
                        entry_id=entry_id,
                        chain_id=chain_id,
                        residue_id=residue_id,
                        name=a_name,
                        spin_type=a_spin_type,
#                        wi_ba2lst=a_wi_ba2lst,
#                        wi_bh2chk=a_wi_bh2chk,
                        wi_chichk=a_wi_chichk,
                        wi_dunchk=a_wi_dunchk,
                        wi_hndchk=a_wi_hndchk,
#                            wi_mischk=a_wi_mischk,
#                            wi_mo2chk=a_wi_mo2chk,
                        wi_pl2chk=a_wi_pl2chk,
                        wi_wgtchk=a_wi_wgtchk,
                        wi_wsvacc=a_wi_wsvacc,
                        cs = a_cs,
                        cs_err = a_cs_err,
                        cs_ssa = a_cs_ssa,
                        queen_information  = a_queen_information ,
                        queen_uncertainty1 = a_queen_uncertainty1,
                        queen_uncertainty2 = a_queen_uncertainty2,
                        rog=a_rog
                        )
                    )
#                    atom_id = result.last_inserted_ids()[0] # TODO: update to this again.
                    s = select([catom.c.atom_id],and_(
                          catom.c.entry_id == entry_id,
                          catom.c.chain_id == chain_id,
                          catom.c.residue_id == residue_id,
                          catom.c.name == a_name
                          ))
                    atom_id = execute(s).fetchall()[0][0]
#                        nTdebug("Inserted atom %s %s" % (atom_id, atom))
                    atomIdHash[ atom ] = atom_id
                    atomCommittedCount += 1
                except:
                    nTtracebackError()
                    nTerror("Failed to insert atom [%s] with info: %s" % ( atom, str(atomInfoList)))
                    continue
                # end try
            # end for atom
        # end for residue
    # end for chain
    nTmessage("Committed %d chains %d residues %d atoms" % (chainCommittedCount,residueCommittedCount,atomCommittedCount))
#    nTdebug("Memorized %d chains %d residues %d atoms" % (len(chainIdHash.keys()),len(residueIdHash.keys()),len(atomIdHash.keys())))
    if chainCommittedCount != molecule.chainCount:
        msg = "chainCommittedCount %s != molecule.chainCount %s" % (chainCommittedCount, molecule.chainCount)
        nTerror(msg)
    # end if
    if (residueCommittedCount + waterResidueCount) != molecule.residueCount:
        msg = "residueCommittedCount %s + waters %s != molecule.residueCount %s" % (
            residueCommittedCount, waterResidueCount, molecule.residueCount)
        nTerror(msg)
    # end if
    if (atomCommittedCount + waterResidueCount*WATER_ATOM_COUNT) != molecule.atomCount:
        msg = "atomCommittedCount %s + waterResidueCount (%s) *3 (=%s) != molecule.atomCount %s" % (
            atomCommittedCount,                     waterResidueCount,
            atomCommittedCount + WATER_ATOM_COUNT * waterResidueCount,
            molecule.atomCount)
        nTerror(msg)
    # end if

    drlCommittedCount = 0
    drCommittedCount = 0
    drRowCommittedCount = 0
#    drlIdHash = NTdict()
    drIdHash = NTdict()
    for drl_number, drl in enumerate(project.distances, 1):
        if not drl:
            continue
        drl_name = drl.name
        drl_rog = drl.rogScore.rogInt()
        result = execute(cdrlist.insert().values(
            entry_id=entry_id,
            name=drl_name,
            number=drl_number,

            viol_count1       = drl.violCount1,
            viol_count3       = drl.violCount3,
            viol_count5       = drl.violCount5,
            viol_max          = drl.violMax   ,
            viol_upper_max    = drl.violUpperMax,
            viol_lower_max    = drl.violLowerMax,

            intra_residual_count     = len( drl.intraResidual ),
            sequential_count         = len( drl.sequential  ),
            medium_range_count       = len( drl.mediumRange ),
            long_range_count         = len( drl.longRange  ),
            ambiguous_count          = len( drl.ambiguous  ),
            unique_distances_count   = drl.uniqueDistancesCount  ,
            without_duplicates_count = len( drl.withoutDuplicates ),
            with_duplicates_count    = len( drl.withDuplicates    ),
            rog = drl_rog
            )
        )
        s = select([cdrlist.c.drlist_id],and_(cdrlist.c.entry_id == entry_id, cdrlist.c.number == drl_number))
        drl_id = execute(s).fetchall()[0][0]
#        drlIdHash[ drl ] = drl_id
        drlCommittedCount += 1
        for dr_number,dr in enumerate(drl, 1):
            if not dr:
                nTerror("Failed to get dr from drl: %s" % drl)
                continue
            dr_rog = dr.rogScore.rogInt()

#            dr_target            = dr.target
            dr_lower             = dr.lower
            dr_upper             = dr.upper
#            dr_contribution      = dr.contribution
            dr_viol_count1       = dr.violCount1
            dr_viol_count3       = dr.violCount3
            dr_viol_count5       = dr.violCount5
            dr_viol_max          = dr.violMax
            dr_viol_av           = dr.violAv
            dr_viol_sd           = dr.violSd
            dr_av                = dr.av
            dr_sd                = dr.sd
            dr_min               = dr.min
            dr_max               = dr.max
            dr_viol_count_lower  = dr.violCountLower
            dr_viol_upper_max    = dr.violUpperMax
            dr_viol_lower_max    = dr.violLowerMax
            dr_has_analyze_error = bool(dr.error)

            for item_id, atomPair in enumerate(dr.atomPairs, 1):
                item_logic_code = None
                if len(dr.atomPairs) > 1:
                    item_logic_code = 'OR'
                atom1, atom2 = atomPair
                residue1 = getDeepByKeysOrAttributes( atom1, '_parent')
                chain1 = getDeepByKeysOrAttributes( residue1, '_parent')
                atom_id_1       = getDeepByKeysOrAttributes(atomIdHash, atom1)
                residue_id_1    = getDeepByKeysOrAttributes(residueIdHash, residue1)
                chain_id_1      = getDeepByKeysOrAttributes(chainIdHash, chain1)

                residue2 = getDeepByKeysOrAttributes( atom2, '_parent')
                chain2 = getDeepByKeysOrAttributes( residue2, '_parent')
                atom_id_2       = getDeepByKeysOrAttributes(atomIdHash, atom2)
                residue_id_2    = getDeepByKeysOrAttributes(residueIdHash, residue2)
                chain_id_2      = getDeepByKeysOrAttributes(chainIdHash, chain2)


                result = execute(cdr.insert().values(
                    entry_id=entry_id,
                    drlist_id=drl_id,
                    number=dr_number,
                    item_id = item_id,
                    item_logic_code = item_logic_code,
                    atom_id_1 = atom_id_1,
                    residue_id_1 = residue_id_1,
                    chain_id_1 = chain_id_1,
                    atom_id_2 = atom_id_2,
                    residue_id_2 = residue_id_2,
                    chain_id_2 = chain_id_2,

                    atom_name_1     = getDeepByKeysOrAttributes(atom1, NAME_STR),
                    residue_num_1   = getDeepByKeysOrAttributes(residue1, RES_NUMB_STR),
                    residue_name_1  = getDeepByKeysOrAttributes(residue1, RES_NAME_STR),
                    chain_name_1    = getDeepByKeysOrAttributes(chain1, NAME_STR),

                    atom_name_2     = getDeepByKeysOrAttributes(atom2, NAME_STR),
                    residue_num_2   = getDeepByKeysOrAttributes(residue2, RES_NUMB_STR),
                    residue_name_2  = getDeepByKeysOrAttributes(residue2, RES_NAME_STR),
                    chain_name_2    = getDeepByKeysOrAttributes(chain2, NAME_STR),

#                    target            = dr_target           ,
                    lower             = dr_lower            ,
                    upper             = dr_upper            ,
#                    contribution      = dr_contribution     ,
                    viol_count1       = dr_viol_count1      ,
                    viol_count3       = dr_viol_count3      ,
                    viol_count5       = dr_viol_count5      ,
                    viol_max          = dr_viol_max         ,
                    viol_av           = dr_viol_av          ,
                    viol_sd           = dr_viol_sd          ,
                    av                = dr_av               ,
                    sd                = dr_sd               ,
                    min               = dr_min              ,
                    max               = dr_max              ,
                    viol_count_lower  = dr_viol_count_lower ,
                    viol_upper_max    = dr_viol_upper_max   ,
                    viol_lower_max    = dr_viol_lower_max   ,
                    has_analyze_error = dr_has_analyze_error,

                    rog=dr_rog
                    )
                )
                s = select([cdr.c.dr_id],and_(cdr.c.entry_id == entry_id,
                                              cdr.c.drlist_id == drl_id,
                                              cdr.c.number == dr_number,
                                              cdr.c.item_id == item_id))
                dr_id = execute(s).fetchall()[0][0]
                drIdHash[ dr_id ] = dr_id # bogus statement
                drRowCommittedCount += 1
            # end for
            drCommittedCount += 1
        # end for
#        nTdebug("Committed %d dr %d drrows" % (drCommittedCount,drRowCommittedCount))
        drlCommittedCount += 1
    # end for
    nTmessage("Committed %d drl and overall %d dr %d drrows" % (drlCommittedCount,drCommittedCount,drRowCommittedCount))
#    project.close(save=False) # needed ???
    # Needed for the above hasn't been auto-committed.
#    nTdebug("Committing changes")
    csql.session.commit()
# end def

if __name__ == "__main__":
    cing.verbosity = verbosityDebug

    # Assume CING didn't already printed this.
    nTmessage(cing.cingDefinitions.getHeaderString())
    nTmessage(cing.systemDefinitions.getStartMessage())
    try:
        status = doStoreCING2db(*sys.argv[1:])
        if status:
            nTerror("Failed script: storeCING2db.py")
    finally:
        nTmessage(cing.systemDefinitions.getStopMessage())
