from cing import cingPythonCingDir
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTstruct
from cing.Libs.NTutils import printDebug
from cing.Libs.NTutils import printMessage
from cing.core.classes import Project
from cing.core.parameters import cingPaths
from cing.core.parameters import plugins
from cing.Libs.NTutils import printWarning
import cing
import glob
import os
import traceback

#-----------------------------------------------------------------------------
# import the plugins
#-----------------------------------------------------------------------------
def importPlugin( pluginName ):
    """
    Import a plugin
    Returns None on error
    """
#    printDebug('==> Importing plugin ' + pluginName)
    try:
        plugin = plugins[pluginName]
        reload( plugin.module )
    except KeyError, AttributeError:
        moduleName = 'cing.' + cingPaths.plugins + '.' + pluginName
#        printDebug('A reload failed for ' + pluginName)
        try:
            module = __import__( moduleName, globals(), locals(), [] )
        except ImportError:
            NTerror('ERROR importPlugin: plugin "%s"\n', pluginName )
            traceback.print_exc()
            return None
        #end try
        # set p to plugin module
        print module
        print dir(module)
        p = getattr( module, pluginName )
        plugin = NTstruct( module = p, name = pluginName)
    #end try
#    printDebug('==> Staging plugin ' + pluginName)
    plugins[pluginName] = plugin

    # update the methods, saves, restores and exports
    # plugin.methods        list of tuples (methods-function, object) 
    # plugin.saves          list of tuples (save-function, object)
    # plugin.restores       list of tuples (restore-function, object)
    # plugin.exports        list of tuples (export-function, object)

    for attributeName in ['methods', 'saves', 'restores', 'exports']:
        plugin[attributeName] = []
        if attributeName in dir(plugin.module):
            for f,o in getattr(plugin.module, attributeName):
                setattr( Project, f.__name__, f )
                plugin[attributeName].append( (f, o) )
            #end for
        #end if
    #end for

#    plugin.printAttr()
       
    printMessage('==> Imported plugin ' + plugin.module.__file__ )
    #end if
    return plugin

#end def

# get all *.py files in plugin directory excluding __init__
pluginDir = os.path.join(cingPythonCingDir, cingPaths.plugins)
pluginFileList  = glob.glob( os.path.join(pluginDir, '*.py') )
#printDebug("found plugin file list: " + `pluginFileList`)
pluginFileList.remove( os.path.join( pluginDir, '__init__.py') )
printWarning("TODO: reintroduce the ccpn plugin code here once fixed")
pluginFileList.remove( os.path.join( pluginDir, 'ccpn.py') )
printWarning("TODO: reintroduce the validate plugin code here once fixed")
pluginFileList.remove( os.path.join( pluginDir, 'validate.py') )
for p in pluginFileList:
    d,pname,e = NTpath(p)
    importPlugin( pname )
#end for
del( pluginDir )
del( pluginFileList)
