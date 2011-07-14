#!/usr/bin/env python
"""
#=======================================================================

 xplor2pdb.py

 GWV 2 Feb 2006: Xplor generated pdb-files to single-file pdb format
 GWV 24 May 2007: using cing routines
#=======================================================================
"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.PyMMLib import MODEL
from cing.Libs.PyMMLib import PDBFile
from cing.Libs.PyMMLib import REMARK
from cing.Libs.PyMMLib import TER
from cing.core.constants import * #@UnusedWildImport
from cing.core.database import NTdb

version = "%prog 1.1 alpha"
usage   = "usage: %prog [options] [xplor-files]"

#=======================================================================
#
# Arguments to program
#
#=======================================================================

parser = OptionParser(usage=usage, version=version)
parser.add_option("--doc",
                  action="store_true",
                  dest="doc", default=False,
                  help="print extended documentation to stdout"
                 )
parser.add_option("-m", "--modelList",
                  dest="modelList", default=None,
                  help="optional file with names of xplor files",
                  metavar="MODELLIST"
                 )
parser.add_option("-o", "--outFile",
                  dest="outFile",
                  help="pdb file (required)",
                  metavar="OUTFILE"
                 )
parser.add_option("-c", "--convention",
                  dest="convention", default='PDB',
                  help="Input convention (PDB (default), CYANA or CYANA2)",
                  metavar="CONVENTION"
                 )
parser.add_option("-t", "--ter",
                  action="store_true", default=False,
                  dest="terRecord",
                  help="Patch with TER record"
                 )
(options, args) = parser.parse_args()

#print options
#print args

if options.doc:
    parser.print_help(file=sys.stdout)
    print __doc__
    sys.exit(0)

parser.check_required('-o')

if options.modelList != None:
    files = []
    for line in AwkLike( options.modelList ):
        files.append( line.dollar[1] )
    #end for
else:
    files = args
#endif

# convention
convention = 'PDB'
if options.convention != None:
    convention = options.convention
#end if

verbose = 1

#=======================================================================
#
# Start of routine
#
#=======================================================================

pdbFile = open( options.outFile, 'w' )
nTmessage("==> Opened %s", options.outFile )

xplorCount = 0
for fName in files:
    xplorCount += 1
    rem = REMARK()
    rem.remarkNum = xplorCount
    rem.text = 'model %d from xplor file: %s' % (xplorCount, fName)
    fprintf( pdbFile, '%s\n', rem )
pass

modelCount = 0
for fName in files:
    # parse this xplor pdbfile
    pdbfile = PDBFile( fName )

    # print a MODEL record
    modelCount += 1
    mdl         = MODEL()
    mdl.serial  = modelCount
    fprintf( pdbFile, '%s\n', mdl )

    atomCount = 0
    lastRecord = None
    for record in pdbfile:
        if record._name.strip() in ["ATOM","HETATM"]:

            # see if we can find a definition for this residue, atom name in the database
            atm = NTdb.getAtomDefByName( record.resName, record.name, XPLOR )

            # we found a match
            if (atm != None):
                # check if there is an convention equivalent; skip otherwise
                if (atm.translate(convention) != None and atm.residueDef.translate(convention) != None):
                    atomCount     += 1
                    record.serial  = atomCount
                    record.resName = atm.residueDef.translate( convention )
                    record.name    = atm.translate( convention )
                    if not 'chainID' in record:
                        record.chainID = 'A'
                    #end if
                    fprintf( pdbFile, "%s\n", record )
                    lastRecord = record
                else:
                    nTerror('WARNING: cannot translate record to %s (%s)\n', convention, record )
                #end if
            else:
                nTerror('WARNING: %s incompatible record (%s)\n', convention, record )
            #end if
        pass
    pass

    if options.terRecord != None:
        # generate a TER record
        atomCount += 1
        ter        = TER()
        ter.serial = atomCount
        ter.resName = lastRecord.resName
        ter.chainID = lastRecord.chainID
        ter.resSeq  = lastRecord.resSeq
        fprintf( pdbFile, "%s\n", ter )
    #end if
    fprintf( pdbFile, 'ENDMDL\n' )
pass
fprintf( pdbFile, "END\n" )

pdbFile.close()

nTmessage("==> Converted %d xplor files to %s (%s format)\n", xplorCount, options.outFile, convention )




