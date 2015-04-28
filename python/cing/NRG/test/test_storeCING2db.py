"""
Unit test execute as:
python $CINGROOT/python/cing/NRG/test/test_storeCING2db.py
"""
from cing import cingDirTestsData #@UnusedImport
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import ARCHIVE_NRG_ID
from cing.NRG import NRG_DB_NAME
from cing.NRG import PDBJ_DB_NAME
from cing.NRG import PDBJ_DB_USER_NAME
from cing.NRG.PDBEntryLists import * #@UnusedWildImport
from cing.PluginCode.sqlAlchemy import CsqlAlchemy
from unittest import TestCase
from sqlalchemy.sql.expression import select
import unittest

class AllChecks(TestCase):

    def _test_storeCING2db(self): #DEFAULT disabled because it's a specific test for services not commonly used.
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        entry_code = '1brv'
        pdb_id = entry_code
        schema = NRG_DB_NAME
        archive_id = ARCHIVE_NRG_ID
        db_name = PDBJ_DB_NAME
        user_name = PDBJ_DB_USER_NAME

        nTdebug("Starting doStoreCING2db using:")
        nTdebug("entry_code:           %s" % entry_code)
    #    nTdebug("inputDir:             %s" % inputDir)
        nTdebug("archive_id:           %s" % archive_id)
        nTdebug("user_name:            %s" % user_name)
        nTdebug("db_name:              %s" % db_name)
        nTdebug("schema:               %s" % schema)

        csql = CsqlAlchemy(user=user_name, db=db_name,schema=schema)
        self.assertFalse( csql.connect(), "Failed to connect to DB")
        csql.autoload()

        execute = csql.conn.execute
        centry = csql.cingentry

        result = execute(centry.delete().where(centry.c.pdb_id == pdb_id))

        if result.rowcount:
            nTdebug("Removed original entries numbering: %s" % result.rowcount)
            if result.rowcount > 1:
                nTerror("Removed more than the expected ONE entry; this could be serious.")
                return True
        else:
            nTdebug("No original entry present yet.")
        # end if
        datetime_first = datetime.datetime(2011, 4, 7, 11, 12, 26)
        nTdebug("Trying datetime_first %s" % datetime_first)
        result = execute(centry.insert().values(
            pdb_id=pdb_id,
            name=entry_code,
            rev_first = 9,
            rev_last = 99,
            timestamp_first = datetime_first
#            datetime_last = datetime_last
        ))
        entry_id_list = execute(select([centry.c.entry_id]).where(centry.c.pdb_id==pdb_id)).fetchall()
        self.assertTrue( entry_id_list, "Failed to get the id of the inserted entry but got: %s" % entry_id_list)
        self.assertEqual( len( entry_id_list ), 1, "Failed to get ONE id of the inserted entry but got: %s" % entry_id_list)
    # end def
# end class


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()

