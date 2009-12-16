"""
Create some pics and statistics based on NRG-CING RDB.

python $CINGROOT/python/cing/NRG/nrgCingStats.py

Fails if MySql backend is absent.
"""
from cing import verbosityDebug
from cing.Libs.NTutils import NTerror
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from unittest import TestCase
import cing
import sys

class NrgCingStats(TestCase):

    def __init__(self):
        self.csql = csqlAlchemy()
        if self.csql.connect():
            NTerror("Failed to connect")
            sys.exit(1)
        self.csql.autoload()


    def distributionRogByResidue(self):

        execute = self.csql.conn.execute #@UnusedVariable
        centry = self.csql.entry #@UnusedVariable
        cchain = self.csql.chain #@UnusedVariable
        cresidue = self.csql.residue #@UnusedVariable



if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    n = NrgCingStats()
    n.distributionRogByResidue()

