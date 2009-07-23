"""
Adds x3dna method to analyze DNA structures. The x3dna program is included as binaries for Mac OSX and 32 bit
Linux in the bin directory.
"""
from cing.Libs.NTutils import ExecuteProgram
from cing.Libs.NTutils import ImportWarning
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTprogressIndicator
from cing.PluginCode.pdb import moleculeToPDBfile
from cing.core.parameters import cingPaths
from cing.core.parameters import validationSubDirectories
import cing
import os

useModule = True
# TODO: test if the binary is actually applicable to the system os.
if not os.path.exists(cingPaths.x3dna):
    NTdebug("Missing x3dna directory which is a dep for x3dna; currently only tested for mac and disabled for other os")
    useModule = False
if not useModule:
    raise ImportWarning('x3dna')

contentFile = 'content.xml'

X3DNA_NAN = '----'

def x3dnaPath(project, *args):
    """
    Return x3dna path from active molecule of project
    Creates directory if does not exist
    """
    return project.validationPath(validationSubDirectories['x3dna'], *args)


def runX3dna(project, parseOnly = False, modelNum = None):
    """
    Runs x3dna on all models found in the project file.
    The input file for X3DNA is a pdbFile
    The routine writes all the models found in the project file to separate pdb file, which are analyzed using x3dna:
        - x3dna.csh (cingPaths.x3dna) is a shell script that calls the various subroutines of the x3dna package and writes
          output files in rootPath:
            - find_pair

    Return None on error.
    """

    root = project.mkdir(project.molecule.name, project.moleculeDirectories.x3dna)
    rootPath = root
#    if not project.molecule.hasDNA():
    if not project.molecule.hasNucleicAcid():
        NTdebug("Not running x3dna for molecule has no DNA")
        return True # return true to notify caller that there is no error

    x3dnascript = os.path.join(cingPaths.x3dna, 'x3dna.csh')
    x3dnaMainDir = os.path.join(cingPaths.x3dna, 'x3dna_MacOS_intel')
    appendPathList = [ os.path.join(x3dnaMainDir, 'bin') ]
    appendEnvVariableDict = {}
    appendEnvVariableDict[ 'X3DNA' ] = x3dnaMainDir
    x3dna = ExecuteProgram(pathToProgram = x3dnascript, rootPath = root, redirectOutput = True,
        appendPathList = appendPathList, appendEnvVariableDict = appendEnvVariableDict)

    # Storage of results for later
    project.x3dnaStatus.completed    = False
    project.x3dnaStatus.parsed       = False
    project.x3dnaStatus.version      = cing.cingVersion
    project.x3dnaStatus.moleculeName = project.molecule.name # just to have it
#    project.x3dnaStatus.models       = models
#    project.x3dnaStatus.baseName     = baseName
    project.x3dnaStatus.path         = root
    project.x3dnaStatus.contentFile  = contentFile
    project.x3dnaStatus.chains       = NTlist()    # list of (chainNames, outputFile) tuples to be parsed
    project.x3dnaStatus.keysformat()

    # The input file for is a pdb file
    skippedAtoms = [] # Keep a list of skipped atoms for later
    skippedResidues = []
    skippedChains = []

    for chain in project.molecule.allChains():
        skippChain = True
        for res in chain.allResidues():
            if not res.hasProperties('nucleic'):
                skippedResidues.append(res)
                for atm in res.allAtoms():
                    atm.pdbSkipRecord = True
                    skippedAtoms.append( atm )
                #end for
            else:
                res.x3dna = NTlist()
                skippChain = False
            #end if
            if skippChain:
                skippedChains.append(chain)
        #end for
    #end for
    if skippedResidues:
        NTmessage('x3dna: non-nucleotides %s will be skipped.',  skippedResidues)



    # We do not specify any output files, these are set based on the input filename in the x3dna.csh script
    # pdbFile=project.molecule.toPDB()
    nModels = project.molecule.modelCount
    name = project.molecule.name
#    modelDict={}
    for modelNum in NTprogressIndicator(range(nModels)):
#    for modelNum in range(0, nModels):
        NTmessage('Running X3DNA on modelNum %i of %s' % (modelNum, name))
        baseName = '%s_model_%i' % (name, modelNum)
        pdbFilePath = os.path.join(rootPath, baseName + '.pdb')
        moleculeToPDBfile(project.molecule, pdbFilePath, model = modelNum)
        status = x3dna(rootPath, baseName)
        if status:
            NTerror("Failed to run x3dna for modelNum %d" % modelNum)
            return None
#        modelDict[modelNum]=parseX3dnaOutput(baseName+'.out')
        results = parseX3dnaOutput(os.path.join(rootPath, baseName + '.out'))
        if not results:
            NTerror("Failed to parseX3dnaOutput")
            return None
        NTdebug( "X3DNA results: %s" % results )
#        print results

    # Restore the 'default' state
    for atm in skippedAtoms:
        atm.pdbSkipRecord = False

    project.x3dnaStatus.completed    = True
    project.x3dnaStatus.parsed       = True

    return True

def parseX3dnaOutput(fileName):
    """
    Parse x3dna generated output, we only parse the ".out" file.
    Store result in x3dna dictionary

    format file:
    """

    # Read in the output file, and split into the different parameter blocks
    x3dnaOutput = open(fileName, 'r').read()
    parameterBlocks = x3dnaOutput.split('****************************************************************************')

    # loop over the parameterBlocks
    results = {}
    for parameterBlock in parameterBlocks:
        # identify the parameter block type
        # Parse the block
        r = parseX3dnaParameterBlock(parameterBlock)
        for key in r.keys():
            results[key] = results.get(key, {})
            results[key].update(r[key])
    return results

def identifyParameterBlock(block):
    # Identify the block by the first line
#    print '#',block.split('\n')[1]
    found = False
    for parameterBlockId, infoText in x3dnaOutputInfoDict.iteritems():
#        print parameterBlockId, infoText
        try:
            if block.split('\n')[1].strip() in infoText:
                found = True
                break
        except IndexError:
            pass
    if found:
        return parameterBlockId, infoText
    else:
        return None, None

def step2bp(step):
    '''
    converts "GA/TC" to "G-C"
    '''
    return step[0] + '-' + step[-1]

def parseX3dnaParameterBlock(parameterBlock):
    '''
    Parses various parameter blocks in X3DNA output.
    Results are stored on basis of base pairs.
    In case of step parameters, the result is stored as an attribute of the first base pair
    i.e.
    1 GA/TC     -0.86      0.54      2.99     -4.13      2.08     31.35
    is stored as in bp "1 G-C"
    '''
    parameterBlockId, infoText = identifyParameterBlock(parameterBlock) #@UnusedVariable
    splitLines = parameterBlock.split('\n')
    parseLine = False
    results = {}
    if parameterBlockId == 'localBPPars':
        #     bp        Shear    Stretch   Stagger    Buckle  Propeller  Opening
        #    1 G-C      -0.44     -0.22     -0.62     -2.36      3.15     -3.95
        #    2 A-T      -0.09     -0.22     -0.19     12.78     -7.95     -0.93
        #    ......
        #          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #      ave.      0.02     -0.24      3.33      0.20      4.00     33.41
        #      s.d.      0.71      0.90      0.26      3.68      8.17      6.97
        for line in splitLines:
            if line.strip() == '':
                continue
            elif line.split()[0] == 'bp':
                parseLine = True
                continue
            elif line.split()[0] == '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~':
                break
            elif parseLine == True:
                bp = int(line.split()[0])
                results[bp] = results.get(bp, {})
                results[bp].update(dict(
                                        bp_str = line.split()[1],
                                        shear = parseX3dnaFloat(line.split()[2]),
                                        stretch = parseX3dnaFloat(line.split()[3]),
                                        stagger = parseX3dnaFloat(line.split()[4]),
                                        buckle = parseX3dnaFloat(line.split()[5]),
                                        propeller = parseX3dnaFloat(line.split()[6]),
                                        opening = parseX3dnaFloat(line.split()[7])
                                        )
                                   )

    if parameterBlockId == 'localBPStepPars':
        #    step       Shift     Slide      Rise      Tilt      Roll     Twist
        #   1 GA/TC     -0.86      0.54      2.99     -4.13      2.08     31.35
        #   2 AA/TT     -0.88     -0.27      3.34     -4.59      3.92     39.72
        #    ......
        #          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #      ave.      0.02     -0.24      3.33      0.20      4.00     33.41
        #      s.d.      0.71      0.90      0.26      3.68      8.17      6.97
        for line in splitLines:
            if line.strip() == '':
                continue
            elif line.split()[0] == 'step':
                parseLine = True
                continue
            elif line.split()[0] == '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~':
                break
            elif parseLine == True:
                step = int(line.split()[0])
                bp = step
                step_str = line.split()[1]
                bp_str = step2bp(step_str)
                results[bp] = results.get(bp, {})
                results[bp].update(dict(
                                    step = step,
                                    step_str = step_str,
                                    bp_str = bp_str,
                                    shift = parseX3dnaFloat(line.split()[2]),
                                    slide = parseX3dnaFloat(line.split()[3]),
                                    rise = parseX3dnaFloat(line.split()[4]),
                                    tilt = parseX3dnaFloat(line.split()[5]),
                                    roll = parseX3dnaFloat(line.split()[6]),
                                    twist = parseX3dnaFloat(line.split()[7])
                                    )
                                )

    if parameterBlockId == 'grooveWidthsPPDist':
        #                  Minor Groove        Major Groove
        #                 P-P     Refined     P-P     Refined
        #   1 GA/TC       ---       ---       ---       ---
        #   2 AA/TT       ---       ---       ---       ---
        #   3 AT/AT      11.2       ---      15.9       ---
        #   4 TT/AA      11.1      11.0      16.1      15.3
        #   5 TG/CA      13.2      13.1      18.5      17.5
        for line in splitLines:
            if line.strip() == '':
                continue
            elif line.split()[0] == 'P-P':
                parseLine = True
                continue
            elif parseLine == True:
                line = line.replace('---', '-0')
                step = int(line.split()[0])
                bp = step
                step_str = line.split()[1]
                bp_str = step2bp(step_str)
                results[bp] = results.get(bp, {})
                results[bp].update(dict(
                                    step = step,
                                    step_str = step_str,
                                    bp_str = bp_str,
                                    minPP = parseX3dnaFloat(line.split()[2]),
                                    minPP_ref = parseX3dnaFloat(line.split()[3]),
                                    majPP = parseX3dnaFloat(line.split()[4]),
                                    majPP_ref = parseX3dnaFloat(line.split()[5])
                                    )
                                )

    if parameterBlockId == 'sugarConfParameters':
        # function can be replaced by built in functions in CING
        #Strand I
        # base       v0      v1      v2      v3      v4      tm       P    Puckering
        #   1 G    -39.9    46.9   -36.6    14.9    15.5    46.3   142.2    C1'-exo
        #   2 A    -36.8    46.6   -38.5    18.5    11.3    45.8   147.3    C2'-endo
        #   3 A    -25.3    38.1   -36.2    22.8     1.3    38.6   159.4    C2'-endo

        #Strand II
        # base       v0      v1      v2      v3      v4      tm       P    Puckering
        #   1 C    -15.9   -11.7    32.7   -42.2    37.6    42.6    39.9    C4'-exo
        #   2 T    -39.3    30.4   -11.4   -10.8    31.2    38.0   107.4    O4'-endo
        #   3 T    -40.8    40.2   -24.8     2.1    24.2    41.7   126.5    C1'-exo
        pass

    if parameterBlockId == 'diNucStepClassRHelix':
        #    step       Xp      Yp      Zp     XpH     YpH     ZpH    Form
        #   1 GA/TC   -2.80    9.22   -0.29   -2.10    9.21    0.32     B
        #   2 AA/TT   -2.96    8.85    0.08   -3.60    8.80    0.85     B
        #   3 AT/AT   -3.26    9.19   -0.04   -5.33    9.19    0.23     B
        #   4 TT/AA   -3.16    8.94    0.32   -4.07    8.92    0.76     B
        #   5 TG/CA   -2.87    9.09    0.20   -3.91    8.88    1.92     B
        #   6 GT/AC   -2.57    9.40    0.01   -2.32    9.36   -0.90     B
        #   7 TG/CA   -2.15    9.15    0.59   -3.21    9.11    1.13
        #   8 GA/TC   -2.51    9.25    0.94   -5.66    9.06    2.10
        pass

    if parameterBlockId == 'baseRmsds':
        #            Strand I                    Strand II          Helix
        #   1   (0.037) ....>A:...1_:[.DG]G-----C[.DC]:..22_:B<.... (0.022)     |
        #   2   (0.030) ....>A:...2_:[.DA]A-----T[.DT]:..21_:B<.... (0.023)     |
        pass

    if parameterBlockId == 'hbondInfo':
        #   1 G-----C  [3]  N2 - O2  2.80  N1 - N3  2.97  O6 - N4  2.91
        #   2 A-----T  [2]  N1 - N3  2.80  N6 - O4  2.88
        #   3 A-----T  [2]  N1 - N3  2.87  N6 - O4  2.80
        pass

    if parameterBlockId == 'polygonOverlapArea':
        #     step      i1-i2        i1-j2        j1-i2        j1-j2        sum
        #   1 GA/TC  3.94( 0.99)  0.00( 0.00)  0.00( 0.00)  7.62( 2.29) 11.56( 3.28)
        #   2 AA/TT  1.42( 0.26)  0.00( 0.00)  0.00( 0.00)  6.89( 1.23)  8.31( 1.49)
        pass

    if parameterBlockId == 'originAndMNVector':
        #      bp        Ox        Oy        Oz        Nx        Ny        Nz
        #    1 G-C      77.18     44.78     39.96     -0.80     -0.58     -0.16
        #    2 A-T      74.85     43.25     38.47     -0.84     -0.51     -0.17
        pass

    if parameterBlockId == 'localBPHelicalPars':
        #    step       X-disp    Y-disp   h-Rise     Incl.       Tip   h-Twist
        #   1 GA/TC      0.63      0.86      3.11      3.82      7.60     31.68
        #   2 AA/TT     -0.85      0.75      3.37      5.73      6.71     40.15
        pass

    if parameterBlockId == 'structureClass':
        #   This is a right-handed nucleic acid structure
        pass

    if parameterBlockId == 'lambda':
        #    bp     lambda(I) lambda(II)  C1'-C1'   RN9-YN1   RC8-YC6
        #   1 G-C      49.6      55.2      10.8       9.0       9.8
        #   2 A-T      53.5      53.6      10.5       8.8       9.6
        pass



    if parameterBlockId == 'globalHelixAxis':
        # Deviation from regular linear helix: 3.17(0.91)
        pass

    if parameterBlockId == 'mainChainAndChiAngles':
        #Strand I
        #  base    alpha    beta   gamma   delta  epsilon   zeta    chi
        #   1 G     ---     ---     57.6   138.6  -104.4   179.4  -104.7
        #   2 A    -64.7   125.2    48.1   141.5  -150.0  -149.0  -110.9

        #Strand II
        #  base    alpha    beta   gamma   delta  epsilon   zeta    chi
        #   1 C    -72.7   151.6    50.1    79.4    ---     ---   -125.3
        #   2 T    -68.6   168.3    51.7   105.8  -148.7   -91.0  -121.7
        pass

    if parameterBlockId == 'intraStrandDist':
        #                 Strand I                    Strand II
        #    base      P--P     C1'--C1'       base      P--P     C1'--C1'
        #   1 G/A       ---       5.1         1 C/T       6.1       4.9
        #   2 A/A       6.9       5.2         2 T/T       6.7       5.1
        pass

    if parameterBlockId == 'diNucStepPosition':
        #      bp        Px        Py        Pz        Hx        Hy        Hz
        #   1 GA/TC     76.62     43.18     39.13     -0.79     -0.54     -0.30
        #   2 AA/TT     73.14     42.30     39.01     -0.80     -0.51     -0.31
        pass

    if parameterBlockId == 'helixRadius':
        #                        Strand I                      Strand II
        #     step         P        O4'       C1'        P        O4'        C1'
        #   1 GA/TC      10.0       7.3       6.4       8.9       5.6       4.7
        #   2 AA/TT       9.7       7.7       6.8       9.4       6.2       5.6
        pass
    return results

#===============================================================================
# """
#        Example of processed data structure attached to say a residue (or molecule / chain / atom ):
#            "x3dna": {
#                "COMPCHK": {
#                    "valeList": [ 0.009, 0.100 ],
#                    "qualList": ["POOR", "GOOD" ]},
#                "BLABLACHK": {
#                    "valeList": [ 0.009, 0.100 ],
#                    }}
#                    """
# #
# # To create the datastructure:
# # self.molecule.setDeepByKeys([completenessMol], WATTOS_STR, COMPLCHK_STR, VALUE_LIST_STR)
# #
# # self.residue.setDeepByKeys([rollValue], X3DNA_STR, ROLLCHK_STR, VALUE_LIST_STR)
#===============================================================================


def averageX3dna(project, tmp = None):
    """Average x3dna array for each atom
    """
    pass

def restoreX3dna(project, tmp = None):
    """restore x3dna results for project.molecule
    Return project or None on error
    """
    pass


# Dictionary describing the identifier strings in x3dna output file, with shortKeys
x3dnaOutputInfoDict = \
{
'baseRmsds':
'''RMSD of the bases (----- for WC bp, + for isolated bp, x for helix change)''',

'hbondInfo':
'''Detailed H-bond information: atom-name pair and length [ON]''',

'polygonOverlapArea':
'''
Overlap area in Angstrom^2 between polygons defined by atoms on successive
bases. Polygons projected in the mean plane of the designed base-pair step.

Values in parentheses measure the overlap of base ring atoms only. Those
outside parentheses include exocyclic atoms on the ring. Intra- and
inter-strand overlap is designated according to the following diagram:

                    i2  3'      5' j2
                       /|\      |
                        |       |
               Strand I |       | II
                        |       |
                        |       |
                        |      \|/
                    i1  5'      3' j1
''',

'originAndMNVector':
'''
Origin (Ox, Oy, Oz) and mean normal vector (Nx, Ny, Nz) of each base-pair in
the coordinate system of the given structure
''',

'localBPPars':
'''Local base-pair parameters''',

'localBPStepPars':
'''Local base-pair step parameters''',

'localBPHelicalPars':
'''Local base-pair helical parameters''',

'structureClass':
'''Structure classification:''',

'lambda':
'''
lambda: virtual angle between C1'-YN1 or C1'-RN9 glycosidic bonds and the
base-pair C1'-C1' line

C1'-C1': distance between C1' atoms for each base-pair
RN9-YN1: distance between RN9-YN1 atoms for each base-pair
RC8-YC6: distance between RC8-YC6 atoms for each base-pair
''',

'diNucStepClassRHelix':
'''
Classification of each dinucleotide step in a right-handed nucleic acid
structure: A-like; B-like; TA-like; intermediate of A and B, or other cases
''',

'grooveWidthsPPDist':
'''
Minor and major groove widths: direct P-P distances and refined P-P distances
which take into account the directions of the sugar-phosphate backbones

(Subtract 5.8 Angstrom from the values to take account of the vdw radii
of the phosphate groups, and for comparison with FreeHelix and Curves.)

Ref: M. A. El Hassan and C. R. Calladine (1998). ``Two Distinct Modes of
     Protein-induced Bending in DNA.'' J. Mol. Biol., v282, pp331-343.
''',

'globalHelixAxis':
'''
Global linear helical axis defined by equivalent C1' and RN9/YN1 atom pairs
Deviation from regular linear helix: 2.85(0.76)
''',

'mainChainAndChiAngles':
'''
Main chain and chi torsion angles:

Note: alpha:   O3'(i-1)-P-O5'-C5'
      beta:    P-O5'-C5'-C4'
      gamma:   O5'-C5'-C4'-C3'
      delta:   C5'-C4'-C3'-O3'
      epsilon: C4'-C3'-O3'-P(i+1)
      zeta:    C3'-O3'-P(i+1)-O5'(i+1)

      chi for pyrimidines(Y): O4'-C1'-N1-C2
          chi for purines(R): O4'-C1'-N9-C4
''',

'sugarConfParameters':
'''
Sugar conformational parameters:

Note: v0: C4'-O4'-C1'-C2'
      v1: O4'-C1'-C2'-C3'
      v2: C1'-C2'-C3'-C4'
      v3: C2'-C3'-C4'-O4'
      v4: C3'-C4'-O4'-C1'

      tm: amplitude of pseudorotation of the sugar ring
      P:  phase angle of pseudorotation of the sugar ring
''',

'intraStrandDist':
'''Same strand P--P and C1'--C1' virtual bond distances''',

'helixRadius':
'''
Helix radius (radial displacement of P, O4', and C1' atoms in local helix
frame of each dimer)
''',

'diNucStepPosition':
'''
Position (Px, Py, Pz) and local helical axis vector (Hx, Hy, Hz)
for each dinucleotide step
'''
}

def parseX3dnaFloat(str):
    if str == X3DNA_NAN:
        return None
    return float(str)

# register the functions
methods = [(runX3dna, None),
           ]
#saves    = []

#restores = [
#            (restoreX3dna, None),
#           ]

#exports  = []
