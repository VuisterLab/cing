# CASD-NMR analysis
#
# Execute like:
# python -u $CINGROOT/python/cing/Scripts/CASD/casd2.py --target CGR26A

from cing import cingVersion
from cing.Libs.AwkLike import AwkLikeS
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Scripts.CASD import programHoH
from cing.core.classes import ProjectTree

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
AR3436A                  13-95                 13-96				        13-96			        13-95
AtT13                    5-57,70-118           6-119				        7-57,62-67,71-117       7-57,71-117
CGR26A                   15-129                16-20,23-53,58-71,75-128		15-21,24-71,74-127	    16-20,24-53,58-71,75-128
CtR69A                   4-53                  6-51				            5-53			        6-51
HR5537A                  32-135                37-109,112-134			    39-104,117-134		    39-104,117-134
NeR103A                  18-98                 18-98				        21-87,90-96		        21-87,90-96
ET109Aox                 91-189                91-136,138-189			    91-137,140-154,158-189	91-136,140-154,158-189
PGR122A                  418-479               418-444,447-478			    418-425,429-478		    418-425,429-444,447-478
ET109Ared                91-190                91-189				        91-137,140-154,158-189	91-137,140-154,158-189
VpR247                   2-100                 1-101				        2-43,48,52-99		    2-43,48,52-99"""
for line in AwkLikeS( rangesDefs, commentString='#', minNF=5 ):
    ranges[line.dollar[1]] = line.dollar[3]
#
ranges['CGR26A'] = '56-60,63-93,98-111,115-168' # 40 residue offset
ranges['AR3436A']='13-95' # 'auto = '13-96: One smaller as Utrecht2 does not have coordinates for 96, Chesire not byond 87
ranges['1brv']='172-189'
ranges.keysformat()


# Colors  and groupDefs
#colors = NTlist(*range(180,180+30*len(groups),30)).limit(0,360)
colors = {   'Org': 240,
             'A': 105,
             'B': 60,
             'C': 75,
             'Frankfurt': 105,
             'Lyon': 60,
             'Lyon2': 75,
             'Lyon3': 90,
             'Paris': 30,
             'Paris2': 45,
             'Piscataway': 0,
             'Piscataway2': 15,
             'Seattle': 330,
             'Seattle2': 330,
             'Seattle3': 330,
             'Seattle4': 330,
             'Seattle5': 330,
             'Utrecht': 345,
             'Utrecht2': 345,
             'Cheshire': 315
}
groupDefs = NTdict()
for i,g in enumerate(groups):
    groupDefs[g] = NTdict( id = i, color = colors[g], name=g, __FORMAT__ = 'Group %(name)-12s (%(id)2d), color %(color)s' )
groupDefs.keysformat()

# testing
#groups  = ['Org','Piscataway2','Cheshire']
#groups  = ['Org','Piscataway2']
#groups  = ['Org','Utrecht2']
#groups = ['Org','Seattle2','Cheshire','Utrecht2']

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
    CASD-NMR       version %s
======================================================================================================
""" % (cingVersion)

NTmessage( header )
#NTmessage( "Targets:         " + str(targets ))
#NTmessage( "Groups:          " + str(groups ))
#for g in groups:
#    print  groupDefs[g].format()


parser = OptionParser(usage="casd.py [options] Use -h or --help for full options.")

parser.add_option("--target",
                  dest="target",
                  help="Define CASD-NMR target.",
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
    NTerror("set verbosity is outside range [0-9] at: " + options.verbosity)
    NTerror("Ignoring setting")
#end if

#options.target = 'CGR26A'
options.target = '1brv'

# Check the targets
if not options.target:
    NTerror('No target defined, aborting')
    sys.exit(1)
if not options.target in targets:
    NTerror('Target "%s" not in %s, aborting', options.target, targets)
    sys.exit(1)

target = options.target
groupsForTarget = getGroupsForTarget(target, groups)[0:2]
NTmessage( "Target:          " + target )
NTmessage( "Ranges target:   " + ranges[target] )
NTmessage( "Groups target:   " + str( groupsForTarget ))
#sys.exit(1)

# Open the project instances.
pTree = ProjectTree( target, groups=groupsForTarget, ranges=ranges[target], groupDefs=groupDefs )
pTree.openCompleteTree()
p0 = pTree.entries[0] # shortcut

fp = sys.stdout
if options.outFile:
    fp = open(pTree.path(options.outFile), 'w')
    NTmessage('\n==> Starting analysis: Output to %s', pTree.path(options.outFile))

fprintf( fp, '%s\n\n', pTree.format() )

if False:
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
    for p in pTree:
       p.molecule.toPDBfile( pTree.path(p.name+'.pdb'), model=p.molecule.rmsd.closestToMean)

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
