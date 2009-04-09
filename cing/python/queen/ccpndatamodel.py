#!/usr/bin/env python

# ADD QUEEN SOURCE TO SYSTEM PATH
import sys,os

sys.path += [os.path.join(sys.path[0],'src/py'),
             os.path.join(sys.path[0],'src/c'),
             os.path.join(sys.path[0],'src/3rd-party')]

# DO IMPORTS
import optparse
from qn import *

# THE TEXT HEADER
def txt_header():
  print"**********************************************************"
  print"*                      Q U E E N                         *"
  print"* QUantitative Evaluation of Experimental Nmr restraints *"
  print"**********************************************************"
  print"*        Written in 2004 by s.nabuurs@cmbi.kun.nl        *"
  print"*     CMBI, University of Nijmegen, The Netherlands      *"
  print"**********************************************************"
  print"*            For help: ccpndatamodel.py -h               *"
  print"**********************************************************"
  print"* Note: this a beta-version of the QUEEN/CCPN interface. *"
  print"*    Please contact us if you encounter any problems!    *"
  print"**********************************************************"
  print
  sys.stdout.flush()

# CHECK PYTHON VERSION
version = nmv_checkpython()

# OPTION PARSER
usage = "usage: %prog [option] project.xml"
parser = optparse.OptionParser(usage=usage,version="%prog 0.1-beta")
parser.add_option("-i","--import",action="store_true",dest="importxml",
                  help="import project from CPPN datamodel XML file.")
(options,args) = parser.parse_args()

# READ THE QUEEN CONFIGURATION FILE
nmvconf = dct_read(os.path.join(sys.path[0],'queen.conf'))

# SHOW TEXT HEADER
txt_header()

# CCPN RELATED IMPORTS
try:
  from memops.general.Io import loadXmlProjectFile
  from ccpnmr.format.converters.CnsFormat import CnsFormat
except ImportError:
  error("""You do not seem to have the Python API to the CPPN
        datamodel installed.
        Please download and install it from: www.ccpn.ac.uk""")

# OPTIONS TAKE TWO ARGUMENTS
if len(args)==1:
  xmlfile = args[0]
  # TAKE THE SELECTED OPTION
  if options.importxml:
    # IF XML FILE EXISTS
    if os.path.exists(xmlfile):
      xmlproject = loadXmlProjectFile('.',xmlfile)
      print "Read XML file."
      # TAKE FIRST MOLSYSTEM
      print "\n..... CCPN Format Messages ....."
      if len(xmlproject.molSystems)==0:
        error("CCPN: No molSystems present")
      elif len(xmlproject.molSystems)==1:
        print "CCPN: Found molSystem."
      elif len(xmlproject.molSystems)>1:
        warning("CCPN: Multiple molSystems found. Taking first one")
      print "^^^^^ CCPN Format Messages ^^^^^\n"
      molSys = xmlproject.molSystems[0]
      chainDict = {}
      # TAKE ALL CHAINS
      for chain in molSys.chains:
        chainDict[chain.code] = []
        for residue in chain.residues:
          chainDict[chain.code].append(residue.molResidue.ccpCode)
      format = CnsFormat(xmlproject)
      # TAKE FIRST STRUCTURE GENERATION
      if len(xmlproject.structureGenerations)==0:
        error("CPPN: No structureGenerations present")
      elif len(xmlproject.structureGenerations)==1:
        print "CCPN: Found structureGeneration."
      elif len(xmlproject.structureGenerations)>1:
        warning("CPPN: Multiple structureGenerations found. Taking first one")
      strucGen = xmlproject.structureGenerations[0]
      print "CCPN: Projectname is '%s'."%strucGen.project.name
      project = strucGen.project.name
      # SETUP QUEEN
      if not os.path.exists(os.path.join(nmvconf["Q_PROJECT"],project)):
        qn_createproject(nmvconf,project)
      queen = qn_setup(nmvconf,project)
      xplr  = qn_setupxplor(nmvconf,project)
      # CYCLE RESTRAINTLISTS
      restraintlists = []
      for cslist in strucGen.constraintLists:
        # GET NUMBER OF RESTRAINTS
        nconstraints = len(cslist.constraints)
        print "CCPN: Found %s of length %i."%(cslist.className,
                                              nconstraints)
        # HANDLE THE DIFFERENT TYPES OF RESTRAINTS
        read = 1
        if cslist.className == 'DistanceConstraintList':
          constraintType='distance'
          constrainttype='DIST'
        elif cslist.className == 'DihedralConstraintList':
          constraintType='dihedral'
          constrainttype='DIHE'
        elif cslist.className == 'HBondConstraintList':
          constraintType='hbond'
          constrainttype='DIST'
        else:
          read = 0
          warning("%s currently not supported by QUEEN"%cslist.className)
        # DO THE CONVERSION
        if read:
          print "\n..... CCPN Format Converter ....."
          print "Setname '%s'."%cslist.name
          format.writeConstraints(fileName ='',
                                  constraintList = cslist,
                                  constraintType = constraintType,
                                  minimalPrompts = 1,
                                  noWrite = 1,
                                  compressResonances = 0)
          rlist = []
          # CYCLE THE CONSTRAINTS
          for constraint in format.constraintFile.constraints:
            # DEFINE DISTANCE RESTRAINTS
            r = nmr_restraint(type=constrainttype)
            if constrainttype=='DIST':
              r.target = constraint.targetDist
              r.lowerb = constraint.targetDist - constraint.minusDist
              r.upperb = constraint.targetDist + constraint.plusDist
              for item in constraint.items:
                members = item.members
                for i in range(2):
                  r.data[i]["RESI"].append(members[i].seqCode)
                  if members[i].chainCode != ' ':
                    r.data[i]["SEGI"].append(members[i].chainCode)
                  r.data[i]["NAME"].append(members[i].atomName)
              rlist.append(r)
            # DEFINE DIHEDRAL ANGLE RESTRAINTS
            if constrainttype=='DIHE':
              r = nmr_restraint(type=constrainttype)
              r.angle = constraint.targetAngle
              r.range = constraint.devAngle
              # CYCLE ITEMS IN THE CONSTRAINT
              for item in constraint.items:
                members = item.members
                for i in range(4):
                  r.data[i]["RESI"].append(members[i].seqCode)
                  if members[i].chainCode != ' ':
                    r.data[i]["SEGI"].append(members[i].chainCode)
                  r.data[i]["NAME"].append(members[i].atomName)
              rlist.append(r)
          print "Succesfully read %i restraints."%len(rlist)  
          print "^^^^^ CCPN Format Converter ^^^^^\n"
          # STORE THE FILES IN THE PROPER PLACE
          table = nmv_adjust(queen.table,cslist.name.replace(' ','_'))
          if os.path.exists(table):
            warning("Restraint file exists")
          rfile = restraint_file(table,'w',type=constrainttype)
          rfile.mwrite(rlist)
          rfile.close()
          # STORE FOR THE DATASET DESCRIPTION FILE
          restraintlists.append([cslist.name,
                                 constrainttype,
                                 cslist.name.replace(' ','_')])
      # WRITE DATASET DESCRIPTION FILE
      print "\nWriting dataset description file."
      setfile = nmv_adjust(queen.dataset,strucGen.project.name)
      file = open(setfile,'w')
      for list in restraintlists:
        file.write("NAME = %s\n"%list[0])
        file.write("TYPE = %s\n"%list[1])
        file.write("FILE = %s\n"%list[2])
        file.write("//\n")
      file.close()
      # WRITE SEQUENCE FILE
      print "Writing sequence file."
      file = open(queen.sequence,'w')
      for ch in chainDict.keys():
        file.write("> %s\n"%ch)
        for aa in chainDict[ch]:
          file.write("%s\n"%aa)
      file.close()
      # GENERATE PSF FROM SEQUENCE
      print "Generating PSF file from sequence file."
      xplor_buildstructure(xplr.psf,queen.sequence,'sequence',
                           xplr.topology,
                           xplr.peptide,
                           nmvconf["XPLOR"])
      # GENERATE TEMPLATE FROM PSF
      print "Generating template file from PSF file."
      xplor_generatetemplate(xplr.template,xplr.psf,
                             xplr.parameter,
                             nmvconf["XPLOR"])
      print "\nDone."
    else:
      print "XML file does not exist:"
      print xmlfile
else:
  error("Provide the path to a datamodel XML file as argument")
