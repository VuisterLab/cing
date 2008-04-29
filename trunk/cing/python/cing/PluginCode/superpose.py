"""
Test superpose
        
"""
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NoneObject
from cing.Libs.NTutils import sprintf
from cing.Libs.cython.superpose import NTcMatrix #@UnresolvedImport
from cing.Libs.cython.superpose import calculateRMSD #@UnresolvedImport
from cing.Libs.cython.superpose import superposeVectors #@UnresolvedImport
from cing.core.molecule import Molecule
from cing.core.molecule import dots


class SuperposeEnsemble( NTlist ):
    def __init__( self, molecule ):
        NTlist.__init__( self )
        self.averageModel = None
        self.molecule     = molecule
        
        for i in range(0,molecule.modelCount):
            m = SuperposeModel('model'+str(i), i )
            self.append( m )
        #end for
        self.averageModel = SuperposeModel('averageModel', molecule.modelCount )
        
        # Assemble the coordinates of the models
        for atm in molecule.allAtoms():
            if len(atm.coordinates) == molecule.modelCount:
                for i in range(0,molecule.modelCount):
                    self[i].coordinates.append( atm.coordinates[i] )
                #end for
                self.averageModel.coordinates.append( atm.meanCoordinate )
            #end if
        #end for
    #end def
    
    def calculateAverageModel( self ):
        """
        Calculate averageModel from members of self
        Calculate rmsd to average for each model using fitCoordinates
        Set rmsd of average model to <rmsd>
        Return averageModel or None on error
        
        """
        for atm in self.molecule.allAtoms():
            atm.calculateMeanCoordinate()
        #end for
        rmsd = NTlist()
        for m in self:
            rmsd.append( m.calculateRMSD( self.averageModel ) )
        #end for
        self.averageModel.rmsd, _tmp, _tmp = rmsd.average()
        return self.averageModel
    #end def
    
    def setFitCoordinates( self, fitAtoms ):
        """
        Initialize the fitCoordinates lists of models of self from fitAtoms
        """
        for model in self:
            model.fitCoordinates = NTlist()
        #end for
        self.averageModel.fitCoordinates = NTlist()
    
        for atm in fitAtoms:
            for i in range(0, len(self) ):
                self[i].fitCoordinates.append( atm.coordinates[i] )
            #end for
            self.averageModel.fitCoordinates.append( atm.meanCoordinate )
        #end for
    #end def
    
    def superpose( self, fitAtoms, iterations=2 ):
        # superpose the members of the ensemble using fitAtoms
        # calculate averageModel
        #
        # iteration 0: superpose on model[0]
        # iterations 1-n: calculate average; superpose on average
        #
        # return averageModel or None on error
    
        if len( self) == 0 or len( fitAtoms ) == 0: 
            return None
        #end if
        
        # Assemble the coordinates for the fitting
        self.setFitCoordinates( fitAtoms )

        # iteration 1: fit to first model
        m0 = self[0]
        for m in self[1:]:
            if len(m.fitCoordinates) != len(m0.fitCoordinates):
                return None
            #end if
            m.superpose( m0 )
        #end for
        
        niter = 1
        while ( niter < iterations ):
            av = self.calculateAverageModel()
            for m in self:
                m.superpose( av )
            #end for
            niter = niter + 1
        #end while
        
        return self.calculateAverageModel()
    #end def
    
    def __str__( self ):
        return sprintf( '<Ensemble ("%s", models:%d)>', self.molecule.name, len(self) )
    #end def
        
    def __repr__( self ):
        return str(self)
    #end def

    def format( self ):
        return str( self )
    #end def
#end class


class SuperposeModel( NTcMatrix ):
    """
    SuperposeModel class, rotation translation 4x4  superpose
    
    """
    def __init__( self, name, index ):
        
        NTcMatrix.__init__( self )
        self.name              = name
        self.index             = index
        self.coordinates       = NTlist()  # All coordinate instances of SuperposeModel 
        self.fitCoordinates    = NTlist()  # Coordinates used for fitting
        self.rmsd              = 0.0
    #end def

    def superpose( self, other ):
        """
        Superpose coordinates of self onto other.
        Use vectors of fitCoordinates for superposition.
        return rmsd between self and other using fitCoordinates or -1.0 on Error
        """
        v1 = self.fitCoordinates.zap( 'e' )
        v2 = other.fitCoordinates.zap( 'e' )
        if len(v1) != len(v2):
            NTerror("SuperposeModel.superpose: unequal length fitCoordinates (%s and %s)\n", self, other)
            return -1.0
        #end if

        smtx = superposeVectors( v1, v2 )
        #copy the result to self
        smtx.copy( self )
    
        # transform and calculate rmsd
        self.transform()
        self.rmsd = calculateRMSD( v1, v2 )
        return self.rmsd
    #end def
    
    def calculateRMSD( self, other ):
        """
        Calculate rmsd of fitCoordinates of SuperposeModel with respect to other
        store in rmsd attribute
        return rmsd or -1.0 on Error
        """
        v1 = self.fitCoordinates.zap( 'e' )
        v2 = other.fitCoordinates.zap( 'e' )
        if len(v1) != len(v2):
            NTerror("SuperposeModel.calculateRMSD: unequal length fitCoordinates (%s and %s)\n", self, other)
            return -1.0
        #end if
        self.rmsd = calculateRMSD( v1, v2 )
        return self.rmsd
    #end def
    
    def transform( self ):
        # Transform all coordinates according to rotation/translation matrix
        for c in self.coordinates:
            self.transformVector( c.e )
        #end for
    #end def

    def __str__( self ):
        return sprintf('<SuperposeModel "%s" (coor:%d,fit:%d)>', self.name, len(self.coordinates), len(self.fitCoordinates) )
    #end def
        
    def __repr__( self ):
        return str(self)
    #end def
    
    def format( self ):
        # generate a string representation
        s = sprintf('%s %s %s\n', dots, str(self), dots)
        s = s + "rmsd:  %10.3f\n" %  (self.rmsd, )
        s = s + "matrix:\n%s\n" % (NTcMatrix.__str__(self), )
        return s
    #end def
#end class


#-----------------------------------------------------------------------------
# Superpose routines
#-----------------------------------------------------------------------------
def superpose( molecule, ranges=None, backboneOnly=True, includeProtons = False, 
               iterations=2, verbose = True ):
    """
    Superpose the coordinates of molecule
    returns ensemble or NoneObject on error 
    """

    if not molecule:
        return NoneObject
    #end if

    if molecule.modelCount <= 0:
        return NoneObject
    #end if
    
    ensemble = SuperposeEnsemble( molecule )
    
    # Partition the Atoms
    fitted        = []
    notFitted     = []
    noCoordinates = []
    fitResidues   = molecule.ranges2list( ranges )
    for res in molecule.allResidues():
        fitResidue = res in fitResidues
        for a in res.allAtoms():
            if len(a.coordinates) != molecule.modelCount:
                noCoordinates.append( a )
                continue
            if ( (not fitResidue) or
                 (not includeProtons and a.isProton()) ):
                notFitted.append( a )
                continue
            if backboneOnly and a.isSidechain():
                notFitted.append( a )
            else:
                fitted.append( a )
            #end if
        #end for
    #end for
    
    if verbose:
        NTmessage("==> Superposing: fitting on %d atoms (ranges=%s, backboneOnly=%s, includeProtons=%s)\n", 
                  len(fitted), ranges, backboneOnly, includeProtons
                 )
                 
    ensemble.superpose( fitted, iterations=iterations )
    #molecule.calculateRmsd( ranges=ranges )
    return ensemble
#end def

#add method to Molecule class
Molecule.superpose = superpose


# register the functions
#methods  = []
#saves    = []
#restores = []
#exports  = []

#print '>>at the end'


