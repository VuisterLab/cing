"""
Add some Yasara commands to cing.

#Example commands to get to CING ipython prompt using a project with a molecule loaded already.
cd $CINGROOT/Tests/data/cing
cing --name 1brv --old --ipython

#Example commands possible from CING ipython prompt:
project.yasaraShell()

# Get the Yasara "heads up display" and enter the Yasara ipython shell.
hud(1)

# Copy your CING structure to: 1brv.cing/1brv/Macros/Yasara/1brv.pdb
# and have Yasara load it.
loadPDB()

# Use the information in CING to color the residues according to their ROG score in Yasara
colorROG()

# Save for the family archives
screenDump(project.name+'.png')

#Hit ^D four times to leave Yasara and CING shells.
"""

from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.PluginCode.required.reqYasara import YASARA_STR
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Atom
from cing.main import pformat
from cing.main import startIpythonShell

try:
#    import yasara
#    from yasaramodule import *
    from yasara import HUD #@UnresolvedImport
    from yasaramodule import ColorPar #@UnresolvedImport
    from yasaramodule import ColorRes #@UnresolvedImport
    from yasaramodule import Console #@UnresolvedImport
    from yasaramodule import LoadPDB #@UnresolvedImport
    from yasaramodule import MarkAtom #@UnresolvedImport
    from yasaramodule import PropRes #@UnresolvedImport
    from yasaramodule import SaveBmp #@UnresolvedImport
    from yasaramodule import Style #@UnresolvedImport
except:
    raise ImportWarning(YASARA_STR)
finally: # finally fails in python below 2.5
    switchOutput(True)

# it only seems to work this way, we would need to make this a variable in the setup
#sys.path.append(os.path.join('/Applications/YASARA-dynamics 8.2.3.app/yasara/','pym'))
#sys.path.append(os.path.join('/Applications/YASARA-dynamics 8.2.3.app/yasara/','plg'))

def yasaraShell(project):

    if not cing.yasaradir:
        nTcodeerror('yasaraShell: please put a proper yasara.py module on PYTHONPATH first (check yasaradir!)')
        exit(1)

    # shortcuts
    f = pformat             #@UnusedVariable # pylint: disable=W0612
    p = project             #@UnusedVariable # pylint: disable=W0612
    mol = project.molecule  #@UnusedVariable # pylint: disable=W0612

    def commands(): # pylint: disable=W0612
        cmds = ['commands', 'colorByResidue', 'colorGF', 'colorJanin', 'colorROG', 'colorWhatif',
                'getSelectedResidue', 'hud', 'loadPDB', 'screenDump', 'showHtml']
        cmds.sort()
        for c in cmds:
            nTmessage( c )
        #end for
    #end def

    def loadPDB(model = None):
        """
        Load project.molecule model [0,modelCount-1] or all models if None
        """
        if not project.molecule:
            nTerror('loadPDB: no molecule defined')
            return True

        if model == None or model == 'all':
            path = project.moleculePath('yasara', sprintf('%s.pdb', project.molecule.name))
            model = None
        else:
            path = project.moleculePath('yasara', sprintf('%s_%s.pdb', project.molecule.name, model))

        project.molecule.toPDBfile(path, model = model)

        nTmessage('loadPDB: %s' % path)
        LoadPDB(os.path.abspath(path))
        Style('Ribbon', 'off')
    #end def
    # alternate names
    loadpdb = loadPDB #@UnusedVariable # pylint: disable=W0612
    loadPdb = loadPDB #@UnusedVariable # pylint: disable=W0612

    def colorROG(object = 1): # pylint: disable=W0612
        """
        Color residues according to Cing ROG score
        """
        Console('off')
        ColorRes('object ' + str(object), 'Gray')
        yasaraColorDict = dict(green = 240, orange = 150, red = 120)

        for res in project.molecule.allResidues():
            cmd = sprintf('object %s residue %d,%s', object, res.resNum, yasaraColorDict[res.rogScore.colorLabel])
            ColorRes(cmd)
        #end for
        Console('on')
    #end def

    def colorGF(object = 1, minValue = -3.0, maxValue = 1.0): # pylint: disable=W0612
        """
        Color residues according to Procheck gf score
        """
        colorByResidue(['procheck', 'gf'],
                          minValue = minValue, maxValue = maxValue,
                          reverseColorScheme = True
                       )
    #end def

    def colorWhatif(checkId, object = 1, minValue = -4.0, maxValue = 1.0, reverseColorScheme = True):
        """
        Color according to Whatif checkId score
        """
        Console('off')
        objectStr = 'object ' + str(object)
        ColorRes(objectStr, 'Gray')
        PropRes(objectStr, -999)

        if reverseColorScheme:
            ColorPar('Property ', 'Min', 'red', minValue)
            ColorPar('Property ', 'Max', 'blue', maxValue)
        else:
            ColorPar('Property ', 'Min', 'blue', minValue)
            ColorPar('Property ', 'Max', 'red', maxValue)

        for res in project.molecule.allResidues():
            list = getDeepByKeysOrAttributes(res, WHATIF_STR, checkId, VALUE_LIST_STR)
            if list:
                value, _sd, _n = list.average()
                if value != None and not isNaN(value):
                    PropRes(sprintf('object %s Residue %d', object, res.resNum), value)
                #end if
            #end if
        #end for
        ColorRes(objectStr, 'Property')
        Console('on')
    #end def

    def colorRama(object = 1): # pylint: disable=W0612
        """
        Color according to Whatif ramachandran score
        """
        colorWhatif('ramachandran', object = object, minValue = -1.5, maxValue = 1.0)

    def colorJanin(object = 1): # pylint: disable=W0612
        """
        Color according to Whatif janin score
        """
        colorWhatif('janin', object = object, minValue = -1.5, maxValue = 1.0)

    def colorByResidue(keys, object = 1,
                       minValue = 0.0, maxValue = 1.0, reverseColorScheme = False
                      ):
        Console('off')
        objectStr = 'object ' + str(object)
        ColorRes(objectStr, 'Gray')
        PropRes(objectStr, -999)
        #end if
        if reverseColorScheme:
            ColorPar('Property ', 'Min', 'red', minValue)
            ColorPar('Property ', 'Max', 'blue', maxValue)
        else:
            ColorPar('Property ', 'Min', 'blue', minValue)
            ColorPar('Property ', 'Max', 'red', maxValue)

        for res in project.molecule.allResidues():
            value = getDeepByKeysOrAttributes(res, *keys)
    #        if res.has_key(property) and res[property] != None and not isNaN(res[property]):
            if value != None and not isNaN(value):
                PropRes(sprintf('object %s Residue %d', object, res.resNum), value)
        #end for

        ColorRes(objectStr, 'Property')
        Console('on')
    #end def

    def getSelectedResidue():
        """
        Get the residue that is selected in yasara
        """
        atomId = MarkAtom()[0]
        if int(atomId) == 0:
            nTerror('getSelectedResidue: nothing selected')
            return None
        a = Atom('atom ' + str(atomId))
        fields = str(a).split()
        atmName = fields[2]
        resName = fields[3]
        chainName = fields[4]
        resNum = int(fields[5])
        nTmessage( 'Selected:', chainName, resName, resNum, atmName )
        nameTuple = (project.molecule.name, chainName, resNum, None, None, None, IUPAC)
        #print nameTuple
        res = project.molecule.decodeNameTuple(nameTuple)
        #print res
        return res
    #end def

    def showHtml():
        """
        Show the html page of the selected residue
        """
        res = getSelectedResidue()
        if not res:
            nTerror('showHtml: invalid residue')

        path = os.path.abspath(project.htmlPath('Molecule', res.chain.name, res.name, 'index.html'))
        nTmessage( 'showHtml: %s' % path )
        webbrowser.open('file://' + path) #@UndefinedVariable
    #end def
    showhtml = showHtml #@UnusedVariable # pylint: disable=W0612

    def screenDump(fileName, hideHUD = True):
        """
        Make a screen dump; optionally hide HUD temporarily (default True)
        """
        path = project.moleculePath('yasara', fileName)
        if hideHUD:
            hud('off')
        nTmessage( 'screenDump to: %s' % path )
        SaveBmp(path)
        hud('on')
    #end def
    screendump = screenDump #@UnusedVariable # pylint: disable=W0612

    def hud(toggle):
        """
        Toggle HUD on/off
        """
        if toggle == 'off':
            HUD('off', 'on')
        else:
            HUD('obj', 'on')
    #end def

    startIpythonShell(
        in_template =  sprintf('yasara (%s) \#> ', project.name),
        banner = '--------Dropping to yasara--------',
        exit_msg='--------Leaving yasara--------'
    )
#end def yasaraShell

methods  = [(yasaraShell, None),
           ]
#saves    = []
#restores = []
#exports  = []
