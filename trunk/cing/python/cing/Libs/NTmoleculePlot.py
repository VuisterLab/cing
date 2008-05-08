#No matplotlib items imported here.
# Only code specific for molecule.py related things.
# It would be good to move the ResPlot class here too.

from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import ResPlot
from cing.Libs.NTutils import NTcodeerror


class MoleculePlotSet:
    def __init__(self, project, ranges, keyLoL, nrows):
        self.project = project
        self.ranges  = ranges
        self.nrows   = nrows
        self.keyLoLoL = keyLoL
#        E.g. keyList of one plotable parameter off of a residue: [ 'whatif', 'RAMCHK' ]
        if len( self.keyLoL ) != nrows:
            NTcodeerror('keyLoL does not contain nrows: %d but has length: %d' % (
                            nrows, len( self.keyLoL )))

    def createMoleculePlotSet(self):
        _rangeList = self.project.molecule.getFixedRangeList(
            max_length_range = ResPlot.MAX_WIDTH_IN_RESIDUES, ranges=self.ranges )

class ResPlotSet(NTplotSet):
    def __init__(self):
        pass
    def createResPlotSet(self):
        pass
