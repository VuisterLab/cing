"""
Adds validation methods


Methods:

Version 0.48 will overhaul the routines in this file.    

----------------  Methods  ----------------


validate( verbose = True )  

checkForSaltbridges( toFile = False )


----------------  Attributes generated  ----------------


Molecule:
    rmsd: RmsdResult object containing postional rmsd values



Residue:
    rmsd: RmsdResult object containing postional rmsd values

    distanceRestraints: NTlist instance containing all distance restraints of this residue, sorted on violation count over 0.3A.

    saltbridges: NTlist instances of (potential) saltbridges

Atom: 
    validateAssignment: NTlist instance with potential warnings/errors concerning the assignment of this atom
    
    shiftx, shiftx.av, shiftx.sd: NTlist instance with shiftx predictions, average and sd                
"""
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import boxAttributes
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTlimit
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTsort
from cing.Libs.NTutils import NTstruct
from cing.Libs.NTutils import NTvalue
from cing.Libs.NTutils import NTvector
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import formatList
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import list2asci
from cing.Libs.NTutils import mprintf
from cing.Libs.NTutils import printError
from cing.Libs.NTutils import printf
from cing.Libs.NTutils import removedir
from cing.Libs.NTutils import sprintf
from cing.Libs.peirceTest import peirceTest
from cing.core.classes import HTMLfile
from cing.core.classes import htmlObjects
from cing.core.constants import COLOR_GREEN
from cing.core.constants import COLOR_ORANGE
from cing.core.constants import COLOR_RED
from cing.core.constants import NOSHIFT
from cing.core.constants import UNDEFINED_FLOAT
from cing.core.molecule import dots
from cing.core.parameters import htmlDirectories
from cing.core.parameters import moleculeDirectories
import cing
import math
import os
import sys


#def printm( fps, fmt, *args ):
#    """
#    Print to list of filepointers (fps) using format and args.
#    Skip element of fp if it is None
#    """
#    for fp in fps:
#        if fp != None:
#            fprintf( fp, fmt, *args )
#        #end if
#    #end for
##end def

def setupValidation( project, ranges=None ):
    """
    Run the initial validation calculations or programs
    """
    
    validateDihedrals( project, verbose=project.parameters.verbose() )
    
    validateModels( project, verbose=project.parameters.verbose() )

    project.predictWithShiftx( verbose=project.parameters.verbose() )
    project.validateAssignments( toFile=True, verbose=project.parameters.verbose() )
    
    project.checkForSaltbridges( toFile=True, verbose=project.parameters.verbose() )
    
    project.validateRestraints( toFile = True, verbose=project.parameters.verbose() )
    
    project.calculateRmsd( ranges=ranges, verbose = project.parameters.verbose() )
    
    project.procheck( ranges=ranges, verbose = project.parameters.verbose() )
    
    project.summary( verbose = project.parameters.verbose() )
#end def

def summary( project, verbose=True ):
    """
    Generate a summary
    """

    fps = []
    if verbose: fps.append( sys.stdout )
    fname = project.path(project.molecule.name, project.moleculeDirectories.analysis,'summary.txt')
    fp = open( fname, 'w' )
    printf( '==> summary, output to %s\n', fname)
    fps.append( fp )
    
    mprintf( fps, '%s\n', project.format() )
    
    if project.molecule:
        mprintf( fps, '%s\n', project.molecule.format() )
        if project.molecule.has_key('rmsd' ):
            mprintf( fps, '%s\n', project.molecule.rmsd.format() )
        #end if
        for drl in project.distances + project.dihedrals + project.rdcs:
            mprintf( fps, '%s\n', drl.format() )
        #end for
    #end if
    fp.close()
#end def


class RmsdResult( NTdict ):
    """Class to store rmsd results
    """
    def __init__(self, modelList, ranges, comment='' ):
        NTdict.__init__( self, 
                         __CLASS__       = 'RmsdResult',
                         backbone        = NTfill(0.0, len(modelList)),
                         backboneCount   = 0,
                         backboneAverage = NTvalue( 0.0, 0.0, fmt='%5.3f (+- %5.3f)' ),
                         heavyAtoms      = NTfill(0.0, len(modelList)),
                         heavyAtomsCount = 0,
                         heavyAtomsAverage = NTvalue( 0.0, 0.0, fmt='%5.3f (+- %5.3f)' ),
                         models          = modelList,
                         closestToMean   = 0,
                         ranges          = ranges,
                         comment         = comment
                       )
    #end def
    
    def _closest(self):
        """Internal routine to calculate the model closest to mean
        """
        c = zip(self.heavyAtoms, self.models)
        c.sort()
        self.closestToMean = c[0][1]
    #end def
    
    def _average(self):
        """Calculate the averages
        """
        self.backboneAverage.value, self.backboneAverage.error, dummy_n = self.backbone.average()
        self.heavyAtomsAverage.value, self.heavyAtomsAverage.error, dummy_n = self.heavyAtoms.average()
    #end def

    def __str__(self):
        return sprintf('<RmsdResult %s>', self.comment)
    
    def format(self):
        return sprintf('%s %s %s\n' +\
                       'backboneAverage:    %s\n'  +\
                       'heavyAtomsAverage:  %s\n'  +\
                       'models:             %s\n' +\
                       'backbone:          [%s]\n' +\
                       'heavyAtoms:        [%s]\n' +\
                       'closestToMean:      model %d',
                       dots, self, dots,
                       str(self.backboneAverage),
                       str(self.heavyAtomsAverage),
                       self.models.format('%5d '), 
                       self.backbone.format(fmt='%5.3f '), 
                       self.heavyAtoms.format(fmt='%5.3f '), 
                       self.closestToMean
                      )
    #end def
#end class


def calculateRmsd( project, ranges=None, models = None, verbose = True ):
    """
    Calculate the positional rmsd's. Store in rmsd attributes of molecule and residues
    return rmsd result of molecule, or None on error
    
    """

    if not project.molecule:
        NTerror('Error calculateRmsd: undefined molecule\n')
        return None
    #end if
    
    if project.molecule.modelCount == 0:
        NTerror('Error calculateRmsd: no coordinates for %s\n', project.molecule)
        return None
    #end if

    selectedResidues = project.molecule.ranges2list( ranges )
    selectedModels   = project.molecule.models2list( models )

    project.molecule.rmsd = RmsdResult( selectedModels, selectedResidues, comment='Residues ' + list2asci( selectedResidues.zap('resNum')) )
    for res in project.molecule.allResidues():
        res.rmsd = RmsdResult( selectedModels,  NTlist( res ), comment = res.name )
    #end for
    
    if verbose: NTmessage("==> Calculating rmsd's ")
    
    num = 0 # number of evaluated models (does not have to coincinde with model
            # since we may supply an external list
    for model in selectedModels:

        if verbose: 
            NTmessage(".")
            NTmessage.flush()
        #end if
        project.molecule.rmsd.backbone[num]   = 0.0
        project.molecule.rmsd.backboneCount   = 0
        project.molecule.rmsd.heavyAtoms[num] = 0.0
        project.molecule.rmsd.heavyAtomsCount = 0
                
        for res in project.molecule.allResidues():
            res.rmsd.backbone[num]   = 0.0
            res.rmsd.backboneCount   = 0
            res.rmsd.heavyAtoms[num] = 0.0
            res.rmsd.heavyAtomsCount = 0
            # calculate rmsd over backbone atms for this residue 
            for atm in res.allAtoms():
                d=None
                if atm.meanCoordinate:
                    d=0.0
                    for i in ['x','y','z']:
                        tmp = atm.coordinates[model][i]-atm.meanCoordinate[i]
                        d += tmp*tmp
                    #end for    
                #end if
                     
                # rmsd over backbone atms for this residue
                if atm.hasProperties('backbone','notproton'):
                    if (d==None):
                        NTerror('Error calculateRmsd: expected coordinates for atom %s\n', atm)
                    else:
                        res.rmsd.backbone[num] += d
                        res.rmsd.backboneCount += 1
                    #end if
                #endif
                
                # rmsd over all atms for this residue
                if atm.hasProperties('notproton'):
                    if (d==None):
                        NTerror('Error calculateRmsd: expected coordinates for atom %s\n', atm)
                    else:
                        res.rmsd.heavyAtoms[num] += d
                        res.rmsd.heavyAtomsCount += 1
                    #end if
                #endif
            #end for
            
            # sum for the rmsd of selected residues
            if (res in selectedResidues):
                project.molecule.rmsd.backbone[num]   += res.rmsd.backbone[num]
                project.molecule.rmsd.backboneCount   += res.rmsd.backboneCount
                project.molecule.rmsd.heavyAtoms[num] += res.rmsd.heavyAtoms[num]
                project.molecule.rmsd.heavyAtomsCount += res.rmsd.heavyAtomsCount
            #end if
                
            # calculate rmsd for the model of this residue
            res.rmsd.backbone[num]   = math.sqrt(res.rmsd.backbone[num]/max(res.rmsd.backboneCount,1))
            res.rmsd.heavyAtoms[num] = math.sqrt(res.rmsd.heavyAtoms[num]/max(res.rmsd.heavyAtomsCount,1))
        #end for
        
        # rmsd of selected residues for this model
        project.molecule.rmsd.backbone[num]   = math.sqrt(project.molecule.rmsd.backbone[num]/max(project.molecule.rmsd.backboneCount,1))
        project.molecule.rmsd.heavyAtoms[num] = math.sqrt(project.molecule.rmsd.heavyAtoms[num]/max(project.molecule.rmsd.heavyAtomsCount,1))
        
        # Increment the evaluated number of models 
        num += 1
    #end for

    # get the closest to mean models and averages
    for res in project.molecule.allResidues():
        res.rmsd._closest()
        res.rmsd._average()
    #end for
    project.molecule.rmsd._closest()
    project.molecule.rmsd._average()

    if verbose: 
        NTmessage(" done\n")
        NTmessage.flush()
    #end if
    
    return project.molecule.rmsd
#end def    


def validateRestraints( project, toFile = True, verbose=True ):
    """
    Calculate rmsd's and violation on restraints
    """

    fps = []
    if verbose: fps.append( sys.stdout )
    if toFile:
        #project.mkdir(project.directories.analysis, project.molecule.name)
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis,'restraints.txt')
        fp = open( fname, 'w' )
        printf( '==> validateRestraints, output to %s\n', fname)
        fps.append( fp )
    #end if
    
    mprintf( fps, '%s\n', project.format() )
    
    # distances and dihedrals
    for res in project.molecule.allResidues():
        res.distanceRestraints = NTlist()
        res.dihedralRestraints = NTlist()
    #end for
    
    # distances
    for drl in project.distances:
        drl.analyze()
        mprintf( fps, '%s\n', drl.format())
        drl.sort('violMax').reverse()
        mprintf( fps, '%s Sorted on Maximum Violations %s\n', dots, dots)
        mprintf( fps, '%s\n', formatList( drl[0:min(len(drl),30)] ) )
        
        drl.sort('violCount3').reverse()
        mprintf( fps, '%s Sorted on Violations > 0.3 A %s\n', dots, dots)
        mprintf( fps, '%s\n', formatList( drl[0:min(len(drl),30)] ) )
        
        # Sort restraints on a per-residue basis
        for restraint in drl:
            for atm1,atm2 in restraint.atomPairs:
                atm1.residue.distanceRestraints.add( restraint ) #AWSS
                atm2.residue.distanceRestraints.add( restraint ) #AWSS
            #end for
        #end for
    #end for   
    
    # dihedrals     
    for drl in project.dihedrals:
        drl.analyze()
        mprintf( fps, '%s\n', drl.format())
        drl.sort('violMax').reverse()
        mprintf( fps, '%s Sorted on Maximum Violations %s\n', dots, dots)
        mprintf( fps, '%s\n', formatList( drl[0:min(len(drl),30)] ) )
        
        drl.sort('violCount3').reverse()
        mprintf( fps, '%s Sorted on Violations > 3 degree %s\n', dots, dots)
        mprintf( fps, '%s\n', formatList( drl[0:min(len(drl),30)] ) )
        
        # sort the restraint on a per residue basis
        for restraint in drl:
            restraint.atoms[2].residue.dihedralRestraints.add( restraint ) #AWSS
        #end for
    #end for   

    # Process the per residue restraints data
    mprintf( fps, '%s Per residue scores %s\n', dots, dots )
    count = 0
    for res in project.molecule.allResidues():

        if (len(res.distanceRestraints) > 0):
        
            # Sort on violation count
            NTsort(res.distanceRestraints, 'violCount3', inplace=True )
            res.distanceRestraints.reverse()
        
            # Calculate rmsd of restraints per residue
            sumsq = 0.0
            n = 0
            for d in res.distanceRestraints:
                sumsq = d.violations.sumsq( sumsq )
                n += len(d.violations)
            #end for
            res.distanceRestraints.rmsd = math.sqrt(sumsq/n)
            res.distanceRestraints.violCount1 = res.distanceRestraints.zap('violCount1').sum()
            res.distanceRestraints.violCount3 = res.distanceRestraints.zap('violCount3').sum()
            res.distanceRestraints.violCount5 = res.distanceRestraints.zap('violCount5').sum()
        else:
            res.distanceRestraints.rmsd = 0.0
            res.distanceRestraints.violCount1 = 0
            res.distanceRestraints.violCount3 = 0
            res.distanceRestraints.violCount5 = 0
        #end if
        
        # print every 10 lines
        if (not count%30):
            mprintf(fps, '%-18s %15s  %15s   %s\n', '--- RESIDUE ---', '--- PHI ---', '--- PSI ---', '-- dist 0.1A 0.3A 0.5A   rmsd --')
        #end if
        if res.has_key('PHI'):
            phi = NTvalue( res.PHI.cav, res.PHI.cv, fmt='%7.1f %7.2f' )
        else:
            phi = NTvalue( '-', '-', fmt='%7s %7s' )
        #end if
        if res.has_key('PSI'):
            psi = NTvalue( res.PSI.cav, res.PSI.cv, fmt='%7.1f %7.2f' )
        else:
            psi = NTvalue( '-', '-', fmt='%7s %7s' )
        #end if
        try:
            mprintf( fps,    '%-18s %-15s  %-15s      %3d %4d %4d %4d  %6.3f\n',
                 res, phi, psi,
                 len(res.distanceRestraints), res.distanceRestraints.violCount1, res.distanceRestraints.violCount3, 
                 res.distanceRestraints.violCount5, res.distanceRestraints.rmsd              
                   )
        except:
            NTerror("No coordinates for residue %s\n", res)
        count += 1
    #end for
#end def

def checkForSaltbridges( project, cutoff = 5, toFile=False, verbose=True ):
    """ 
    Routine to analyze all potential saltbridges involving E,D,R,K and H residues. 
    Initiates an NTlist instances as saltbridges attribute for all residues. 
    
    Returns a NTlist with saltbridge summaries.
    
    Optionally print output to file in analysis directory of project.
    """
    
    if toFile:
        #project.mkdir(project.directories.analysis, project.molecule.name)
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis,'saltbridges.txt')
        fp = open( fname, 'w' )
        printf( '==> checkSaltbridges, output to %s\n', fname)
    else:
        fp = None
    #end if

    if toFile: fprintf( fp, '%s\n', project.molecule.format() )
    if verbose: printf(     '%s\n', project.molecule.format() )

    residues1 = project.molecule.residuesWithProperties('E') + \
                project.molecule.residuesWithProperties('D')

    residues2 = project.molecule.residuesWithProperties('R') + \
                project.molecule.residuesWithProperties('K') + \
                project.molecule.residuesWithProperties('H')

    # initialize
    for res in project.molecule.allResidues():
        res.saltbridges = NTlist()
    #end for

    result = NTlist()
    for res1 in residues1:
        for res2 in residues2:              
            #print '>>', res1, res2
            s = validateSaltbridge(res1,res2)
        
            if s:
                if (s.types[4][1] <= cutoff):    # less then cutoff 'not observed'
                    if toFile: fprintf(fp, '%s\n', s.format() )
                    if verbose: printf(    '%s\n', s.format() )
                    res1.saltbridges.append( s )
                    res2.saltbridges.append( s )
                    result.append( s )
                #end if
            #end if
        #end for
    #end for
    
    if s:
        if toFile: fprintf( fp, '%s\n', s.comment )
        if verbose: printf(     '%s\n', s.comment )
    #end if

    if toFile:
        fp.close()
    if verbose:
        sys.stdout.flush()
    #end if
    
    return result
#end def

def validateSaltbridge( residue1, residue2 ):
    """
    ValidateSaltbridge( residue1, residue2 )
    
    Validate presence of saltbridge, CC-Bridge, NO-bridge, or ion-pair beteween residue1 and residue2
    Ref: Kumar, S. and Nussinov, R. Biophys. J. 83, 1595-1612 (2002)
    
    residue1, residue2: Residue instances of type E,D,H,K,R
    
    Arbitrarily set the criteria for ion-pair r,theta to be within 2 sd of average, 
    else set type to none.
    
    Returns summary NTdict or None on error
    """
    
    # Definitions of the centroids according to the paper
    centroids = NTdict(
        E = ['OE1','OE2'],
        D = ['OD1','OD2'],
        H = ['CG','ND1','CD2','CE1', 'NE2'],
        K = ['NZ'],
        R = ['NE','CZ','NH1','NH2'] 
    )
    donorAcceptor = NTdict(
        E = ['OE1','OE2'],
        D = ['OD1','OD2'],
        H = ['ND1','NE2'],
        K = ['NZ'],
        R = ['NE','NH1','NH2'] 
    )

    if (residue1 == None):  
        NTerror('validateSaltbridge: undefined residue1\n')
        return None
    #end if
    if (residue2 == None):  
        NTerror('validateSaltbridge: undefined residue2\n')
        return None
    #end if
    
    modelCount = residue1.chain.molecule.modelCount
    if (modelCount == 0): 
        NTerror('validateSaltbridge: no structure models\n')
        return None
    #end if
    
    if (residue1.db.shortName not in ['E','D','H','K','R']): 
        NTerror('validateSaltbridge: invalid residue %s, should be E,D,H,K, or R\n', residue1)    
        return None
    #end if
   
    
    if (residue2.db.shortName not in ['E','D','H','K','R']): 
        NTerror('validateSaltbridge: invalid residue %s, should be E,D,H,K, or R\n', residue2)    
        return None
    #end if
    
    for residue in [residue1, residue2]:
        for atmName in centroids[residue.db.shortName]:
            atm = residue[atmName]
            if len(atm.coordinates) == 0:
                NTerror('validateSaltbridge: no coordinates for atom %s\n', atm)    
                return None
           #end if
        #end for
    #end for
         
    # get the vectors c1, c1a, c2, c2a for each model and compute the result
    result  = NTlist()
    summary = NTdict(
        residue1 = residue1,
        residue2 = residue2,
        comment  = """
Ref: Kumar, S. and Nussinov, R. Biophys. J. 83, 1595-1612 (2002)
Arbitrarily set the criteria for ion-pair (r,theta) to be within 
2 sd ~ 2*(1.2A,39) of average (7.6A,118), else set type to 'not observed'.
""",
        __FORMAT__ = '------------------ Saltbridge ------------------\n' +\
                     'residues:          %(residue1)s %(residue2)s\n' +\
                     'r (av,sd,min,max): (%(rAv).1f, %(rSd).1f, %(min).1f, %(max).1f)\n' +\
                     'theta (av,sd):     (%(thetaAv).1f, %(thetaSd).1f)\n' +\
                     'types:             %(types)s'
    )
    types = ['saltbridge','C-C bridge','N-O bridge','ion pair','not observed']
    counts = NTfill(0,5)
    
    # get the vectors c1, c1a, c2, c2a for each model and compute the result
    for model in range( modelCount ):
        
        #c1 is geometric mean of centroid atms
        c1 = NTvector(0,0,0)
        for atmName in centroids[residue1.db.shortName]:
            atm = residue1[atmName]
            c1 += atm.coordinates[model]()
        #end for
        # not yet: c1 /= len(centroids[residue1.db.shortName])
        for j in range(3):
            c1[j] /= len(centroids[residue1.db.shortName])
            
        try: c1a = residue1['CA'].coordinates[model]()
        except: break
        
        #c2 is geometric mean of centroid atms
        c2 = NTvector(0,0,0)
        for atmName in centroids[residue2.db.shortName]:
            atm = residue2[atmName]
            c2 += atm.coordinates[model]()
        #end for
        # not yet: c2 /= len(centroids[residue2.db.shortName])
        for j in range(3):
            c2[j] /= len(centroids[residue2.db.shortName])

        c2a = residue2['CA'].coordinates[model]()
        
        #print '>>', c1, c2
        r = c2-c1
        rl = r.length()
        theta = 180.0 - (c1-c1a).angle(c2-c2a)
        
        # Check criteria
        criterium1 = (rl < 4.0)
        count = 0
        for atmName1 in donorAcceptor[residue1.db.shortName]:
            atm1 = residue1[atmName1]
            for atmName2 in donorAcceptor[residue2.db.shortName]:
                atm2 = residue2[atmName2]
                d = (atm1.coordinates[model]()-atm2.coordinates[model]()).length()
                if ( d< 4.0): count += 1
                #print '>', atm1,atm2,d,count
            #end for
        #end for
        criterium2 = (count>0)
        if   (criterium1 and criterium2):     
            type = 0 
        elif (criterium1 and not criterium2): 
            type = 1
        elif (not criterium1 and criterium2): 
            type = 2
        elif (not criterium1 and not criterium2 and rl < 7.6+2.1*2 and 118-39*2< theta and theta < 118+39*2 ): 
            type = 3
        else:                                 
            type = 4
        #end if
        counts[type] += 1
               
        data = NTdict(
            residue1   = residue1,
            residue2   = residue2,
            model      = model,
            r          = rl,
            theta      = theta,
            criterium1 = criterium1,
            criterium2 = criterium2,
            type       = types[type],
            
            __FORMAT__ = '--- saltbridge analysis %(residue1)s-%(residue2)s ---\n' +\
                         'model: %(model)d\n' +\
                         'type:  %(type)s\n' +\
                         'r (A): %(r).1f\n' +\
                         'theta: %(theta).1f\n' +\
                         'criteria: %(criterium1)s, %(criterium2)s\n'
        )
        
        
        result.append(data)
    #end for
        
    summary.result = result
    summary.rAv, summary.rSd, summary.modelCount = result.zap('r').average()
    summary.min   = min( result.zap('r') )
    summary.max   = max( result.zap('r') )
    summary.thetaAv, summary.thetaSd, dummy_n = result.zap('theta').average()
    summary.types = zip( types,counts)
    return summary
#end def
cing.Residue.checkSaltbridge = validateSaltbridge

#==============================================================================
def checkHbond( donorH, acceptor, 
                minAngle = 100.0, maxAngle=225.0, maxDistance = 2.4,
                fraction = 0.5
              ):
    
    if not donorH or not donorH.isProton():
        NTerror('ERROR checkHbond: non-proton donor %s\n', donorH )
        return None
    #end if
    
    if not acceptor:
        NTerror('ERROR checkHbond: undefined acceptor %s\n', donorH )
        return None
    #end if
    
    result = NTstruct( __FORMAT__ = '=== H-bond %(donor)s - %(donorH)s - %(acceptor)s ===\n' +\
                                    'accepted: %(accepted)s (%(acceptedCount)d out of %(modelCount)d)\n' +\
                                    'distance: %(distance).2f  +- %(distanceSD).2f\n' +\
                                    'angle:    %(angle).1f  cv: %(angleCV).2f\n'
                     )
    result.donor         = donorH.topology()[0]
    result.donorH        = donorH
    result.acceptor      = acceptor
    result.minAngle      = minAngle
    result.maxAngle      = maxAngle
    result.maxDistance   = maxDistance
    result.fraction      = fraction
    result.distance      = UNDEFINED_FLOAT
    result.distanceSD    = 0.0
    result.angle         = UNDEFINED_FLOAT
    result.angleCV       = 0.0
    result.accepted      = False
    
    result.av, result.sd, dummy_mind, dummy_maxd = donorH.distance( acceptor )
    result.cav, result.cv = donorH.angle( result.donor, acceptor, 
                                          radians=False 
                                        ) 
    
    result.data           = map( None, donorH.distances, donorH.angles )
    result.acceptedModels = NTlist()
    result.acceptedCount  = 0
    result.modelCount     = 0
    distances             = NTlist()    # make copies to calculate averages of accepted
    angles                = NTlist()    # make copies to calculate averages of accepted
    for d,a in result.data:
        if (d <= maxDistance and a >= minAngle and a <= maxAngle ):
            result.acceptedModels.append( (result.modelCount, d, a ) )
            result.acceptedCount += 1
            distances.append( d )
            angles.append( a )
        #end if
        result.modelCount += 1
    #end for
    if len(distances) > 0: result.distance, result.distanceSD, dummy_n = distances.average()
    if len(angles) > 0: result.angle, result.angleCV, dummy_n = angles.cAverage()  
    result.accepted = ((float(len( result.acceptedModels)) / float(len( result.data ))) >= fraction)
    del distances
    del angles
    return result
#end def
cing.Atom.checkHbond = checkHbond


def validateAssignments( project, toFile = True, verbose = True ):
    """
    Validate the assignments; check for potential problems and inconsistencies
    Add's NTlist instance with string's with warning description to each atom as 
    validateAssignment attribute
    
    return a NTlist with atms with errors.
    Generate output in moleculename/Cing/validateAssignments.txt if toFile is True.
    """
    
    funcName = validateAssignments.func_name
    
    result = NTlist()
    
    if project.molecule.resonanceCount == 0: return result

    for atm in project.molecule.allAtoms():
       atm.validateAssignment = NTlist()

       if atm.isAssigned():
            # Check database
            #print '===>', atm
            if not atm.db.shift:
                dummy = atm.pseudoAtom()
                if dummy.db.shift:
                    av = dummy.db.shift.average
                    sd = dummy.db.shift.sd
                else:
                    NTerror("%s: '%s' not in in DB SHIFTS\n", funcName, atm)
                    continue
                #end if
            else:
                av = atm.db.shift.average
                sd = atm.db.shift.sd
            #end if

            shift = atm.shift()
            
            # Check the shift against the database
            delta = math.fabs(shift - av) / sd 
            if (delta > 3.0):
                string = sprintf('%s: %.2f ppm is %.1f*sd away from average (%.2f,%.2f)', 
                                 'SHIFT', shift, delta, av, sd
                                )  
#                if verbose: printf('%-20s %s\n', atm, string)
                result.append( atm )
                atm.validateAssignment.append(string)
            #end if
    
            # Check if not both realAtom and pseudoAtom are assigned
            if atm.hasPseudoAtom() and atm.pseudoAtom().isAssigned():
                string = sprintf('%s: atm also has %s assigned', 'MULTIPLE_ASSIGNMENT', atm.pseudoAtom() )
 #               if verbose: printf('%-20s %s\n', atm, string)
                result.append( atm )
                atm.validateAssignment.append(string)
            #end if
        
            # Check if not pseudoAtom and realAtom are assigned
            if atm.isPseudoAtom():
                for a in atm.realAtoms():
                    if a.isAssigned():
                        string = sprintf('%s: atm also has %s assigned', 'MULTIPLE_ASSIGNMENT', a )
#                        if verbose: printf('%-20s %s\n', atm, string)
                        result.append( atm )
                        atm.validateAssignment.append(string)
                 #end if
                #end for
            #end if
        
            # Check if all realAtoms are assigned in case there is a pseudoatom
            if atm.hasPseudoAtom():
                for a in atm.pseudoAtom().realAtoms():
                    if not a.isAssigned():
                        string = sprintf('%s: expected also %s to be assigned.', 'MISSING_PROTON_ASSIGNMENT', a )
#                        if verbose: printf('%-20s %s\n', atm, string )
                        result.append( atm )
                        atm.validateAssignment.append(string)
                    #end if
                #end for
            #end if
        
            # Check for protons with unassigned heavy atoms
            if atm.isProton():
                heavyAtm = atm.topology()[0]
                if not heavyAtm.isAssigned():
                    string = sprintf('%s: expected %s to be assigned', 'MISSING_HEAVY_ATOM_ASSIGNMENT', heavyAtm )
#                    if verbose: printf('%-20s %s\n', atm, string )
                    result.append( atm )
                    atm.validateAssignment.append(string)
                #end if
            #end if
        #end if
    #end for
    if verbose:
        for atm in result:
            # check for shiftx averages
            if atm.has_key('shiftx'):
                sav = atm.shiftx.av
                ssd = atm.shiftx.sd
            else:
                sav = -NOSHIFT
                ssd = 0.0
                dummy_sn  = 0
            #end if
            if atm.db.shift:
                dav = atm.db.shift.average
                dsd = atm.db.shift.sd
            else:
                dav = -999.0
                dsd = 0.0
            #end if
            printf('%s %s %s\n' +\
                   'shift:    %7.2f %7.2f \n' +\
                   'shiftx:   %7.2f %7.2f \n' +\
                   'database: %7.2f %7.2f \n', 
                   dots, atm, dots,
                   atm.resonances().value, atm.resonances().error,
                   sav, ssd,
                   dav, dsd
                  )
            printf('\n%s\n', atm.validateAssignment.format('Warning %s\n') )
        #end for
    #end if
    if toFile:
        #path = project.mkdir( project.directories.analysis, project.molecule.name )
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis, 'validateAssignments.txt')
        fp = open( fname,'w' )
        for atm in project.molecule.allAtoms():
            if atm.has_key('shiftx') and len(atm.shiftx) > 0:
                sav = atm.shiftx.av
                ssd = atm.shiftx.sd
            else:
                sav = -NOSHIFT
                ssd = 0.0
            #end if
            
            if atm.isAssigned() and sav != -NOSHIFT:
                delta = atm.resonances().value - sav
                rdelta = 1.0
                if (ssd > 0.0): rdelta = sav/ssd
            else:
                delta  = 0.0
                rdelta = 0.0                
            #end if
                
            if atm.db.shift:
                dav = atm.db.shift.average
                dsd = atm.db.shift.sd
            else:
                dav = -999.0
                dsd = 0
            #end if
            fprintf(fp,'%-18s (%7.2f %6.2f)   (shiftx: %7.2f %6.2f)   (delta: %6.2f %6.2f)   (db: %7.2f %6.2f)   %s\n', 
                    atm,
                    atm.resonances().value, atm.resonances().error,
                    sav, ssd, delta, rdelta, 
                    dav, dsd,
                    atm.validateAssignment.format()
                   )            
        #end for
        fp.close()
        if verbose:
            NTmessage('==> validateAssignments: result to "%s"\n', fname)
    #end if
        
    return result
#end def

def validateDihedrals( self, verbose=True ):
    """Validate the dihedrals of dihedralList for outliers and cv using pierceTest
    """

    if not self.molecule or self.molecule.modelCount == 0: return
    
    for res in self.molecule.allResidues():

#        for dihed in [res.db.dihedrals[i].name for i in range(len(res.db.dihedrals))]:
        for dihed in res.db.dihedrals.zap('name'):

#            print res, dihed, dihed in res, res[dihed]
#            if dihed in res and res[dihed] != None:
            if dihed in res and res[dihed]:
                d = res[dihed]

                plotpars = self.plotParameters.getdefault(dihed,'dihedralDefault')
                
                cav, dummy_cv, dummy_n = d.cAverage(min=plotpars.min, max=plotpars.max)
                NTlimit( d, cav-180.0, cav+180.0 )

                d.good,d.outliers = peirceTest( d )
                
                if not d.good: continue
                
                d.limit( plotpars.min, plotpars.max ).cAverage(min=plotpars.min,
                                                               max=plotpars.max)
                d.good.limit( plotpars.min, plotpars.max, byItem=1 ).cAverage( 
                              plotpars.min, plotpars.max, byItem=1 )
                d.outliers.limit( plotpars.min, plotpars.max, byItem=1 )

                if verbose:
                    NTmessage( '--- Residue %s, %s ---\n', res, dihed )
                    NTmessage( 'good:     %2d %6.1f %4.3f\n', 
                               d.good.n, d.good.cav, d.good.cv )
                    NTmessage( 'outliers: %2d models: %s\n', 
                               len(d.outliers), d.outliers.zap(0) )
                #end if
            #end if
        #end for
    #end for
#end def
    
def validateModels( self, verbose=True ):
    """Validate the models on the basis of the dihedral outliers
    """

    if not self.molecule or self.molecule.modelCount == 0: return
    
    backbone = ['PHI','PSI','OMEGA']

#    self.validateDihedrals( verbose=False )

    self.models = NTstruct()
    for m in range(self.molecule.modelCount):
        self.models[m] = 0
    #end for

    for res in self.molecule.allResidues():

#        for dihed in [res.db.dihedrals[i].name for i in range(len(res.db.dihedrals))]:
#        for dihed in res.db.dihedrals.zap('name'):
        for dihed in backbone:

#            print res, dihed
#            if dihed in res and res[dihed] != None:
            if dihed in res and res[dihed]:
                d = res[dihed]
                if not d.good: continue
                for m in d.outliers.zap( 0 ):    #get all modelId of outliers
                    #print res, dihed, d.outliers, m
                    self.models[m] += 1
                #end for
            #end if
        #end for
    #end for
    if verbose:
        for m, count in self.models.items():
            NTmessage('Model %s: %2d backbone dihedral outliers\n', str(m), count )
        #end for
    #end if
    
#end def

def makeDihedralHistogramPlot( project, residue, dihedralName, binsize = 5 ):
    '''Return NTplot instance with histogram of dihedralName
       or None on error.
       TODO: make this work on JFD's install.
    '''
    NTerror("TODO: make makeDihedralHistogramPlot work on JFD's install.")
    return None

    if project == None or dihedralName not in residue or residue[dihedralName] == None:
        return None
    #end if

    
    bins       = 360/binsize
    plotparams = project.plotParameters.getdefault(dihedralName,'dihedralDefault')
    
    angle = residue[dihedralName]
    
    plot = NTplot.NTplot( title  = residue._Cname(1),
                          xRange = (plotparams.min, plotparams.max),
                          xTicks = range(int(plotparams.min), int(plotparams.max+1), plotparams.ticksize),
                          xLabel = dihedralName,
                          yLabel = 'Occurence',
                          hardcopySize= (600,300),
                          aspectRatio = 0.5
                        )
    if angle.good:
        plot.histogram( angle.good.zap(1),
                        plotparams.min, plotparams.max, bins,
                        attributes = NTplot.boxAttributes( fillColor=plotparams.color )
                      )
    else:
        NTwarning("No angle.good plots made")
        
    if not plot.maxY:
        NTerror("Failed to get a plot.maxY set")
        return None
    
    hight = plot.maxY

    if angle.outliers:
        plot.histogram( angle.outliers.zap(1),
                    plotparams.min, plotparams.max, bins,
                    attributes = NTplot.boxAttributes( fillColor=plotparams.outlier )
                  )
    else:
        NTwarning("No angle.outliers plots made")
    # AWSS
    # Let's check if for this 'angle' is a dihedral restraint
    aAv  = angle.cav
    width = 4.0
    dd = 3.0
    dr = _matchDihedrals(residue, dihedralName)

    if dr:
        lower, upper = dr.lower, dr.upper
    else:
        lower, upper = plotparams.min+dd, plotparams.max-dd        
            
    plot.line( (lower, 0), (lower, hight), 
               NTplot.lineAttributes(color=plotparams.lower, width=width) )
    plot.line( (upper, 0), (upper, hight), 
               NTplot.lineAttributes(color=plotparams.upper, width=width) )
    #end if

    # Always plot the cav line
    plot.line( (aAv, 0), (aAv, hight), NTplot.lineAttributes( 
                                        color=plotparams.average, width=width) )    
    return plot
#end def

def makeDihedralPlot( project, residue, dihedralName1, dihedralName2 ):
    '''Return NTplot instance with plot of dihedralName1 vrs dihedralName2 or
       None on error
    '''

    if (project == None or
        dihedralName1 not in residue or residue[dihedralName1] == None or
        dihedralName2 not in residue or residue[dihedralName2] == None or
        len(residue[dihedralName1]) == 0 or len(residue[dihedralName2]) == 0 ):
        return None
    #end if

    plotparams1 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')
    plotparams2 = project.plotParameters.getdefault(dihedralName2,'dihedralDefault')

    d1 = residue[dihedralName1]
    d2 = residue[dihedralName2]
    
    d1cav = d1.cav
    d2cav = d2.cav

    plot = NTplot.NTplot( title  = residue._Cname(1),

                          xRange = (plotparams1.min, plotparams1.max),
                          xTicks = range(int(plotparams1.min), int(plotparams1.max+1), plotparams1.ticksize),
                          xLabel = dihedralName1,

                          yRange = (plotparams2.min, plotparams2.max),
                          yTicks = range(int(plotparams2.min), int(plotparams2.max+1), plotparams2.ticksize),
                          yLabel = dihedralName2,

                          hardcopySize= (400,400),
                          aspectRatio = 1.0
                        )
    plot.points( zip( d1, d2 ), attributes=NTplot.plusPoint )

    dummy_width = 4.0
    
    dr1 = _matchDihedrals(residue, dihedralName1)
    dr2 = _matchDihedrals(residue, dihedralName2)
    
    #dr2 = dr1 # just for test
    
    #if dr1 and dr2:
    #    lower1, upper1 = dr1.lower, dr1.upper
    #    lower2, upper2 = dr2.lower, dr2.upper
    #    plot.box( (lower1,lower2), (abs(upper1-lower1),abs(upper2-lower2)),
    #              NTplot.NTplotAttributes(fill=False, line=True, lineWidth=2, 
    #                                      lineColor=plotparams1.lower) ) 
    dd = 3
    if dr1:
        lower1, upper1 = dr1.lower, dr1.upper
    else:
        lower1, upper1 = plotparams1.min+dd, plotparams1.max-dd
    #    plot.line( (lower1, plotparams2.min), (lower1, plotparams2.max),
    #               NTplot.lineAttributes(color=plotparams1.lower, width=width) )
    #    plot.line( (upper1, plotparams2.min),(upper1, plotparams2.max),
    #               NTplot.lineAttributes(color=plotparams1.upper, width=width) )        
    if dr2:
        lower2, upper2 = dr2.lower, dr2.upper
    else:
        lower2, upper2 = plotparams2.min+dd, plotparams2.max-dd
    #    plot.line( (lower2, plotparams1.min), (lower2, plotparams1.max),
    #               NTplot.lineAttributes(color=plotparams2.lower, width=width) )
    #    plot.line( (upper2, plotparams1.min),(upper2, plotparams1.max),
    #               NTplot.lineAttributes(color=plotparams2.upper, width=width) )
    #end if
    plot.box( (lower1,lower2), (abs(upper1-lower1),abs(upper2-lower2)),
              NTplot.NTplotAttributes(fill=False, line=True, lineWidth=dd, 
                                      lineColor=plotparams1.lower) ) 
    
    # Always plot the cav point
    plot.point( (d1cav, d2cav), 
                NTplot.pointAttributes(type='filled circle', size=2,
                                       color='green') )
    return plot
#end def

def _matchDihedrals(residue, dihedralName):
    for dr in residue.dihedralRestraints:
        if dr.angle == '%s_%i' % (dihedralName, residue.resNum):
            return dr
    return None
#end def

def setupHtml(project):
    '''Descrn: create all folders and subfolders related to a Cing.Molecule
               under Molecul/HTML directory and initiatilise attribute html
               for the due Cing objects.
       Inputs: list of Cing.Molecules, Cing.Peaks, Cing.Distances and
               Cing.Dihedrals
       Output:
    '''

    HTMLfile.killHtmlObjects()

    # values for residue table
    ncols = 10
    width = '75px'
    top = '#_top'

    # initialise project html page
    project.htmlLocation = (project.path('index.html'), top)
    project.html = HTMLfile( project.htmlLocation[0],
                                  title = 'Project ' + project.name )
    project.html.header('h1', 'Project: ' + project.name)
    
    # A list of all objects that will be in project/index.html
    project.mainPageObjects = NTdict()

    # Do Molecules HTML pages
    for molecule in project.molecules:        
        molecule = project[molecule]

        if (project.molecule.modelCount == 0):
            NTerror('ERROR setupHtml(): No structural models\n' )
            return
        #end if
        
        #create new folders for Molecule/HTML
        htmlPath = project.htmlPath()
        if os.path.exists( htmlPath ):
            removedir( htmlPath )
        #end if
        os.makedirs( htmlPath )
        
        for subdir in htmlDirectories.values():
            project.mkdir( project.molecule.name, moleculeDirectories.html,
                           subdir )
        #end for
        
        if hasattr(molecule, 'html'): del(molecule['html'])
        
        molecule.htmlLocation = (project.htmlPath('index.html'), top)
        molecule.html = HTMLfile( molecule.htmlLocation[0],
                                       title = 'Molecule ' + molecule.name )
    
    for molecule in project.molecules:
        index = project.molecules.index(molecule)
        molecule = project[molecule]
        
        molecule.html.header('h1', 'Molecule: ' + molecule.name)

        previous = None
        next = None
        
        if index > 0:
            try: previous = project[project.molecules[index-1]]
            except: pass
        
        try: next = project[project.molecules[index+1]]
        except: pass

        if previous:
            molecule.html.insertHtmlLink( molecule.html.header, molecule,
                                          previous, text='Previous' )
        #end if
        
        molecule.html.insertHtmlLink( molecule.html.header, molecule,
                                      project, text='UP' )

        if next:
            molecule.html.insertHtmlLink( molecule.html.header, molecule,
                                          next, text='Next' )
            
        #end if

        molecule.html.main('h1','Residue-based analysis')

        if project.mainPageObjects.has_key('Molecules'):
            project.mainPageObjects['Molecules'].append(molecule)
        else:
            project.mainPageObjects['Molecules'] = [molecule]
        #end if

        for chain in molecule.allChains():
    
            #Create the directory for this chain
            chaindir = project.htmlPath(chain.name)
            if not os.path.exists( chaindir ):
                os.mkdir( chaindir )
            #end if
            
            #if hasattr(chain, 'html'): del(chain['html'])
            if chain.has_key('html'): del(chain.html)
            
            chain.htmlLocation = ( os.path.join(chaindir,'index.html'), top )
            chain.html = HTMLfile(chain.htmlLocation[0],
                                       title='%s %s'%(molecule.name,chain.name))
        #end for

        for chain in molecule.allChains():
                       
            moleculeMain = molecule.html.main
            molecule.html.insertHtmlLinkInTag( 'h1', moleculeMain, molecule,
                                            chain, text='Chain %s' % chain.name)
    
            residues = chain.allResidues()
            if not residues: break
            
            #Chain page
            chainHeader = chain.html.header
            chainHeader('h1', '%s %s' % (molecule.name, chain.name))
    
            # Refs to move to previous, next chain or UP
            previous = chain.sister(-1)
            next = chain.sister(1)
            if previous:
                chain.html.insertHtmlLink( chainHeader, chain, previous,
                                           text=previous._Cname(-1))
            #end if
            chain.html.insertHtmlLink( chainHeader, chain, molecule,
                                           text='UP')
            if next:
                chain.html.insertHtmlLink( chainHeader, chain, next,
                                           text=next._Cname(-1))
            #end if
    
            # Html objs that share residues tables elements
            htmlList = [ molecule, chain ]
    
            # make a table with residue links
            r0 = residues[0]
            r1 = r0.resNum
            r2 = r0.resNum/ncols *ncols + ncols-1
            for obj in htmlList:
                if obj.html == chain.html: obj.html.main('h1','Residues')
                obj.html.main('table', closeTag=False)
                obj.html.main('tr', closeTag=False)
                obj.html.main( 'td',sprintf('%d-%d',r1,r2), style="width: %s" % 
                               width )
            #end for
            for dummy in range( 0, r0.resNum%ncols ):
                for obj in htmlList:
                    obj.html.main('td', style="width: %s" % width)
                #end for
            #end for
                
            for res in residues:

                # Create the directory for this residue
                resdir = project.htmlPath(chain.name, res.name)
                if not os.path.exists( resdir ):
                    os.mkdir( resdir )
                #end if
                
                #if hasattr(res, 'html'): del(res['html'])
                if res.has_key('html'): del(res.html)
                
                res.htmlLocation = ( os.path.join(resdir,'index.html'), top )
                res.html = HTMLfile( res.htmlLocation[0], title=res.name )

            for res in residues:
                if res.resNum%ncols == 0:
                    r1 = res.resNum/ncols *ncols
                    r2 = r1+ncols-1
                    for obj in htmlList:
                        obj.html.main('tr', openTag=False)
                        obj.html.main('tr', closeTag=False)
                        obj.html.main( 'td',sprintf('%d-%d',r1,r2), 
                                       style="width: %s" % width )
                    #end for
                #end if
                # add residue to table
                for obj in htmlList:
                    objMain = obj.html.main
                    objMain('td', style="width: %s" % width, closeTag=False)
                    obj.html.insertHtmlLink(objMain, obj, res, text=res.name)
                    objMain('td', openTag=False)
                #end for
                
                # Create a page for each residue
        
                # generate html file for this residue
                resHeader = res.html.header
                resHeader('h1', res._Cname(-1) )
        
                # Refs to move to previous, next residue or UP
                previous = res.sister(-1)
                next = res.sister(1)
                if previous:
                    res.html.insertHtmlLink( resHeader, res, previous, 
                                             text = previous._Cname(-1) )
                #end if
                res.html.insertHtmlLink( resHeader, res, chain, 
                                             text = 'UP' )
                if next:
                    res.html.insertHtmlLink( resHeader, res, next, 
                                             text = next._Cname(-1) )
                #end if
            #end for
            for obj in htmlList:
                obj.html.main('tr', openTag=False)
                obj.html.main('table', openTag=False)
            #end for
        #end for
        molecule.html.main('h1', 'Model-based analysis')
        molecule.html.main( 'p', molecule.html._generateTag('a', 'Models page',
                                            href='models.html', newLine=False) )
    #end for

    # TODO: setup Models page
    
    # Do Peaks HTML pages    
    for peakList in project.peaks:
        
        plLink = project.htmlPath( htmlDirectories.peaks, 
                                   peakList.name+'.html' )
        
        peakList.htmlLocation = ( plLink, top )
        peakList.html = HTMLfile( peakList.htmlLocation[0],
                                       title = 'Peak List ' + peakList.name )

    for peakList in project.peaks:    

        index = project.peaks.index(peakList)
        
        peakHeader = peakList.html.header
        peakHeader('h1', 'Peak List: ' + peakList.name)
        
        previous = None
        next = None
        
        if index > 0:
            try: previous = project.peaks[index-1]
            except: pass
        
        try: next = project.peaks[index+1]
        except: pass

        if previous:
            peakList.html.insertHtmlLink( peakHeader, peakList, previous,
                                          text = 'Previous')
        #end if
        
        peakList.html.insertHtmlLink( peakHeader, peakList, project,
                                      text = 'UP')

        if next:
            peakList.html.insertHtmlLink( peakHeader, peakList, next,
                                          text = 'Next')
        #end if

        if project.mainPageObjects.has_key('Peaks'):
            project.mainPageObjects['Peaks'].append(peakList)
        else:
            project.mainPageObjects['Peaks'] = [peakList]
        #end if
        
        #count = 0
        for peak in peakList:
            count = peak.peakIndex #count += 1
            peakTag = 'o'+str(peak.__OBJECTID__) #str(peak.peakIndex) #
            peak.htmlLocation = ( plLink, '#' + peakTag )
            peakMain = peakList.html.main
            #peakMain( 'h2', peakList.html._generateTag('a', 'Peak %i' 
            #          % count, id = peakTag, newLine=False) )
            peakMain( 'h2', 'Peak %i' % count, id = peakTag )
            
            peakMain('ul', closeTag=False)
            peakMain('li', 'Positions: %s' % peak.positions.__str__())
            peakMain('li', 'Height: %.3e (%.3e)' % ( peak.height, 
                                                     peak.heightError))
            peakMain('li', 'Volume: %.3e (%.3e)' % ( peak.volume, 
                                                     peak.volumeError))
            peakMain('li', 'Atoms:', closeTag=False)
            for resonance in peak.resonances:
                if resonance:
                    residue = resonance.atom._parent
                    resonanceAtomName = "%s.%s" % ( residue.name, 
                                                    resonance.atom.name )
                    peakList.html.insertHtmlLink( peakMain, peakList, residue, 
                                                  text = resonanceAtomName )
                else:
                    peakMain('b', 'None')
                #end if
            #end for
            peakMain('li', openTag=False)
            peakMain('ul', openTag=False)
        #end for
    #end for

    # For all RestraintList
    allRestraintList = project.distances + project.dihedrals
    
    for restraintList in allRestraintList:
        
        RLLink = project.htmlPath( htmlDirectories.whatif, 
                                   restraintList.name+'.html' )
        restraintList.htmlLocation = ( RLLink, top )
        restraintList.html = HTMLfile( restraintList.htmlLocation[0],
                                         title = 'Restraints List ' +
                                         restraintList.name )
    
    for restraintList in allRestraintList:

        index = allRestraintList.index(restraintList)
        
        RLLink = restraintList.htmlLocation[0]
        
        restrHeader = restraintList.html.header
        restrHeader('h1', 'Restraints List: '+ restraintList.name)
        
        previous = None
        next = None
        
        if index > 0:
            try: previous = allRestraintList[index-1]
            except: pass
        
        try: next = allRestraintList[index+1]
        except: pass

        if previous:
            restraintList.html.insertHtmlLink( restrHeader, restraintList, 
                                               previous, text = 'Previous' )
        #end if
        
        restraintList.html.insertHtmlLink( restrHeader, restraintList, 
                                           project, text = 'UP' )

        if next:
            restraintList.html.insertHtmlLink( restrHeader, restraintList, 
                                               next, text = 'Next' )
        #end if

        if project.mainPageObjects.has_key('Restraints'):
            project.mainPageObjects['Restraints'].append(restraintList)
        else:
            project.mainPageObjects['Restraints'] = [restraintList]
        #end if

        if str(type(restraintList)).count('DistanceRestraintList'):
            #count = 0
            for restraint in restraintList:
                count = restraint.id #count += 1
                tag = 'o'+str(restraint.__OBJECTID__)
                restraint.htmlLocation = ( RLLink, '#' + tag )
                restrMain = restraintList.html.main
                #restrMain('h2', restraintList.html._generateTag( 'a',
                #     'Distance Restraint %i' % count, id = tag, newLine=False) )
                restrMain('h2', 'Distance Restraint %i' % count, id = tag)
                restrMain('ul', closeTag=False)
                restrMain('li', 'Lower/Upper: %.2f / %.2f' % (restraint.lower, 
                                                              restraint.upper))
                restrMain('li', 'Average (Min/Max):  %.3e (%.3e / %.3e)'
                                 % (restraint.av, restraint.min, restraint.max))
                restrMain('li', 'ViolCount3: %i' % restraint.violCount3)
                restrMain('li', 'Viol Average / SD / Max: %.2f / %.2f / %.2f' % 
                        (restraint.violAv, restraint.violSd, restraint.violMax))
                restrMain('li', 'Pair of Atoms:', closeTag=False)
                
                if len(restraint.atomPairs) < 1: restrMain('b', 'None')
    
                for atomPair in restraint.atomPairs:
                    res1 = atomPair[0]._parent
                    res2 = atomPair[1]._parent
                    atomName1 = "(%s.%s," % ( res1.name, atomPair[0].name )
                    atomName2 = "%s.%s)" % ( res2.name, atomPair[1].name )
                    restraintList.html.insertHtmlLink( restrMain, restraintList,
                                                       res1, text = atomName1 )
                    restraintList.html.insertHtmlLink( restrMain, restraintList,
                                                       res2, text = atomName2 )
                #end for
                restrMain('li', openTag=False)
                restrMain('ul', openTag=False)
            #end for
        elif str(type(restraintList)).count('DihedralRestraintList'):
            for restraint in restraintList:
                count = restraint.id
                tag = 'o'+str(restraint.__OBJECTID__)
                restraint.htmlLocation = ( RLLink, '#' + tag )
                restrMain = restraintList.html.main
                
                #restrMain('h2', restraintList.html._generateTag( 'a',
                #      'Dihedral Restraint %i' % count, id = tag, newLine=False))
                restrMain('h2', 'Dihedral Restraint %i' % count, id = tag)
                restrMain('ul', closeTag=False)
                restrMain('li', 'Lower/Upper: %.2f / %.2f' % (restraint.lower, 
                                                              restraint.upper))
                restrMain('li', 'Average (CV):  %.2f (%.2f)'
                                 % (restraint.cav, restraint.cv))
                restrMain('li', 'ViolCount3: %i' % restraint.violCount3)
                restrMain('li', 'Viol Average / SD / Max: %.2f / %.2f / %.2f' % 
                        (restraint.violAv, restraint.violSd, restraint.violMax))

                val1, val2, dummy_val3 = restraint.retrieveDefinition()
                restraint.residue = val1
                restraint.angle = '%s_%i' % (val2, val1.resNum) 
                                
                restrMain('li', 'Angle Name:', closeTag=False)
                restraintList.html.insertHtmlLink( restrMain, restraintList, 
                                       restraint.residue, text=restraint.angle )
                restrMain('li', openTag=False)
                
                restrMain( 'li', 'Torsional Angle Atoms:', closeTag=False )
                
                if len(restraint.atoms) < 1: restrMain('b','None')

                ind = 0
                for atom in restraint.atoms:
                    res = atom._parent
                    atomName = "%s.%s," % ( res.name, atom.name )
                    if ind == 0: atomName = '(' + atomName
                    if ind == 3: atomName = atomName[:-1] + ')'
                    restraintList.html.insertHtmlLink( restrMain, restraintList,
                                                       res, text = atomName )
                    ind += 1
                #end for
                restrMain('li', openTag=False)
                restrMain('ul', openTag=False)
            #end for
        #end if
    #end for
    
    # Do Project HTML page    
    for key in project.mainPageObjects.keys():
        projectMain = project.html.main
        projectMain('h1', key)
        for item in project.mainPageObjects[key]:
            projectMain('ul', closeTag=False)
            project.html.insertHtmlLinkInTag( 'li', projectMain, project, item,
                                              text=item.name )
            projectMain('ul', openTag=False)
        #end for
    #end for
#end def

def renderHtml(project):
    '''Descrn: render HTML content for a Cing.Molecule or for just a 
               Cing.Chain, Cing.Residue or Cing.Atom.
       Inputs: a Cing.Molecule, Cing.Chain, Cing.Residue or Cing.Atom.
       Output: 
    '''
        
    for htmlObj in htmlObjects:
        htmlObj.render()
    #end for   
#end def

def populateHtmlMolecules( project ):
    '''Descrn: generate the Html content for Molecules and Residues pages.
       Inputs: a Cing.Project.
       Output: 
    '''

    for molecule in [project[mol] for mol in project.molecules]:
        for chain in molecule.allChains():
            for res in chain.allResidues():
                
                resdir = os.path.dirname(res.htmlLocation[0])

                fp = open( os.path.join( resdir, 'summary.txt' ), 'w' )
                fprintf(fp, '----- %5s -----\n', res)

                plot = makeDihedralPlot( project, res, 'PHI', 'PSI' )
                if plot:
                    plot.hardcopy( fileName = os.path.join(resdir, 'PHI_PSI' ),
                                   graphicsFormat = 'gif' )
                    del( plot )
                    #generate HTML code for plot
                    res.html.left( 'h2', 'Ramanchandran', id='Ramanchandran')
                    res.html.left( 'img', src = 'PHI_PSI' )
                #endif
                    
                plot = makeDihedralPlot( project, res, 'CHI1', 'CHI2' )
                if plot:
                    plot.hardcopy( fileName = os.path.join(resdir, 'CHI1_CHI2'),
                                   graphicsFormat = 'gif' )
                    del( plot )
                    #generate HTML code for plot
                    res.html.left( 'h2','CHI1-CHI2', id='CHI1-CHI2')
                    res.html.left( 'img', src = 'CHI1_CHI2' )
                #endif
        
                for dihed in res.db.dihedrals.zap('name'):
                    if dihed in res and res[dihed]:
                        #print '------>>>>>', dihed, res, res[dihed]
                        d = res[dihed]
        
                        # summarize the results
                        phrase = \
                            '%-6s: average: %7.1f   cv: %4.3f  ||  outliers:' +\
                            '%2d (models %s)'
                        lenOutliers = -999 # JFD adds: Indicating None
                        outlierList = -999
                        if d.outliers:
                          NTwarning("Found no outliers; code wasn't prepared to deal with that or is JFD wrong?")
                          lenOutliers = len(d.outliers)
                          outlierList = d.outliers.zap(0)
                        summary = sprintf( phrase, dihed, d.cav, d.cv, 
                                           lenOutliers, outlierList
                                         )
                        fprintf( fp, '%s\n', summary )
                        print summary
        
                        #generate a dihedral histogram plot
                        plot = makeDihedralHistogramPlot( project, res, dihed )
                        tmpPath = os.path.join(resdir,dihed + '.gif')
#                        printDebug("Will write to: "+tmpPath)
                        if not os.path.isdir(resdir):
                            printError("Failed to find an existing location in: " + resdir)
                            return None
                        plot.hardcopy( fileName = tmpPath,graphicsFormat = 'gif' )
                        del( plot )
        
                        #generate HTML code for plot and text
                        res.html.left( 'h2', dihed, id=dihed),
                        res.html.left( 'img', src = dihed + '.gif'  )
                        res.html.left( 'p', summary )                
                    #end if
                #end for
                # Right side
                # Distance Restraints
                _generateHtmlResidueRestraints(project, res, type = 'Distance')
                # Dihedral Restraints
                _generateHtmlResidueRestraints(project, res, type = 'Dihedral')
            #end for residue
        #end for chain
         
        # Procheck
        molecule.html.main('h1','Procheck_NMR')
        molecule.html.main('ul', closeTag=False)
        for p,d in [
             ('_01.ps','Ramanchandran (all models)'),
             ('_02.ps','Ramanchandran (residue types)'),
             ('_03.ps','chi1-chi2'),
             ('_04.ps','chi1'),
             ('_05.ps','chi2'),
             ('_06.ps','Ramanchandran (per residue)'),
             ('_07.ps','Ensemble chi1-chi2'),
             ('_08.ps','Residue properties'),
             ('_09.ps','Equivalent resolution')
            ]:
            molecule.html.main('li', closeTag=False)
            procheckLink = os.path.join('..', 
                        project.moleculeDirectories.procheck, molecule.name + p)
    
            molecule.html.main('a', d, href = procheckLink )
            molecule.html.main('li', openTag=False)
        #end for
        molecule.html.main('ul', openTag=False)

    #end for molecule
#end def

def _generateHtmlResidueRestraints( project, residue, type = None ):
    '''Descrn: internal routine to generate the Html content for restraints
               linked to a particular residue.
       Inputs: Cing.Residue, string type of restraint: 'Distance', 'Dihedral',
               'RDC' (?).
       Output: 
    '''
        
    if type == 'Distance':
        restraintList = residue.distanceRestraints
    elif type == 'Dihedral':
        restraintList = residue.dihedralRestraints
    else:
        return
    #end if
    
    if len(restraintList) == 0: return
    
    resRight = residue.html.right 
    resRight('h2','%s Restraints' % type)
    
    tmpDict = NTdict()
    for restraint in restraintList:
        RLname = os.path.basename(restraint.htmlLocation[0]).split('.')[0]
        if tmpDict.has_key(RLname):
            tmpDict[RLname].append(restraint)
        else:
            tmpDict[RLname] = NTlist(restraint)
        #end if
    #end for
    RLists = tmpDict.keys()
    # display Restraint list
    resRight('p', closeTag=False)
    for k in RLists:
        RLobj = project[k]
        residue.html.insertHtmlLink(resRight, residue, RLobj, text=k)
        resRight('br')
        resRL = tmpDict[k]
        # sort list by 'violCount3' reverse order (higher to lower values)
        NTsort(resRL, 'violCount3', inplace=True)
        resRL.reverse()
        # sort by color: 1st red, 2nd orange, then green and by violCount3 reverse order
        listRed, listOrange, listGreen = [], [], []
        for dr in resRL:
            if not hasattr(dr,'colorLabel'): dr.colorLabel = COLOR_GREEN
            if dr.colorLabel == COLOR_GREEN: listGreen.append(dr)
            if dr.colorLabel == COLOR_RED: listRed.append(dr)
            if dr.colorLabel == COLOR_ORANGE: listOrange.append(dr)
            #if dr.colorLabel == COLOR_GREEN: listGreen.append(dr)
        resRL = listRed + listOrange + listGreen
        # display restraint by number, in line, sorted by violCount3 reverse
        #for dr in resRL:
        #    residue.html.insertHtmlLink(resRight, residue, dr, text=str(dr.id))
        #end for
        # display restraint by line
        toShow = 5 # number of restraints to show on the right side of Residue page
        for dr in resRL:
            text = '%s:' % (str(dr.id))
            residue.html.insertHtmlLink(resRight, residue, dr, text=text)
            #resRight('ul', closeTag=False)
            if type == 'Distance':
                av = dr.av
                for atomPair in dr.atomPairs:
                    res1 = atomPair[0]._parent
                    res2 = atomPair[1]._parent
                    atomName1 = "(%s.%s," % ( res1.name, atomPair[0].name )
                    atomName2 = "%s.%s)" % ( res2.name, atomPair[1].name )
                    residue.html.insertHtmlLink( resRight, residue, res1,
                                                 text = atomName1 )
                    residue.html.insertHtmlLink( resRight, residue, res2,
                                                 text = atomName2 )
                #end for
            #end if
            if type == 'Dihedral':
                av = dr.cav
                #resRight( 'a', '%s' % dr.angle)
                angleName = dr.angle.split('_')[0]
                residue.html.insertHtmlLink( resRight, residue, residue,
                                             text=angleName, id=angleName )
            #end if
            resRight( 'a', 'Lower/Av/Upper: %.2f/ %.2f / %.2f' % (dr.lower, av,
                                                                  dr.upper) )
            #resRight('li', 'Average (Min/Max):  %.3e (%.3e / %.3e)'
            #                 % (restraint.av, restraint.min, restraint.max))
            resRight( 'a', 'ViolCount3: %i' % dr.violCount3)
            resRight( 'a', 'Viol Average / SD / Max: %.2f / %.2f / %.2f' % 
                      (dr.violAv, dr.violSd, dr.violMax) )
            #resRight('ul', openTag=False)
            resRight('br')
            if resRL.index(dr) + 1 == toShow:
                resRight('a','More: ')
                for dr in resRL[toShow:]:
                    residue.html.insertHtmlLink( resRight, residue, dr, 
                                                 text=str(dr.id) )
                #end for
                resRight('br')
                break
            #end if
        #end for
        #if RLists.index(k) != RLists.index(RLists[-1]): resRight('br')
    #end for
    resRight('p', openTag=False)    
#end def

def populateHtmlModels(project):

    # Models page
    for molecule in [project[mol] for mol in project.molecules]:    

        # should go to setupHtml
        molecule.modelPage = HTMLfile( project.htmlPath( 'models.html' ),
                                            title = 'outliers' )
        molecule.modelPage.header('h1', molecule.name + ' models' )
        ########################
        
        plot = NTplot( xLabel = 'Model',
                              xRange = (0, project.molecule.modelCount), 
                              yLabel = 'Outliers',
                              hardcopySize= (600,300),
                              aspectRatio = 0.5
                            )
    
        outliers = [project.models[i] for i in range(molecule.modelCount)]
        print '>>', molecule.modelCount, outliers
        plot.barChart( project.models.items(),
                       0.05, 0.95,
                       attributes = boxAttributes( fillColor='green' )
                     )
        plot.hardcopy( project.htmlPath('outliers'), 'gif' )
        molecule.modelPage.main('img', src = 'outliers' )

#end def

def validate( project, verbose=True ):
    """Validatation tests returns None on error.
    """
    #validateSetup(project)
    setupValidation( project )

    setupHtml(project)
        
    # populate Molecule (Procheck) and Residues
    if 1:
        NTerror("code failes for JFD; please fix")
    else:
        if not populateHtmlMolecules(project):
            printError("Failed to populateHtmlMolecules")
            return None  
        if not populateHtmlModels(project):
            printError("Failed to populateHtmlModels")
            return None  
        if not renderHtml(project):
            printError("Failed to renderHtml")
            return None  
       
    if verbose: 
        NTmessage('done\n' )
  
#end def

# register the functions
methods  = [(validateDihedrals, None),
            (validateModels,None), 
            (validateAssignments, None), 
            (validate, None),
            (checkForSaltbridges, None),
            (validateRestraints, None),
            (setupValidation, None),
            (calculateRmsd, None),
            (summary, None),
            (makeDihedralHistogramPlot, None),
            (makeDihedralPlot, None)
           ]
#saves    = []
#restores = []
#exports  = []
