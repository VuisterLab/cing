# Execute like:
# cd /Library/WebServer/Documents/CASD-NMR-CING/data/eR/NeR103ALyon2; \
# python -u $CINGROOT/python/cing/NRG/storeCING2db.py NeR103ALyon2 ARCHIVE_CASD
#
# cd /Library/WebServer/Documents/CASP-NMR-CING/data/05/T0538Org; \
# python -u $CINGROOT/python/cing/NRG/storeCING2db.py T0538Org ARCHIVE_CASP
#
# cd /Library/WebServer/Documents/NRG-CING/data/br/1brv; \
# python -u $CINGROOT/python/cing/NRG/storeCING2db.py 1brv ARCHIVE_NRG
#
# NB this script fails if the Postgresql backend is not installed. Which is exactly why it's kept out of CING's core routines.

from cing import header
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.PluginCode.required.reqDssp import * #@UnusedWildImport
from cing.PluginCode.required.reqProcheck import * #@UnusedWildImport
from cing.PluginCode.required.reqQueeny import * #@UnusedWildImport
from cing.PluginCode.required.reqWattos import * #@UnusedWildImport
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from cing.core.classes import Project
from cing.core.molecule import getAssignmentCountMapForResList
from cing.main import getStartMessage
from cing.main import getStopMessage
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import select

db_name = PDBJ_DB_NAME
user_name = PDBJ_DB_USER_NAME

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
    schema = PDB_DB_NAME
    if archive_id == ARCHIVE_NRG_ID or archive_id == ARCHIVE_DEV_NRG_ID or archive_id == ARCHIVE_PDB_ID:
        pdb_id = entry_code
        if pdb_id == None:
            NTerror("Expected pdb_id argument")
            return True
        if not is_pdb_code(pdb_id):
            NTerror("Expected pdb_id argument and [%s] isn't recognized as such." % pdb_id)
            return True
        if archive_id == ARCHIVE_NRG_ID:
            schema = NRG_DB_NAME
        elif archive_id == ARCHIVE_DEV_NRG_ID:
            schema = DEV_NRG_DB_NAME

    elif archive_id == ARCHIVE_CASD_ID or archive_id == ARCHIVE_CASP_ID:
        casd_id = entry_code
        if casd_id == None:
            NTerror("Expected casd_id argument")
            return True
        entry_code = casd_id
        schema = CASD_DB_NAME
        if archive_id == ARCHIVE_CASP_ID:
            schema = CASP_DB_NAME
    else:
        NTerror("Expected valid archive_id argument but got: %s" % archive_id)
        return True


    NTdebug("Starting doStoreCING2db using:")
    NTdebug("entry_code:           %s" % entry_code)
#    NTdebug("inputDir:             %s" % inputDir)
    NTdebug("archive_id:           %s" % archive_id)
    NTdebug("user_name:            %s" % user_name)
    NTdebug("db_name:              %s" % db_name)
    NTdebug("schema:               %s" % schema)
    NTdebug("doReadProject:        %s" % doReadProject)


#    csql = csqlAlchemy(user=archive_user, db=archive_db, echo=False)
    csql = csqlAlchemy(user=user_name, db=db_name,schema=schema)

    if csql.connect():
        NTerror("Failed to connect to DB")
        return True
    csql.autoload()

    execute = csql.conn.execute
    centry = csql.cingentry
    cchain = csql.cingchain
    cresidue = csql.cingresidue
    catom = csql.cingatom

    if doReadProject:
        # presume the directory still needs to be created.
        cingEntryDir = entry_code + ".cing"
        if not os.path.isdir(cingEntryDir):
            NTerror("Failed to find input directory: %s" % cingEntryDir)
            return
        # end if.
        # Needs to be copied because the open method doesn't take a directory argument..
        project = Project.open(entry_code, status='old')
        if not project:
            NTerror("Failed to init old project")
            return True
        # end if.
    # end if project

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
        NTdebug("Removed original entries numbering: %s" % result.rowcount)
        if result.rowcount > 1:
            NTerror("Removed more than the expected ONE entry; this could be serious.")
            return True
#    else:
#        NTdebug("No original entry present yet.")

    ranges = getDeepByKeysOrAttributes(molecule,RANGES_STR)
    p_rmsd_backbone = getDeepByKeysOrAttributes(molecule, RMSD_STR, BACKBONE_AVERAGE_STR)
    p_rmsd_sidechain = getDeepByKeysOrAttributes(molecule, RMSD_STR, HEAVY_ATOM_AVERAGE_STR)
    p_cv_backbone = getDeepByKeysOrAttributes(molecule, CV_BACKBONE_STR)
    p_cv_sidechain = getDeepByKeysOrAttributes(molecule, CV_SIDECHAIN_STR)

    chainList = molecule.allChains()
    is_multimeric = len(chainList) > 1

    chothia_class = molecule.chothiaClassInt()

    p_distance_count = project.distances.lenRecursive()
    p_dihedral_count = project.dihedrals.lenRecursive()
    p_rdc_count = project.rdcs.lenRecursive()
    p_peak_count = project.peaks.lenRecursive()

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

    result = execute(centry.insert().values(
        pdb_id=pdb_id,
        casd_id=casd_id,
        name=entry_code,
        is_multimeric=is_multimeric,
        chothia_class=chothia_class,
        ranges=ranges,
#        omega_dev_av_all = p_omega_dev_av_all,
        cv_backbone      = p_cv_backbone     ,
        cv_sidechain     = p_cv_sidechain    ,
        rmsd_backbone    = p_rmsd_backbone   ,
        rmsd_sidechain   = p_rmsd_sidechain  ,

        res_count=molecule.residueCount,
        model_count=molecule.modelCount,
        distance_count=p_distance_count,
        dihedral_count=p_dihedral_count,
        rdc_count=p_rdc_count,
        peak_count=p_peak_count,
        cs_count=p_cs_count,
        cs1h_count=p_cs1H_count,
        cs13c_count=p_cs13C_count,
        cs15n_count=p_cs15N_count,
        cs31p_count=p_cs31P_count,

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
        NTerror("Failed to get the id of the inserted entry but got: %s" % entry_id_list)
        return True
    if len( entry_id_list ) != 1:
        NTerror("Failed to get ONE id of the inserted entry but got: %s" % entry_id_list)
        return True
    entry_id = entry_id_list[0][0] # NB this is an integer and different from entry_code which is a string.
#    NTdebug("Inserted entry id %s" % entry_id)


#    for residue in csql.session.query(cresidue):
#        NTdebug("New residue number %s" % residue.number)
#
#    for instance in csql.session.query(centry):
#        NTdebug( "Retrieved entry instance: %s" % instance.entry_id )
    chainCommittedCount = 0
    residueCommittedCount = 0
    atomCommittedCount = 0
    for chain in project.molecule.allChains():
        nameC = chain.name
        chothia_class = molecule.chothiaClassInt()
        rogC = chain.rogScore.rogInt()
        result = execute(cchain.insert().values(
            entry_id=entry_id,
            name=nameC,
            chothia_class=chothia_class,
            rog=rogC,
            )
        )
        s = select([cchain.c.chain_id],and_(cchain.c.entry_id == entry_id, cchain.c.name == nameC))
        chain_id = execute(s).fetchall()[0][0]
#        NTdebug("Inserted chain id %s" % chain_id)
        chainCommittedCount += 1
        for residue in chain.allResidues():

            if residue.hasProperties('water'):
                continue

#            NTmessage("Residue: %s" % residue)

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
            dssp_id = getDsspSecStructConsensusId(residue)

            r_distance_count = residue.distanceRestraints.lenRecursive() # filled by filled in partition restraints
            r_dihedral_count = residue.dihedralRestraints.lenRecursive()
            r_rdc_count = residue.rdcRestraints.lenRecursive()

#            NTdebug("r_distance_count r_dihedral_count r_rdc_count %d %d %d" % (r_distance_count, r_dihedral_count, r_rdc_count))
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
                number=numberR,
                dssp_id=dssp_id,
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
            residueCommittedCount += 1
#            NTdebug("Inserted residue %s" % residue_id)
            if True:
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

                    a_cs = None
                    a_cs_err = None
                    a_cs_ssa = None
                    a_first_resonance = getDeepByKeysOrAttributes(atom, RESONANCES_STR, 0)
                    if a_first_resonance != None:
                        a_cs = getDeepWithNone(a_first_resonance, VALUE_STR)
                        if a_cs != None:
                            a_cs_err = getDeepWithNone(a_first_resonance, ERROR_STR)
                            a_cs_ssa = truthToInt( atom.isStereoAssigned() )
                    # Store only atoms for which there is useful info.
                    useFulColumns = [
#                        a_wi_ba2lst,
#                        a_wi_bh2chk,
                        a_wi_chichk,
                        a_wi_dunchk,
                        a_wi_hndchk,
#                        a_wi_mischk,
#                        a_wi_mo2chk,
                        a_wi_pl2chk,
                        a_wi_wgtchk,
                        a_cs,
                        a_cs_err,
                        a_cs_ssa
                    ]
                    hasUsefulColumn = False
                    for _i,column in enumerate(useFulColumns):
                        if column != None:
#                            NTdebug("Found useful column: %s %s" % ( i, column))
                            hasUsefulColumn = True
                    if not hasUsefulColumn:
                        continue
                    a_rog = atom.rogScore.rogInt()
                    atomInfoList = [entry_id,chain_id,residue_id,a_name,a_wi_chichk,a_wi_dunchk,a_wi_hndchk, a_wi_pl2chk, a_wi_wgtchk, a_cs,a_cs_err,a_cs_ssa,a_rog]
#                    NTdebug("Inserting atom: " + str(atomInfoList))
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
                            cs = a_cs,
                            cs_err = a_cs_err,
                            cs_ssa = a_cs_ssa,
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
    #                    atom_id = execute(s).fetchall()[0][0]
    #                    NTdebug("Inserted atom %s %s" % (atom_id, atom))
                        atomCommittedCount += 1
                    except:
                        NTtracebackError()
                        NTerror("Failed to insert atom [%s] with info: %s" % ( atom, str(atomInfoList)))
                        continue
                # end for atom
            # end if atom
        # end for residue
    # end for chain
    NTmessage("Committed %d chains %d residues %d atoms" % (chainCommittedCount,residueCommittedCount,atomCommittedCount))
#    project.close(save=False) # needed ???

    # Needed for the above hasn't been auto-committed.
#    NTdebug("Committing changes")
    csql.session.commit()
# end def

if __name__ == "__main__":
    cing.verbosity = verbosityDebug

    # Assume CING didn't already printed this.
    NTmessage(header)
    NTmessage(getStartMessage())
    try:
        status = doStoreCING2db(*sys.argv[1:])
        if status:
            NTerror("Failed script: storeCING2db.py")
    finally:
        NTmessage(getStopMessage())
