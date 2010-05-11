# CASD-NMR analysis
from cing import cingVersion
from cing.Libs.AwkLike import AwkLikeS
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode import compareProjects

cp = compareProjects



# Data about the CASD-NMR entries
#from cing.NRG.CasdNmrMassageCcpnProject import programHoH
programHoH = {
 'AR3436A': {'Cheshire': 'XPLOR',
             'Frankfurt': 'CYANA',
             'Lyon': None,
             'Lyon2': None,
             'Lyon3': 'CYANA',
             'Paris': None,
             'Paris2': None,
             'Piscataway': None,
             'Piscataway2': 'XPLOR',
             'Seattle': None,
             'Seattle2': 'PDB',
             'Seattle3': None,
             'Seattle4': None,
             'Seattle5': None,
             'Utrecht': None,
             'Utrecht2': 'XPLOR'},
 'AtT13': {'Cheshire': None,
           'Frankfurt': 'CYANA',
           'Lyon': None,
           'Lyon2': None,
           'Lyon3': 'CYANA',
           'Paris': 'XPLOR',
           'Paris2': None,
           'Piscataway': 'XPLOR',
           'Piscataway2': None,
           'Seattle': None,
           'Seattle2': None,
           'Seattle3': 'PDB',
           'Seattle4': 'PDB',
           'Seattle5': None,
           'Utrecht': 'XPLOR',
           'Utrecht2': None},
 'CGR26A': {'Cheshire': 'CYANA',
            'Frankfurt': 'CYANA',
            'Lyon': 'CYANA',
            'Lyon2': None,
            'Lyon3': None,
            'Paris': 'XPLOR',
            'Paris2': None,
            'Piscataway': 'XPLOR',
            'Piscataway2': None,
            'Seattle': None,
            'Seattle2': None,
            'Seattle3': None,
            'Seattle4': 'PDB',
            'Seattle5': 'PDB',
            'Utrecht': None,
            'Utrecht2': 'XPLOR'},
 'CtR69A': {'Cheshire': 'CYANA',
            'Frankfurt': 'CYANA',
            'Lyon': 'CYANA',
            'Lyon2': 'CYANA',
            'Lyon3': None,
            'Paris': 'XPLOR',
            'Paris2': None,
            'Piscataway': 'XPLOR',
            'Piscataway2': None,
            'Seattle': None,
            'Seattle2': None,
            'Seattle3': None,
            'Seattle4': 'PDB',
            'Seattle5': None,
            'Utrecht': 'XPLOR',
            'Utrecht2': None},
 'ET109Aox': {'Cheshire': None,
              'Frankfurt': 'CYANA',
              'Lyon': 'CYANA',
              'Lyon2': None,
              'Lyon3': None,
              'Paris': 'XPLOR',
              'Paris2': None,
              'Piscataway': None,
              'Piscataway2': 'XPLOR',
              'Seattle': 'PDB',
              'Seattle2': None,
              'Seattle3': None,
              'Seattle4': None,
              'Seattle5': None,
              'Utrecht': None,
              'Utrecht2': 'XPLOR'},
 'ET109Ared': {'Cheshire': 'CYANA',
               'Frankfurt': 'CYANA',
               'Lyon': 'CYANA',
               'Lyon2': None,
               'Lyon3': None,
               'Paris': 'XPLOR',
               'Paris2': None,
               'Piscataway': None,
               'Piscataway2': 'XPLOR',
               'Seattle': 'PDB',
               'Seattle2': None,
               'Seattle3': None,
               'Seattle4': None,
               'Seattle5': None,
               'Utrecht': None,
               'Utrecht2': 'XPLOR'},
 'HR5537A': {'Cheshire': 'CYANA',
             'Frankfurt': 'CYANA',
             'Lyon': None,
             'Lyon2': None,
             'Lyon3': 'CYANA',
             'Paris': 'XPLOR',
             'Paris2': None,
             'Piscataway': None,
             'Piscataway2': 'XPLOR',
             'Seattle': None,
             'Seattle2': None,
             'Seattle3': 'PDB',
             'Seattle4': None,
             'Seattle5': None,
             'Utrecht': None,
             'Utrecht2': 'XPLOR'},
 'NeR103A': {'Cheshire': 'CYANA',
             'Frankfurt': 'CYANA',
             'Lyon': 'CYANA',
             'Lyon2': 'CYANA',
             'Lyon3': None,
             'Paris': 'XPLOR',
             'Paris2': None,
             'Piscataway': 'XPLOR',
             'Piscataway2': None,
             'Seattle': None,
             'Seattle2': None,
             'Seattle3': None,
             'Seattle4': 'PDB',
             'Seattle5': None,
             'Utrecht': None,
             'Utrecht2': 'XPLOR'},
 'PGR122A': {'Cheshire': 'CYANA',
             'Frankfurt': 'CYANA',
             'Lyon': 'CYANA',
             'Lyon2': None,
             'Lyon3': None,
             'Paris': None,
             'Paris2': 'XPLOR',
             'Piscataway': 'XPLOR',
             'Piscataway2': None,
             'Seattle': None,
             'Seattle2': None,
             'Seattle3': None,
             'Seattle4': 'PDB',
             'Seattle5': None,
             'Utrecht': 'XPLOR',
             'Utrecht2': None},
 'VpR247': {'Cheshire': 'CYANA',
            'Frankfurt': 'CYANA',
            'Lyon': None,
            'Lyon2': None,
            'Lyon3': 'CYANA',
            'Paris': 'XPLOR',
            'Paris2': None,
            'Piscataway': None,
            'Piscataway2': 'XPLOR',
            'Seattle': None,
            'Seattle2': 'PDB',
            'Seattle3': None,
            'Seattle4': None,
            'Seattle5': None,
            'Utrecht': None,
            'Utrecht2': 'XPLOR'}
}


targets = programHoH.keys()
g=programHoH[targets[0]].keys()
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
ranges.keysformat()


# Colors  and groupDefs
#colors = NTlist(*range(180,180+30*len(groups),30)).limit(0,360)
colors = {   'Org': 240,
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
    groupDefs[g] = NTdict( id = i, color = colors[g], name=g, __FORMAT__ = 'Group %(name)-10s (%(id)2d), color %(color)s' )
groupDefs.keysformat()

# testing
#groups  = ['Org','Piscataway2','Cheshire']
#groups  = ['Org','Piscataway2']
#groups  = ['Org','Utrecht2']
#groups = ['Org','Seattle2','Cheshire','Utrecht2']


def openProjects( target, groups ):
    """Open all project of specific target
    Return Projects instance with CING projects
    Added target and group name to Project instance
    """
    projects = cp.Projects( target, ranges=ranges[target], root='OverviewByTarget' )

    for group in groups:
        if group == 'Org' or programHoH[target][group]:
            path = os.path.join('data', target[1:3],  target + group, target + group + '.cing')
            NTdebug('opening %s', path)
            p = projects.open( path )
            if p:
                #p.runTalosPlus()
                p.target = target
                p.group  = group
                p.color  = groupDefs[group].color
                if p.molecule == None:
                    NTerror('Strange: no molecule, aborting')
                    sys.exit(1)
                #end if
            #end if
        #end if
    #end for
    projects.mapMolecules()
    return projects
#end def

header = """
======================================================================================================
    CASD-NMR       version %s
======================================================================================================
""" % (cingVersion)

print header
print "Targets:", targets
print "Groups: ", groups
for g in groups:
    print  groupDefs[g].format()


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

options.target = 'CGR26A'

# Check the targets
if not options.target:
    NTerror('No target defined, arborting')
    sys.exit(1)
if not options.target in targets:
    NTerror('Target "%s" not in %s, arborting', options.target, targets)
    sys.exit(1)

# Open the projects
projects = openProjects(options.target, groups)
p0 = projects.entries[0] # shortcut

fp = sys.stdout
if options.outFile:
    fp = open(projects.path(options.outFile), 'w')
    NTmessage('\n==> Starting analysis: Output to %s', projects.path(options.outFile))

fprintf( fp, '%s\n\n', projects.format() )

# Superpose (also defines fitAtoms)
for p in projects:
    p.superpose(ranges=projects.ranges)
    fprintf( fp, '%s\n%s\n', p.molecule, p.molecule.rmsd.format() )

# Get the closestToMean models, superpose, export to PDB file
closestToMean = NTlist()
for p in projects:
    cl = p.molecule.rmsd.closestToMean
    closestToMean.append( p.molecule.ensemble[cl] )
fitted = closestToMean.zap('fitCoordinates')
for m in closestToMean[1:]:
    r = m.superpose(closestToMean[0])
    #print '>', r
# Export
for p in projects:
   p.molecule.toPDBfile( projects.path(p.name+'.pdb'), model=p.molecule.rmsd.closestToMean)

exit

# Positional global RMSDs
rmsds = cp.calcRmsds( projects, ranges=projects.ranges )
cp.printRmsds('  Pairwise positional RMSDs residues '+projects.ranges, rmsds, fp )

# Pih-Psi global RMSDs
rmsds2 = cp.calcPhiPsiRmsds( projects, ranges=projects.ranges )
cp.printRmsds('  Relative pairwise Phi-Psi RMSDs residues '+projects.ranges, rmsds2, fp )

cp.printOverallScores( projects, fp )
cp.printRestraintScores( projects, fp )

#cp.test( projects, fp )

# yasara macros
cp.loadPDBmacro( projects )
cp.colorPDBmacro( projects )
cp.ROGmacro( projects )
cp.QshiftMacro(projects)
#cp.colorPhiPsiMacro( projects )

if options.outFile:
    fp.close()

cp.copyFiles2Project( projects )
