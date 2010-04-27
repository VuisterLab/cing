from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTlistOfLists
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTvector
from cing.Libs.NTutils import fprintf #@UnusedImport
from cing.Libs.NTutils import printf
from cing.Libs.NTutils import sprintf
from cing.core.classes import Project
from cing.core.constants import INTERNAL
import math


"""
Routines to compare different Project instances
"""

class Projects( NTdict ):

    def __init__(self, name, **kwds):

        NTdict.__init__(self, __CLASS__='Projects', **kwds)
        self.name = name
        self.entries = NTlist()
    #end def

    def append(self, project ):
        if not project:
            return
        self.entries.append(project)
        self[project.name] = project
    #end

    def open(self, path, status='old'):
        """
        Open a project and append
        return project or None on error
        """
        project = Project.open(path=path, status=status)
        if not project:
            NTerror('Projects.open: failed opening "%s"', path)
            return None
        self.append( project )
        return project
    #end def

    def format(self):
        return sprintf("""------------ Projects %s ------------
entries: %s
""", self.name, self.entries.zap('name').format('%r ') )
#end class

class CircularVector( NTvector ):
    """
    Circular Distance vector class
    """
    def distanceSquared( self, other, period=360.0 ):
        l = len(self)
        if l != len(other):
            return None

        d = 0.0
        for i in range(l):
            delta = self[i]-other[i]
            fdelta = math.fabs( delta )

            if math.fabs(delta+period) < fdelta:
                d += (delta+period)*(delta+period)
            elif math.fabs(delta-period) < fdelta:
                d += (delta-period)*(delta-period)
            else:
                d += (delta)*(delta)
            #end if
        #end for
        return d
    #end def

    def distance( self, other, period=360.0 ):
        return math.sqrt( self.distanceSquared( other, period ) )
    #end def
#end class

class PhiPsiModelList( NTlist ):
    """
    Class to contain phi,psi values per model as CircularVector instances
    """

    def __init__(self, name, index ):
        NTlist.__init__(self)
        self.name = name
        self.index = index
    #end def

    def append( self, phi, psi ):
        c = CircularVector( phi, psi )
        NTlist.append(self, c)
    #end def

    def calculateRMSD( self, other ):
        l = len(self)
        if l != len(other) or l==0:
            return -1.0

        rmsd = 0.0
        for i in range(l):
            rmsd += self[i].distanceSquared(other[i], period=360.0)
            #print '>',i, self[i].residue, other[i].residue, rmsd
        return math.sqrt( rmsd/l )
    #end def

    def __str__(self):
        return sprintf('<PhiPsiModelList %s (%d)>', self.name, len(self))
    #end def
#end class

class PhiPsiLists( NTlist ):
    """
    Class to contain modelCount PhiPsiModelList instances
    """

    def __init__(self, molecule, residueList):
        NTlist.__init__( self )
        self.molecule     = molecule

        for i in range(0,molecule.modelCount):
            mName = sprintf('%s_model_%d', molecule.name, i)
            m = PhiPsiModelList(mName, i )
            self.append( m )
        #end for

        # Assemble the phi,psi of the models from residueList
        for res in residueList:
            if res and res.has_key('PHI') and res.has_key('PSI'):
                for i in range(0,molecule.modelCount):
                    #print '>>', res, i,molecule.modelCount,len(res.PHI),len(res.PSI)
                    self[i].append(res.PHI[i],res.PSI[i])
                    self[i].last().residue = res
                #end for
            #end if
        #end for
    #end def

    def __str__(self):
        return sprintf('<PhiPsiLists (%d)>', len(self))
    #end def
#end class


def calculatePairWisePhiPsiRmsd( mol1, mol2, ranges='auto' ):
    """
    Calculate a pairwise angular Phi,Psi rmsd between the models of mol1 and mol2
    return result NTlistOfLists, pairwise1, pairwise2, pairwise12 tuple
    """

    fitResidues1 = mol1.getResiduesFromRanges(ranges)
    models1 = PhiPsiLists( mol1, fitResidues1 )

    fitResidues2 = mol2.getResiduesFromRanges(ranges)
    models2 = PhiPsiLists( mol2, fitResidues2 )

    l1 = len(models1)
    l2 = len(models2)

    models = models1 + models2

    result = NTlistOfLists(len(models), len(models), 0.0)

    #NTmessage( '==> Calculating dihedral pairwise rmsds' )

    for i in range(len(models)):
        for j in range(i+1, len(models)):
            #print '>>', i,j
            r = models[i].calculateRMSD( models[j] )
            if r == None:
                NTerror('calculatePairWisePhiPsiRmsd: error for %s and %s', models[i], model[j]) #@UndefinedVariable for model
            else:
                result[i][j] = r
                result[j][i] = r
        #end for
    #end for

    pairwise1 = NTlist()
    for i in range(l1):
        for j in range(i+1, l1):
            pairwise1.append(result[i][j])
#            print '1>', i,j

    pairwise2 = NTlist()
    for i in range(l1, l1+l2):
        for j in range(i+1, l1+l2):
            pairwise2.append(result[i][j])
#            print '2>', i,j

    pairwise12 = NTlist()
    for i in range(l1):
        for j in range(l1, l1+l2):
            pairwise12.append(result[i][j])

#            print '12>', i,j
#    print len(pairwise1), len(pairwise2), len(pairwise12)
    return result, pairwise1.average2(fmt='%6.2f +- %5.2f'),pairwise2.average2(fmt='%6.2f +- %5.2f'),pairwise12.average2(fmt='%6.2f +- %5.2f')
#end def


def calculatePairWiseRmsd( mol1, mol2, ranges=None ):
    """Calculate pairwise rmsd between mol1 and mol2
       Optionally use ranges for the fitting
    """

    #Use ranges routines to define fitAtoms ed
    fitResidues1 = mol1.getResiduesFromRanges(ranges)
    mol1.selectFitAtoms( fitResidues1, backboneOnly=True, includeProtons = False )
    fitResidues2 = mol2.getResiduesFromRanges(ranges)
    mol2.selectFitAtoms( fitResidues2, backboneOnly=True, includeProtons = False )
#    mol2.superpose( ranges )

    l1 = len(mol1.ensemble)
    l2 = len(mol2.ensemble)

    models = mol1.ensemble + mol2.ensemble

    result = NTlistOfLists(len(models), len(models), 0.0)

    NTmessage('==> Calculating pairwise rmsds')

    for i in range(len(models)):
        for j in range(i+1, len(models)):
            result[i][j] = models[i].superpose( models[j] )
            result[j][i] = result[i][j]
        #end for
    #end for

    pairwise1 = NTlist()
    for i in range(l1):
        for j in range(i+1, l1):
            pairwise1.append(result[i][j])
#            print '1>', i,j

    pairwise2 = NTlist()
    for i in range(l1, l1+l2):
        for j in range(i+1, l1+l2):
            pairwise2.append(result[i][j])
#            print '2>', i,j

    pairwise12 = NTlist()
    for i in range(l1):
        for j in range(l1, l1+l2):
            pairwise12.append(result[i][j])

#            print '12>', i,j
#    print len(pairwise1), len(pairwise2), len(pairwise12)
    return result, pairwise1.average2(fmt='%6.2f +- %5.2f'),pairwise2.average2(fmt='%6.2f +- %5.2f'),pairwise12.average2(fmt='%6.2f +- %5.2f')
#end def


def calcPhiPsiRmsds( projects, ranges='auto', relative = True ):

    l = len(projects)

    rmsds = NTlistOfLists( l, l )
    for i in range(l):
        for j in range(i+1,l):
            #print projects[i].group, projects[j].group
            _r, pw_i, pw_j, pw_ij = calculatePairWisePhiPsiRmsd( projects[i].molecule, projects[j].molecule, ranges = ranges)
            if relative:
                rmsds[i][i] = pw_i/(pw_i*pw_i).sqrt()
                rmsds[j][j] = pw_j/(pw_j*pw_j).sqrt()
                rmsds[i][j] = pw_ij/(pw_i*pw_j).sqrt()
                rmsds[j][i] = rmsds[i][j]
            else:
                rmsds[i][i] = pw_i
                rmsds[j][j] = pw_j
                rmsds[i][j] = pw_ij
                rmsds[j][i] = rmsds[i][j]
            #end if
            rmsds[i].group = projects[i].group
            rmsds[j].group = projects[j].group
            #print pw_i, pw_j, pw_ij
        #end for
    #end for
    return rmsds
#end def

def calcRmsds( projects, ranges='auto' ):

    l = len(projects)

    rmsds = NTlistOfLists( l, l )
    for i in range(l):
        for j in range(i+1,l):
            print projects[i].group, projects[j].group
            _r, pw_i, pw_j, pw_ij = calculatePairWiseRmsd( projects[i].molecule, projects[j].molecule, ranges = ranges)
            rmsds[i][i] = pw_i
            rmsds[j][j] = pw_j
            rmsds[i][j] = pw_ij
            rmsds[j][i] = pw_ij
            rmsds[i].group = projects[i].group
            rmsds[j].group = projects[j].group
            #print pw_i, pw_j, pw_ij
        #end for
    #end for
    return rmsds
#end def

def printRmsds( title, rmsds ):

    l = len(rmsds)
    print '-'*20*(l+1)
    print title
    print '-'*20*(l+1)
    printf('%-20s%s\n','', rmsds.zap('group').format('  %-16s  '))
    for row in rmsds:
        printf('%-20s%s\n',  row.group, row.format('%-18s  '))
#end def

def printOverallScores( projects ):
    # Overall scores

    l = len(projects)
    if l == 0:
        return

    for p in projects:
       p.cingSummary = p.getCingSummaryDict()

    print '-'*20*(l+1)
    print '    Overall scores', projects[0].target
    print '-'*20*(l+1)
    printf('%-20s%s\n\n', 'Parameter', projects.zap('group').format('%-20s'))

    # CING scores
    for key in ['CING_red', 'CING_orange', 'CING_green']:
        printf('%-20s', key)
        for p in projects:
            printf('%-20s', p.cingSummary[key])
        printf('\n')
    print

    # Procheck scores
    for key in ['PC_core','PC_allowed','PC_generous','PC_disallowed','PC_gf']:
        printf('%-20s', key)
        for p in projects:
            printf('%-20s', p.cingSummary[key])
        printf('\n')
    print

    # Whatif scores
    for checkId in projects[0].molecule.runWhatif.summaryCheckIdList:
        key = 'WI_'+projects[0].molecule.runWhatif.cingCheckId(checkId)
        printf('%-20s', key)
        for p in projects:
            printf('%-20s', p.cingSummary[key])
        printf('\n')
    print ''
#end def

def printRestraintScores( projects ):

    l = len(projects)
    if l == 0:
        return

#    print '-'*20*(l+1)
#    print ' Restraints target', projects[0].target
#    print '-'*20*(l+1)
#    print

    hlen=40

    for p in projects:
        header = sprintf('%s project %-20s %s', '-'*hlen, p.name, '-'*hlen)
        print header

        if len(p.dihedrals)+len(p.distances) == 0:
            print "  No restraints"
            print '-'*len(header)
            print
            continue


        printf(    '%-25s %5s %5s %5s %5s %5s %5s   %-7s  %4s %4s %4s %4s    rmsd\n',
               'DistanceRestraintLists', 'count', 'intra', 'seq', 'med', 'long', 'amb', 'ROG','low','>0.1','>0.3','>0.5'
               )

        for r in p.distances:
            printf('  %-23s %5d %5d %5d %5d %5d %5d   %-7s  %4d %4d %4d %4d    %5.3f +- %5.3f\n',
                    r.name,
                    len(r), len(r.intraResidual), len(r.sequential), len(r.mediumRange), len(r.longRange), len(r.ambigious),
                    r.rogScore,
                    r.violCountLower, r.violCount1, r.violCount3, r.violCount5,
                    r.rmsdAv, r.rmsdSd
                   )
        print
        printf(    '%-25s %5s %5s %5s %5s %5s %5s   %-7s  %4s %4s %4s %4s    rmsd\n',
               'DihedralRestraintsLists', 'count', '','','','','', 'ROG','','>1','>3','>5',
               )
        for r in p.dihedrals:
            printf('  %-23s %5s %5s %5s %5s %5s %5s   %-7s  %4s %4d %4d %4d    %5.3f +- %5.3f\n',
                    r.name,
                    len(r), '.', '.', '.', '.', '.',
                    r.rogScore, '.',
                    r.violCount1, r.violCount3, r.violCount5,
                    r.rmsdAv, r.rmsdSd
                   )
        print '-'*len(header)
        print
    #end for
#end def

def printScore( name, rogScore ):
    clist = rogScore.colorCommentList.zap(1)
    if len(clist) == 0: clist.append('---')
    printf('%-20s%-10s %s\n', name, rogScore, clist[0])
    for c in clist[1:]:
        printf('%-20s%-10s %s\n', '', '', c)
#end def

def printResidueScores( projects ):

    l = len(projects)

    print '-'*20*(l+1)
    print '    Residues'
    print '-'*20*(l+1)
    p0 = projects[0]
    for res in p0.molecule.allResidues():
        printf('%s %s %s\n',  '-'*5, res, '-'*5 )
#        printf('%-20s%-10s %s\n', p0.name, res.rogScore, res.rogScore.colorCommentList.zap(1).format())
        printScore( p0.name, res.rogScore )
        # find the corresponding residues
        for p in projects[1:]:
            nameTuple = (p.molecule.name, res.chain.name, res.resNum, None, None, None, INTERNAL)
            res2 = p.decodeNameTuple( nameTuple )
            if res2:
                #printf('%-20s%-10s %s\n', p.name, res2.rogScore, res2.rogScore.colorCommentList.zap(1).format())
                printScore( p.name, res2.rogScore )
            else:
                printf('%-20s%-10s\n', p.name, 'Not found')
            #end if
        #end for
        print
    #end for
#end def

def test( projects, ranges ):
    # A hack to get residue specifc results
    selectedResidues = projects[0].molecule.getResiduesFromRanges('all')
    for res in selectedResidues:
        rmsds3 = calcPhiPsiRmsds( projects, ranges=[res.resNum] )
        printf('%-20s  %s  %s  %s \n',res, rmsds3[0][0], rmsds3[1][1], rmsds3[0][1]
              )







