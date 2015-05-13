'''
Execute like:
python -u $CINGROOT/python/cing/Scripts/interactive/nmr_redo_compareProjects.py --target 2kq3
'''

from cing import cingVersion
from cing.Libs.AwkLike import AwkLikeS
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import ProjectTree

# Data about the CASD-NMR entries
#from cing.NRG.CasdNmrMassageCcpnProject import programHoH
entry_id = '2kq3'
programHoH = {
 entry_id:   {
              '_redo': 'redo'
}}
targets = programHoH.keys()
g = NTlist()
for target in targets:
    g.addList(programHoH[target].keys())
g.removeDuplicates()
g.sort()
groups  = ['Org'] + g

# ranges for each target
ranges  = NTdict()
rangesDefs = """
# target                 CYANA                 PSVS                         CING                    Consensus
2kq3                     8-41,46,54-139                 8-41,46,54-139				        8-41,46,54-139			        8-41,46,54-139
"""
for line in AwkLikeS( rangesDefs, commentString='#', minNF=5 ):
    ranges[line.dollar[1]] = line.dollar[3]
# end for
ranges['2kq3'] = '8-41,46,54-139'
ranges.keysformat()


# Colors  and groupDefs
#colors = NTlist(*range(180,180+30*len(groups),30)).limit(0,360)
colors = {   'Org': 240,
             '_redo': 105
}
groupDefs = NTdict()
for i,g in enumerate(groups):
    groupDefs[g] = NTdict( id = i, color = colors[g], name=g, __FORMAT__ = 'Group %(name)-12s (%(id)2d), color %(color)s' )
groupDefs.keysformat()

def getGroupsForTarget(target, groups):
    groupList = []
    for group in groups:
        if not (group == 'Org' or getDeepByKeysOrAttributes( programHoH, target, group)):
            continue
        groupList.append(group)
    return groupList
# end def

header = """
======================================================================================================
    nmr_redo_compareProjects       version %s
======================================================================================================
""" % (cingVersion)

nTmessage( header )
nTmessage( "Targets:         " + str(targets ))
nTmessage( "Groups:          " + str(groups ))
for g in groups:
    print  groupDefs[g].format()


parser = OptionParser(usage="nmr_redo_compareProjects.py [options] Use -h or --help for full options.")

parser.add_option("--target",
                  dest="target",
                  help="Define target.",
                  metavar="TARGET"
                 )
parser.add_option("--out",
                  dest="outFile",
                  help="Define result output file.",
                  metavar="OUTFILE"
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
    nTerror("set verbosity is outside range [0-9] at: " + options.verbosity)
    nTerror("Ignoring setting")
#end if

#options.target = 'CGR26A'
options.target = entry_id

# Check the targets
if not options.target:
    nTerror('No target defined, aborting')
    sys.exit(1)
if not options.target in targets:
    nTerror('Target "%s" not in %s, aborting', options.target, targets)
    sys.exit(1)

target = options.target
groupsForTarget = getGroupsForTarget(target, groups)[0:2]
nTmessage( "Target:          " + target )
nTmessage( "Ranges target:   " + ranges[target] )
nTmessage( "Groups target:   " + str( groupsForTarget ))
#sys.exit(1)

# Open the project instances.
pTree = ProjectTree( target, groups=groupsForTarget, ranges=ranges[target], groupDefs=groupDefs )
pTree.openCompleteTree()
p0 = pTree.entries[0] # shortcut

fp = sys.stdout
if options.outFile:
    fp = open(pTree.path(options.outFile), 'w')
    nTmessage('\n==> Starting analysis: Output to %s', pTree.path(options.outFile))

fprintf( fp, '%s\n\n', pTree.format() )

if 1:
    # Superpose (also defines fitAtoms)
    for p in pTree:
        p.superpose(ranges=pTree.ranges)
        fprintf( fp, '%s\n%s\n', p.molecule, p.molecule.rmsd.format() )

    # Get the closestToMean models, superpose, export to PDB file
    closestToMean = NTlist()
    for p in pTree:
        cl = p.molecule.rmsd.closestToMean
        closestToMean.append( p.molecule.ensemble[cl] )
    fitted = closestToMean.zap('fitCoordinates')
    for m in closestToMean[1:]:
        r = m.superpose(closestToMean[0])
        #print '>', r
    # Export'
#    for p in pTree:
#        p.molecule.toPDBfile( pTree.path(p.name+'.pdb'), model=p.molecule.rmsd.closestToMean)
#sys.exit(1)

# Positional global RMSDs
rmsds = pTree.calcRmsds( ranges=pTree.ranges )
pTree.printRmsds('  Pairwise positional RMSDs residues '+pTree.ranges, rmsds, fp )

# Pih-Psi global RMSDs
rmsds2 = pTree.calcPhiPsiRmsds( ranges=pTree.ranges )
pTree.printRmsds('  Relative pairwise Phi-Psi RMSDs residues '+pTree.ranges, rmsds2, fp )

pTree.printOverallScores( fp )
pTree.printRestraintScores( fp )

#cp.test( pTree, fp )

# yasara macros
pTree.loadPDBmacro(  )
pTree.colorPDBmacro(  )
pTree.rogMacro(  )
pTree.qShiftMacro()
#pTree.colorPhiPsiMacro(  )

if options.outFile:
    fp.close()

pTree.copyFiles2Project(  )
