"""
Create the macros that external programs such as Yasara, Molmol, and PyMol
can read to work on CING data.
"""
from cing import header
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqProcheck import * #@UnusedWildImport
from cing.main import getStartMessage
from random import random

try:
    import yasaramodule as yasara #@UnresolvedImport
except:
    pass
#    NTdebug("Yasara is not available for interactive work in CING; no problem have a homebrew")

MolmolColorDict = dict(green = '0 1 0', orange = '1 0.647 0', red = '1 0 0')

loadTestingFile = True


originatingProgramDeclaration = """Created by:
%s
%s""" % (header, getStartMessage())
originatingProgramDeclaration = toPoundedComment(originatingProgramDeclaration)

molmolMacroFileHeader = """# Execute by issuing command (without pound sign):
# molmol -f THIS_FILE_NAME
""" + originatingProgramDeclaration

pyMolMacroFileHeader = """# Execute by issuing command  (without pound sign):
# pymol THIS_FILE_NAME
""" + originatingProgramDeclaration

yasaraMacroFileHeader = """# Execute by issuing command  (without pound sign):
# ???? THIS_FILE_NAME
""" + originatingProgramDeclaration

def mkMacros(project):
    """
    Generate the macros in the moleculeDirectories.macros dir.
    """
    makePdbForMacros(project)

    NTmessage('==> Generating Macros')
    makePyMolMacros(project)
    makeMolmolMacros(project)
    mkYasaraMacros(project)
#end def

def makePdbForMacros(project):
    """
    Other todos
    Link naar macros vanaf de project page. TODO: finish coding.
    """
#    NTmessage('==> Exporting pdb files with one and all models for macros.')
    pass
#    pathPdb = project.path( project.directories.PDB )
#    path = os.path.join( pathPdb, project.molecule.name + '.pdb')
#
#    project.molecule.toPDBfile(path, convention=IUPAC, max_models = MAX_PROCHECK_NMR_MODELS)
#    path = os.path.join( pathPdb, project.molecule.name + '_000.pdb')
#    project.molecule.toPDBfile(path, convention=IUPAC, max_models = MAX_PROCHECK_NMR_MODELS)


def makePyMolMacros(project):
    """
    Generate the pyMol macros in the moleculeDirectories.pyMol dir.
    """
    if not project.molecule:
        NTerror('makeMolmolMacros: no molecule defined')
        return
    #end if
    makePyMolByResidueMacro(project, ['procheck', 'gf'],
                               minValue = PCgFactorMinValue, maxValue = PCgFactorMaxValue,
                               reverseColorScheme = PCgFactorReverseColorScheme,
                               path = project.moleculePath('pymol', 'gf.pml')
                              )

    makePyMolByResidueMacro(project, ['Qshift', 'backbone'],
                           minValue = QshiftMinValue, maxValue = QshiftMaxValue,
                           reverseColorScheme = QshiftReverseColorScheme,
                           path = project.moleculePath('pymol', 'Qshift.pml')
                          )
#
    makePyMolByResidueROGMacro(project, path = project.moleculePath('pymol', 'rog.pml'))
    makePyMolReadPdbMacro(project, path = project.moleculePath('pymol', 'read.pml'))
#end def

def makeMolmolMacros(project):
    """
    Generate the Molmol macros in the moleculeDirectories.molmol dir.
    """
    if not project.molecule:
        NTerror('makeMolmolMacros: no molecule defined')
        return
    #end if
    makeMolmolByResidueMacro(project, ['procheck', 'gf'],
                               minValue = PCgFactorMinValue, maxValue = PCgFactorMaxValue,
                               reverseColorScheme = PCgFactorReverseColorScheme,
                               path = project.moleculePath('molmol', 'gf.mac')
                              )

    makeMolmolByResidueMacro(project, ['Qshift', 'backbone'],
                           minValue = QshiftMinValue, maxValue = QshiftMaxValue,
                           reverseColorScheme = QshiftReverseColorScheme,
                           path = project.moleculePath('molmol', 'Qshift.mac')
                          )

    makeMolmolByResidueROGMacro(project, path = project.moleculePath('molmol', 'rog.mac'))
#end def

def mkYasaraMacros(project):
    """
    Generate the Yasara macros in the moleculeDirectories.yasara dir.
    """
    if not project.molecule:
        NTerror('mkYasaraMacros: no molecule defined')
        return
    #end if
    mkYasaraByResidueMacro(project, ['procheck', 'gf'],
                               minValue = PCgFactorMinValue, maxValue = PCgFactorMaxValue,
                               reverseColorScheme = PCgFactorReverseColorScheme,
                           path = project.moleculePath('yasara', 'gf.mcr')
                          )

    mkYasaraByResidueMacro(project, ['Qshift', 'backbone'],
                           minValue = QshiftMinValue, maxValue = QshiftMaxValue,
                           reverseColorScheme = QshiftReverseColorScheme,
                           path = project.moleculePath('yasara', 'Qshift.mcr')
                          )

    mkYasaraByResidueROGMacro(project, path = project.moleculePath('yasara', 'rog.mcr'))
#end def

def makePyMolByResidueROGMacro(project, path = None):
    """See doc at:
http://pymolwiki.org/index.php/Color#Reassigning_B-Factors_and_Coloring
"""
#    NTdebug('makePyMolByResidueROGMacro')

    _scriptStartupTxt = """#!/usr/bin/env python
# Or execute: python THIS_FILE
# From http://pymolwiki.org/index.php/Launching_From_a_Script

import __main__

# Importing the PyMOL module will create the window.
import pymol #@UnresolvedImport
from pymol import cmd #@UnresolvedImport

# Tell PyMOL we don't want any GUI features.
__main__.pymol_argv = [ 'pymol', '-Gi' ]

# Call the function below before using any PyMOL modules.

pymol.finish_launching()

"""
    # Just for testing:
    pdbCode = '1brv'
    scriptPdbLoad = "cmd.load('/Users/jd/workspace35/cing/Tests/data/pdb/%s/pdb%s.ent')" % (pdbCode, pdbCode)

    macroTxt = \
"""

%s

# Coloring residues by CING ROG scores.

""" % pyMolMacroFileHeader

    # Macro can be much shortened by combining categories ROG.
    # JFD has not found the command to actually set the values to e.g. the b-factor to use that to color/store.
    for res in project.molecule.allResidues():
        pyMolColor = res.rogScore.colorLabel # no translation needed for red, orange, green.
        if True:
            if random() > 0.7:
                pyMolColor = 'red'
            if random() > 0.7:
                pyMolColor = 'orange'
        pyMolColorQuoted = "'" + pyMolColor + "'"
        macroTxt += "cmd.color( %-8s, 'chain %2s and resi %4d')\n" % (pyMolColorQuoted, res.chain.name, res.resNum)
    #end for

    # Make it into a selfcontained script for testing.
    if True:
        macroTxt = scriptPdbLoad + macroTxt

    if path:
        writeTextToFile(path, macroTxt)
    else:
        NTmessage(macroTxt)
    #end if
#end def


def makePyMolReadPdbMacro(project, path = None):
    # Just for testing:
    pdbCode = '1brv'
    scriptPdbLoad = "load /Users/jd/workspace35/cing/Tests/data/pdb/%s/pdb%s.ent" % (pdbCode, pdbCode)
    macroTxt = pyMolMacroFileHeader + '\n' + scriptPdbLoad +'\n'

    if path:
        writeTextToFile(path, macroTxt)
    else:
        NTmessage(macroTxt)



def makePyMolByResidueMacro(project, keys,
                            minValue = 0.0, maxValue = 1.0, reverseColorScheme = False,
                            path = None):

    """From http://pymolwiki.org/index.php/Color#Reassigning_B-Factors_and_Coloring
    http://pymolwiki.org/index.php/Command_Line_Options
    """
#    NTdebug('makePyMolByResidueMacro: keys: %s, minValue: %s maxValue: %s reverseColorScheme: %s', keys, minValue, maxValue, reverseColorScheme)

    # Just for testing:
    pdbCode = '1brv'
    if loadTestingFile:
        scriptPdbLoad = "load /Users/jd/workspace35/cing/Tests/data/pdb/%s/pdb%s.ent" % (pdbCode, pdbCode)

    macroTxt = \
"""

%s

# Scaling colors to MinValue, MaxValue, ReverseColorScheme: minValue, maxValue, reverseColorScheme

# clear out the old B Factors
#cmd.alter( 'all', 'b=0.0' )
alter all, b=0.0

# update the B Factors with new properties
""" % pyMolMacroFileHeader

    spectrumName = 'green_yellow_red'
    if reverseColorScheme:
        spectrumName = 'red_yellow_green'
    for res in project.molecule.allResidues():
        value = getDeepByKeysOrAttributes(res, *keys)
        if False: # Used for testing.
            value = random() * 0.05
        if value != None and not isNaN(value):
            pyMolSelection = 'chain %2s and resi %4d' % (res.chain.name, res.resNum)
#            pyMolSelectionQuoted = "'%s'" % pyMolSelection
#            macroTxt += "cmd.alter( %-30s, 'b = %10f')\n" % ( pyMolSelectionQuoted, value )
            macroTxt += "alter ( %-30s ), b = %10f\n" % (pyMolSelection, value)
        # end if
    # end for

    # Documented in source: pymol/modules/pymol/viewing.py
#cmd.spectrum(expression='b', palette='%s', selection='all', minimum=minValue, maximum=maxValue)
    macroTxt += """
# color the molecule based on the new B Factors of the atoms
spectrum b, %s, selection=all, minimum=minValue, maximum=maxValue

""" % spectrumName
    macroTxt = macroTxt.replace('minValue', `minValue`)
    macroTxt = macroTxt.replace('maxValue', `maxValue`)
    macroTxt = macroTxt.replace('reverseColorScheme', `reverseColorScheme`)

    # Make it into a self-contained script for testing.
    macroTxt = scriptPdbLoad + macroTxt

    if path:
        writeTextToFile(path, macroTxt)
    else:
        NTmessage(macroTxt)
    #end if
#end def


def makeMolmolByResidueROGMacro(project, path = None):

#    NTdebug('makeMolmolByResidueROGMacro')

    macroTxt = """%s

# Coloring residues by CING ROG scores.

ReadPdb /Users/jd/workspace35/cing/Tests/data/pdb/1brv/pdb1brv.ent

DefPropAtom 'prev_sel' 'selected'
DefPropBond 'prev_sel' 'selected'

""" % molmolMacroFileHeader

    # Macro can be much shortened by combining categories ROG.
    # JFD has not found the command to actually set the values to e.g. the b-factor to use that to color/store.
    for res in project.molecule.allResidues():
        molmolColor = MolmolColorDict[res.rogScore.colorLabel]
#        if testing:
#            if random() > 0.7:
#                molmolColor = MolmolColorDict['red']
#            if random() > 0.7:
#                molmolColor = MolmolColorDict['orange']
#        SelectAtom '#1-5:10-20,25-30@N,CA,C'
         # N, CA and C atoms of residues 10 to 20 and 25 to 30
         # in molecules 1 to 5
        macroTxt += \
"""
SelectAtom ':%d'
SelectBond 'atom2.selected'
ColorAtom %s
ColorBond %s
""" % (res.resNum, molmolColor, molmolColor)
    #end for


    macroTxt += \
"""
SelectAtom 'prev_sel'
SelectBond 'prev_sel'
"""

    if path:
        writeTextToFile(path, macroTxt)
    else:
        NTmessage(macroTxt)
    #end if

#end def

def mapValueToMolmolColor(value, minValue, maxValue, reverseColorScheme, msgHol=None):
    """Map from min to middle; blue to red and
           from middle to max; red to yellow
           TODO: implement reverseColorScheme
           """
    if minValue > maxValue:
        msg = "mapValueToMolmolColor: minValue > maxValue (%s > %s) which is impossible in algorithm, swapping" % (minValue, maxValue)
        if msgHol == None:
            NTwarning(msg)
        else:
            msgHol.appendWarning(msg)
        swapMemory = minValue
        minValue = maxValue
        maxValue = swapMemory
    if value > maxValue:
        msg = "mapValueToMolmolColor: value > maxValue (%s > %s) got limited to bound" % (value, maxValue)
        if msgHol == None:
            NTwarning(msg)
        else:
            msgHol.appendWarning(msg)
        value = maxValue
    if value < minValue:
        msg = "mapValueToMolmolColor: value < minValue (%s > %s) got limited to bound" % (value, minValue)
        if msgHol == None:
            NTwarning(msg)
        else:
            msgHol.appendWarning(msg)
        value = minValue


    # rangeValue is always positive
#    rangeValue = maxValue - minValue
#    middleValue = rangeValue / 2.
    fractionOnZeroToOne = abs(value - minValue) / (maxValue - minValue)
    if reverseColorScheme:
        fractionOnZeroToOne = 1. - fractionOnZeroToOne

    # blue to red; in rgb: 0 0 1 to 1 0 0
    if fractionOnZeroToOne < 0.5:
        colorRed = 2. * fractionOnZeroToOne
        colorGreen = 0.
        colorBlue = 1. - 2. * fractionOnZeroToOne
    else:
    # red to yellow; in rgb: 1 0 0 to 1 1 0
        colorRed = 1.
        colorGreen = 2. * (fractionOnZeroToOne - 0.5)
        colorBlue = 0.
    molmolColor = "%s %s %s" % (colorRed, colorGreen, colorBlue)
#    NTdebug( "mapValueToMolmolColor fraction %s red, green, blue: %s" %(fractionOnZeroToOne, molmolColor) )
    return molmolColor

def makeMolmolByResidueMacro(project, keys,
                            minValue = 0.0, maxValue = 1.0, reverseColorScheme = False,
                            path = None
                           ):

#    NTdebug('makeMolmolByResidueMacro: keys: %s, minValue: %s maxValue: %s reverseColorScheme: %s', keys, minValue, maxValue, reverseColorScheme)
    macroTxt = \
"""%s

# Scaling colors to MinValue, MaxValue, ReverseColorScheme: minValue, maxValue, reverseColorScheme

ReadPdb /Users/jd/workspace35/cing/Tests/data/pdb/1brv/pdb1brv.ent

DefPropAtom 'prev_sel' 'selected'
DefPropBond 'prev_sel' 'selected'

""" % molmolMacroFileHeader

    msgHol = MsgHoL()
    for res in project.molecule.allResidues():
        value = getDeepByKeysOrAttributes(res, *keys)
#            value = random() * 4. - 3
#        if testing:
#        if res.has_key(property) and res[property] != None and not isNaN(res[property]):
        if value != None and not isNaN(value):
            molmolColor = mapValueToMolmolColor(value, minValue, maxValue, reverseColorScheme, msgHol=msgHol)
            macroTxt += \
    """
SelectAtom ':%d'
SelectBond 'atom2.selected'
ColorAtom %s
ColorBond %s
""" % (res.resNum, molmolColor, molmolColor)
    #end for
    msgHol.showMessage(MAX_WARNINGS=1)

    macroTxt += """
SelectAtom 'prev_sel'
SelectBond 'prev_sel'
"""
    macroTxt = macroTxt.replace('minValue', `minValue`)
    macroTxt = macroTxt.replace('maxValue', `maxValue`)
    macroTxt = macroTxt.replace('reverseColorScheme', `reverseColorScheme`)

    if path:
        writeTextToFile(path, macroTxt)
    else:
        NTmessage(macroTxt)
    #end if
#end def

def mkYasaraByResidueMacro(project, keys,
                            minValue = 0.0, maxValue = 1.0, reverseColorScheme = False,
                            path = None
                           ):

#    NTdebug('mkYasaraByResidueMacro: keys: %s, minValue: %s maxValue: %s', keys, minValue, maxValue)

    if path:
        stream = open(path, 'w')
    else:
        stream = sys.stdout
    #end if

    fprintf(stream, 'Console off\n')
    fprintf(stream, yasaraMacroFileHeader + '\n')
    fprintf(stream, 'ColorRes All, Gray\n')
    fprintf(stream, 'PropRes All, -999\n')
    if reverseColorScheme:
        fprintf(stream, 'ColorPar Property Min,red,%f\n', minValue)
        fprintf(stream, 'ColorPar Property Max,blue,%f\n', maxValue)
    else:
        fprintf(stream, 'ColorPar Property Min,blue,%f\n', minValue)
        fprintf(stream, 'ColorPar Property Max,red,%f\n', maxValue)

    for res in project.molecule.allResidues():
        value = getDeepByKeysOrAttributes(res, *keys)
#        if res.has_key(property) and res[property] != None and not isNaN(res[property]):
        if value != None and not isNaN(value):
            fprintf(stream, 'PropRes Residue %d,%.4f\n', res.resNum, value)
    #end for

    fprintf(stream, 'ColorAll Property\n')
    fprintf(stream, 'Console on\n')

    if path:
        stream.close()
#end def

def mkYasaraByResidueROGMacro(project, path = None):
    if path:
        stream = open(path, 'w')
#     else:
#         stream = sys.stdout
#     #end if

    if path:
        fprintf(stream, 'Console off\n')
        fprintf(stream, yasaraMacroFileHeader + '\n')
        fprintf(stream, 'ColorRes  All, Gray\n')
    else:
        yasara.Console('off')
        yasara.ColorRes('All, Gray')


    YasaraColorDict = dict(green = 240, orange = 150, red = 120)

    for res in project.molecule.allResidues():
        cmd = sprintf('residue %d,%s', res.resNum, YasaraColorDict[res.rogScore.colorLabel])
        if path:
            fprintf(stream, 'ColorRes %s\n', cmd)
        else:
            yasara.ColorRes(cmd)
    #end for

    if path:
        fprintf(stream, 'Console on\n')
        stream.close()
    else:
        yasara.Console('on')
#end def

# register the functions
methods = [
            (mkYasaraByResidueROGMacro, None),
            (mkYasaraByResidueMacro, None),
            (mkYasaraMacros, None),
            (makeMolmolByResidueROGMacro, None),
            (makeMolmolByResidueMacro, None),
            (makeMolmolMacros, None),
            (mkMacros, None)
           ]
#saves    = []
#restores = []
#exports  = []

