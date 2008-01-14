#! /usr/bin/env python
#==============================================================================
"""
 run as:
 > cyana2cing.py  [options] CyanaDirectoryName 
 
  Use the flags to detrmine which files get imported.

  Uses the CING API to convert cyana run to cing framework.
  Optionally export on-the-fly to a xplor refine setup.
 
"""
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import OptionParser
from cing.Libs.NTutils import printError
from cing.core.classes import Project
from cing.Libs.NTutils import printWarning
import os
import sys

parser = OptionParser(usage="cyana2cing.py [options] cyanaDirectory Use -h or --help for full options.")

parser.add_option("-o","--overwrite", 
                  action="store_true", 
                  dest="overwrite", default=False,
                  help="Overwrite existing cing output directory (default: no-overwrite)."
                 )
parser.add_option("-c", "--convention", 
                  dest="convention", default="CYANA2",
                  help="Set convention (CYANA,CYANA2).", 
                  metavar="CONVENTION"
                 )
parser.add_option("--seqFile", 
                  dest="seqFile", 
                  help="Define seqFile (no .seq extention).", 
                  metavar="SEQFILE"
                 )
parser.add_option("--protFile", 
                  dest="protFile", 
                  help="Define protFile (no .prot extention).", 
                  metavar="PROTFILE"
                 )
parser.add_option("--pdbFile", 
                  dest="pdbFile", 
                  help="Define pdbFile (no .pdb extention).", 
                  metavar="PDBFILE"
                 )
parser.add_option("-n", "--nmodels", 
                  dest="nmodels", default=20,
                  help="Define number of models to extract from PDBFILE.", 
                  metavar="PDBFILE"
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
parser.add_option("--refine", 
                  dest="refine",
                  help="Setup and export to Refine/NAME directory of project.", 
                  metavar="NAME"
                 )
parser.add_option("--export", 
                  action="store_true", 
                  dest="export", default=False,
                  help="Export to different formats (default: no-export)."
                 )
                 
(options, args) = parser.parse_args()

if not options.seqFile:   
    options.seqFile = None
if not options.protFile:  
    options.protFile = None
if not options.pdbFile:   
    options.pdbFile = None
    
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
    printError('no arguments found')
    sys.exit(1)
    
if not os.path.exists( args[0] ):
    NTerror('ERROR: directory "%s" not found\n', args[0] )
    sys.exit(1)

projectRoot = Project.rootPath( args[0] )
if os.path.exists( projectRoot ) and not options.overwrite:
    NTerror('ERROR: output directory "%s" already exists; Use -o or --overwrite to overwrite\n', projectRoot )
    sys.exit(1)
    
project = Project.open(args[0], 'new', verbose=False )
project.cyana2cing( args[0], convention=options.convention,
                    seqFile   = options.seqFile,
                    protFile  = options.protFile,
                    peakFiles = options.peakFiles,
                    uplFiles  = options.uplFiles,
                    acoFiles  = options.acoFiles,
                    pdbFile   = options.pdbFile,
                    nmodels   = int(options.nmodels),
                    copy2sources = True
)

if not project:
    printWarning("No project generated. Aborting further execution.")
    sys.exit(0)
    
if options.refine: 
    project.export2refine( options.refine )

if options.export: 
    project.export()

project.save()

#printDebug("Doing a hard system exit")
#sys.exit(0)


