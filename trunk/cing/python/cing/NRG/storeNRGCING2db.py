# Execute like:
# cd /Library/WebServer/Documents/NRG-CING/data/br/1brv; \
# python -u $CINGROOT/python/cing/NRG/storeNRGCING2db.py 1brv .
#
# NB this script fails if the MySql backend is not installed.
from cing import header
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from cing.core.classes import Project
from cing.main import getStartMessage
from cing.main import getStopMessage
import cing
import os
import sys


def main(pdb_id, *extraArgList):
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
    NTdebug("pdb_id:              " + pdb_id)
    NTdebug("inputDir:             " + inputDir)
    # presume the directory still needs to be created.
    cingEntryDir = pdb_id + ".cing"

    NTmessage("Now in %s" % os.path.curdir)

    if not os.path.isdir(cingEntryDir):
        NTerror("Failed to find input directory: %s" % cingEntryDir)
        return
    # end if.

    # Needs to be copied because the open method doesn't take a directory argument..
    project = Project.open(pdb_id, status='old')
    if not project:
        NTerror("Failed to init old project")
        return True

    # shortcuts
    p = project
    mol = project.molecule #@UnusedVariable
    m = project.molecule #@UnusedVariable
    p.runCingChecks() # need because otherwise the restraints aren't partitioned etc.

    csql = csqlAlchemy()
    if csql.connect():
        NTerror("Failed to connect to DB")
        return True

    csql.autoload()

    execute = csql.conn.execute
    centry = csql.entry
    cchain = csql.chain
    cresidue = csql.residue

    # WATCH OUT WITH THE BELOW COMMANDS.
    #result = csql.conn.execute(centry.delete())
    result = execute(centry.delete().where(centry.c.pdb_id == pdb_id))
    if result.rowcount:
        NTdebug("Removed original entries numbering: %s" % result.rowcount)
    else:
        NTdebug("No original entry present yet.")

    result = csql.conn.execute(centry.insert().values(pdb_id=pdb_id, name=pdb_id, res_count=m.residueCount, model_count = m.modelCount))
    entry_id = result.last_inserted_ids()[0]
    NTdebug("Inserted entry id %s" % entry_id)

#    for residue in csql.session.query(cresidue):
#        NTdebug("New residue number %s" % residue.number)
#
#    for instance in csql.session.query(centry):
#        NTdebug( "Retrieved entry instance: %s" % instance.entry_id )

    for chain in project.molecule.allChains():
        nameC = chain.name
        rogC = chain.rogScore.rogInt()
        result = csql.conn.execute(cchain.insert().values(entry_id=entry_id, name=nameC, rog=rogC))
        chain_id = result.last_inserted_ids()[0]
        NTdebug("Inserted chain id %s" % chain_id)
        for residue in chain.allResidues():
            valueMapList = []
#            NTmessage("Residue: %s" % residue)

            valueMap = NTdict()
            valueMapList.append(valueMap)

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
            #for j in range(1):
            #    for i in range(1):
            nameR = residue.resName
            numberR = residue.resNum
            rogR = residue.rogScore.rogInt()
            result = csql.conn.execute(cresidue.insert().values(entry_id=entry_id, chain_id=chain_id),
                        name=nameR,number=numberR, rog=rogR)
            residue_id = result.last_inserted_ids()[0]
            NTdebug("Inserted residue %s" % residue_id)

        # end for residue
    # end for chain

    # Needed for the above hasn't been autocommitted.
    NTdebug("Committing changes")
    csql.session.commit()
# end def

if __name__ == "__main__":
    cing.verbosity = verbosityDebug

#        sys.exit(1) # can't be used in forkoff api
    try:
        status = main(*sys.argv[1:])
        if status:
            NTerror("Failed script: storeNRGCING2db.py")
    finally:
        NTmessage(getStopMessage())
