#!/usr/bin/env python

"""
This script will use NRG-CING files to generate new structures for existing NMR PDB entries.

Execute like NrgCing, e.g.

$C/python/cing/NRG/recoord.py updateWeekly
$C/python/cing/NRG/recoord.py 1brv replaceCoordinates
"""

from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.helper import * #@UnusedWildImport
from cing.NRG import ARCHIVE_RECOORD_ID
from cing.NRG.nrgCing import NrgCing
from cing.NRG.nrgCing import runNrgCing
from cing.NRG.nrgCingRdb import NrgCingRdb
from cing.NRG.settings import * #@UnusedWildImport

class Recoord(NrgCing):
    """Main class for preparing and running NMR recalculations."""
    def __init__(self,
                 useTopos=False,
                 getTodoList=True,
                 max_entries_todo=1,
                 max_time_to_wait=86400,
                 # one day. 2p80 took the longest: 5.2 hours. 
#                 But <Molecule "2ku1" (C:7,R:1659,A:36876,M:30)> is taking longer. 2ku2 is taking over 12 hrs now.
                 processes_max=None,
                 prepareInput=False,
                 writeWhyNot=True,
                 writeTheManyFiles=False,
                 updateIndices=True,
#                 isProduction=True
                ):
        kwds = NTdict( 
                 useTopos=useTopos, # There must be an introspection possible for this.
                 getTodoList=getTodoList,
                 max_entries_todo=max_entries_todo,
                 max_time_to_wait=max_time_to_wait, # one day. 2p80 took the longest: 5.2 hours. 
#                 But <Molecule "2ku1" (C:7,R:1659,A:36876,M:30)> is taking longer. 2ku2 is taking over 12 hrs now.
                 processes_max=processes_max,
                 prepareInput=prepareInput,
                 writeWhyNot=writeWhyNot,
                 writeTheManyFiles=writeTheManyFiles,
                 updateIndices=updateIndices,
#                 isProduction=isProduction,
)
        kwds = kwds.toDict()
        NrgCing.__init__( self, **kwds ) # Steal most from super class. 
        self.results_base = results_base_recoord

        self.entry_to_delete_count_max = 0 # can be as many as fail every time.
        self.usedCcpnInput = 0  # For NMR_REDO it is not from the start.
        self.validateEntryExternalDone = 0
        self.nrgCing = NrgCing() # Use as little as possible thru this inconvenience variable.                
        self.archive_id = ARCHIVE_RECOORD_ID        
        self.validateEntryExternalDone = False # DEFAULT: True 
#        in the future and then it won't change but for NrgCing it is True from the start.
        self.updateDerivedResourceSettings() # The paths previously initialized in NrgCing. Will also chdir.
        
        if 1:
            nTmessage("Going to use specific entry_list_todo in prepare")
#            self.entry_list_done = readLinesFromFile('/Library/WebServer/Documents/NRG-CING/list/entry_list_recoord_nrgcing_shuffled.csv')
            m = NrgCingRdb(schema=self.schema_id)
            self.entry_list_done = m.getPdbIdList(fromCing=True)            
            self.entry_list_done = NTlist( *self.entry_list_done )
        if 0:
            self.entry_list_todo.clear() 
            # Random set of 10 from RECOORD still present in PDB.
#            self.entry_list_todo += "1mmc 1ks0 1b4r 1nxi 1eww 1hp3 1iox 2u2f 1kjs 1orx".split()
            self.entry_list_todo += "1brv".split()
        if 0: # DEFAULT: 0
            nTmessage("Going to use specific entry_list_todo in prepare")
            self.entry_list_todo = readLinesFromFile('/Library/WebServer/Documents/NRG-CING/list/entry_list_recoord_nrgcing_shuffled.csv')
            self.entry_list_todo = NTlist( *self.entry_list_todo )
    # end def
    def setPossibleEntryList(self): # pylint: disable=W0221        
        pass
    # end def
# end class.

if __name__ == '__main__':
    max_entries_todo = 10 # DEFAULT: 10
    runNrgCing( useClass = Recoord, max_entries_todo = max_entries_todo )
