# cd /Library/WebServer/Documents/NRG-CING/data/br/1brv; python -u $CINGROOT/python/cing/NRG/storeNRGCING2db.py 1brv .
from cing import header
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.core.classes import Project
from cing.main import getStartMessage
from cing.main import getStopMessage
import MySQLdb
import cing
import os
import sys


def main(entryId, *extraArgList):
    """inputDir may be a directory or a url.
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
    NTdebug("entryId:              " + entryId)
    NTdebug("inputDir:             " + inputDir)
    # presume the directory still needs to be created.
    cingEntryDir = entryId + ".cing"

    NTmessage("Now in %s" % os.path.curdir)

    if not os.path.isdir(cingEntryDir):
        NTerror("Failed to find input directory: %s" % cingEntryDir)
        return
    # end if.

    # Needs to be copied because the open method doesn't take a directory argument..
    project = Project.open(entryId, status = 'old')
    if not project:
        NTerror("Failed to init old project")
        return True

    conn = None
    try:
        conn = MySQLdb.connect (host = "localhost",
                         user = "nrgcing1",
                         passwd = "4I4KMS",
                         unix_socket = '/tmp/mysql.sock',
                         db = "mysql")
        NTdebug("Connection to Mysql nrgcing made")
    except MySQLdb.Error, e:
        NTerror("Mysql connection failed: %d: %s" % (e.args[0], e.args[1]))
        return True

    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    row = cursor.fetchone()
    NTmessage("server version: %s" % row[0])

    for residue in project.molecule.allResidues():
        NTmessage("Residue: %s" % residue)

#    cursor.execute ("""
#           INSERT INTO entry (name, category)
#           VALUES
#             ('snake', 'reptile'),
#             ('frog', 'amphibian'),
#             ('tuna', 'fish'),
#             ('racoon', 'mammal')
#         """)
#
#    NTmessage("Number of rows inserted: %d" % cursor.rowcount)



    cursor.close()
    conn.close ()


if __name__ == "__main__":
    cing.verbosity = verbosityDebug

#        sys.exit(1) # can't be used in forkoff api
    try:
        status = main(*sys.argv[1:])
    finally:
        NTmessage(getStopMessage())

