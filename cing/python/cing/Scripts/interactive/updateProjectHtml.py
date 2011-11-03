# Execute like:
# cd $D/NRG-CING/data/br/1brv; python -u $CINGROOT/python/cing/Scripts/interactive/mouseBuffer5.py 1brv 9
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
    # Autoderive also the related entries.
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
    # Needs to be executed in directory with cing project.
#    pdb_id = '1brv'
    pdb_id = sys.argv[1]
    cing.verbosity = int( sys.argv[2] )
    nTmessage( 'Arguments: %s' % str(sys.argv) )
#    pdb_id = '2duw'
#    ch23 = pdb_id[1:3]
#    extraArgListStr = '/Library/WebServer/Documents/NRG-CING/data/%(ch23)s/%(pdb_id)s' % dict ( ch23=ch23, pdb_id=pdb_id)
    if updateProjectHtml(pdb_id, ''):
        nTerror("Failed updateProjectHtml")
    # end if
# end if
        