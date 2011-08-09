# Original from Xplor-NIH retrieved on Feb 8, 2011
from ivm import IVM
from monteCarlo import randomizeTorsions
from noePotTools import create_NOEPot
#from psfGen import seqToPSF
from simulationTools import * #@UnusedWildImport
from torsionTools import setTorsionsFromTable
from xplorPot import XplorPot #@UnresolvedImport
import os
import protocol

#if 1: # Fails with current setup:
#    sys.path.append("/Users/jd/workspace35/cing/python")
#    sys.path.append("/Users/jd/workspace35/cing/dist/Cython")
#    from cing.Libs.NTutils import * #@UnusedWildImport


# Execute in directory with (empty) data files
# Input:
# $x.psf             protein sequence file (kinda)
# $x_dis.tbl         distances
# $x_dih.tbl         dihedrals
# $x_dis.tbl         distances

# Output coordinate will be in files:
# $x_SCRIPT_STRUCTURE_sa.pdb

# Execute like:
# alias xplor 'env -i PATH=$PATH HOME=$HOME USER=$USER /Users/jd/workspace/xplor-nih-2.27/bin/xplor'
# set x = 1brv
# cd /Users/jd/tmp/cingTmp/$x
# xplor -py $CINGROOT/python/cing/Scripts/XplorNIH/anneal2.py


# Block for pydev checking in eclipse under CING environment
#pname = '1brv'
pname = 'H2_2Ca'

print "Starting cing.Scrips.XplorNIH/anneal2 on project: %s" % pname
# pylint: disable=E0601
xplor = xplor #@UndefinedVariable
xplor.requireVersion("2.24")

expectedInputFileList = ('%s.seq %s_dis.tbl %s_dis.tbl' % ( pname, pname, pname )).split()
for fn in expectedInputFileList:
    if not os.path.exists(fn):
        print "Failed to find input: %s" % fn
        os._exit(1)
#
# slow cooling protocol in torsion angle space for protein G. Uses
# NOE, RDC, J-coupling restraints.
#
# this script performs annealing from an extended structure.
# It is faster than the original anneal.py
#
# CDS 2009/07/24
#

# this checks for typos on the command-line. User-customized arguments can
# also be specified.
#
(opts,args) = xplor.parseArguments(["quick"])

quick=True
for opt in opts:
    if opt[0]=="quick":  #specify -quick to just test that the script runs
        quick=True
# end for

# filename for output structures. This string must contain the STRUCTURE
# literal so that each calculated structure has a unique name. The SCRIPT
# literal is replaced by this filename (or stdin if redirected using <),
# but it is optional.
#
outFilename = "%s_SCRIPT_STRUCTURE_sa.pdb" % pname
numberOfStructures=20   #usually you want to create at least 20

if quick:
    numberOfStructures=3
# end if

# protocol module has many high-level helper functions.
#

protocol.initRandomSeed() #set random seed - by time

command = xplor.command

# generate PSF data from sequence and initialize the correct parameters.
#
#seqToPSF('%s.seq'% pname)
#Simply read the psf already generated.
xplor.command("""struct @%s.psf end""" % pname)

# generate random extended initial structure with correct covalent geometry
#
protocol.genExtendedStructure()

#
# a PotList contains a list of potential terms. This is used to specify which
# terms are active during refinement.
#
potList = PotList()

# parameters to ramp up during the simulated annealing protocol
#

rampedParams=[]
highTempParams=[]

## compare atomic Cartesian rmsd with a reference structure
##  backbone and heavy atom RMSDs will be printed in the output
##  structure files
##
#refRMSD = create_PosDiffPot("refRMSD","name CA or name C or name N",
#                            pdbFile='g_xray.pdb',
#                            cmpSel="not name H*")

# orientation Tensor - used with the dipolar coupling term
#  one for each medium
#   For each medium, specify a name, and initial values of Da, Rh.
#
#media={}
##                        medium  Da   rhombicity
#for (medium,Da,Rh) in [ ('t',   -6.5, 0.62),
#                        ('b',   -9.9, 0.23) ]:
#    oTensor = create_VarTensor(medium)
#    oTensor.setDa(Da)
#    oTensor.setRh(Rh)
#    media[medium] = oTensor
#    pass

# dipolar coupling restraints for protein amide NH.
#
# collect all RDCs in the rdcs PotList
#
# RDC scaling. Three possible contributions.
#   1) gamma_A * gamma_B / r_AB^3 prefactor. So that the same Da can be used
#      for different expts. in the same medium. Sometimes the data is
#      prescaled so that this is not needed. scale_toNH() is used for this.
#      Note that if the expt. data has been prescaled, the values for rdc rmsd
#      reported in the output will relative to the scaled values- not the expt.
#      values.
#   2) expt. error scaling. Used here. A scale factor equal to 1/err^2
#      (relative to that for NH) is used.
#   3) sometimes the reciprocal of the Da^2 is used if there is a large
#      spread in Da values. Not used here.
#
#rdcs = PotList('rdc')
#for (medium,expt,file,                 scale) in \
#    [('t','NH' ,'tmv107_nh.tbl'       ,1),
#     ('t','NCO','tmv107_nc.tbl'       ,.05),
#     ('t','HNC','tmv107_hnc.tbl'      ,.108),
#     ('b','NH' ,'bicelles_new_nh.tbl' ,1),
#     ('b','NCO','bicelles_new_nc.tbl' ,.05),
#     ('b','HNC','bicelles_new_hnc.tbl',.108)
#     ]:
#    rdc = create_RDCPot("%s_%s"%(medium,expt),file,media[medium])
#
#    #1) scale prefactor relative to NH
#    #   see python/rdcPotTools.py for exact calculation
#    # scale_toNH(rdc) - not needed for these datasets -
#    #                        but non-NH reported rmsd values will be wrong.
#
#    #3) Da rescaling factor (separate multiplicative factor)
#    # scale *= ( 9.9 / rdc.oTensor.Da(0) )**2
#    rdc.setScale(scale)
#    rdcs.append(rdc)
#    pass
#potList.append(rdcs)
#rampedParams.append( MultRamp(0.01,1.0, "rdcs.setScale( VALUE )") )


# set up NOE potential
noe=PotList('noe')
potList.append(noe)
for (name,scale,file) in [('all',1,"%s_dis.tbl"%pname),
                          #add entries for additional tables
                          ]:
    pot = create_NOEPot(name,file)
    # pot.setPotType("soft") # if you think there may be bad NOEs
    pot.setScale(scale)
    noe.append(pot)
rampedParams.append( MultRamp(2,30, "noe.setScale( VALUE )") )

# set up J coupling - with Karplus coefficients
#jCoup = create_JCoupPot("jcoup","jna_coup.tbl",
#                        A=6.98,B=-1.38,C=1.72,phase=-60.0)
#potList.append(jCoup)

# Set up dihedral angles
protocol.initDihedrals("%s_dih.tbl"%pname,
                       #useDefaults=False  # by default, symmetric sidechain
                                           # restraints are included
                       )
potList.append( XplorPot('CDIH') )
highTempParams.append( StaticRamp("potList['CDIH'].setScale(10)") )
rampedParams.append( StaticRamp("potList['CDIH'].setScale(200)") )
# set custom values of threshold values for violation calculation
#
potList['CDIH'].setThreshold( 5 )



# radius of gyration term
#
#protocol.initCollapse("resid -999:999",
#                      Rtarget=10.16)
#potList.append( XplorPot('COLL') )

# hbda - distance/angle bb hbond term
#
#protocol.initHBDA('hbda.tbl')
#potList.append( XplorPot('HBDA') )

#Rama torsion angle database
#
protocol.initRamaDatabase()
potList.append( XplorPot('RAMA') )
rampedParams.append( MultRamp(.002,1,"potList['RAMA'].setScale(VALUE)") )

#
# setup parameters for atom-atom repulsive term. (van der Waals-like term)
#
potList.append( XplorPot('VDW') )
rampedParams.append( StaticRamp("protocol.initNBond()") )
rampedParams.append( MultRamp(0.9,0.8,
                              "command('param nbonds repel VALUE end end')") )
rampedParams.append( MultRamp(.004,4,
                              "command('param nbonds rcon VALUE end end')") )
# nonbonded interaction only between CA atoms
highTempParams.append( StaticRamp("""protocol.initNBond(cutnb=100,
                                                        rcon=0.004,
                                                        tolerance=45,
                                                        repel=1.2,
                                                        onlyCA=1)""") )


potList.append( XplorPot("BOND") )
potList.append( XplorPot("ANGL") )
potList['ANGL'].setThreshold( 5 )
rampedParams.append( MultRamp(0.4,1,"potList['ANGL'].setScale(VALUE)") )
potList.append( XplorPot("IMPR") )
potList['IMPR'].setThreshold( 5 )
rampedParams.append( MultRamp(0.1,1,"potList['IMPR'].setScale(VALUE)") )



# Give atoms uniform weights, except for the anisotropy axis
#
protocol.massSetup()


# IVM setup
#   the IVM is used for performing dynamics and minimization in torsion-angle
#   space, and in Cartesian space.
#
dyn = IVM()

# initialize ivm topology for torsion-angle dynamics

#for m in media.values():
#    m.setFreedom("fixDa, fixRh")        #fix tensor Rh, Da, vary orientation
##    m.setFreedom("varyDa, varyRh")      #vary tensor Rh, Da, vary orientation
protocol.torsionTopology(dyn)

# minc used for final cartesian minimization
#
minc = IVM()
protocol.initMinimize(minc)

#for m in media.values():
#    m.setFreedom("varyDa, varyRh")    #allow all tensor parameters float here
#    pass
protocol.cartesianTopology(minc)



# object which performs simulated annealing
#
init_t  = 3500.     # Need high temp and slow annealing to converge
cool = AnnealIVM(initTemp =init_t,
                 finalTemp=25,
                 tempStep =12.5,
                 ivm=dyn,
                 rampedParams = rampedParams)

#cart_cool is for optional cartesian-space cooling
cart_cool = AnnealIVM(initTemp =init_t,
                  finalTemp=25,
                  tempStep =12.5,
                  ivm=minc,
                  rampedParams = rampedParams)

def calcOneStructure(loopInfo):
    """ this function calculates a single structure, performs analysis on the
    structure, and then writes out a pdb file, with remarks.
    """

    # generate a new structure with randomized torsion angles
    #
    randomizeTorsions(dyn)
    protocol.fixupCovalentGeom(maxIters=100,useVDW=1)

    # set torsion angles from restraints
    #
    setTorsionsFromTable("dihed_g_all.tbl")

    # calc. initial tensor orientation
    #
#    for medium in media.values():
#        calcTensorOrientation(medium)
#        pass

    # initialize parameters for high temp dynamics.
    InitialParams( rampedParams )
    # high-temp dynamics setup - only need to specify parameters which
    #   differfrom initial values in rampedParams
    InitialParams( highTempParams )

    # high temp dynamics
    #
    protocol.initDynamics(dyn,
                          potList=potList, # potential terms to use
                          bathTemp=init_t,
                          initVelocities=1,
                          finalTime=100,   # stops at 800ps or 8000 steps
                          numSteps=1000,   # whichever comes first
                          printInterval=100)
    # pylint: disable=E1101
    dyn.setETolerance( init_t/100 )  #used to det. stepsize. default: t/1000
    dyn.run()

    # initialize parameters for cooling loop
    InitialParams( rampedParams )


    # initialize integrator for simulated annealing
    #
    protocol.initDynamics(dyn,
                          potList=potList,
                          numSteps=100,       #at each temp: 100 steps or
                          finalTime=.2 ,       # .2ps, whichever is less
                          printInterval=100)

    # perform simulated annealing
    #
    cool.run()


    # final torsion angle minimization
    #
    protocol.initMinimize(dyn,
                          printInterval=50)
    dyn.run()

    # optional cooling in Cartesian coordinates
    #
    protocol.initDynamics(minc,
                          potList=potList,
                          numSteps=100,       #at each temp: 100 steps or
                          finalTime=.4 ,       # .2ps, whichever is less
                          printInterval=100)
    #cart_cool.run()
    # final all- atom minimization
    #
    protocol.initMinimize(minc,
                          potList=potList,
                          dEPred=10)
    minc.run()

    #do analysis and write structure
    loopInfo.writeStructure(potList)
# end def



StructureLoop(numStructures=numberOfStructures,
              pdbTemplate=outFilename,
              structLoopAction=calcOneStructure,
              genViolationStats=1,
              averageTopFraction=0.5, #report stats on best 50% of structs
              averageContext=FinalParams(rampedParams),
#              averageCrossTerms=refRMSD,
              averageSortPots=[potList['BOND'],potList['ANGL'],potList['IMPR'], noe,
#                               rdcs,
                               potList['CDIH']],
              averagePotList=potList).run()
