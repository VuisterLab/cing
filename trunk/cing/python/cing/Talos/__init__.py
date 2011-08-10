# File to allow this directory to be treated as a python package.
# import sys
#
# header = """
# ====================================
#  Talos: python talos package
#  (c) GWV 2006
# ====================================
#
# """
from cing.Talos.nmrPipeTable import NmrPipeTable
import  os

talosPath = os.path.split( __file__)[0]

talosDb          = NmrPipeTable( talosPath + '/talos.tab' )
talosDb.atoms    = ['N', 'CA', 'HA', 'C', 'CB']
talosDb.residues = ['R1', 'R2', 'R3']

talosDb.shiftNames = []
for a in talosDb.atoms:
    for r in talosDb.residues:
        talosDb.shiftNames.append( a + '_' + r )
    #end for
#end for

#subsitute the 9999 values with None
for row in talosDb.values():
    for s in talosDb.shiftNames:
        if (row[s] == 9999.00):
            row[s] = None
        #end if
    #end for
#end for

