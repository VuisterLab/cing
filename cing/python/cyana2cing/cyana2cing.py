#! /usr/bin/env python
#==============================================================================
"""
    run as:
    cyana2cing.py  [options] CyanaDirectoryName

    Use the flags to determine which files get imported.

    Uses the CING API to convert cyana run to cing framework.
    Optionally export on-the-fly to a xplor refine setup.

"""

import cing
from cing import cingVersion
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import NTerror
from cing.core.classes import Project

from cing.Libs.NTutils import OptionParser
import os
import sys

header = """
======================================================================================================
    cyana2cing       version %s
======================================================================================================
""" % (cingVersion)

parser = OptionParser(usage="cyana2cing.py [options] cyanaDirectory Use -h or --help for full options.")

parser.add_option("-o","--overwrite",
                  action="store_true",
                  dest="overwrite", default=False,
                  help="Overwrite existing cing output directory (default: no-overwrite)."
                 )
parser.add_option("-c", "--convention",
                  dest="convention",
                  default="CYANA2",
                  help="Set convention: CYANA,CYANA2 (default=CYANA2).",
                  metavar="CONVENTION"
                 )
parser.add_option("--coordinateConvention",
                  dest="coordinateConvention",
                  default="CYANA2",
                  help="Set convention: CYANA,CYANA2,XPLOR (default=CYANA2).",
                  metavar="COORDINATE_CONVENTION"
                 )
parser.add_option("--seqFile",
                  dest="seqFile",
                  help="Define seqFile (no .seq extension).",
                  metavar="SEQFILE"
                 )
parser.add_option("--protFile",
                  dest="protFile",
                  help="Define protFile (no .prot extention).",
                  metavar="PROTFILE"
                 )
parser.add_option("--stereoFile",
                  dest="stereoFile",
                  help="Define stereoFile (no .cya extention).",
                  metavar="STEREOFILE"
                 )
parser.add_option("--pdbFile",
                  dest="pdbFile",
                  help="Define pdbFile (no .pdb extention).",
                  metavar="PDBFILE"
                 )
parser.add_option("--nmodels",
                  dest="nmodels", default=20,
                  help="Define number of models to extract from PDBFILE (default=20).",
                  metavar="NMODELS"
                 )
parser.add_option("--peakFiles",
                  dest="peakFiles",
                  help="Define peakFiles (no .peaks extention; separate by comma's:e.g. c13,n15).",
                  metavar="PEAKFILES"
                 )
parser.add_option("--uplFiles",
                  dest="uplFiles",
                  help="Define uplFiles (no .upl extention; separate by comma's:e.g. final,manual).",
                  metavar="UPLFILES"
                 )
parser.add_option("--acoFiles",
                  dest="acoFiles",
                  help="Define acoFiles (no .aco extention; separate by comma's:e.g. talos,hnha).",
                  metavar="ACOFILES"
                 )
parser.add_option("--export",
                  action="store_true",
                  dest="export", default=False,
                  help="Export to different formats (default: no-export)."
                 )
parser.add_option("-v", "--verbosity", type='int',
                  default=cing.verbosityDefault,
                  dest="verbosity", action='store',
                  help="verbosity: [0(nothing)-9(debug)] no/less messages to stdout/stderr (default: 3)"
                 )

(options, args) = parser.parse_args()

if options.verbosity >= 0 and options.verbosity <= 9:
#        print "In main, setting verbosity to:", options.verbosity
    cing.verbosity = options.verbosity
else:
    NTerror("set verbosity is outside range [0-9] at: " + options.verbosity)
    NTerror("Ignoring setting")
#end if


if not options.seqFile:
    options.seqFile = None

if not options.protFile:
    options.protFile = None

if not options.pdbFile:
    options.pdbFile = None

if not options.stereoFile:
    options.stereoFile = None

if not options.peakFiles:
    options.peakFiles = []
else:
    options.peakFiles = options.peakFiles.split(',')

if not options.uplFiles:
    options.uplFiles = []
else:
    options.uplFiles = options.uplFiles.split(',')

if not options.acoFiles:
    options.acoFiles = []
else:
    options.acoFiles = options.acoFiles.split(',')


#if (len(args) >= 1):
if not args:
    NTerror('no arguments found')
    sys.exit(1)

if not os.path.exists( args[0] ):
    NTerror('directory "%s" not found\n', args[0] )
    sys.exit(1)

if Project.exists( args[0] ) and not options.overwrite:
    NTerror('Cing project "%s" already exists; Use -o or --overwrite to overwrite\n', args[0] )
    sys.exit(1)

#=====================================================================================
# Done checking arguments, lets have some action
#=====================================================================================
NTmessage( header )

project = Project.open(args[0], 'new')
if not project:
    NTwarning("No project generated. Aborting further execution.")
    sys.exit(0)
#end if

project.cyana2cing( args[0],
                    convention   = options.convention,
                    coordinateConvention = options.coordinateConvention,
                    seqFile      = options.seqFile,
                    protFile     = options.protFile,
                    stereoFile   = options.stereoFile,
                    peakFiles    = options.peakFiles,
                    uplFiles     = options.uplFiles,
                    acoFiles     = options.acoFiles,
                    pdbFile      = options.pdbFile,
                    nmodels      = int(options.nmodels),
                    copy2sources = True,
                    update       = False
                  )

print project.format()

if options.export:
    project.export()

project.close()

#NTdebug("Doing a hard system exit")
#sys.exit(0)


