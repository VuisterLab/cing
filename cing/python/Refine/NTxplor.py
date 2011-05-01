from cing.Libs.NTutils import * #@UnusedWildImport

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
use dictionaries with setups for non-bond etc??

Path issues: all relative, defs include '/'? or use path.join (cleaner but less
readable
-Why use environmental variables directories script/xplor, rather then full paths?

Cluster issues
"""

#------------------------------------------------------------------------------

class refineParameters( NTdict ):

    def __init__(self, **kwds):
        NTdict.__init__( self, __CLASS__ = "refineParameters",

      baseName          = 'model%03d.pdb',      # Basename used for pdb files
      models            = '',
      overwrite         = False,                # Overwrite existing files
      verbose           = False,                # verbose on/off
      useCluster        = False,                # use cluster; not yet implemented

      # PSF generation
      psfFile           = 'name.psf',
      patchHISD         = [],                   # HISD patches are needed for CYANA->XPLOR compatibility.
      patchHISE         = [],                   # HISE patches are needed for CYANA->XPLOR compatibility.
      patchCISP         = [],                   # Cis prolines
      patchDISN         = [],                   # Disulfide pairs

      # initial analysis, The advantage of doing this is that missing protons will not cause a bombed out xplor
      # Disadvantage is that violations might differ if SSA is incompatible with IUPAC.
      minimizeProtons   = True,

      # NOE restraints
      noeMaxRestraints  = 30000,
      noeCeiling        = 100,
      noeRestraints     = [],                   # Noe restraint lists, should be in the Tables directory

      # dihedral restraints
      dihedralMaxRestraints = 10000,
      dihedralScale      = 200,
      dihedralRestraints = [],                  # dihedral restraint lists, should be in the Tables directory

      # water refinement protocol
      # type of non-bonded parameters: "PROLSQ" "PARMALLH6" "PARALLHDG" "OPLSX"
      # The water refinement uses the OPLSX parameters
      nonBonded         = 'OPLSX',
      temp              = 500,                  # temperature (K); 500 initially
      mdheat            = NTdict( # 100,0.003 initially with Chris
                                    nstep  = 100,       # number of MD steps
                                    timest = 0.003,     # timestep of MD (ps)
                                ),
      mdhot             = NTdict( # 2000, 0.004 initially with Chris
                                    nstep  = 2000,      # number of MD steps
                                    timest = 0.004,     # timestep of MD (ps)
                                  ),
      mdcool            = NTdict( # 200, 0.004 initially with Chris
                                    nstep  = 200,       # number of MD steps
                                    timest = 0.004,     # timestep of MD (ps)
                                 ),

      # Analysis
      bestModels        = '',
      superpose         = '',

      # Run time
      inPath            = '',       # Run time, no need to edit
      outPath           = '',       # Run time, no need to edit
      basePath          = '',       # Run time, no need to edit

      __FORMAT__ = """
parameters = refineParameters(
      baseName          = "%(baseName)s",

      # ascii list to select the model(s) to refine; e.g 0-19
      # can also be modified as command-line argument
      models            = '%(models)s',

      # Overwrite existing files
      overwrite         = %(overwrite)s,
      # verbose on/off
      verbose           = %(verbose)s,
      # use cluster; not yet implemented
      useCluster        = %(useCluster)s,

      # PSF generation
      psfFile           = "%(psfFile)s",
      # HISD patches are needed for CYANA->XPLOR compatibility; enter your residue numbers here
      patchHISD         = %(patchHISD)s,
      # HISE patches are needed for CYANA->XPLOR compatibility; enter your residue numbers here
      patchHISE         = %(patchHISE)s,
      # Cis-proline patches are needed for CYANA->XPLOR compatibility; enter your residue numbers here
      patchCISP         = %(patchCISP)s,
      # Disulfide pairs
      patchDISN         = %(patchDISN)s,

      # initial analysis
      minimizeProtons   = %(minimizeProtons)s,

      # NOE restraints
      noeMaxRestraints  = %(noeMaxRestraints)s,
      noeCeiling        = %(noeCeiling)s,
      # Noe restraint lists, should be in the Tables directory
      noeRestraints     = %(noeRestraints)r,

      # dihedral restraints
      dihedralMaxRestraints = %(dihedralMaxRestraints)s,
      dihedralScale      = %(dihedralScale)s,
      # dihedral restraint lists, should be in the Tables directory
      dihedralRestraints = %(dihedralRestraints)r,

      # water refinement protocol
      # type of non-bonded parameters: "PROLSQ" "PARMALLH6" "PARALLHDG" "OPLSX"
      # The water refinement uses the OPLSX parameters
      nonBonded         = "%(nonBonded)s",
      # temperature (K); 500 initially
      temp              = %(temp)s,
      # nstep: number of MD steps; timest: # timestep of MD (ps)
      mdheat            = %(mdheat)r,            # 100,  0.003 initially with Chris
      mdhot             = %(mdhot)r,             # 2000, 0.004 initially with Chris
      mdcool            = %(mdcool)r,            # 200, 0.004 initially with Chris

      # analysis
      # bestModels; asciilist, e.g. '3,4,1,7,20,5'; typically generated by --best option
      bestModels        = "%(bestModels)s",
      # Superpose residues; asciilist e.g. 200-270,276-300,320-350
      superpose         = "%(superpose)s",

      # Run time, no need to edit
      # basePath        = %(basePath)s
      # inPath          = %(inPath)s
      # outPath         = %(outPath)s
)
"""
)
        if kwds:
            self.update( kwds )
    #end def

    def toFile( self, path ):
        f = open( path, 'w' )
        fprintf( f, '%s', self )
        f.close()
    #end def

    def __str__( self ):
        return self.format()
    #end def
#end class

class refineNoeParameters( NTdict ):
    def __init__( self, name, **kwds ):
        NTdict.__init__( self, __CLASS__ = "refineNoeParameters",

                         name      = name,
                         averaging = 'sum',
                         scale     = 50,
                         accept    = 0.5,
                         fileName  = name+'.tbl',  # should be in the Tables directory

                         __FORMAT__ = """
                            refineNoeParameters(
                                    name      = "%(name)s",
                                    averaging = "%(averaging)s",
                                    scale     = %(scale)s,
                                    accept    = %(accept)s,
                                    fileName  = "%(fileName)s" \t# should be in the Tables directory
                                  )
                            """
)

        if kwds:
            self.update( kwds )
    #end def

    def __str__( self ):
        return self.format()
    #end def
    def __repr__( self ):
        return self.format()
    #end def
#end class

class refineDihedralParameters( NTdict ):
    def __init__( self, name, **kwds ):
        NTdict.__init__( self, __CLASS__ = "refineDihedralParameters",

                         name      = name,
                         accept    = 5.0,
                         fileName  = name+'.tbl',  # should be in the Tables directory

                         __FORMAT__ = """
                            refineDihedralParameters(
                                    name      = "%(name)s",
                                    accept    = %(accept)s,
                                    fileName  = "%(fileName)s" \t# should be in the Tables directory
                                  )
                            """
)

        if kwds:
            self.update( kwds )
    #end def

    def __str__( self ):
        return self.format()
    #end def
    def __repr__( self ):
        return self.format()
    #end def
#end class


class Xplor( refineParameters ):

    #------------------------------------------------------------------------
    def __init__( self, config, *args, **kwds ):
        refineParameters.__init__( self )
        self.update( config )
        for arg in args:
            self.update( arg )
        self.update( kwds )

        # check for directories relative to basePath
        self.setdefault( 'basePath', '.')
        for dummy_dirname, dirpath in self.directories.items():
            self.makePath( self.joinPath( dirpath ) )
        #end for

        self.script = None

        self.setdefault( 'run_cluster', 'n' )
        self.setdefault( 'queu_cluster', '/usr/local/pbs/bin/qsub -l nodes=1:ppn=1 ')

        self.setdefault( 'seed',          12397 )

        self.setdefault( 'overwrite', False )
        self.setdefault( 'verbose', True )

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
            os.makedirs(path)

    #------------------------------------------------------------------------
    def joinPath( self, *args):
        """Return a path relative to basePath
        """
        return os.path.join( self.basePath, *args )
    #end def

    #------------------------------------------------------------------------
    def checkPath( self, *args):
        """Check existence of path relative to basePath
           Returns joined path on success
        """
        path = self.joinPath( *args )
        if not os.path.exists( path ):
            NTerror('path "%s" does not exist', path )
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
                NTerror('path "%s" already exists; use --overwrite', path )
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
  @""" + self.joinPath( self.directories.toppar, filename ) + """
end
"""
        for filename in self.topologyFiles:
            code = code + """
topology
  @""" + self.joinPath( self.directories.toppar, filename ) + """
end"""
        return code


    #------------------------------------------------------------------------
    def readMolCode( self, useCoordinates = True ):
        """Return code for setup of molecular files"""
        code = """
{*==========================================================================*}
{*=== READ MOLECULAR FILES =================================================*}
{*==========================================================================*}
"""
        for mol in self.molecules:
            code += "structure @%s end\n" % self.checkPath( self.directories.psf, mol.psfFile )
            if useCoordinates: # end is in PDB file.
                code += "coordinates @%s\n" % self.checkPath( self.inPath, mol.pdbFile )
            # end if
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
        """Return code for restraint analysis.
        Returns False on error. Needs to be False (not None).
        """
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
#                maxlength = 20 - len('viol.noe.')
                if len(noe.name) > MAX_SIZE_XPLOR_RESTRAINT_LIST_NAME:
                    NTerror("NOE list name is over %s chars and xplor wouldn't be able to handle it: [%s]" % (MAX_SIZE_XPLOR_RESTRAINT_LIST_NAME, noe.name))
                    return False
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
#            maxlength = 20 - len('viol.cdih.')
            if len(dihed.name) > MAX_SIZE_XPLOR_RESTRAINT_LIST_NAME:
                NTerror("Dihedral angle list name is over %s chars and xplor wouldn't be able to handle it: [%s]" % (MAX_SIZE_XPLOR_RESTRAINT_LIST_NAME, dihed.name))
                return False
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
        if self.verbose:
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
        fprintf( jobFile, 'cd %r \n', os.getcwd() )
        fprintf( jobFile, '%r < %r > %r  \n', self.XPLOR, scriptFileName, logFileName )
        jobFile.close()

        os.system('/bin/chmod +x %r' % jobFileName)
        if self.verbose:
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
        return randint(10000,1000000)

# END class Xplor -----------------------------------------------------------

#==============================================================================
# Water refinement
# Adapted from Chris Spronk
#==============================================================================
class WaterRefine( Xplor ):

    #------------------------------------------------------------------------
    def __init__( self, config, *args, **kwds ):

        Xplor.__init__( self, config, *args, **kwds )
        self.inPath  = self.directories.analyzed
        self.outPath = self.directories.refined

        if self.verbose:
            #self.keysformat()
            NTmessage('%s\n', self.format())
        #end if

    #------------------------------------------------------------------------
    def createScript( self ):
        """ Create script.
        Return True on error.
        """


        restraintsAnalysisCode = self.restraintsAnalysisCode()
        if None in [ restraintsAnalysisCode ]:
            NTerror("In WaterRefine#createScript: Failed to generate code for at least one part.")
            return True


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

! We loop until we have an accepted structure, maximum trials=1
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
restraintsAnalysisCode + """

if ($accept = 0 ) then
  exit main
else
  evaluate ( $count = $count + 1 )
end if

end loop main

""" + \
self.writeMolCode() + """

set message on echo on end

stop
"""

# END class WaterRefine -----------------------------------------------------------

#==============================================================================
# Quick and fast anneal
# Adapted from anneal.py fro
#==============================================================================
class Anneal( Xplor ):

    #------------------------------------------------------------------------
    def __init__( self, config, *args, **kwds ):
        Xplor.__init__( self, config, *args, **kwds )
        if self.verbose:
            #self.keysformat()
            NTmessage('%s\n', self.format())
        #end if
    #end if
    def createScript( self ):
        """ Create script.
        Return True on error.
        """


        restraintsAnalysisCode = self.restraintsAnalysisCode()
        if None in [ restraintsAnalysisCode ]:
            NTerror("In WaterRefine#createScript: Failed to generate code for at least one part.")
            return True


        self.script = """
{*==========================================================================*}
remarks Anneal protocol adapted from tutorial/nmr/sa_new.inp
remarks in XPLOR-NIH (Charles D. Schwieters)
remarks by Jurgen F. Doreleijers 2011-04-30
{*==========================================================================*}

""" + \
self.setupPTcode() + self.readMolCode() + """

set message on echo on end

remarks file  nmr/sa.inp
remarks  Simulated annealing protocol for NMR structure determination.
remarks  The starting structure for this protocol can be any structure with
remarks  a reasonable geometry, such as randomly assigned torsion angles or
remarks  extended strands.
remarks  Author: Michael Nilges

{====>}
evaluate ($init_t = 1000 )       {*Initial simulated annealing temperature.*}
{====>}
evaluate ($high_steps= 24000 )         {*Total number of steps at high temp.*}
{====>}
evaluate ($cool_steps = 3000 )      {*Total number of steps during cooling.*}


noe
{====>}
   nres=3000             {*Estimate greater than the actual number of NOEs.*}
   class all
{====>}
   @il8_noe.tbl                           {*Read NOE distance ranges.*}
   @il8_hbonds.tbl
end

{====>}
restraints dihedral
   nass = 1000
   @il8_dihe.tbl                       {*Read dihedral angle restraints.*}
end


{* Reduce the scaling factor on the force applied to disulfide            *}
{* bonds and angles from 1000.0 to 100.0 in order to reduce computation instability. *}
parameter
      bonds ( name SG ) ( name SG ) 100. TOKEN
      angle ( name CB ) ( name SG ) ( name SG ) 50. TOKEN
end


flags exclude * include bonds angle impr vdw noe cdih end

                        {*Friction coefficient for MD heatbath, in 1/ps.   *}
vector do (fbeta=10) (all)
                        {*Uniform heavy masses to speed molecular dynamics.*}
vector do (mass=100) (all)

noe                             {*Parameters for NOE effective energy term.*}
  ceiling=1000
  averaging  * cent
  potential  * soft
  scale      * 50.
  sqoffset   * 0.0
  sqconstant * 1.0
  sqexponent * 2
  soexponent * 1
  asymptote  * 0.1                         {*Initial value--modified later.*}
  rswitch    * 0.5
end

parameter                       {*Parameters for the repulsive energy term.*}
    nbonds
      repel=1.                   {*Initial value for repel--modified later.*}
      rexp=2 irexp=2 rcon=1.
      nbxmod=3
      wmin=0.01
      cutnb=4.5 ctonnb=2.99 ctofnb=3.
      tolerance=0.5
   end
end

restraints dihedral
      scale=5.
end

coor copy end

set seed """ + str(self.seed()) + """ end

! We loop until we have an accepted structure, maximum trials=1
evaluate ($end_count = 1)
evaluate ($count = 0)

while ($count < $end_count ) loop main

    coor swap end
    coor copy end

      {* ============================================= Initial minimization.*}
    restraints dihedral   scale=5.   end
    noe asymptote * 0.1  end
    parameter  nbonds repel=1.   end end
    constraints interaction
            (all) (all) weights * 1  vdw 0.002 end end
    minimize powell nstep=50 drop=10.  nprint=25 end


      {* ======================================== High-temperature dynamics.*}
    constraints interaction (all) (all)
                weights * 1  angl 0.4  impr 0.1 vdw 0.002 end end

    evaluate ($nstep1=int($high_steps * 2. / 3. ) )
    evaluate ($nstep2=int($high_steps * 1. / 3. ) )

    dynamics  verlet
       nstep=$nstep1   timestep=0.005   iasvel=maxwell   firstt=$init_t
       tcoupling=true  tbath=$init_t  nprint=50  iprfrq=0
    end


      {* ============== Tilt the asymptote and increase weights on geometry.*}
    noe asymptote * 1.0  end

    constraints interaction
               (all) (all) weights * 1  vdw 0.002  end end

    {* Bring scaling factor for S-S bonds back *}
    parameter
       bonds ( name SG ) ( name SG ) 1000. TOKEN
       angle ( name CB ) ( name SG ) ( name SG ) 500. TOKEN
    end

    dynamics  verlet
       nstep=$nstep2   timestep=0.005    iasvel=current   tcoupling=true
       tbath=$init_t  nprint=50  iprfrq=0
    end

     {* ==================================================  Cool the system.*}

    restraints dihedral   scale=200.   end

    evaluate ($final_t = 100)      { K }
    evaluate ($tempstep = 50)      { K }

    evaluate ($ncycle = ($init_t-$final_t)/$tempstep)
    evaluate ($nstep = int($cool_steps/$ncycle))

    evaluate ($ini_rad  = 0.9)        evaluate ($fin_rad  = 0.75)
    evaluate ($ini_con=  0.003)       evaluate ($fin_con=  4.0)

    evaluate ($bath  = $init_t)
    evaluate ($k_vdw = $ini_con)
    evaluate ($k_vdwfact = ($fin_con/$ini_con)^(1/$ncycle))
    evaluate ($radius=    $ini_rad)
    evaluate ($radfact = ($fin_rad/$ini_rad)^(1/$ncycle))

    evaluate ($i_cool = 0)
    while ($i_cool < $ncycle) loop cool
       evaluate ($i_cool=$i_cool+1)

       evaluate ($bath  = $bath  - $tempstep)
       evaluate ($k_vdw=min($fin_con,$k_vdw*$k_vdwfact))
       evaluate ($radius=max($fin_rad,$radius*$radfact))

       parameter  nbonds repel=$radius   end end
       constraints interaction (all) (all)
                      weights * 1. vdw $k_vdw end end

       dynamics  verlet
          nstep=$nstep time=0.005 iasvel=current firstt=$bath
          tcoup=true tbath=$bath nprint=$nstep iprfrq=0
       end


    {====>}                                                  {*Abort condition.*}
       evaluate ($critical=$temp/$bath)
       if ($critical >  10. ) then
          display  ****&&&& rerun job with smaller timestep (i.e., 0.003)
          stop
       end if

    end loop cool

    {* ================================================= Final minimization.*}

    constraints interaction (all) (all) weights * 1. vdw 1. end end
    parameter
       nbonds
          repel=0.80
          rexp=2 irexp=2 rcon=1.
          nbxmod=3
          wmin=0.01
          cutnb=6.0 ctonnb=2.99 ctofnb=3.
          tolerance=1.5
       end
    end

    minimize powell nstep=1000 drop=10.0 nprint=25 end
"""  + \
restraintsAnalysisCode + """

if ($accept = 0 ) then
  exit main
else
  evaluate ( $count = $count + 1 )
end if

end loop main

""" + \
self.writeMolCode() + """

set message on echo on end

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
        self.inPath  = self.directories.converted
        self.outPath = self.directories.analyzed

        if self.verbose:
            #self.keysformat()
            NTmessage('%s\n', self.format())
        #end if

    #------------------------------------------------------------------------
    def createScript( self ):
        """ Create script"""

        restraintsAnalysisCode = self.restraintsAnalysisCode()
        if False in [ restraintsAnalysisCode ]:
            NTerror("In Analyze#createScript: Failed to generate code for at least one part.")
            return True

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
restraintsAnalysisCode + \
self.writeMolCode() + """

set message on echo on end

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
        # make relative Path
        self.pdbFile = self.checkPath( self.directories.converted, self.pdbFile )
        self.psfFile = self.newPath( self.directories.psf, self.psfFile )

        if self.verbose:
            #self.keysformat()
            NTmessage('%s\n', self.format())
        #end if
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
    @""" + self.joinPath( self.directories.toppar,'topallhdg5.3.pep') + """
    coord @""" + self.pdbFile + """
  end
end

"""
        for pair in self.patchDISN:
            self.script += "patch DISN  reference=1  =( resid %s )  reference=2=( resid %s )        end\n" % pair
        for resid in self.patchHISD:
            self.script += "patch HISD  reference=nil=( resid %s ) end\n" % resid
        for resid in self.patchHISE:
            self.script += "patch HISE  reference=nil=( resid %s ) end\n" % resid
        for resid in self.patchCISP:
            self.script += "patch CISP  reference=nil=( resid %s ) end\n" % resid

        self.script += """
write psf output=""" + self.psfFile  + """ end

set message on echo on end

stop
"""

# END class GeneratePSF---------------------------------------------------------




#==============================================================================
# Generate extended structure
#==============================================================================
class GenerateTemplate( Xplor ):

    #------------------------------------------------------------------------
    def __init__( self, config, *args, **kwds ):
        NTmessage("a")

        Xplor.__init__( self, config, *args, **kwds )
        # make relative Path
        self.psfFile = self.checkPath( self.directories.psf, self.psfFile )
#        self.outPath = self.directories.template
        if self.verbose:
            #self.keysformat()
            NTmessage('%s\n', self.format())
        #end if
    #endif

    #------------------------------------------------------------------------
    def createScript( self ):
        """ Create script.
        Return True on error.
        """

        self.script = """
{*==========================================================================*}
remarks  file  nmr/generate_template.inp
remarks  Generates a "template" coordinate set.  This produces
remarks  an arbitrary extended conformation with ideal geometry.
remarks  Author: Axel T. Brunger
{*==========================================================================*}

""" + \
self.setupPTcode() + "\n\n" + \
"structure @" + self.psfFile +  " end\n\n" + \
"""

set seed """ + str(self.seed()) + """ end

vector ident (x) ( all )
vector do (x=x/10.) ( all )
vector do (y=random(0.5) ) ( all )
vector do (z=random(0.5) ) ( all )

vector do (fbeta=50) (all)                 {*Friction coefficient, in 1/ps.*}
vector do (mass=100) (all)                         {*Heavy masses, in amus.*}

{* JFD note the above parameters are reset here *}
parameter
   nbonds
      cutnb=5.5 rcon=20. nbxmod=-2 repel=0.9  wmin=0.1 tolerance=1.
      rexp=2 irexp=2 inhibit=0.25
   end
end

flags exclude * include bond angle vdw end

minimize powell nstep=50  nprint=10 end

flags include impr end

minimize powell nstep=50 nprint=10 end

dynamics  verlet
   nstep=50  timestep=0.001 iasvel=maxwell  firsttemp= 300.
   tcoupling = true  tbath = 300.   nprint=50  iprfrq=0
end

parameter
   nbonds
      rcon=2. nbxmod=-3 repel=0.75
   end
end

minimize powell nstep=100 nprint=25 end

dynamics  verlet
   nstep=500  timestep=0.005 iasvel=maxwell  firsttemp= 300.
   tcoupling = true  tbath = 300.   nprint=100  iprfrq=0
end

flags exclude vdw elec end
vector do (mass=1.) ( name h* )
hbuild selection=( name h* ) phistep=360 end
flags include vdw elec end

minimize powell nstep=200 nprint=50 end

{*Write coordinates.*}

remarks produced by Refine.NTxplor.GenerateTemplate

""" + self.writeMolCode() + """

set message on echo on end

stop
"""


# END class GeneratePSF---------------------------------------------------------
