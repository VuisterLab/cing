#
#
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import removedir
from cing.Libs.NTutils import NTerror
import time
import os
import random
import sys
todo = """

-copying tlog, log
- looping for accepted structure; but loop is set to 1?
-how to do the seeds!
-different NOE classes handling, combine with evaluation?
-check for multiple dihedral constraints, syntax?
- RDC's

-print output of evaluation directly
-have xplor only print the data (energies, violations etc., run acceptance later
on result

- clean xplor script for variables that can be 'implemented" in python
use dictionaries with setups for  non-bond etc??

Path issues: all relative, defs include '/'? or use path.join (cleaner but less
readable
-Why use enviromental variables directories script/xplor, rather then full paths?

Cluster issues
"""



class Xplor( NTdict ):

    #------------------------------------------------------------------------
    def __init__( self, config, *args, **kwds ):
        NTdict.__init__( self )
        self.update( config )
        for arg in args:
            self.update( arg )
        self.update( kwds )
        
        # check for directories relative to basePath
        self.setdefault( 'basePath', '.')
        for _dirname, dirpath in self.directories.items():
            self.makePath( self.joinPath( dirpath ) )
        #end for
        
        self.script = None

        self.setdefault( 'run_cluster', 'n' )
        self.setdefault( 'queu_cluster', '/usr/local/pbs/bin/qsub -l nodes=1:ppn=1 ')  
        
        self.setdefault( 'seed',          12397 )
        
        self.setdefault( 'overwrite', False )

    #------------------------------------------------------------------------
    def cleanPath( self, path ):
        if not os.path.exists(path):
                os.mkdir(path)
        else:
                removedir(path)
                os.mkdir(path)

    #------------------------------------------------------------------------
    def makePath( self, path ):
        if not os.path.exists(path):
            os.mkdir(path)

    #------------------------------------------------------------------------
    def joinPath( self, *args):
        """Return a path relative to basePath
        """
        return os.path.join( self.basePath, *args )
    #end def
    
    #------------------------------------------------------------------------
    def checkPath( self, *args):
        """Check existance of path relative to basePath
           Returns joined path on success
        """
        path = self.joinPath( *args )
        if not os.path.exists( path ):
            NTerror('Error: path "%s" does not exist\n', path )
            sys.exit(1)
        #end if
        return path
    #end def
        
    #------------------------------------------------------------------------
    def newPath( self, *args):
        """Check existence of joined path, relative to basePath, 
           remove if exists and overwrite
           Return joined path or do a system exit.
        """
        path = self.joinPath( *args )
        if os.path.exists( path ):
            if self.overwrite:
                os.remove( path )
            else:
                NTerror('Error: path "%s" already exists\n', path )        
                sys.exit(1)
            #end if
        #end if
        return path
    #end def

    #------------------------------------------------------------------------
    def setupPTcode( self ):
        """Return code for setup of parameters, topology and structure files"""
        code = '''
{*==========================================================================*}
{*=== READ THE PARAMETER AND TOPOLOGY FILES ================================*}
{*==========================================================================*}

{* Non-bonded parameters; choice: "PROLSQ" "PARMALLH6" "PARALLHDG" "OPLSX"  *}
evaluate ( $par_nonbonded = "''' + self.nonBonded + '''" )
'''
        for filename in self.parameterFiles:
            code = code + """
parameter
  @""" + filename + """
end
""" 
        for filename in self.topologyFiles:
            code = code + """
topology
  @""" + filename + """
end"""     
        return code
        
        
    #------------------------------------------------------------------------        
    def readMolCode( self ):
        """Return code for setup of molecular files"""
        code = """
{*==========================================================================*}
{*=== READ MOLECULAR FILES =================================================*}
{*==========================================================================*}
"""     
        for mol in self.molecules:
            code = code + """
structure
  @""" + self.checkPath( self.directories.psf, mol.psfFile ) + """
end

coordinates
  @""" + self.checkPath( self.inPath, mol.pdbFile ) + """

"""
        #end for
        return code

    #------------------------------------------------------------------------
    def writeMolCode( self ):
        """Return code for writing of molecular files"""
        code = """
{*==========================================================================*}
{*=== WRITE MOLECULAR FILES ================================================*}
{*==========================================================================*}
"""
        for mol in self.molecules:
            code = code + """
write coordinates 
  sele=""" + mol.selectionCode + """ 
  output=""" + self.newPath( self.outPath, mol.pdbFile ) + """ 
end                 
"""
        return code


    #------------------------------------------------------------------------
    def restraintsCode( self ):
        """Return code for restraints"""        
        code = """      
{*==========================================================================*}
{*========================= READ THE EXPERIMENTAL DATA =====================*}
{*==========================================================================*}
set message off echo off end
"""
        if ( len(self.noeRestraints) > 0 ):
            code = code + """
noe reset
  nrestraints = """ + str(self.noeMaxRestraints) + """
  ceiling     = """ + str(self.noeCeiling ) 
  
            for noe in self.noeRestraints:
                noe.setdefault( 'averaging', 'sum' )
                noe.setdefault( 'scale',      50 )
                noe.setdefault( 'sqconstant', 1.0 )
                code = code + """ 
  class      """ + noe.name + """
  averaging  """ + noe.name + ' ' + noe.averaging + """
  potential  """ + noe.name + """ soft
  scale      """ + noe.name + ' ' + str(noe.scale) + """
  sqconstant """ + noe.name + ' ' + str(noe.sqconstant) + """
  sqexponent """ + noe.name + """ 2
  soexponent """ + noe.name + """ 1
  rswitch    """ + noe.name + """ 1.0
  sqoffset   """ + noe.name + """ 0.0
  asymptote  """ + noe.name + """ 2.0
  @@""" + self.checkPath( self.directories.tables, noe.fileName ) + """
"""         
            #end for      
            code = code + """
end
"""     
        #end if

        if ( len(self.dihedralRestraints) > 0 ): 
            code = code + """
restraints dihedral reset 
  nassign = """ + str( self.dihedralMaxRestraints )
  
            for dihed in self.dihedralRestraints:
                code = code + """
  @@""" + self.checkPath( self.directories.tables, dihed.fileName ) + """
  scale   = """ + str(self.dihedralScale)  
            #end for
            code = code + """
end
"""     #end if
        return code
    #end def

    #------------------------------------------------------------------------
    def restraintsAnalysisCode( self ):
        """Return code for restraint analysis"""
        code = """
{*==========================================================================*}
{*======================= CHECK RESTRAINT VIOLATIONS =======================*}
{*==========================================================================*}
evaluate ( $accept = 0 )
evaluate ( $viol.noe.total = 0 )
evaluate ( $viol.cdih.total = 0 )

"""
        if (len( self.noeRestraints) > 0):
            code = code + """
! NOES overall analysis
print threshold=0.5 noe
evaluate ( $viol.noe.viol05 = $violations )
print threshold=0.3 noe
evaluate ( $viol.noe.viol03 = $violations )
print threshold=0.1 noe
evaluate ( $viol.noe.viol01 = $violations )
evaluate ( $rms.noe = $result )

! NOES per category analysis
""" 
# THE NOE RESTRAINT TABLES HAVE TO BE RESET AND READ AGAIN
# TO MAKE THE ANALYSIS OF SEPARATE CLASSES WITH DIFFERENT
# ACCEPTANCE CRITERIA POSSIBLE. THIS IS A WORKAROUND
# XPLOR CANNOT DO IT DIRECTLY
            for noe in self.noeRestraints:
                noe.setdefault( 'averaging', 'sum' )
                noe.setdefault( 'scale',      50 )
                noe.setdefault( 'sqconstant', 1.0 )
                code = code + """
noe reset
  nrestraints = """ + str(self.noeMaxRestraints) + """
  ceiling     = """ + str(self.noeCeiling ) + """

  class      """ + noe.name + """
  averaging  """ + noe.name + ' ' + noe.averaging + """
  potential  """ + noe.name + """ soft
  scale      """ + noe.name + ' ' + str(noe.scale) + """
  sqconstant """ + noe.name + ' ' + str(noe.sqconstant) + """
  sqexponent """ + noe.name + """ 2
  soexponent """ + noe.name + """ 1
  rswitch    """ + noe.name + """ 1.0
  sqoffset   """ + noe.name + """ 0.0
  asymptote  """ + noe.name + """ 2.0
  print threshold = """ + str( noe.accept ) + """
end
evaluate ( $viol.noe.""" + noe.name + """ = $violations )
evaluate ( $viol.noe.total = $violations + $viol.noe.total )

! DIHEDRALS
"""
# DO ALL THE CDIH CLASSES SEPARATELY:
        for dihed in self.dihedralRestraints:
            code = code + """
restraints dihedral reset 
  nassign = """ + str( self.dihedralMaxRestraints ) + """
  @@"""  + self.checkPath( self.directories.tables, dihed.fileName) + """
  scale   = """ + str(self.dihedralScale) + """
end
print threshold = """ + str( dihed.accept ) + """ cdih
evaluate ( $rms.cdih = $result )
evaluate ( $viol.cdih.""" + dihed.name + """ = $violations )
evaluate ( $viol.cdih.total = $viol.cdih.total + $violations )

{*==========================================================================*}
{*======================= CHECK ACCEPTANCE CRITERIA ========================*}
{*==========================================================================*}
    
if ( $viol.cdih.total  > 0 ) then  evaluate ( $accept=$accept + 1 ) end if
if ( $viol.noe.total  > 0 ) then  evaluate ( $accept=$accept + 1 ) end if

if ($accept = 0 ) then
  evaluate ( $label = "ACCEPTED" )
else
  evaluate ( $label = "NOT ACCEPTED" )
end if

"""             
        return code


    #------------------------------------------------------------------------
    def createScript( self ):
        # dummy, to be filled
        self.script = """
{* Script sould be created elsewhere *}
"""
        pass
        
    #------------------------------------------------------------------------
    def printScript( self, stream = sys.stdout ):
        fprintf( stream, self.script )
        
    #------------------------------------------------------------------------
    def runScript( self ):

        # Write script to file
        scriptFileName = self.joinPath(self.directories.jobs, self.jobName + '.inp')
        scriptFile = open( scriptFileName, 'w' )
        self.printScript( scriptFile )
        scriptFile.close()
        NTmessage('==> Created script "%s"\n',  scriptFileName)

        # Create job/log file
        jobFileName = self.joinPath(self.directories.jobs, self.jobName + '.csh') 
        jobFile=open( jobFileName, 'w' )
        logFileName = self.joinPath(self.directories.jobs, self.jobName + '.log') 

        fprintf( jobFile, '#!/bin/tcsh\n' )
        fprintf( jobFile, 'setenv SOLVENT %s\n',           self.protocolsPath )
#        fprintf( jobFile, 'setenv STRUCTURES %s\n',        self.psfPath )
#        fprintf( jobFile, 'setenv TABLES %s\n',            self.tablePath )
#        fprintf( jobFile, 'setenv INPUTCOORDINATES %s\n',  self.inPath )
#        fprintf( jobFile, 'setenv OUTPUTCOORDINATES %s\n', self.outPath )
        fprintf( jobFile, 'cd %s \n', os.getcwd() )
        fprintf( jobFile, '%s < %s > %s  \n', self.XPLOR, scriptFileName, logFileName )
        jobFile.close()

        os.system('/bin/chmod +x %s' % jobFileName)
        NTmessage('==> Starting XPLOR job "%s"\n', jobFileName)

        if self.useCluster:
            NTmessage( 'Sending job to the queu %s\n', self.queu_cluster )
            os.system( '%s %s &' % (self.queu_cluster, jobFileName) )
            time.sleep(5)
        else:
            os.system('%s' % jobFileName )
# ask sander why?
#        os.rename(tlog,log)


    #------------------------------------------------------------------------
    def seed( self ):
        return random.randint(10000,1000000)
        
# END class Xplor -----------------------------------------------------------

#==============================================================================
# Water refinement
# Adapted from Chris Spronk
#==============================================================================
class WaterRefine( Xplor ):

    #------------------------------------------------------------------------
    def __init__( self, config, *args, **kwds ):
    
        Xplor.__init__( self, config, *args, **kwds )
        # set default values if not supplied through args or kwds 
        self.setdefault( 'temp',    500 )
        self.setdefault( 'mdheat',  NTdict( 
                                             nstep  = 100,      # number of MD steps
                                             timest = 0.003,    # timestep of MD (ps)
                                            )
                       )
        self.setdefault( 'mdhot',   NTdict( 
                                             nstep  = 2000,     # number of MD steps
                                             timest = 0.004,    # timestep of MD (ps)
                                            )
                       )
        self.setdefault( 'mdcool',  NTdict( 
                                             nstep  = 200,      # number of MD steps
                                             timest = 0.004,    # timestep of MD (ps)
                                            )
                       )
        self.setdefault( 'inPath',  self.directories.analyzed )
        self.setdefault( 'outPath', self.directories.refined )

        self.keysformat()
        NTmessage('%s\n', self.format())
        #end if

    #------------------------------------------------------------------------
    def createScript( self ):
        """ Create script"""
                
        self.script = """
{*==========================================================================*}
remarks Solvent refinement protocol from ARIA1.2 (Nilges and Linge), 
remarks modified for XPLOR-NIH
{*==========================================================================*}

""" + \
self.setupPTcode() + self.readMolCode() + """   

set message on echo on end

! Set occupancies to 1.00
vector do (Q = 1.00) (all)

! Minimize proton positions to remove problems with wrong stereochemical types
constraints fix=(not hydrogen) end
constraints
  interaction (not resname ANI) (not resname ANI)
  interaction ( resname ANI) ( resname ANI)
end

{*==========================================================================*}
{*================== SET VALUES FOR NONBONDED PARAMETERS ===================*}
{*==========================================================================*}

parameter
nbonds
nbxmod=5 atom cdiel shift
cutnb=9.5 ctofnb=8.5 ctonnb=6.5 eps=1.0 e14fac=0.4 inhibit 0.25
wmin=0.5
tolerance  0.5
end
end

flags exclude * include bond angle impr vdw end
minimize powell nstep=50 nprint=50 end
constraints fix=(not all) end


{*==========================================================================*}
{*============== COPY THE COORDINATES TO THE REFERENCE SET =================*}
{*==========================================================================*}

vector do (refx = x) (all)
vector do (refy = y) (all)
vector do (refz = z) (all)

{*==========================================================================*}
{*========================= GENERATE THE WATER LAYER =======================*}
{*==========================================================================*}

vector do (segid = "PROT") (segid "    ")
@SOLVENT:generate_water.inp
vector do (segid = "    ") (segid "PROT")

""" + \
self.restraintsCode() + """

{*==========================================================================*}
{*============================ SET FLAGS ===================================*}
{*==========================================================================*}

flags exclude *
include bond angle dihe impr vdw elec
        noe cdih coup oneb carb ncs dani
        vean sani dipo prot harm
end

{*==========================================================================*}
{*========================= START THE MD REFINEMENT ========================*}
{*==========================================================================*}

{* Temperature for high-T stage *}
evaluate ( $temperature = """ + str(self.temp) + """ )

set seed """ + str(self.seed()) + """ end

! We loop untill we have an accepted structure, maximum trials=1
evaluate ($end_count = 1)
evaluate ($count = 0)

while ($count < $end_count ) loop main

! since we do not use SHAKe, increase the water bond angle energy constant
parameter
angle (resn tip3) (resn tip3) (resn tip3) 500 TOKEN
end

! reduce improper and angle force constant for some atoms
evaluate ($kbonds = 1000)
evaluate ($kangle = 50)
evaluate ($kimpro = 5)
evaluate ($kchira = 5)
evaluate ($komega = 5)
parameter
angle    (not resn tip3)(not resn tip3)(not resn tip3) $kangle  TOKEN
improper (all)(all)(all)(all) $kimpro  TOKEN TOKEN
end

! fix the protein for initial minimization
constraints fix (not resn tip3) end
minimize powell nstep=500 drop=100 nprint=10 end
 
! release protein and restrain harmonically
constraints fix (not all) end
vector do (refx=x) (all)
vector do (refy=y) (all)
vector do (refz=z) (all)
restraints harmonic
exponent = 2
end
vector do (harmonic = 0)  (all)
vector do (harmonic = 10) (not name h*)
vector do (harmonic = 20.0)(resname ANI and name OO)
vector do (harmonic = 0.0) (resname ANI and name Z )
vector do (harmonic = 0.0) (resname ANI and name X )
vector do (harmonic = 0.0) (resname ANI and name Y )

constraints
interaction (not resname ANI) (not resname ANI)
interaction ( resname ANI) ( resname ANI)
end
    
evaluate ($mini_steps = 10)
evaluate ($mini_step = 1)
while ($mini_step <= $mini_steps) loop mini
  minimize powell nstep=100 drop=10 nprint=50 end
  vector do (refx=x) (not resname ANI)
  vector do (refy=y) (not resname ANI)
  vector do (refz=z) (not resname ANI)
  evaluate ($mini_step=$mini_step+1)
end loop mini


vector do (mass =50) (all)
vector do (mass=1000) (resname ani)
vector do (fbeta = 0) (all)
vector do (fbeta = 20. {1/ps} ) (not resn ani)
evaluate ($kharm = 50)

! heat to high-T temperature
evaluate ($bath = 0)
while ($bath < $temperature) loop heat
evaluate ($bath = $bath + 100)
vector do (harm = $kharm) (not name h* and not resname ANI)
vector do (vx=maxwell($bath)) (all)
vector do (vy=maxwell($bath)) (all)
vector do (vz=maxwell($bath)) (all)
dynamics verlet
        nstep="""  + str(self.mdheat.nstep)  + """
        timest=""" + str(self.mdheat.timest) + """
        tbath=$bath  
        tcoupling = true
        iasvel=current
        nprint=50
end
evaluate ($kharm = max(0, $kharm - 4))
vector do (refx=x) (not resname ANI)
vector do (refy=y) (not resname ANI)
vector do (refz=z) (not resname ANI)
end loop heat

! refinement at high T:
constraints
interaction (not resname ANI) (not resname ANI) weights * 1 dihed 2 end
interaction ( resname ANI) ( resname ANI) weights * 1 end
end

vector do (harm = 0)  (not resname ANI)
vector do (vx=maxwell($bath)) (all)
vector do (vy=maxwell($bath)) (all)
vector do (vz=maxwell($bath)) (all)
dynamics verlet
        nstep="""  + str(self.mdhot.nstep)  + """
        timest=""" + str(self.mdhot.timest) + """
        tbath=$bath  
        tcoupling = true
        iasvel=current
        nprint=50
end

constraints
interaction (not resname ANI) (not resname ANI) weights * 1 dihed 3 end
interaction ( resname ANI) ( resname ANI) weights * 1  end
end


! cool
evaluate ($bath = $temperature)
evaluate ($ncycle = 20)
evaluate ($stepsize = $temperature/$ncycle)
while ($bath >= $stepsize) loop cool

evaluate ($kbonds    = max(225,$kbonds / 1.1))
evaluate ($kangle    = min(200,$kangle * 1.1))
evaluate ($kimpro    = min(200,$kimpro * 1.4))
evaluate ($kchira    = min(800,$kchira * 1.4))
evaluate ($komega    = min(80,$komega * 1.4))

parameter
        bond     (not resn tip3 and not name H*)(not resn tip3 and not name H*) $kbonds  TOKEN
        angle    (not resn tip3 and not name H*)(not resn tip3 and not name H*)(not resn tip3 and not name H*) $kangle  TOKEN
        improper (all)(all)(all)(all) $kimpro  TOKEN TOKEN
        !VAL: stereo CB
        improper (name HB and resn VAL)(name CA and resn VAL)(name CG1 and resn VAL)(name CG2 and resn VAL) $kchira TOKEN TOKEN
        !THR: stereo CB
        improper (name HB and resn THR)(name CA and resn THR)(name OG1 and resn THR)(name CG2 and resn THR) $kchira TOKEN TOKEN
        !LEU: stereo CG
        improper (name HG and resn LEU)(name CB and resn LEU)(name CD1 and resn LEU)(name CD2 and resn LEU) $kchira TOKEN TOKEN
        !ILE: chirality CB
        improper (name HB and resn ILE)(name CA and resn ILE)(name CG2 and resn ILE)(name CG1 and resn ILE) $kchira TOKEN TOKEN
        !chirality CA
        improper (name HA)(name N)(name C)(name CB) $kchira TOKEN TOKEN
        improper (name O)  (name C) (name N) (name CA) $komega TOKEN TOKEN
        improper (name HN) (name N) (name C) (name CA) $komega TOKEN TOKEN
        improper (name CA) (name C) (name N) (name CA) $komega TOKEN TOKEN
        improper (name CD) (name N) (name C) (name CA) $komega TOKEN TOKEN
end

vector do (vx=maxwell($bath)) (all)
vector do (vy=maxwell($bath)) (all)
vector do (vz=maxwell($bath)) (all)
dynamics verlet
        nstep     = """ + str(self.mdcool.nstep)  + """
        timest    = """ + str(self.mdcool.timest) + """
        tbath     = $bath  
        tcoupling = true
        iasvel    = current
        nprint    = 50
end

evaluate ($bath = $bath - $stepsize)
end loop cool


!final minimization:
mini powell nstep=200 nprint=20 end

constraints interaction
(not resname TIP* and not resname ANI)
(not resname TIP* and not resname ANI)
end

energy end

"""  + \
self.restraintsAnalysisCode() + """

if ($accept = 0 ) then
  exit main
else
  evaluate ( $count = $count + 1 )
end if

end loop main

""" + \
self.writeMolCode() + """

stop
"""
        
# END class Refine -----------------------------------------------------------



#==============================================================================
# Initial analysis and minimization
#  DO AN ANALYSIS OF STRUCTURES IN THE XPLOR FORCEFIELD USED FOR
#  REFINEMENT IN EXPLICIT SOLVENT (ADAPTED FROM ARIA1.2)
# Adapted from Chris Spronk
#==============================================================================
class Analyze( Xplor ):

    #------------------------------------------------------------------------
    def __init__( self, config, *args, **kwds ):
    
        Xplor.__init__( self, config, *args, **kwds )
        self.setdefault( 'minimizeProtons', True )        
        self.setdefault( 'inPath',  self.directories.converted )
        self.setdefault( 'outPath', self.directories.analyzed )

        self.keysformat()
        NTmessage('%s\n', self.format())
        #end if

    #------------------------------------------------------------------------
    def createScript( self ):
        """ Create script"""
                
        self.script = """
{*==========================================================================*}
remarks initial analysis refinement protocol 
remarks modified for XPLOR-NIH
{*==========================================================================*}

""" + \
self.setupPTcode() + self.readMolCode() + """   
set message on echo on end 

constraints
  interaction (not resname ANI) (not resname ANI)
  interaction ( resname ANI) ( resname ANI)
end
    
! Set occupancies to 1.00
vector do (Q = 1.00) (all)
"""

        if self.minimizeProtons:
            self.script = self.script + """
! Minimize proton positions to remove problems with wrong stereochemical types from other programs
flags exclude vdw elec end
hbuild selection=(name H*) end
flags include vdw elec end
constraints fix=(not hydrogen) end

minimize powell nstep=500 nprint=50 end

! now minimize the protons in the OPLS force field
{*==========================================================================*}
{*================== SET VALUES FOR NONBONDED PARAMETERS ===================*}
{*==========================================================================*}

parameter
nbonds
repel=0
nbxmod=5 atom cdiel shift
cutnb=9.5 ctofnb=8.5 ctonnb=6.5 eps=1.0 e14fac=0.4 inhibit 0.25
wmin=0.5
tolerance  0.5
end
end

flags exclude * include bond angle impr vdw elec end
minimize powell nstep=500 nprint=50 end
constraints fix=(not all) end
"""

        self.script = self.script + \
self.restraintsCode() + """

{*==========================================================================*}
{*============================ SET FLAGS ===================================*}
{*==========================================================================*}

flags exclude *
include bond angle dihe impr vdw elec
        noe cdih coup oneb carb ncs dani
        vean sani dipo prot harm
end

! FIRST Do an optimization of the alignment tensors
! fix the protein
constraints fix (not resn ani) end

! restrain ANI harmonically
vector do (refx=x) (resname ani)
vector do (refy=y) (resname ani)
vector do (refz=z) (resname ani)
restraints harmonic
exponent = 2
end
vector do (harmonic = 20.0)(resname ANI and name OO)
vector do (harmonic = 0.0) (resname ANI and name Z )
vector do (harmonic = 0.0) (resname ANI and name X )
vector do (harmonic = 0.0) (resname ANI and name Y )

constraints
interaction ( resname ANI) ( resname ANI)
end
    
minimize powell nstep=100 drop=10 nprint=50 end
minimize powell nstep=100 drop=10 nprint=50 end

constraints interaction
  (not resname TIP* and not resname ANI)
  (not resname TIP* and not resname ANI)
end

energy end

""" + \
self.restraintsAnalysisCode() + \
self.writeMolCode() + """

stop
"""
            
# END class Analyze------------------------------------------------------------



#==============================================================================
# Generate psf-file
#==============================================================================
class GeneratePSF( Xplor ):

    #------------------------------------------------------------------------
    def __init__( self, config, *args, **kwds ):
    
        Xplor.__init__( self, config, *args, **kwds )
        self.setdefault( 'patchHISD', [] )
        self.setdefault( 'patchHISE', [] )
        self.setdefault( 'patchCISP', [] )
        # make relative Path
        self.pdbFile = self.checkPath( self.directories.converted, self.pdbFile )
        self.psfFile = self.newPath( self.directories.psf, self.psfFile )

        self.keysformat()
        NTmessage('%s\n', self.format())
    #endif

    #------------------------------------------------------------------------
    def createScript( self ):
        """ Create script"""
        
        self.script = """
{*==========================================================================*}
remarks Generation of psf-file
remarks modified for XPLOR-NIH
{*==========================================================================*}
""" + \
self.setupPTcode() + """   
set message on echo on end 

segment
  chain 
    @""" + os.path.realpath(os.path.join(self.topparPath,'topallhdg5.3.pep')) + """
    coord @""" + self.pdbFile + """
  end
end
"""
        for resid in self.patchHISD:
            self.script = self.script + """
patch HISD 
   reference=nil=( resid """ + str(resid) + """ ) 
end
"""
        for resid in self.patchHISE:
            self.script = self.script + """
patch HISE 
   reference=nil=( resid """ + str(resid) + """ ) 
end
"""
        for resid in self.patchCISP:
            self.script = self.script + """
patch CISP
   reference=nil=( resid """ + str(resid) + """ ) 
end
"""

        self.script = self.script + """
write psf output=""" + self.psfFile  + """ end 

stop 
""" 
  
# END class GeneratePSF---------------------------------------------------------
  
