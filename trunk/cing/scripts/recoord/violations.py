#!/usr/bin/env python

from string import join
from sys    import argv,exit
import math

def average( x ): return sum( x ) / len( x )
def stdev( x ):   return math.sqrt( ( sum( map( lambda y:y**2, x ) ) - sum(x)**2 / len(x) ) / ( len(x) - 1 ) )
def angleaverage( x ):
    y = map( lambda z: z * math.pi / 180, x )
    aver = math.atan2( sum( map( math.sin, y ) ) / len( y ) , sum( map( math.cos, y ) ) / len( y ) )
    return 180 * aver / math.pi

class Restraint:
    def __init__( self, num ):
        self.num         = num # Model number 
        self.atoms       = []  # Atom tuples
        self.ids         = []  # Restraint IDs
        self.restraints  = []  # Restraint values
        self.values      = []  # Actual values
        self.delta       = []  # Violations
        self.nrestraints = 0

    def __len__( self ):
        return len( self.delta )

class Noe(Restraint):
    def __init__( self, num, f ):
        Restraint.__init__( self, num )
        self.fill( f )

    def fill( self, f ):
        l = f.readline()

        while not l.startswith( "</NOE" ):
            if l.startswith( " ========== spectrum" ):
                # Indicates new noe entry
                #01234567890123456789012345678901234567890123456789012
                # ========== spectrum     1 restraint     1 ==========

                id = int( l[36:42] )
                self.ids.append( id )

                iatoms = []
                jatoms = []
    
                f.readline() # set-i-atoms
                l = f.readline()
                while not l.strip().startswith( "set-j-atoms" ):
                    iatoms.append( tuple(l.split()) )
                    l = f.readline()
                l = f.readline()
                while not l.strip().startswith( "R<average>=" ):
                    jatoms.append( tuple(l.split()) )
                    l = f.readline()
                self.atoms.append( ( tuple( iatoms ), tuple( jatoms ) ) )

                #            ||||||||     |||||                       ||||||||
                #01234567890123456789012345678901234567890123456789012345678901234567890
                # R<average>=   2.739 NOE= 2.56 (- 0.76/+ 0.00) Delta=  -0.183  E(NOE)=   1.672
                self.delta.append( float( l[53:61] ) )
                self.restraints.append( float( l[12:20] ) )
                self.values.append( float( l[25:30] ) )
                
            if l.startswith( " NOEPRI:" ):
                self.nrestraints = int( l.split()[-2] )
                l = f.readline()
                
            l = f.readline()

        dlen = range(len(self.delta))
        self.rms  = math.sqrt( sum( map( lambda x: x**2, self.delta ) ) / self.nrestraints )
        self.max  = min( [0]+self.delta ) # Maximum deviation ;P
        self.sum  = sum( map( lambda x: x <    0 and x or 0, self.delta ) ) # Sum of negative violations
        self.id0  = filter( lambda x: self.delta[x] <  0.0, dlen )
        self.nr0  = len( self.id0 )
        self.id3  = filter( lambda x: self.delta[x] < -0.3, dlen ) # Count violations < 0.3
        self.nr3  = len( self.id3 )
        self.id5  = filter( lambda x: self.delta[x] < -0.5, dlen ) # Count violations < 0.5
        self.nr5  = len( self.id5 )
        self.id10 = filter( lambda x: self.delta[x] < -1.0, dlen ) # Count violations < 1.0
        self.nr10 = len( self.id10 )
        self.id20 = filter( lambda x: self.delta[x] < -2.0, dlen ) # Count violations < 2.0
        self.nr20 = len( self.id20 )

        self.ok   = not self.nr10

    def __repr__( self ):
        return "%5d   %5d   %5d  %5.2f %6.3f %6.3f %6.4f   %5d   %5d   %5d   %5d   %5d" % (
               self.num, self.nrestraints, len( self.delta ), 100.*len( self.delta )/self.nrestraints,
               self.max, self.sum, self.rms, self.nr0, self.nr3, self.nr5, self.nr10, self.nr20 )
                        
class Dihre(Restraint):
    def __init__( self, num, f ):
        Restraint.__init__( self, num )

        self.fill( f )

    def fill( self, f ):
        l = f.readline()

        while not l.startswith( "</DIHEDRAL" ):
            if l.startswith( " ==========" ):
                # Indicates new dihedral entry
                ai = join( f.readline().split(), ":" )
                aj = join( f.readline().split(), ":" )
                ak = join( f.readline().split(), ":" )
                al = join( f.readline().split(), ":" )
                
                self.ids.append( (ai,aj,ak,al) )

                l = f.readline()
                #          |-------|                                     |-------|       |-------|
                #          1         2         3         4         5         6         7         8
                #012345678901234567890123456789012345678901234567890123456789012345678901234567890
                # Dihedral= -140.704  Energy=    0.000 C=    1.000 Equil= -120.000 Delta=    0.704
                self.values.append( float( l[10:19] ) )
                self.restraints.append( float( l[56:65] ) )
                self.delta.append( float( l[72:81] ))

            if l.startswith( " Number of dihedral angle restraints" ): self.nrestraints = int( l.split("=")[1] )
            if l.startswith( " RMS deviation" ): self.rms = float( l.split("=")[1] )
            
            l = f.readline()

        dlen      = range(len(self.delta))
        delta2    = map( lambda x: x**2, self.delta )
        self.max  = math.sqrt( max( map( lambda x: x**2, self.delta ) ) )   # Maximum deviation
        self.id0  = filter( lambda x: delta2[x] > 0.0, dlen ) # Count violations
        self.nr0  = len( self.id0 )
        self.id5  = filter( lambda x: delta2[x] >  25, dlen ) # Count violations >  5 degrees
        self.nr5  = len( self.id5 )
        self.id10 = filter( lambda x: delta2[x] > 100, dlen ) # Count violations > 10 degrees
        self.nr10 = len( self.id10 )
        self.id20 = filter( lambda x: delta2[x] > 400, dlen ) # Count violations > 20 degrees
        self.nr20 = len( self.id20 )

    def __repr__( self ):
        return "%5d   %5d   %5d  %5.2f %6.3f %6.4f   %5d   %5d   %5d   %5d" % (
               self.num, self.nrestraints, len( self.delta ), 100.*len( self.delta )/self.nrestraints,
               self.max, self.rms, self.nr0, self.nr5, self.nr10, self.nr20 )

### MAIN ###
    
noes      = []
dihedrals = []

# Reading the CNS log file(s)


for arg in argv[1:]:
    log = open( arg )

    l = log.readline()
    while l:
        if l.startswith( "<NOE" ):
            # <NOE 1>
            noes.append( Noe( int( l.split()[1][:-1] ), log ) )
        if l.startswith( "<DIHEDRAL" ):
            # <DIHEDRAL 1>
            dihedrals.append( Dihre( int( l.split()[1][:-1] ), log ) )
        l = log.readline()
    log.close()

### DOING NOES ###

nmodels = len( noes )
print "========NOES=========="
print "Model Restraints #Viol %Viol MaxDev SumDev RMSDev Dev<-0.0 Dev<-0.3 Dev<-0.5 Dev<-1.0 Dev<-2.0"
for i in range( nmodels ):
    print noes[i]

rmod   = range( nmodels )
trest  = sum( map( lambda x: noes[x].nrestraints, rmod ) )
nviol  = sum( map( lambda x: len(noes[x]), rmod ) )
rviol  = 100. * nviol / trest
maxdev = average( map( lambda x: noes[x].max, rmod ) )
sumdev = sum( map( lambda x: noes[x].sum, rmod ) )
averms = average( map( lambda x: noes[x].rms, rmod ) )
stdv   = stdev( map( lambda x: noes[x].rms, rmod ) )

print "=======SUMMARY========="
print "Total Restraints #Viol %Viol AveMaxDev TotSumDev AveRMSDev RMSDevDev"
print "%5d   %5d   %5d  %5.2f   %6.4f  %8.3f  %8.3f  %8.5f\n" % (
      nmodels, trest, nviol, rviol, maxdev, sumdev, averms, stdv )

count0  = {}
count3  = {}
count5  = {}
count10 = {}
count20 = {}
for i in noes:
    for id in i.id0:  count0[ id ]  = count0.get( id, 0 )  + 1
    for id in i.id3:  count3[ id ]  = count3.get( id, 0 )  + 1
    for id in i.id5:  count5[ id ]  = count5.get( id, 0 )  + 1
    for id in i.id10: count10[ id ] = count10.get( id, 0 ) + 1
    for id in i.id20: count20[ id ] = count20.get( id, 0 ) + 1

nm   = nmodels/2
nc0  = len( filter( lambda x: x > nm, count0.values()  ) )
nc3  = len( filter( lambda x: x > nm, count3.values()  ) )
nc5  = len( filter( lambda x: x > nm, count5.values()  ) )
nc10 = len( filter( lambda x: x > nm, count10.values() ) )
nc20 = len( filter( lambda x: x > nm, count20.values() ) )

print "Consistent violations:"
print "  < 0.0   <-0.3   <-0.5   <-1.0   <-2.0"
print "  %5d   %5d   %5d   %5d   %5d" % ( nc0, nc3, nc5, nc10, nc20 )

# Overall criterion
ok = not 0 in map( lambda x: noes[x].nr5, rmod )
               
### DOING DIHEDRAL RESTRAINTS ###

nmodels = len( dihedrals )
print "\n\n======DIHEDRALS======="
print "Model Restraints #Viol %Viol MaxDev RMSDev Dev>0.0 Dev>5 Dev>10 Dev>20"
for i in range( nmodels ):
    print dihedrals[i]

rmod   = range( nmodels )
trest  = sum( map( lambda x: dihedrals[x].nrestraints, rmod ) )
nviol  = sum( map( lambda x: len(dihedrals[x]), rmod ) )
rviol  = 100. * nviol / trest
maxdev = average( map( lambda x: dihedrals[x].max, rmod ) )
averms = average( map( lambda x: dihedrals[x].rms, rmod ) )
stdv   = stdev( map( lambda x: dihedrals[x].rms, rmod ) )

print "=======SUMMARY========="
print "Total Restraints #Viol %Viol AveMaxDev AveRMSDev RMSDevDev"
print "%5d   %5d   %5d  %5.2f   %6.4f  %8.3f  %8.5f\n" % (
      nmodels, trest, nviol, rviol, maxdev, averms, stdv )

count0  = {}
count5  = {}
count10 = {}
count20 = {}
for i in dihedrals:
    for id in i.id0:  count0[ id ]  = count0.get( id, 0 )  + 1
    for id in i.id5:  count5[ id ]  = count5.get( id, 0 )  + 1
    for id in i.id10: count10[ id ] = count10.get( id, 0 ) + 1
    for id in i.id20: count20[ id ] = count20.get( id, 0 ) + 1

nm   = nmodels/2
nc0  = len( filter( lambda x: x > nm, count0.values()  ) )
nc5  = len( filter( lambda x: x > nm, count5.values()  ) )
nc10 = len( filter( lambda x: x > nm, count10.values() ) )
nc20 = len( filter( lambda x: x > nm, count20.values() ) )

print "Consistent violations:"
print "    > 0    > 5   > 10   > 20"
print "  %5d  %5d  %5d  %5d" % ( nc0, nc5, nc10, nc20 ) 

# Overall check: return 0 if any of the models has no violations < -0.5A
exit( ok )
