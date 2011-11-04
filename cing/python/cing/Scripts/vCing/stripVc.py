'''
Created on Nov 4, 2011

@author: jd
'''
from cing.Libs.NTutils import * #@UnusedWildImport
from shutil import rmtree

homeDir = '/Users/jd'
#homeDir = '/home/i' # DEFAULT: '/home/i'

# Only include directories that will automatically be regenerated.
deleteListHomeI = """
    .bash_history
    .local/share/Trash/files
    .ssh
    Dropbox
    tmp/cingTmp    
""".split()

deleteListTmp = """
"""

def stripVc(deletePersonal = 0, deleteTmp = 1 ):
    '''
    Remove resources that may be personal of nature. Such as Dropbox, commercial programs and ssh keys.
    Return True on error like not removing resources.
    '''
    
    deleteList = []
    if deletePersonal:
        deleteList += deleteListHomeI
    # end if
    if deleteTmp:
        deleteList += deleteListTmp
    # end if    
    nTmessage("Will remove: %s" % deleteList)
    answer = None
    while answer not in ["y","n"]:
        answer = raw_input("Please confirm you are about to remove all non-public resources; please enter y or n:")
    isOk = answer == "y"
    if not isOk:
        nTerror("Not removing resources.")
        return True
    # end if
    for item in deleteList:
        fullPath = os.path.join(homeDir, item)
        nTmessage("Deleting: %s" % fullPath)
        rmtree(fullPath)
        if os.path.exists(fullPath):
            nTerror("Failed to remove %s" % fullPath)
            return True
        # end if
    # end for
    nTmessage("Removed all listed resources")
# end def

if __name__ == '__main__':
    stripVc()
# end def
