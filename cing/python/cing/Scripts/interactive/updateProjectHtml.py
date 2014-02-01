# Execute like:
# cd $D/NRG-CING/data/br/1brv; python -u $CINGROOT/python/cing/Scripts/interactive/updateProjectHtml.py 1brv 9
import cing
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.Utils import getArchiveIdFromDirectoryName
from cing.core.classes import Project


def updateProjectHtml(pdb_id, extraArgListStr):
#    extraArgList = extraArgListStr.split()
    htmlOnly = True
    project = Project.open(pdb_id, status='old')
    nTmessage("Opened existing project")
    if not project:
        nTerror("Failed to init old project")
        return True
    # end if
    archive_id = getArchiveIdFromDirectoryName( os.getcwd() )
    # Derives the related entry codes in PDB and BMRB.
    project.molecule.setArchiveId( archive_id )
    if True: # DEFAULT: True
        nTmessage("Updating project html")
    #    project.runCingChecks(toFile=True, ranges=ranges)
        project.setupHtml()
        project.generateHtml(htmlOnly = htmlOnly)
        project.renderHtml()
    # end if
    project.save()
    nTmessage("Done with updateProjectHtml")
# end def

if __name__ == '__main__':
    # Give it a good header and footer for automated checking later on.
    starttime = time.time()
    nTmessage( cing.cingDefinitions.getHeaderString() )
    nTmessage( cing.systemDefinitions.getStartMessage())
    pdb_id = sys.argv[1]
    cing.verbosity = int( sys.argv[2] )
    nTmessage( 'Arguments: %s' % str(sys.argv) )
    if updateProjectHtml(pdb_id, ''):
        nTerror("Failed updateProjectHtml")
    # end if
    nTmessage( cing.systemDefinitions.getStopMessage() )
# end if
