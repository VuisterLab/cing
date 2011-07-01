#@PydevCodeAnalysisIgnore # pylint: disable-all
"""
# slow cooling protocol in torsion angle space for protein G. Uses
# NOE, RDC, J-coupling restraints.
#
# CDS 5/14/03
# modified 7/2/03
# JFD modified Thu Apr 28 14:00:17 CEST 2011

# this checks for typos on the command-line. User-customized arguments could
# also be specified.

#Run like:
cd /Users/jd/tmp/xplornih

# Set project name (assuming tcsh)
set x = 1brv

# Remove spurious files like:
rm $x_extended_*.pdb*

# Prepare the following input: $x.seq $x_noe.tbl and $x_dih.tbl
xplor -py $CINGROOT/python/xplornih/anneal.py $x 20 1234 >& anneal.log

# If successful it will write output files:
"""

from atomAction import SetProperty
from atomSel import AtomSel #@UnresolvedImport
from ivm import IVM
from noePotTools import create_NOEPot
from potList import PotList #@UnresolvedImport
from psfGen import seqToPSF
from selectTools import IVM_groupRigidSidechain
from simulationTools import StructureLoop
from xplorPot import XplorPot #@UnresolvedImport
import os
import protocol
import psfGen
import sys
import xplor #@UnresolvedImport # already present when starting up with xplor -py

sys.path.append( '/Users/jd/workspace35/cing/python' )
#sys.path.append( '/Users/jd/workspace35/cing/python' )
if 1:
    from xplorcing.Utils import getRandomSeed # relative url for package since whole CING can't live together with xplor nih yet.


print "sys.argv: %s" % str(sys.argv)
xplor.parseArguments()
argvlist = sys.argv[:]
if len(argvlist) < 3:
    argvlist.append(os.getcwd()) # input dir.
if len(argvlist) < 4:
    argvlist.append(os.getcwd()) # output dir relative to this script
if len(argvlist) < 5:
    argvlist.append(1) # numberOfStructures
if len(argvlist) < 6:
    argvlist.append(getRandomSeed()) # seed
project_name, inputDir, outputDir, numberOfStructures, seed = argvlist[1:]

# Not needed to have input/output directories this explicit if it's all local.
extFilename = "%s/%s_extended_%s.pdb" % ( outputDir, project_name, seed )
noeFilename = "%s/%s_noe.tbl" % ( inputDir, project_name )
dihFilename = "%s/%s_dih.tbl" % ( inputDir, project_name )
pdbTemplate = "%s/anneal_STRUCTURE.pdb" % ( outputDir ) # don't use script as it will contain a path element.
seqFilename = "%s/%s.seq" % ( inputDir, project_name )
psfFilename = "%s/%s.psf" % ( inputDir, project_name )
pdbFilename = "%s/%s.pdb" % ( inputDir, project_name )
cool_steps = 1500   # DEFAULT 15,000 slow annealing TODO: SET BAcK

print "Input" + project_name
print "Project:             " + project_name
print "numberOfStructures:  " + str(numberOfStructures)
print "seed:                " + str(seed)
print ""
print "inputDir:            " + inputDir
print "outputDir:           " + outputDir
print "pdbFilename:         " + pdbFilename
print "psfFilename:         " + psfFilename
print "pdbTemplate:         " + pdbTemplate
print "extFilename:         " + extFilename
print "noeFilename:         " + noeFilename
print "dihFilename:         " + dihFilename
print "cool_steps:         " + str(cool_steps)


#simWorld = simulationWorld.SimulationWorld_world() # already availabel.
simWorld.setRandomSeed(seed)   #set random seed @UndefinedVariable
command = xplor.command

# generate PSF data from sequence, coordinates, or psf in that order.
if os.path.exists( seqFilename ):
    seq = open(seqFilename).read()
    seqToPSF(seq, # Customize here for specific settings or get them from a dictionary with the project or so.
             startResid=1,
             deprotonateHIS=1,
             segName='',
             disulfide_bonds=[],
             disulfide_bridges=[],
             )
elif os.path.exists( pdbFilename ):
    psfGen.pdbToPSF(pdbFilename)
#    protocol.initCoords(pdbFilename)
elif os.path.exists( psfFilename ):
    # read in the PSF file and initial structure
    command("structure @%s end" % psfFilename)
    protocol.initParams("protein.par", weak_omega=1)
#    command("coor @gb3_xray.pdb")
else:
    print "ERROR: failed to find seq or psf file in %s" % os.getcwd()
    sys.exit(1)
# end if

# generate a random extended structure with correct covalent geometry
protocol.genExtendedStructure(extFilename)

#
# a PotList conatins a list of potential terms. This is used to specify which
# terms are active during refinement.
#
potList = PotList()

# set up NOE potential
noe = create_NOEPot("noe",file=noeFilename)
noe.setPotType( "soft" )
noe.setRSwitch( 0.5 )
noe.setAsympSlope( 1. )
noe.setSoftExp(1.)
noe.setThreshold(0.5)
print noe.info()
potList.append(noe)


# Set up dihedral angles
protocol.initDihedrals(dihFilename,
                       scale=5,          #initial force constant
                       useDefaults=0)
potList.append( XplorPot('CDIH') )

#
# setup parameters for atom-atom repulsive term. (van der Waals-like term)
#
protocol.initNBond(nbxmod=4,  # Can use 4 here, due to IVM dynamic
                   repel=0.5) # initial effective atom radius
potList.append( XplorPot('VDW') )

#
# annealing settings
#

init_t  = 3500.     # Need high temp and slow annealing to converge
final_t = 100

#cool_steps = 15000   # slow annealing


#
# initial force constant settings
#
ini_rad  = 0.4
ini_con = 0.004
ini_ang = 0.4
ini_imp = 0.4     # was 0.1
ini_noe = 1       # was 150
ini_sani = 0.01


potList.add( XplorPot("BOND") )
potList.add( XplorPot("ANGL") )
potList.add( XplorPot("IMPR") )


#
# potential terms used for high-temp dynamics
#
hitemp_potList = PotList()
hitemp_potList.add( XplorPot("BOND") )
hitemp_potList.add( XplorPot("ANGL") )
hitemp_potList.add( XplorPot("IMPR") )
hitemp_potList.add( XplorPot("CDIH") )
hitemp_potList.add( noe   )

# Give atoms uniform weights, except for the anisotropy axis
AtomSel("all            ").apply( SetProperty("mass",100.) )
AtomSel("all            ").apply( SetProperty("fric",10.) )

#
# IVM setup
#

dyn = IVM()

# Minimize in Cartesian space with only the covalent constraints.
# Note that bonds, angles and many impropers can't change with the
# internal torsion-angle dynamics
#  breaks bonds topologically - doesn't change force field

dyn.potList().add( XplorPot("BOND") )
dyn.potList().add( XplorPot("ANGL") )
dyn.potList().add( XplorPot("IMPR") )

dyn.breakAllBondsIn("all")

protocol.initMinimize(dyn,numSteps=1000)
dyn.run()

#
# reset ivm topology for torsion-angle dynamics
#
dyn.reset()
dyn.potList().removeAll()

protocol.torsionTopology(dyn)

#
# minc used for final cartesian minimization
#
minc = IVM()
protocol.initMinimize(minc)
IVM_groupRigidSidechain(minc)
minc.breakAllBondsIn("all")

def setConstraints(k_ang,k_imp):
    command("""
      constraints
         interaction (not resname ANI) (not resname ANI)
            weights * 1 angl %f impr %f
         end
      end""" % ( k_ang, k_imp) )
    return
# end def


def structLoopAction(loopInfo):
    #
    # this function calculates a single structure.
    #

    #
    # set some high-temp force constants
    #
    noe.setScale( 20 )       #use large scale factor initially
    command("parameters  nbonds repel %f end end" % ini_rad)
    command("parameters  nbonds rcon %f end end" % ini_con)
    setConstraints(ini_ang, ini_imp)
    # Initial weight--modified later
    command("restraints dihedral scale=5. end")

    #
    # high temp dynamics
    # note no Van der Waals term
    #

    init_t = 3500
    ini_timestep = 0.010
    bath = init_t
    timestep = ini_timestep

    protocol.initDynamics(dyn,
                          potList=hitemp_potList, # potential terms to use
                          bathTemp=bath,
                          initVelocities=1,
                          finalTime=20,
                          printInterval=100)

    dyn.setETolerance( bath/100 )  #used to det. stepsize. default: bath/1000
    dyn.run()

    # increase dihedral term
    command("restraints dihedral scale=200. end")

    #
    # cooling and ramping parameters
    #

    global k_ang, k_imp

    # MultRamp ramps the scale factors over the specified range for the
    # simulated annealing.
    from simulationTools import MultRamp
    k_noe = MultRamp(ini_noe,30.,"noe.setScale( VALUE )")
    radius = MultRamp(ini_rad,0.8,
                                 "command('param nbonds repel VALUE end end')")
    k_vdw  = MultRamp(ini_con,4, "command('param nbonds rcon  VALUE end end')")
    k_ang  = MultRamp(ini_ang,1.0)
    k_imp  = MultRamp(ini_imp,1.0)

    protocol.initDynamics(dyn,
                          potList=potList,
                          bathTemp=bath,
                          initVelocities=1,
                          finalTime=2,
                          printInterval=100,
                          stepsize=timestep)

    from simulationTools import AnnealIVM
    AnnealIVM(initTemp =init_t,
              finalTemp=100,
              tempStep =25,
              ivm=dyn,
              rampedParams = [k_noe,radius,k_vdw,k_ang,k_imp],
              extraCommands= lambda notUsed: \
                setConstraints(k_ang.value(),
                               k_imp.value())).run()


    #
    # final torsion angle minimization
    #
    protocol.initMinimize(dyn, printInterval=50)
    dyn.run()

    #
    # final all atom minimization
    #
    protocol.initMinimize(minc, potList=potList, printInterval=100)
    minc.run()

    #
    # analyze and write out structure
    #
    print "Starting writeStructure"
    loopInfo.writeStructure(potList)
# end def

print "Starting structure loop"
StructureLoop(numStructures=numberOfStructures,
              pdbTemplate=pdbTemplate,
              structLoopAction=structLoopAction,
              genViolationStats=1,
              averagePotList=potList).run()
