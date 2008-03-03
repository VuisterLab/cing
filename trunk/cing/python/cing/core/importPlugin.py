from cing import cingPythonCingDir
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTexception
from cing.Libs.NTutils import NTpath
from cing.core.classes import Project
from cing.core.parameters import cingPaths
from cing.core.parameters import plugins
import glob
import os

#-----------------------------------------------------------------------------
# import the plugins
#-----------------------------------------------------------------------------
def importPlugin( pluginName ):
    """
    Import a plugin
    Returns None on error
    """
#    NTdebug('==> Importing plugin ' + pluginName)
    pluginCodeModule = 'cing.' + cingPaths.plugins
#    moduleName = cingPaths.plugins + '.' + pluginName
    if plugins.has_key(pluginName):
        try:
            plugin = plugins[pluginName]
#            NTdebug("reloading same module just to see it change")
            reload( plugin.module )
        except Exception:
            NTexception('A reload failed for ' + pluginName)
            return None
#    module = __import__( moduleName, globals(), locals(), [] )
#    NTmessage('==> Attempting import plugin ' + pluginName )
# by the manuals words:
# "However, when a non-empty fromlist argument is given, the module named by name is returned."
    pluginCodeModulePackage = __import__( pluginCodeModule,
                         globals(),
                         locals(),
                         [pluginName]) #JFD changed from default to zero which means to only try absolute imports.

#    NTdebug("pluginCodeModulePackage looks like: " + `pluginCodeModulePackage`)
    NTdebug('==> Imported plugin ' + pluginName )
    if not hasattr(pluginCodeModulePackage, pluginName):
        NTerror("Expected an attribute pluginName: " + pluginName + " for package: " + `pluginCodeModulePackage`)
        return None
#     set p to plugin module
    pluginModule = getattr( pluginCodeModulePackage, pluginName )
#    NTdebug("pluginModule looks like: " + `pluginModule`)

    plugin = NTdict( module = pluginModule, name = pluginName)
    #end try
#    NTdebug('==> Staging plugin ' + pluginName)
    plugins[pluginName] = plugin

    # update the methods, saves, restores and exports
    for attributeName in ['methods', 'saves', 'restores', 'exports']:
#        NTdebug("Now working on attribute: " + attributeName)
        plugin[attributeName] = []
        if attributeName in dir(plugin.module):
#            NTdebug("Now working on attributeName: " + attributeName)
            for function, other in getattr(plugin.module, attributeName):
#                NTdebug("Now working on function: " + function.__name__)
                setattr( Project, function.__name__, function )
                plugin[attributeName].append( (function, other) )
            #end for
        #end if
    #end for

    # msg = plugin.getAttr()

#    NTmessage('==> Staged plugin ' + plugin.module.__file__ )
    #end if
    return plugin

#end def

# get all *.py files in plugin directory excluding __init__
pluginDir = os.path.join(cingPythonCingDir, cingPaths.plugins)
pluginFileList  = glob.glob( os.path.join(pluginDir, '*.py') )
#NTdebug("found plugin file list: " + `pluginFileList`)
pluginFileList.remove( os.path.join( pluginDir, '__init__.py') )
#NTwarning("TODO: reintroduce the ccpn plugin code here once fixed")
pluginFileList.remove( os.path.join( pluginDir, 'ccpn.py') )
#NTwarning("TODO: reintroduce the validate plugin code here once fixed")
#pluginFileList.remove( os.path.join( pluginDir, 'validate.py') )
for p in pluginFileList:
    d,pname,e = NTpath(p)
    if not importPlugin( pname ):
        raise Exception("Failed to import plugin: " + pname)
#end for
del( pluginDir )
del( pluginFileList)
