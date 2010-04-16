# Execute like:
# cd /Library/WebServer/Documents/CASD-NMR-CING/data/R3/AR3436ACheshire; \
# python -u $CINGROOT/python/cing/NRG/storeNRGCING2db.py AR3436ACheshire .
#
# NB this script fails if the MySql backend is not installed.
from cing import header
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.NRG import CASD_DB_NAME
from cing.NRG import CASD_DB_USER_NAME
from cing.PluginCode.required.reqDssp import getDsspSecStructConsensusId
from cing.PluginCode.required.reqProcheck import PROCHECK_STR
from cing.PluginCode.required.reqProcheck import gf_CHI12_STR
from cing.PluginCode.required.reqProcheck import gf_CHI1_STR
from cing.PluginCode.required.reqProcheck import gf_PHIPSI_STR
from cing.PluginCode.required.reqProcheck import gf_STR
from cing.PluginCode.required.reqWattos import COMPLCHK_STR
from cing.PluginCode.required.reqWattos import WATTOS_STR
from cing.PluginCode.required.reqWhatif import ACCLST_STR
from cing.PluginCode.required.reqWhatif import ANGCHK_STR
from cing.PluginCode.required.reqWhatif import BA2CHK_STR
from cing.PluginCode.required.reqWhatif import BBCCHK_STR
from cing.PluginCode.required.reqWhatif import BH2CHK_STR
from cing.PluginCode.required.reqWhatif import BMPCHK_STR
from cing.PluginCode.required.reqWhatif import BNDCHK_STR
from cing.PluginCode.required.reqWhatif import C12CHK_STR
from cing.PluginCode.required.reqWhatif import CHICHK_STR
from cing.PluginCode.required.reqWhatif import DUNCHK_STR
from cing.PluginCode.required.reqWhatif import FLPCHK_STR
from cing.PluginCode.required.reqWhatif import HNDCHK_STR
from cing.PluginCode.required.reqWhatif import INOCHK_STR
from cing.PluginCode.required.reqWhatif import MISCHK_STR
from cing.PluginCode.required.reqWhatif import MO2CHK_STR
from cing.PluginCode.required.reqWhatif import NQACHK_STR
from cing.PluginCode.required.reqWhatif import OMECHK_STR
from cing.PluginCode.required.reqWhatif import PL2CHK_STR
from cing.PluginCode.required.reqWhatif import PL3CHK_STR
from cing.PluginCode.required.reqWhatif import PLNCHK_STR
from cing.PluginCode.required.reqWhatif import QUACHK_STR
from cing.PluginCode.required.reqWhatif import RAMCHK_STR
from cing.PluginCode.required.reqWhatif import ROTCHK_STR
from cing.PluginCode.required.reqWhatif import VALUE_LIST_STR
from cing.PluginCode.required.reqWhatif import WGTCHK_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from cing.core.classes import Project
from cing.main import getStartMessage
from cing.main import getStopMessage
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import select
import cing
import os
import sys


def main(casd_id, *extraArgList):
    """inputDir may be a directory or a url.
    Returns True on error.
    """

    NTmessage(header)
    NTmessage(getStartMessage())

    expectedArgumentList = [ 'inputDir']
    expectedNumberOfArguments = len(expectedArgumentList)
    if len(extraArgList) != expectedNumberOfArguments:
        NTerror("Got arguments: " + `extraArgList`)
        NTerror("Failed to get expected number of arguments: %d got %d" % (
            expectedNumberOfArguments, len(extraArgList)))
        NTerror("Expected arguments: %s" % expectedArgumentList)
        return True

    inputDir = extraArgList[0]
#    archiveType = extraArgList[1]
#    projectType = extraArgList[2]

    NTdebug("Using:")
    NTdebug("casd_id:              " + casd_id)
    NTdebug("inputDir:             " + inputDir)

    csql = csqlAlchemy(user=CASD_DB_USER_NAME, db=CASD_DB_NAME, echo=False)
    if csql.connect():
        NTerror("Failed to connect to DB")
        return True
    csql.autoload()

    execute = csql.conn.execute
    centry = csql.entry
    cchain = csql.chain
    cresidue = csql.residue
    catom = csql.atom

    # presume the directory still needs to be created.
    cingEntryDir = casd_id + ".cing"

    NTmessage("Now in %s" % os.path.curdir)

    if not os.path.isdir(cingEntryDir):
        NTerror("Failed to find input directory: %s" % cingEntryDir)
        return
    # end if.

    # Needs to be copied because the open method doesn't take a directory argument..
    project = Project.open(casd_id, status='old')
    if not project:
        NTerror("Failed to init old project")
        return True

    # shortcuts
    p = project
    molecule = project.molecule
#    p.runCingChecks() # need because otherwise the restraints aren't partitioned etc.
    if True: # TODO: enable when done testing overall strategy.
        p.validate(parseOnly=True, htmlOnly=True)

    # WATCH OUT WITH THE BELOW COMMANDS.
    # Use CASD_ID as a kind of unique key. Enforced in DB.
    result = execute(centry.delete().where(centry.c.casd_id == casd_id))
    if result.rowcount:
        NTdebug("Removed original entries numbering: %s" % result.rowcount)
    else:
        NTdebug("No original entry present yet.")

    chainList = molecule.allChains()
    is_multimeric = False
    if len(chainList) > 1:
        is_multimeric = True

    chothia_class = molecule.cothiaClassInt()

    distance_count = project.distances.lenRecursive()
    dihedral_count = project.dihedrals.lenRecursive()
    rdc_count = project.rdcs.lenRecursive()
    peak_count = project.peaks.lenRecursive()
    # TODO: test
    assignmentCountMap = project.molecule.getAssignmentCountMap()
    cs_count = assignmentCountMap['overall']
    cs1H_count = assignmentCountMap['1H']
    cs13C_count = assignmentCountMap['13C']
    cs15N_count = assignmentCountMap['15N']

    # WI
    p_wi_bbcchk = molecule.getDeepAvgByKeys(WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR)
    p_wi_bmpchk = molecule.getDeepAvgByKeys(WHATIF_STR, BMPCHK_STR, VALUE_LIST_STR)
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

    # Wattos
    noe_compl4 = molecule.getDeepByKeys(WATTOS_STR, COMPLCHK_STR, VALUE_LIST_STR)

    # Overall rog
    rogC = molecule.rogScore.rogInt()

    result = csql.conn.execute(centry.insert().values(
        casd_id=casd_id,
        name=casd_id,
        is_multimeric=is_multimeric,
        chothia_class=chothia_class,
        res_count=molecule.residueCount,
        model_count=molecule.modelCount,
        distance_count=distance_count,
        dihedral_count=dihedral_count,
        rdc_count=rdc_count,
        peak_count=peak_count,
        cs_count=cs_count,
        cs1H_count=cs1H_count,
        cs13C_count=cs13C_count,
        cs15N_count=cs15N_count,
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
        noe_compl4=noe_compl4,
        rog=rogC
        )
    )
#    entry_id_list = result.last_inserted_ids() # fails for postgres version I have.
#    entry_id_list = result.inserted_primary_key() # wait for this new feature
    entry_id_list = execute(select([centry.c.entry_id]).where(centry.c.casd_id==casd_id)).fetchall()
    if not entry_id_list:
        NTerror("Failed to get the id of the inserted entry but got: %s" % entry_id_list)
        return True
    if len( entry_id_list ) != 1:
        NTerror("Failed to get ONE id of the inserted entry but got: %s" % entry_id_list)
        return True
    entry_id = entry_id_list[0][0]
    NTdebug("Inserted entry id %s" % entry_id)


#    for residue in csql.session.query(cresidue):
#        NTdebug("New residue number %s" % residue.number)
#
#    for instance in csql.session.query(centry):
#        NTdebug( "Retrieved entry instance: %s" % instance.entry_id )

    for chain in project.molecule.allChains():
        nameC = chain.name
        chothia_class = molecule.cothiaClassInt()
        rogC = chain.rogScore.rogInt()
        result = csql.conn.execute(cchain.insert().values(
            entry_id=entry_id,
            name=nameC,
            chothia_class=chothia_class,
            rog=rogC,
            )
        )
#        chain_id = result.last_inserted_ids()[0]
    #    chain_id = result.inserted_primary_key() # wait for this new feature TODO:
        s = select([cchain.c.chain_id],and_(cchain.c.entry_id == entry_id, cchain.c.name == nameC))
        chain_id = execute(s).fetchall()[0][0]
        NTdebug("Inserted chain id %s" % chain_id)
        for residue in chain.allResidues():
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
            dssp_id = getDsspSecStructConsensusId(residue)

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
            noe_compl4 = residue.getDeepByKeys(WATTOS_STR, COMPLCHK_STR, VALUE_LIST_STR)

            rogR = residue.rogScore.rogInt()
            result = csql.conn.execute(cresidue.insert().values(
                entry_id=entry_id,
                chain_id=chain_id,
                name=nameR,
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
                noe_compl4=noe_compl4,
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
            NTdebug("Inserted residue %s" % residue_id)
            if True:
                for atom in residue.allAtoms():
                    a_name = atom.name
                    # WI
                    a_wi_ba2lst = atom.getDeepAvgByKeys(WHATIF_STR, BA2CHK_STR, VALUE_LIST_STR)
                    a_wi_bh2chk = atom.getDeepAvgByKeys(WHATIF_STR, BH2CHK_STR, VALUE_LIST_STR)
                    a_wi_chichk = atom.getDeepAvgByKeys(WHATIF_STR, CHICHK_STR, VALUE_LIST_STR)
                    a_wi_dunchk = atom.getDeepAvgByKeys(WHATIF_STR, DUNCHK_STR, VALUE_LIST_STR)
                    a_wi_hndchk = atom.getDeepAvgByKeys(WHATIF_STR, HNDCHK_STR, VALUE_LIST_STR)
                    a_wi_mischk = atom.getDeepAvgByKeys(WHATIF_STR, MISCHK_STR, VALUE_LIST_STR)
                    a_wi_mo2chk = atom.getDeepAvgByKeys(WHATIF_STR, MO2CHK_STR, VALUE_LIST_STR)
                    a_wi_pl2chk = atom.getDeepAvgByKeys(WHATIF_STR, PL2CHK_STR, VALUE_LIST_STR)
                    a_wi_wgtchk = atom.getDeepAvgByKeys(WHATIF_STR, WGTCHK_STR, VALUE_LIST_STR)

                    # Store only atoms for which there is usefull info.
                    useFullColumns = [
                        a_wi_ba2lst,
                        a_wi_bh2chk,
                        a_wi_chichk,
                        a_wi_dunchk,
                        a_wi_hndchk,
                        a_wi_mischk,
                        a_wi_mo2chk,
                        a_wi_pl2chk,
                        a_wi_wgtchk
                    ]
                    hasUsefullColumn = False
                    for column in useFullColumns:
                        if column != None:
                            hasUsefullColumn = True
                    if not hasUsefullColumn:
                        continue
                    a_rog = atom.rogScore.rogInt()
                    result = csql.conn.execute(catom.insert().values(
                        entry_id=entry_id,
                        chain_id=chain_id,
                        residue_id=residue_id,
                        name=a_name,
                        wi_ba2lst=a_wi_ba2lst,
                        wi_bh2chk=a_wi_bh2chk,
                        wi_chichk=a_wi_chichk,
                        wi_dunchk=a_wi_dunchk,
                        wi_hndchk=a_wi_hndchk,
                        wi_mischk=a_wi_mischk,
                        wi_mo2chk=a_wi_mo2chk,
                        wi_pl2chk=a_wi_pl2chk,
                        wi_wgtchk=a_wi_wgtchk,
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
                    NTdebug("Inserted atom %s %s" % (atom_id, atom))
                # end for atom
            # end if atom
        # end for residue
    # end for chain

    # Needed for the above hasn't been autocommitted.
    NTdebug("Committing changes")
    csql.session.commit()
# end def

if __name__ == "__main__":
    cing.verbosity = verbosityDebug

    try:
        status = main(*sys.argv[1:])
        if status:
            NTerror("Failed script: storeNRGCING2db.py")
    finally:
        NTmessage(getStopMessage())
