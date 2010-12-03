"""
Adds x3dna method to analyze DNA structures. The x3dna program is included as binaries for Mac OSX in the bin directory.
"""
from cing import OS_TYPE_MAC
from cing import osType
from cing.Libs.NTplot import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqMatplib import MATPLIB_STR
from cing.PluginCode.required.reqX3dna import * #@UnusedWildImport
from cing.core.classes import Coplanar
from cing.core.classes import CoplanarList
from cing.core.parameters import cingPaths
from cing.core.parameters import plugins
from cing.core.parameters import validationSubDirectories

useModule = True
if osType == OS_TYPE_MAC: # only installed for mac os currently.
    if not os.path.exists(cingPaths.x3dna): # cingPaths.x3dna gets set in __init__ for MAC.
        NTdebug("Missing x3dna directory which is a dep for x3dna; currently only tested for mac and disabled for other os")
        useModule = False
else:
    useModule = False

if not useModule:
    raise ImportWarning('x3dna')

contentFile = 'content.xml'

X3DNA_NAN_START = '--' # or that starts with this. sometimes it's 3 sometimes it's 4.

class X3dna(NTdict):

    # Dictionary describing the identifier strings in x3dna output file, with shortKeys
    outputInfoDict = {
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

    def __init__(self, project, parseOnly = False, modelNum = None, **kwds):
        NTdict.__init__(self, __CLASS__ = 'X3dna', **kwds)
        self.project = project
        self.coplanars = project.coplanars
        self.molecule = project.molecule # love this one.
        self.modelCount = project.molecule.modelCount


    def x3dnaPath(self, *args):
        """
        Return x3dna path from active molecule of project
        Creates directory if does not exist
        """
        return self.project.validationPath(validationSubDirectories['x3dna'], *args)


    def doX3dna(self):
        """
        Runs x3dna on all models found in the project file.
        The input file for X3DNA is a pdbFile
        The routine writes all the models found in the project file to separate pdb file, which are analyzed using x3dna:
            - x3dna.csh (cingPaths.x3dna) is a shell script that calls the various subroutines of the x3dna package and writes
              output files in rootPath:
                - find_pair

        Return None on error.
        """
        if not self.molecule:
            NTerror('X3dna: no molecule defined')
            return

        root = self.project.mkdir(self.project.molecule.name, self.project.moleculeDirectories.x3dna)
        rootPath = root
        #    if not project.molecule.hasDNA():
        if not self.project.molecule.hasNucleicAcid():
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
        self.project.x3dnaStatus.completed = False
        self.project.x3dnaStatus.parsed = False
        self.project.x3dnaStatus.version = cing.cingVersion
        self.project.x3dnaStatus.moleculeName = self.project.molecule.name # just to have it
        #    project.x3dnaStatus.models       = models
        #    project.x3dnaStatus.baseName     = baseName
        self.project.x3dnaStatus.path = root
        self.project.x3dnaStatus.contentFile = contentFile
        self.project.x3dnaStatus.chains = NTlist()    # list of (chainNames, outputFile) tuples to be parsed
        self.project.x3dnaStatus.keysformat()

        # The input file for is a pdb file
        skippedAtoms = [] # Keep a list of skipped atoms for later
        skippedResidues = []
        skippedChains = []

        for chain in self.project.molecule.allChains():
            skippChain = True
            for res in chain.allResidues():
                if not res.hasProperties('nucleic'):
                    skippedResidues.append(res)
                    for atm in res.allAtoms():
                        atm.pdbSkipRecord = True
                        skippedAtoms.append(atm)
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
            NTmessage('x3dna: non-nucleotides %s will be skipped.', skippedResidues)



        # We do not specify any output files, these are set based on the input filename in the x3dna.csh script
        # pdbFile=project.molecule.toPDB()
        nModels = self.project.molecule.modelCount
        name = self.project.molecule.name

        if not self.coplanars:
            self.coplanars.append(CoplanarList('x3dna-made'))

        for modelNum in NTprogressIndicator(range(nModels)):
            NTmessage('Running X3DNA on modelNum %i of %s' % (modelNum, name))
            baseName = '%s_model_%i' % (name, modelNum)
            pdbFilePath = os.path.join(rootPath, baseName + '.pdb')
            self.project.molecule.toPDB(pdbFilePath, model = modelNum)
            status = x3dna(rootPath, baseName)
            if status:
                NTerror("Failed to run x3dna for modelNum %d" % modelNum)
                return None

            fileNameOut = os.path.join(rootPath, baseName + '.out')
            if self.parseX3dnaOutput(fileNameOut, modelNum):
                NTerror("Failed to parseX3dnaOutput for model id %d" % modelNum)
                return None
        # end for models

        # Restore the 'default' state
        for atm in skippedAtoms:
            atm.pdbSkipRecord = False

        self.project.x3dnaStatus.completed = True
        self.project.x3dnaStatus.parsed = True

        return True

    def parseX3dnaOutput(self, fileName, modelNum):
        """
        Parse x3dna generated output, we only parse the ".out" file.
        Store result in dictionary keyed by 'step' / suite.

        Currently, without reading the residue ids this might vary between models. TODO: fix this bug.
        """

        # Read in the output file, and split into the different parameter blocks
        x3dnaOutput = open(fileName, 'r').read()
        parameterBlocks = x3dnaOutput.split('****************************************************************************')

        for parameterBlock in parameterBlocks:
            # identify the parameter block type
            # Parse the block
            results = self.parseX3dnaParameterBlock(parameterBlock, modelNum)
            if results == None: # may be an empty dictionary.
                NTerror("Failed to parseX3dnaParameterBlock(parameterBlock) for %s" % parameterBlock)
                return True

            if self.storeX3dnaParameterBlock(results, modelNum):
                NTerror("Failed to parseX3dnaOutput for model id %d" % modelNum)
                return None

        return None

    def identifyParameterBlock(self, block):
        # Identify the block by the first line
        #    print '#',block.split('\n')[1]
        found = False
        for parameterBlockId, infoText in self.outputInfoDict.iteritems():
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

    def step2bp(self, step):
        '''
        converts "GA/TC" to "G-C"
        '''
        return step[0] + '-' + step[-1]

    def storeX3dnaParameterBlock(self, results, modelNum):
        '''
        stores results for one model and one block into CING data model

        For now; also link this to the first residues in the molecule; totally wrong but
        waiting for correspondence to handle this perfectly correct. TODO: finish correspondence.
        '''

        # generalized storing mechanism; see Whatif (here there's one level less).
        coplanarList = self.coplanars[0]
        coplanarIdList = results.keys()
        coplanarIdList.sort()

        for coplanarIdStr in coplanarIdList:
#            NTdebug("Working on coplanarIdStr: %s" % coplanarIdStr)
            coplanarId = int(coplanarIdStr) - 1 # should start at zero.

            # NB This code assumes that the x3dna analysis is done first and will create the coplanars
            # In future look up by residue ids.
            if len(coplanarList) <= coplanarId:
                coplanar = Coplanar(name = coplanarIdStr)
                x3dnaCoplanar = NTdict()
                coplanar[X3DNA_STR] = x3dnaCoplanar
                # TODO: Fix this.
                bogusResidueToLinkForNow = self.molecule.allResidues()[coplanarId]
                bogusResidueToLinkForNow[X3DNA_STR] = x3dnaCoplanar
                NTdebug("Added coplanar to bogus residue TODO")
                coplanarList.append(coplanar)
            # end if

            # take a short cut name.
            x3dnaCoplanar = getDeepByKeys(coplanarList, coplanarId, X3DNA_STR)
            for entity in results[coplanarIdStr].keys():
#                NTdebug("Working on entity: %s" % entity)
                valueList = getDeepByKeysOrDefault(x3dnaCoplanar, NTfill(None, self.modelCount), entity)
                valueList[modelNum] = results[coplanarIdStr][entity]
#                NTdebug("Set value for coplanarIdStr %s entity %s modelNum: %s to be: %s" % (coplanarIdStr, entity, modelNum, valueList[modelNum]))
            # end for entity
        # end for coplanar
        return

    def parseX3dnaParameterBlock(self, parameterBlock, modelNum):
        '''
        Parses various parameter blocks in X3DNA output.
        Results are stored on basis of base pairs.
        In case of step parameters, the result is stored as an attribute of the first base pair
        i.e.
        1 GA/TC     -0.86      0.54      2.99     -4.13      2.08     31.35
        is stored as in bp "1 G-C"

            Example of processed data structure in a dictionary object of class Coplanar:

                x3dna.rise : [ 4.73, 3.99 ] for the first and second model.
        '''
        parameterBlockId, infoText = self.identifyParameterBlock(parameterBlock) #@UnusedVariable
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
                wordList = line.split()
                if line.strip() == '':
                    continue
                elif wordList[0] == 'bp':
                    parseLine = True
                    continue
                elif wordList[0] == '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~':
                    break
                elif parseLine == True:
                    bp = int(wordList[0])
                    results[bp] = results.get(bp, {})
                    results[bp].update(dict(
                                            bp_str = wordList[1],
                                            shear = self.parseX3dnaFloat(wordList[2]),
                                            stretch = self.parseX3dnaFloat(wordList[3]),
                                            stagger = self.parseX3dnaFloat(wordList[4]),
                                            buckle = self.parseX3dnaFloat(wordList[5]),
                                            propeller = self.parseX3dnaFloat(wordList[6]),
                                            opening = self.parseX3dnaFloat(wordList[7])
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
                wordList = line.split()
                if line.strip() == '':
                    continue
                elif wordList[0] == 'step':
                    parseLine = True
                    continue
                elif wordList[0] == '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~':
                    break
                elif parseLine == True:
                    step = int(wordList[0])
                    bp = step
                    step_str = wordList[1]
                    bp_str = self.step2bp(step_str)
                    results[bp] = results.get(bp, {})
                    results[bp].update(dict(
                                        step = step,
                                        step_str = step_str,
                                        bp_str = bp_str,
                                        shift = self.parseX3dnaFloat(wordList[2]),
                                        slide = self.parseX3dnaFloat(wordList[3]),
                                        rise = self.parseX3dnaFloat(wordList[4]),
                                        tilt = self.parseX3dnaFloat(wordList[5]),
                                        roll = self.parseX3dnaFloat(wordList[6]),
                                        twist = self.parseX3dnaFloat(wordList[7])
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
                wordList = line.split()
                if line.strip() == '':
                    continue
                elif wordList[0] == 'P-P':
                    parseLine = True
                    continue
                elif parseLine == True:
#                    line = line.replace('---', '-0') # watch out these are not zero but NAN
                    wordList = line.split()
#                    NTdebug('wordList %r' % wordList)
                    step = int(wordList[0])
                    bp = step
                    step_str = wordList[1]
                    bp_str = self.step2bp(step_str)
                    results[bp] = results.get(bp, {})
                    results[bp].update(dict(
                                        step = step,
                                        step_str = step_str,
                                        bp_str = bp_str,
                                        minPP = self.parseX3dnaFloat(wordList[2]),
                                        minPP_ref = self.parseX3dnaFloat(wordList[3]),
                                        majPP = self.parseX3dnaFloat(wordList[4]),
                                        majPP_ref = self.parseX3dnaFloat(wordList[5])
                                        )
                                    )

        if parameterBlockId == 'sugarConfParameters':
            # function can be replaced by built in functions in CING except this might
            # be nice and easy for puckering amplitude and phase to be harvested.
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
    # end def

    def parseX3dnaFloat(self, str):
#        NTdebug("Found X3dnaFloat wannabe: %s" % str)
        if str.startswith(X3DNA_NAN_START):
#            NTdebug("Parsed X3dnaFloat as NAN")
            return NaN
        return float(str)
# end class

def createHtmlX3dna(project, ranges = None):
    """ Read out wiPlotList to see what get's created. """

    if not getDeepByKeysOrAttributes(plugins, MATPLIB_STR, IS_INSTALLED_STR):
        NTdebug('Skipping createHtmlWattos because no matplib installed.')
        return
    from cing.PluginCode.matplib import MoleculePlotSet #@UnresolvedImport

    # The following object will be responsible for creating a (png/pdf) file with
    # possibly multiple pages
    # Level 1: row
    # Level 2: against main or alternative y-axis
    # Level 3: plot parameters dictionary (extendible).

    keyLoLoL = []
    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ X3DNA_STR, SHIFT_STR]
    plotAttributesRowMain[ KEY_LIST2_STR] = [ X3DNA_STR, SLIDE_STR]
    plotAttributesRowMain[ KEY_LIST3_STR] = [ X3DNA_STR, RISE_STR]
    plotAttributesRowMain[ YLABEL_STR] = shortNameDict[  SHIFT_STR ]
    keyLoLoL.append([ [plotAttributesRowMain] ])

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ X3DNA_STR, TILT_STR]
    plotAttributesRowMain[ KEY_LIST2_STR] = [ X3DNA_STR, ROLL_STR]
    plotAttributesRowMain[ KEY_LIST3_STR] = [ X3DNA_STR, TWIST_STR]
    plotAttributesRowMain[ YLABEL_STR] = shortNameDict[  TILT_STR ]
    keyLoLoL.append([ [plotAttributesRowMain] ])

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ X3DNA_STR, SHEAR_STR]
    plotAttributesRowMain[ KEY_LIST2_STR] = [ X3DNA_STR, STRETCH_STR]
    plotAttributesRowMain[ KEY_LIST3_STR] = [ X3DNA_STR, STAGGER_STR]
    plotAttributesRowMain[ YLABEL_STR] = shortNameDict[  SHEAR_STR ]
    keyLoLoL.append([ [plotAttributesRowMain] ])

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ X3DNA_STR, BUCKLE_STR]
    plotAttributesRowMain[ KEY_LIST2_STR] = [ X3DNA_STR, PROPELLER_STR]
    plotAttributesRowMain[ KEY_LIST3_STR] = [ X3DNA_STR, OPENING_STR]
    plotAttributesRowMain[ YLABEL_STR] = shortNameDict[  BUCKLE_STR ]
    keyLoLoL.append([ [plotAttributesRowMain] ])

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ X3DNA_STR, MINPP_STR]
    plotAttributesRowMain[ KEY_LIST2_STR] = [ X3DNA_STR, MAJPP_STR]
    plotAttributesRowMain[ YLABEL_STR] = shortNameDict[  MINPP_STR ]
    plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
    plotAttributesRowMain[ USE_MAX_VALUE_STR] = 30.0
    keyLoLoL.append([ [plotAttributesRowMain] ])

    printLink = project.moleculePath(X3DNA_STR, project.molecule.name + x3dnaPlotList[0][0] + ".pdf")

    moleculePlotSet = MoleculePlotSet(project = project, ranges = ranges, keyLoLoL = keyLoLoL)
    moleculePlotSet.renderMoleculePlotSet(printLink, createPngCopyToo = True)
#end def

def runX3dna(project, parseOnly = False, modelNum = None):
    x3dna = X3dna(project, parseOnly = parseOnly, modelNum = modelNum)
    return x3dna.doX3dna()

# register the functions
methods = [(runX3dna, None),
           ]
#saves    = []

#restores = [
#            (restoreX3dna, None),
#           ]

#exports  = []
