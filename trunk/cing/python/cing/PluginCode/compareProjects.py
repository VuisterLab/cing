from cing import Project
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import copydir
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Ensemble
from numpy import linalg as LA
import numpy as np

"""
Routines to compare different Project instances
"""

class Projects( NTtree ):
    """
    Class to store multiple projects
    Bit dirty as We use the NTtree class, but append Project instances (NTdict-derived) as children
    Emulate list like behavior by adding append method, 'id' and refs in dictionary: i.e. projects[0] gives first entry
    """

    def __init__(self, name, ranges=None, root='.', **kwds):

        NTtree.__init__(self, __CLASS__='Projects', name=name, ranges=ranges, root=root, **kwds)
        self.entries = self._children
        self.next_id = 0
        self.moleculeMap = None
        self.rmsds = None    # pairwise rmsd comparisons
        self.mkdir()
    #end def

    def append(self, project ):
        if not project:
            return
        #self.entries.append(project)
        self._addChild(project)
        project.id = self.next_id
        self.next_id += 1

        # add references
        self[project.id] = project
        self[project.name] = project
    #end

    def open(self, path, status='old'):
        """
        Open a project and append
        return project or None on error
        """
        project = Project.open( path, status=status)
        if not project:
            NTerror('Projects.open: aborting')
            sys.exit(1)

        self.append( project )
        return project
    #end def

    def _mapIt(self, p1, objects, p2):

        for c1 in objects:
            # find the corresponding object in p2
            ctuple1 = c1.nameTuple()
            ctuple2 = list(ctuple1)
            ctuple2[0] = p2.molecule.name
            ctuple2 = tuple(ctuple2)
            c2 = p2.decodeNameTuple(ctuple2)
            if c2==None:
                NTerror('Projects._mapIt: error mapping %s to %s (derived from %s)', ctuple2, p2, p1)

            self.moleculeMap.setdefault(c1, NTdict())
            self.moleculeMap[c1][(p1.name,p1.molecule.name)] = c1
            self.moleculeMap[c1][(p2.name,p2.molecule.name)] = c2
            if c2 != None:
                self.moleculeMap.setdefault(c2, NTdict())
                self.moleculeMap[c2][(p1.name,p1.molecule.name)] = c1
                self.moleculeMap[c2][(p2.name,p2.molecule.name)] = c2
        #end for
    #end def

    def mapMolecules(self):
        """
        Make maps of chains and residues, between projects

        """

        self.moleculeMap = None
        if len(self) == 0:
            return
        self.moleculeMap = NTdict()
        for p1 in self.entries:
            for p2 in self.entries:
                self._mapIt( p1, p1.molecule.allChains(), p2)
                self._mapIt( p1, p1.molecule.allResidues(), p2)
            #end for
        #end for
    #end def

    def path(self, *args):
        """
        Return a path relative to self.root/projects.name
        """
        path = os.path.join(self.root, self.name, *args)
        return path

    def mkdir(self, *args):
        """Make a path relative a root of projects.name
           Check for presence.
           Return the result
        """
        path = self.path(*args)
        if not os.path.exists(path):
#            NTdebug( "project.mkdir: %s" % dir )
            os.makedirs(path)
        return path
    #end def


    def format(self):
        header = sprintf('------------ Projects %s ------------', self.name)
        footer = '-'*len(header)
        return sprintf("""%s
entries: %s
ranges:  %s
%s""", header, self.entries.zap('name').format('%r '), self.ranges, footer )
    #end def

    def __len__(self):
        return len(self.entries)
    #end def
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

    def append( self, *dihedrals ):
        c = CircularVector( *dihedrals )
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
#            if res and res.has_key('PHI') and res.has_key('PSI'):
            if res and res.has_key('PHI') and res.has_key('PSI') and res.has_key('Cb4N') and res.has_key('Cb4C'):
                for i in range(0,molecule.modelCount):
                    #print '>>', res, i,molecule.modelCount,len(res.PHI),len(res.PSI),len(res.Cb4N),len(res.Cb4C)
#                    self[i].append(res.PHI[i],res.PSI[i])
                    self[i].append(res.PHI[i],res.PSI[i],res.Cb4N[i],res.Cb4C[i])
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

    #print '>', ranges, models1, models2

    l1 = len(models1)
    l2 = len(models2)
    if l1 == 0 or len(models1[0]) == 0 or l2 == 0 or len(models2[0]) == 0:
        NTdebug(">calculatePairWisePhiPsiRmsd> returning None, %s %s %s", l1, l2, ranges)
        return None, None, None, None

    models = models1 + models2

    result = NTlistOfLists(len(models), len(models), 0.0)

    #NTmessage( '==> Calculating dihedral pairwise rmsds' )

    for i in range(len(models)):
        for j in range(i+1, len(models)):
            #print '>>', i,j
            r = models[i].calculateRMSD( models[j] )
            if r == None:
                NTdebug('calculatePairWisePhiPsiRmsd: error for %s and %s', models[i], models[j])
                return None, None, None, None
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


def calcPhiPsiRmsds( projects, ranges='auto', relative = True ):

    l = len(projects)

    rmsds = NTlistOfLists( l, l, NTvalue(NaN, NaN, fmt='%6.2f +- %5.2f' ) )
    for i in range(l):
        for j in range(i+1,l):
            #print projects[i].group, projects[j].group
            rmsds[i].group = projects[i].group
            rmsds[j].group = projects[j].group
            r, pw_i, pw_j, pw_ij = calculatePairWisePhiPsiRmsd( projects[i].molecule, projects[j].molecule, ranges = ranges)
            #print pw_i, pw_j, pw_ij
            if r != None:
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
            #end if
        #end for
    #end for
    projects.PhiPsiRmsds = rmsds
    return rmsds
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

    if (   l1 == 0 or len(mol1.ensemble[0].fitCoordinates) == 0
        or l2 == 0 or len(mol2.ensemble[0].fitCoordinates) == 0
        or len(mol1.ensemble[0].fitCoordinates) != len(mol2.ensemble[0].fitCoordinates)
    ):
        NTdebug( ">calculatePairWiseRmsd> returning None, %s %s %s" , l1, l2, ranges)
        return None, None, None, None


    models = mol1.ensemble + mol2.ensemble

    result = NTlistOfLists(len(models), len(models), 0.0)

    NTmessage('==> Calculating pairwise rmsds %s %s', mol1, mol2)

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


def calcRmsds( projects, ranges='auto' ):

    l = len(projects)

    rmsds = NTlistOfLists( l, l, NTvalue(NaN, NaN, fmt='%6.2f +- %5.2f' ) )
    for i in range(l):
        for j in range(i+1,l):
            #print projects[i].group, projects[j].group
            rmsds[i].group = projects[i].group
            rmsds[j].group = projects[j].group
            r, pw_i, pw_j, pw_ij = calculatePairWiseRmsd( projects[i].molecule, projects[j].molecule, ranges = ranges)
            #print pw_i, pw_j, pw_ij
            if r != None:
                rmsds[i][i] = pw_i
                rmsds[j][j] = pw_j
                rmsds[i][j] = pw_ij
                rmsds[j][i] = pw_ij
                projects[i].summaryDict['pairwiseRmsd'] = rmsds[i][i]
                projects[j].summaryDict['pairwiseRmsd'] = rmsds[j][j]
                projects[i].summaryDict['pairwiseRmsdToFirst'] = rmsds[0][i]
                projects[j].summaryDict['pairwiseRmsdToFirst'] = rmsds[0][j]
#        p.summaryDict['pairwiseRmsdToFirst'] = pairwiseRmsdToFirsts[i]
        #end for
    #end for
    projects.rmsds = rmsds
    return rmsds
#end def


def printTitle(title, length, stream=sys.stdout ):
    line = '-'*length
    fprintf( stream, '%s\n  %s\n%s\n', line, title, line )

def printRmsds( title, rmsds, stream=sys.stdout ):

    l = len(rmsds)
    printTitle(title, 20*(l+1), stream)
    fprintf( stream, '%-20s%s\n','', rmsds.zap('group').format('  %-16s  '))
    for row in rmsds:
        fprintf( stream, '%-20s%s\n',  row.group, row.format('%-18s  '))
    fprintf( stream, '%s\n', '_'*20*(l+1))
#end def


def printOverallScores( projects, stream = sys.stdout ):
    # Overall scores

    l = len(projects)
    if l == 0:
        return

    printTitle('Overall scores target '+projects.name, 20*(l+1), stream)
#    line = '-'*20*(l+1)
#   fprintf( stream, '%s\n    Overall scores %s\n%s\n\n', line, projects.name, line )
    fprintf( stream, '%-20s%s\n\n', 'Parameter', projects.entries.zap('group').format('%-20s'))

    # rmsds
    fprintf( stream, '%-20s%s\n','rmsdToMean', projects.entries.zap('summaryDict','rmsdToMean_backboneAverage').format('  %-18s') )
    fprintf( stream, '%-20s%s\n','pairwiseRmsd', projects.entries.zap('summaryDict','pairwiseRmsd').format('%-16s    ') )
    fprintf( stream, '%-20s%s\n\n','pairwiseRmsdTo_'+projects.entries[0].group, projects.entries.zap('summaryDict','pairwiseRmsdToFirst').format('%-18s  ') )

    # CING scores
    for key in ['CING_red', 'CING_orange', 'CING_green']:
        fprintf( stream, '%-20s%s\n',key, projects.entries.zap('summaryDict',key).format('%-18s  ') )
    fprintf( stream, '\n')

    # Procheck scores
    for key in ['PC_core','PC_allowed','PC_generous','PC_disallowed','PC_gf']:
        fprintf( stream, '%-20s%s\n',key, projects.entries.zap('summaryDict',key).format('%-18s  ') )
    fprintf( stream, '\n')

    # Whatif scores
    for checkId in projects[0].molecule.runWhatif.summaryCheckIdList:
        key = 'WI_'+projects[0].molecule.runWhatif.cingCheckId(checkId)
        fprintf( stream, '%-20s%s\n',key, projects.entries.zap('summaryDict',key).format('%-18s  ') )
    fprintf( stream, '\n')
#end def

def saveCingSummaries( projects ):
    """Save summaryDict's as xml files"""
    for p in projects:
        path = projects.path(p.name+'.summaryDict.xml')
        #print path
        p.summaryDict.save(path)
#end def

def printRestraintScores( projects, stream=sys.stdout ):

    l = len(projects)
    if l == 0:
        return

#    print '-'*20*(l+1)
#    print ' Restraints target', projects[0].target
#    print '-'*20*(l+1)
#    print

    hlen=40

    printTitle('Restraint scores target '+projects.name, 110, stream)

    for p in projects:
        header = sprintf('%s project %-20s %s', '-'*hlen, p.name, '-'*hlen)
        fprintf( stream,'%s\n', header)

        if len(p.dihedrals)+len(p.distances) == 0:
            fprintf( stream,'%s\n%s\n\n',   "  No restraints",'-'*len(header))
            continue


        if len( p.distances ) > 0:
            fprintf( stream,    '%-25s %5s %5s %5s %5s %5s %5s   %-7s  %4s %4s %4s %4s    rmsd\n',
                   'DistanceRestraintLists', 'count', 'intra', 'seq', 'med', 'long', 'amb', 'ROG','low','>0.1','>0.3','>0.5'
                   )

            for r in p.distances:
                fprintf( stream,'  %-23s %5d %5d %5d %5d %5d %5d   %-7s  %4d %4d %4d %4d    %5.3f +- %5.3f\n',
                        r.name,
                        len(r), len(r.intraResidual), len(r.sequential), len(r.mediumRange), len(r.longRange), len(r.ambigious),
                        r.rogScore,
                        r.violCountLower, r.violCount1, r.violCount3, r.violCount5,
                        r.rmsdAv, r.rmsdSd
                       )
            fprintf(stream, "\n")
        #end if
        if len(p.dihedrals) > 0:
            fprintf( stream,    '%-25s %5s %5s %5s %5s %5s %5s   %-7s  %4s %4s %4s %4s    rmsd\n',
                   'DihedralRestraintsLists', 'count', '','','','','', 'ROG','','>1','>3','>5',
                   )
            for r in p.dihedrals:
                fprintf( stream,'  %-23s %5s %5s %5s %5s %5s %5s   %-7s  %4s %4d %4d %4d    %5.3f +- %5.3f\n',
                        r.name,
                        len(r), '.', '.', '.', '.', '.',
                        r.rogScore, '.',
                        r.violCount1, r.violCount3, r.violCount5,
                        r.rmsdAv, r.rmsdSd
                       )
        #end if
        fprintf( stream,'%s\n\n',  '-'*len(header))
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

def test( projects, stream=sys.stdout ):
    # A hack to get residue specifc results
    selectedResidues = projects[0].molecule.getResiduesFromRanges('all')

    for res in selectedResidues:
        rmsds3 = calcPhiPsiRmsds( projects, ranges=[res.resNum] )

        printRmsds('Relative Phi-Psi '+res.name, rmsds3, stream )
        res.phipsiRmsds = rmsds3
        for p in projects.entries[1:]:
            val = getDeepByKeysOrAttributes(projects, 'moleculeMap', res, p.name)
            if val == None:
                NTerror('Setting phipsiRmsds residue %s project %s (mapping not found)', res.name, p)
                continue
            val.phipsiRmsds = rmsds3
        #end for
    #end for
#end def


def test2(projects):
    ensemble = Ensemble()
    for p in projects:
        closest = p.molecule.rmsd.closestToMean
        ensemble.append(p.molecule.ensemble[closest])
    #end for
    return ensemble
#end def


def runningRmsds( projects ):
    selectedResidues = projects[0].molecule.getResiduesFromRanges('all')
    for res in selectedResidues:
        prev = res.sibling(-1)
        next = res.sibling(1)
        if prev and next:
            res.runngRmsds = calcRmsds( projects, [prev,res,next])
    #end for
#end def

def colorPhiPsiMacro( projects, minValue=2.0, maxValue=4.0 ):

    fp = open( projects.path('phipsi.mcr' ), 'w')

    fprintf(fp, 'Console off\n')
    fprintf(fp, 'ColorPar Property Min,blue, %7.3f\n', minValue)
    fprintf(fp, 'ColorPar Property Max,red,  %7.3f\n', maxValue)
    for p in projects.entries[1:]:
        fprintf(fp, 'ColorRes object %d, Gray\n', p.id+1)
        fprintf(fp, 'PropRes object %d, -999\n', p.id+1)
        for res in p.molecule.allResidues():
            if res.has_key('phipsiRmsds'):
                if not isNaN(res.phipsiRmsds[0][p.id].value):
                    fprintf( fp, 'PropRes object %d residue %d, %7.3f\n', p.id+1, res.resNum, res.phipsiRmsds[0][p.id].value)
            #end if
        #end for
        fprintf(fp, 'ColorObject %d, property\n', p.id+1)

    #end for
    fprintf(fp, 'Console off\n')
    fp.close()
#end def

def loadPDBmacro( projects ):


    fp = open( projects.path('loadPDB.mcr' ), 'w')

    fprintf(fp, 'Console off\n')
    for p in projects.entries:
        #fprintf(fp, 'loadPDB %s\n', os.path.abspath(projects.path(p.name+'.pdb')))
        fprintf(fp, 'loadPDB %s,Center=No\n', projects.path(p.name+'.pdb'))
    #end for
    fprintf(fp, 'Style Ribbon\n')
    fprintf(fp, 'macro %s\n', projects.path('colorPDB.mcr'))
    fprintf(fp, 'Console on\n')
    fp.close()
#end def

def colorPDBmacro( projects ):


    fp = open( projects.path('colorPDB.mcr' ), 'w')

    fprintf(fp, 'Console off\n')
    for p in projects.entries:
        #fprintf(fp, 'loadPDB %s\n', os.path.abspath(projects.path(p.name+'.pdb')))
        selectedResidues = p.molecule.getResiduesFromRanges(projects.ranges)
        #print '>>', selectedResidues
        if p.has_key('color'):
            fprintf(fp, 'ColorObject %d, %d\n', p.id+1, p.color)
            for res in p.molecule.allResidues():
                #print res,
                if res in selectedResidues:
                    pass
                else:
                    fprintf(fp, 'ColorRes object %d residue %d, grey\n', p.id+1, res.resNum)
                #end if
            #end for
        #end if
    #end for
    fprintf(fp, 'Console on\n')
    fp.close()
#end def

def ROGmacro( projects ):

    stream = open( projects.path('ROG.mcr' ), 'w')

    fprintf(stream, 'Console off\n')
    fprintf(stream, 'ColorRes  All, Gray\n')

    YasaraColorDict = dict(green = 240, orange = 150, red = 120)

    for p in projects:
        selectedResidues = p.molecule.getResiduesFromRanges(projects.ranges)
        for res in p.molecule.allResidues():
            if res in selectedResidues:
                pass
            else:
                cmd = fprintf(stream, 'ColorRes object %d residue %d, %s\n', p.id+1, res.resNum, YasaraColorDict[res.rogScore.colorLabel]) #@UnusedVariable
    #end for
    fprintf(stream, 'Console on\n')
#end def

def mkYasaraByResidueMacro(projects, keys,
                            minValue = 0.0, maxValue = 1.0, reverseColorScheme = False,
                            path = None
                           ):

#    NTdebug('mkYasaraByResidueMacro: keys: %s, minValue: %s maxValue: %s', keys, minValue, maxValue)

    if path==None:
        stream = sys.stdout
    else:
        stream = open( path, 'w')
    #end if

    fprintf(stream, 'Console off\n')
    fprintf(stream, 'ColorRes All, Gray\n')
    fprintf(stream, 'PropRes All, -999\n')
    if reverseColorScheme:
        fprintf(stream, 'ColorPar Property Min,red,%f\n', minValue)
        fprintf(stream, 'ColorPar Property Max,blue,%f\n', maxValue)
    else:
        fprintf(stream, 'ColorPar Property Min,blue,%f\n', minValue)
        fprintf(stream, 'ColorPar Property Max,red,%f\n', maxValue)

    for p in projects:
        for res in p.molecule.allResidues():
            value = getDeepByKeysOrAttributes(res, *keys)
    #        if res.has_key(property) and res[property] != None and not isNaN(res[property]):
            if value != None and not isNaN(value):
                fprintf(stream, 'PropRes object %d Residue %d, %.4f\n', p.id+1, res.resNum, value)
        #end for

    fprintf(stream, 'ColorAll Property\n')
    fprintf(stream, 'Console on\n')

    if path:
        stream.close()
#end def

QshiftMinValue = 0.0
QshiftMaxValue = 0.05
QshiftReverseColorScheme = False

PCgFactorMinValue = - 3.0
PCgFactorMaxValue = 1.0
PCgFactorReverseColorScheme = True

def QshiftMacro( projects ):
    mkYasaraByResidueMacro(projects, ['Qshift', 'backbone'],
                           minValue = QshiftMinValue, maxValue = QshiftMaxValue,
                           reverseColorScheme = QshiftReverseColorScheme,
                           path = projects.path('Qshift.mcr')
                          )


def copyFiles2Project( projects ):
    """Copy the file in the projects directory to each individual project
    """
    for p in projects:
        source = projects.path('*')
        destination = p.validationPath('Cing','CASD-NMR')
        #print '>>', source, destination
        copydir(source,destination)
#end def

def generatePDBfiles( projects ):

    # Get the closestToMean models, superpose, export to PDB file
    closestToMean = NTlist()
    for p in projects.entries[0:3]:
        cl = p.molecule.rmsd.closestToMean
        #print p.molecule.ensemble[cl].format()
        closestToMean.append( p.molecule.ensemble[cl] )

    for m in closestToMean[1:]:
        #print m.format()
        r = m.superpose(closestToMean[0]) #@UnusedVariable
        #print '>', m.format()
        #print '>', r
    # Export
    for p in projects:
        cl = p.molecule.rmsd.closestToMean
        #print 'saving model>', p.molecule.ensemble[cl].format()
        p.molecule.toPDBfile( projects.path(p.name+'.pdb'), model=cl)

    return closestToMean
#end def

def getRanges( projects, cutoff = 1.7 ):
    """
    Get the ranges from phi, phi order parameters using all members of projects
    As suggested by Aleandre in CASD-NMR meeting

    """
    resList1 = NTlist()
    resList2 = NTlist()
    for res in projects.entries[0].molecule.allResidues():
        phi = NTlist() # list for all phi values
        psi = NTlist() # list for all psi values
        #print '>>>', res
        if res.has_key('PHI') and res.has_key('PSI'):

            for p in projects:
                if projects.moleculeMap.has_key(res) and projects.moleculeMap[res].has_key((p.name, p.molecule.name)):
                    currentRes = projects.moleculeMap[res][(p.name, p.molecule.name)]
                    #print p,currentRes
                    if currentRes.has_key('PHI'):
                        phi.append(*currentRes['PHI'])
                    if currentRes.has_key('PSI'):
                        psi.append(*currentRes['PSI'])
                #end if
            #end for
            phi.cAverage()
            psi.cAverage()

            use1 = 0
            if (2.0 - res.PHI.cv - res.PSI.cv > cutoff): use1 = 1
            use2 = 0
            if (2.0 - phi.cv - psi.cv > cutoff): use2 = 1
            #printf('%-35s %-35s  %6.2f  %1d     %6.2f %6.2f   %6.2f  %1d     %2d\n',
            #       res.PHI, res.PSI, 2.0 - res.PHI.cv - res.PSI.cv, use1,
             #      phi.cv, psi.cv, 2.0 - phi.cv - psi.cv, use2, use1-use2
             #     )
            if use1:
                resList1.append(res.resNum)
            if use2:
                resList2.append(res.resNum)
        #end if
    #end for
    return list2asci(resList1), list2asci(resList2)
#end def


def radiusOfGiration( molecule, ranges=None, model=0 ):
    """
    Return radius of giration of model.
    Uses CA coordinates
    Following
    HAVEL and WUTHRICH. AN EVALUATION OF THE COMBINED USE OF NUCLEAR MAGNETIC-RESONANCE AND DISTANCE GEOMETRY
    FOR THE DETERMINATION OF PROTEIN CONFORMATIONS IN SOLUTION.
    Journal of Molecular Biology (1985) vol. 182 (2) pp. 281-294

    Algorithm: pag 284
    """

    if ranges==None:
        residues = molecule.allResidues()
    else:
        residues = molecule.getResiduesFromRanges(ranges)
    #end if

    xx  = 0.0
    yy  = 0.0
    zz  = 0.0
    xy  = 0.0
    xz  = 0.0
    yz  = 0.0
    n = 0
    for res in residues:
        if res.hasProperties('protein') and res.CA.hasCoordinates() and model < len(res.CA.coordinates):
            x = res.CA.coordinates[model].x
            y = res.CA.coordinates[model].y
            z = res.CA.coordinates[model].z
            xx  += x*x
            yy  += y*y
            zz  += z*z
            xy  += x*y
            xz  += x*z
            yz  += y*z
            n += 1
        #end if
    #end for

    a = np.array([
                  [yy+zz,      -xy,      -xz],
                  [  -xy,    xx+zz,      -yz],
                  [  -xz,      -xy,    xx+yy]
                 ])
    a = a*(3.0/n)

    w, v = LA.eig(a)
    print w,v
    return NTlist(*map(math.sqrt, w))
#end def







